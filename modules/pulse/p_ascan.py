from __future__ import print_function

from io import open as file
from time import strftime,gmtime,sleep,localtime,asctime
from time import time as cputime
import numpy
numpy.seterr(all="ignore")
from numpy import round, array, sum, mean, loadtxt, savetxt
import os
import pylab
import IPython
from PyTango import DeviceProxy
from p_spec_syntax import wait_motor
from GetPositions import GetPositions

#THIS MODULE HAS TO BE COMPLETELY REWRITTEN:
#   Data must be saved in temporary folder in hdf and THEN moved to ruche avoiding home folder
#   Backup mechanism could be removed after.
#   Saving should be performed directly by pseudocounter with the actuator coordinates inserted afterwards

from mycurses import *

from p_spec_syntax import mv, wa, whois, findNextFileName, findNextFileIndex, filename2ruche

import speck_plot

#The following line is commented out
#from spec_syntax import whois
#The right way to import whois is to define it globally by executing the spec_syntax file
#during the startup. This is done by the starter. The import will work, 
#but the globals() containing the objects to search for will be almost empty...

#ScanStats instance of __scanstats must exist in globals to allow ascan to
#write into it statistics results of scan

class __scanstats:
    """This is a special object that should be instantiated with the name ScanStats in globals
    it is used to pass post scan staistics to the user or to be used during a script"""
    def __init__(self):
        self.min,self.max=None,None
        self.max_pos=None
        self.min_pos=None
        self.baricenter=None
        self.baricenter_scaled=None
        return
    def __call__(self):
        l=dir(self)
        for i in l:
            if not(i.startswith("_")):
                print(i+"=",eval("self."+i))
        return

ScanStats=__scanstats()

def ascan_statistics(x,y,glob):
    try:
        stats = eval("ScanStats", glob)
    except:
        return -1
    x, y = array(x), array(y)
    #Calculate baricenter
    sumay = sum(abs(y))
    if sumay != 0:
        stats.baricenter=sum(x * abs(y)) / sumay
    else:
        stats.baricenter = 0.5 * (min(x) + max(x))
    #Calculate_baseline substracted baricenter
    miny=min(y)
    sumay = sum(abs(y - miny))
    if sumay != 0:
        stats.baricenter_scaled=sum(x * abs(y - miny)) / sumay
    else:
        stats.baricenter_scaled = 0.5 * (min(x) + max(x))
    #Calculate max and max pos
    stats.max = max(y)
    stats.max_pos = x[y.argmax()]
    #Calculate min and min pos
    stats.min = min(y)
    stats.min_pos = x[y.argmin()]
    #Calculate pos of maximum derivative (+,-)
    return 0


def __backup_data():
    ##############################################################
    #
    #Define data and backup folders: backup only if
    #current folder is in data path
    #
    try:
        __IPy = get_ipython()
        __Default_Data_Folder = __IPy.user_ns["__SPECK_CONFIG"]["TEMPORARY_HOME"]
        __Default_Backup_Folder = __IPy.user_ns["__SPECK_CONFIG"]["DATA_FOLDER"]
        if __Default_Backup_Folder == "":
            print("No backup/ruche folder defined.")
            return
#the folder is set via the config:
        currentDataFolder=__IPy.user_ns["__SPECK_CONFIG"]["USER_FOLDER"]
#
        currentDataFolder=os.path.realpath(os.getcwd())
        print("Data Folder is :",currentDataFolder)
        if currentDataFolder.startswith(__Default_Data_Folder) and\
        len(currentDataFolder.split(os.sep))>len(__Default_Data_Folder.split(os.sep)):
            currentBackupFolder=__Default_Backup_Folder+"/"+\
            currentDataFolder.lstrip(__Default_Data_Folder.rstrip("/"))
            cbf=currentBackupFolder
            currentBackupFolder=cbf[:cbf.rstrip("/").rfind("/")]
        else:
            print("No backup!")
            return
        print("Backup Folder is :",currentBackupFolder)
    except (KeyboardInterrupt,SystemExit) as tmp:
        print("Backup halted on user request")
        raise tmp
    except:
        print("--------------------------------------------------------------------")
        print("WARNING:")
        print("Error defining backup folders... please, backup data files manually.")
        print("--------------------------------------------------------------------")
        return
        #NOTA:  This version make an integral backup of folder content
        # another strategy could be just to copy current data file.
        # but I prefer a complete backup including other files too.
        #Backup is performed in a separate shell by os.system
    try:
        command="rsync --ignore-existing -auv --temp-dir=/tmp '"+currentDataFolder+"' '"+currentBackupFolder+"'"
        os.system(command)
    except (KeyboardInterrupt,SystemExit) as tmp:
        print("Backup halted on user request")
        raise tmp
    except:
        print("Experimental feature error: Cannot make backup to ruche... do it manually!")
    return

def ascan(mot,p1,p2,dp=0.1,dt=0.1,channel=None,returndata=False,fulldata=False,name=None,delay=0.,delay0=0.,\
scaler="ct",comment="",fullmca=False,graph=1, n = 1):
    """Scan mot from p1 to p2 with step dp, reads ct for dt seconds. The default timebase is named ct."""
    glob  = get_ipython().user_ns
    shell = IPython.core.getipython.get_ipython()
    if "setSTEP" in glob.keys():
        glob["setSTEP"]()
    if p1 < p2:
        dp = abs(dp)
    else:
        dp = -abs(dp)
    __time_at_start = cputime()
    if channel == None: channel = 1
    __no_scans = n
    time_scan = False
    if scaler in glob:
        cpt = glob[scaler]
    else:
        raise Exception("Timebase not defined or wrong timebase name.")
    if name == None:
        name = "ascan_out"
    ext = "txt"
    if graph >=0:
        w = speck_plot.speck_figure(fign=graph, title=name, grid=(1,1))
    for scan_number in range(__no_scans):
        x = []
        y = []
        full = []
        current_name = findNextFileName(name, ext, file_index = scan_number + 1)
        ###################### FULL MCA FILES! #####################################
        if fullmca:
            dirname = current_name[:current_name.rfind(".")]+".d"
            mca_files = {}
        if fullmca:
            os.mkdir(dirname,0o777)
            for mca_channel in cpt.read_mca().keys():
                mca_files[mca_channel] = file(dirname + os.sep + current_name[:current_name.rfind(".")]+"_"+mca_channel+".txt","a")
                print(dirname + os.sep+name + "." + mca_channel)
        ###################### FULL MCA FILES! #####################################
        f=file(current_name, "w")
        print("Saving in file: ",current_name)
        shell.logger.log_write("Saving data in: %s\n" % current_name, kind='output') 
        try:
            if "label" in dir(mot):    f.write("#ascan over motor: "+mot.label+"\n")
        except (KeyboardInterrupt,SystemExit) as tmp:
            print("Scan finished on user request")
            raise tmp
        except:
            pass
        try:
            if mot != cputime:
                motname = whois(mot)
                f.write("#mot=%s p1=%g p2=%g dp=%g dt=%g\n"%(motname, p1, p2, dp, dt))
                if graph >=0:
                    w.set_axis_labels(motname,"ct[%i]"%channel,0)
            else:
                time_scan = True
                motname = "time"
                f.write("#mot=%s p1=%g p2=%g dp=%g dt=%g\n" % (motname, p1, p2, dp, dt))
                if graph >=0:
                    w.set_axis_labels(motname,"ct[%i]"%channel,0)
        except (KeyboardInterrupt,SystemExit) as tmp:
            print("Scan finished on user request")
            f.close()
            __backup_data()
            raise tmp
        except Exception as tmp:
            motname="None"
            print(tmp)
            pass
        print("motor name is : ", motname)
        f.write("#Following line is a comment:")
        f.write("#"+comment+"\n")
        #Call pre scan function:
        pre_scan(handler=f)
        #
        no_channels=len(cpt.read())
        #Mark Header with a special card
        f.write("#HEADER\n")
        #f.write("#"+motname+"\t"+"\t".join(map(lambda x:"Chan%02i"%x,range(no_channels)))+"\tTimeFromEpoch\n")
        header="#" + motname + "\t"\
        + "\t".join(map(lambda x:x.label,cpt.user_readconfig))\
        + "\t".join(map(lambda x:x["name"],cpt.posts))\
        + "\tTimeFromEpoch\n"        
#header="#"+motname+"\t"+"\t".join(map(lambda x:x.label,cpt.user_readconfig))+"\tTimeFromEpoch\n"
        f.write(header)
        try:
            if not time_scan: 
                #mot.pos(p1 - dp)
                mot.pos(p1)
            sleep(delay0)
            for i in arange(p1,p2+dp,dp):
                if not time_scan:
                    mot.pos(i)
                    sleep(delay)
                    x.append(mot.pos())
                else:
                    if delay>0.: sleep(delay)
                    if len(x)==0: 
                        x0=cputime()
                        x.append(0)
                    else:
                        x.append(cputime()-x0)
                __cts=cpt.count(dt)
                y.append(__cts[channel])
                if fulldata:
                    full.append(array(__cts))
                f.write("%14.13e"%(x[-1]))
                for j in __cts:
                    f.write("\t%10.8e"%(j))
                if not(time_scan):
                    f.write("\t%14.13e"%(cputime()))
                else:
                    f.write("\t%14.13e"%(x[-1]+x0))
                f.write("\n")
                ######################################################################################
                #            Write to Full MCA files
                ######################################################################################
                if fullmca:
                    __fullmca=cpt.read_mca()
                    for mca_channel in mca_files.keys():
                        __fullmca_line=__fullmca[mca_channel]
                        __fullmca_line_format="%d\t"*(len(__fullmca_line)-1)+"%d\n"
                        mca_files[mca_channel].write(__fullmca_line_format%tuple(__fullmca_line))
                ######################################################################################
                if graph >=0 and len(mod(x,5)==0):
                    w.plot(x,y,curve=0,update=True,marker="x",linestyle="--",linewidth=2,color="b")
            if graph >= 0:
                w.plot(x,y,curve=0,update=True,marker="x",linestyle="--",linewidth=2,color="b")

        except (KeyboardInterrupt,SystemExit) as tmp:
            print("Scan finished on user request")
            cpt.stop()
            f.close()
            __backup_data()
            raise tmp
        except Exception as tmp:
            f.close()
            raise tmp
        f.close()
        ##################### CLOSE MCA FILES ##################
        if fullmca:
            for mca_channel in mca_files.keys():
                mca_files[mca_channel].close()
        ########################################################

        try:
            __backup_data()
        except (KeyboardInterrupt,SystemExit) as tmp:
            print("Scan finished on user request")
            raise tmp
        except:
            pass
        #You could use this if persist=1 does not work:
        print("Elapsed Time: %8.6fs" % (cputime() - __time_at_start))
    #
    ml=min(len(x),len(y))
    #Call statistisc calculation
    if "ScanStats" in glob: 
        ascan_statistics(x[:ml], y[:ml], glob)
        print(BOLD + "\nScanStats:\n---------------------------" + RESET)
        print(glob["ScanStats"]())
        print("")
    #
    print("Total Elapsed Time: %8.6fs" % (cputime() - __time_at_start))
    #
    if returndata == True:
        if fulldata:
            full = array(full[:ml])
            return array([x[:ml], full.transpose()])
        else:
            return array([x[:ml], y[:ml]])
    return 

def dscan(mot,p1,p2,dp=0.1,dt=0.1,channel=1,returndata=False,fulldata=False,name=None,delay=0.,delay0=0.,scaler="ct",fullmca=False,graph=0):
    """Performs a relaive scan calling ascan and then set the motor back to previous position."""
    if name == None:
        name = "dscan_out"
    previous_pos=mot.pos()
    print("motor %s was at %g"%(whois(mot),mot.pos()))
    abs_p1=previous_pos+p1
    abs_p2=previous_pos+p2
    results=ascan(mot,abs_p1,abs_p2,dp,dt,channel,returndata,fulldata,name,delay=delay,delay0=delay0,scaler=scaler,fullmca=fullmca,graph=graph)
    mot.pos(previous_pos)
    if results != None:
        return results
    else:
        return

def tscan(n,t=1,channel=1,returndata=False,fulldata=False,name=None,delay=0.,delay0=0.,scaler="ct",comment="",fullmca=False,graph=0):
    """Perform a time scan by using ascan capabilities. The integration time t and number of points n must be provided. 
    You may use the delay to set a deadtime between steps... if you want... The time scale is referred to actual time."""
    if name == None:
        name = "tscan_out"
    return ascan(cputime, p1=0, p2=n * t, dp = t,dt = t,channel=channel,returndata=returndata,fulldata=fulldata,name=name,delay=delay,\
    delay0=delay0,scaler=scaler,comment=comment,fullmca=fullmca,graph=graph)

def mapscan(mot1,p11,p12,dp1,mot2,p21,p22,dp2,dt=0.1,channel=1,returndata=False,fulldata=False,name=None,delay=0.,delay0=0.,scaler="ct"):
    """Scan mot1 from p11 to p12 with step dp1;mot2 from p21 to p22 with step dp2; reads scaler for dt seconds. The default scaler is named ct."""
    x=[]
    y,y0=[],[]
    z,z0=[],[]
    if name==None:
        name="mapscan"
    ext="d"
    Dname=findNextFileName(name,ext,file_index=1)
    os.mkdir(Dname)
    print("Saving in folder: ",name)
    motname1=whois(mot1)
    try:
        for i in arange(p11,p12+dp1,dp1):
            mot1.pos(i)
            sleep(delay)
            #x.append(mot1.pos())
            print(Dname+"/"+name)
            #y0,z0=ascan(mot2,p21,p22,dp2,dt,channel,True,False,Dname+"/"+name,delay,glob,scaler,comment=motname1+"=%9.6f"%(mot1.pos()))
            y0,z0=ascan(mot2,p21,p22,dp2,dt,channel,True,False,Dname+"/"+name,delay,delay0,scaler,comment=motname1+"=%9.6f"%(mot1.pos()))
            #y.append(y0)
            z.append(z0)
    except (KeyboardInterrupt,SystemExit) as tmp:
        print("MapScan finished on user request")
    except Exception as tmp:
        raise tmp
    try:
        __backup_data()
    except:
        pass
    z=array(z)
    try:
        matshow(z)
    except Exception as tmp:
        print("matshow error")
        print(tmp)
    return

def pre_scan(handler=None):
    """Execute all operations needed before every and each scan."""
    buffer=[]
    buffer.append("#"+handler.name+"\n")
    try:
        GetPositions(verbose=0)
        for i in wa(verbose=False,returns=True):
            buffer.append("#"+i+"\n")
    except Exception as tmp:
        print(tmp)
        print("ascan: pre_scan: Error when getting motors positions!")
        pass
    try:
        buffer.append("#Machine Current = %g\n" % ( DeviceProxy("ans/ca/machinestatus").read_attribute("current").value) )
    except Exception as tmp:
        buffer.append("#Machine Current = nan\n")
        print(tmp)
    buffer.append("#"+asctime()+"\n")
    handler.writelines(buffer)
    return 

#Step scan (stepscan_open, stepscan_step, stepscan_close)
#__stepscan instance of __StepScan must exist in globals to allow stepscan to
#write into it common values
class __StepScan:
    def __init__(self):
        self.name=None
        self.datafile=None
        self.fullmca=None
        self.mca_files=None
        self.dt=None
        self.cpt=None
        return
    
    def erase(self):
        self.name=None
        self.datafile=None
        self.fullmca=None
        self.mca_files=None
        self.dt=None
        self.cpt=None
        return

#Initialize  instance
__stepscan=__StepScan()

def stepscan_open(name=None,dt=1,scaler="ct",comment="",fullmca=True):
    """Open output files and wait for stepscan_step command to save data, reads ct for dt seconds. The default timebase is named ct. fullmca is active by default."""
    glob  = get_ipython().user_ns
    try:
        __stepscan=eval("__stepscan",glob)
    except:
        glob["__stepscan"] = __StepScan()
        __stepscan=eval("__stepscan",glob)
    __stepscan.dt=dt
    __stepscan.fullmca=fullmca
    if scaler in glob:
        cpt=eval(scaler,glob)
    else:
        raise Exception("Timebase not defined or wrong timebase name.")
    __stepscan.cpt=cpt
    
    if name==None:
        name="ascan_out"
    ext="txt"
    name=findNextFileName(name,ext,file_index=1)    
    __stepscan.name=name
    ###################### FULL MCA FILES! #####################################
    if fullmca:
        dirname=name+".d"
        mca_files={}
        if fullmca:
            os.mkdir(dirname,0o777)
            for mca_channel in cpt.read_mca().keys():
                mca_files[mca_channel]=file(dirname+os.sep+name[:name.rfind(".")]+"_"+mca_channel+".txt","a")
                #print dirname+os.sep+name+"."+mca_channel
        __stepscan.mca_files=mca_files
    ###################### FULL MCA FILES! #####################################
    f=file(name,"w")
    __stepscan.datafile=f
    print("Saving in file: ",name)
    try:
        f.write("#stepscan\n")
        f.write("#dt=%g\n"%(dt))
    except:
        pass
    f.write("#Following line is a comment:\n")
    f.write("#"+comment+"\n")
    #Call pre scan function:
    pre_scan(handler=f)
    #
    no_channels=len(cpt.read())
    #Mark Header with a special card
    f.write("#HEADER\n")
    header="#"+"\t".join(map(lambda x:x.label,cpt.user_readconfig))+"\tTimeFromEpoch\n"
    f.write(header)
    return

    
#def stepscan_step(glob=globals()):
def stepscan_step():
    glob  = get_ipython().user_ns
    __stepscan=eval("__stepscan",glob)
    __cts=__stepscan.cpt.count(__stepscan.dt)
    for j in __cts:
        __stepscan.datafile.write("\t%10.8e"%(j))
    __stepscan.datafile.write("\t%14.13e"%(cputime()))
    __stepscan.datafile.write("\n")
    __stepscan.datafile.flush()
    ######################################################################################
    #            Write to Full MCA files
    ######################################################################################
    if __stepscan.fullmca:
        __fullmca=__stepscan.cpt.read_mca()
        for mca_channel in __stepscan.mca_files.keys():
            __fullmca_line=__fullmca[mca_channel]
            __fullmca_line_format="%d\t"*(len(__fullmca_line)-1)+"%d\n"
            __stepscan.mca_files[mca_channel].write(__fullmca_line_format%tuple(__fullmca_line))
    ######################################################################################
    return
    
#def stepscan_close(glob=globals()):
def stepscan_close():
    glob  = get_ipython().user_ns
    __stepscan=eval("__stepscan",glob)
    __stepscan.datafile.close()
    ##################### CLOSE MCA FILES ##################
    if __stepscan.fullmca:
        for mca_channel in __stepscan.mca_files.keys():
            __stepscan.mca_files[mca_channel].close()
    ########################################################
    try:
        __backup_data()
    except:
        pass
    __stepscan.erase()
    return


#Helpers
#scanfile_info is useless within pulse or should work in the future with HDF files.
def scanfile_info(name):
    f=file(name,"r")
    ll=f.readlines()
    f.close()
    head=ll[ll.index("#HEADER\n")+1][1:-1].split("\t")
    header=[]
    for i in head:
        if i!="": header.append(i)
    print(GREEN+"File contains %i columns"%len(header))
    print(RED+"Column\t"+BLUE+"Label"+RESET)
    i2=0
    for i in range(len(header)):
        i2+=1
        formats=RED+" %03i :"+BLUE+" %-20s   "+RESET
        print(formats%(i+1,header[i]), end=' ')
        if i2>0 and mod(i2,3)==0: print("")
    return 

def scanfile_xplot(name,col1=None,col2=None):
    if col1==None:
        print(RED+"\n----------->Please select columns for x and y!\n"+RESET)
        scanfile_info(name)
        return
    m=loadtxt(name).transpose()
    f = speck_plot.figure(fign=0, title=name, grid=(1,1))
    f.plot(m[col1-1],m[col2-1])
    del m
    return 

def scanfile_data(name):
    return loadtxt(name).transpose()


#trajectory is a dictionary, 
#{"main_axis":name of the main motor
#"integration_time":[all integration times in seconds one per point],
#"trajectory":[{"motor":motor_name,"trajectory":[all positions to reach],"backlash":optional}]}

def nascan(trajectory,channel=None,returndata=False,fulldata=False,name=None,delay=0.,delay0=0.,\
scaler="ct",comment="",fullmca=False,graph=1, n = 1):
    """Scan over trajectory object. 
    The default timebase is named ct.
    delay applies to all points
    delay0 to first after backlash
    
    trajectory has the form:
    trajectory is a dictionary, 
    {
    "main_axis":name_of_the_main_motor,
    "integration_time":[all integration times in seconds one per point],
    "trajectory":[{"motor":motor_name,"points":[all positions to reach],"backlash":optional}]
    "extra_backlash":[
    {"motor":motor,"value":value},...
    ]
    }


    """

#Verify compatibility of trajectories
    npoints = len(trajectory["integration_time"])
    for i in trajectory["trajectory"]:
        if len(i["points"]) != npoints:
            raise Exception("Error in trajectory, one element has not the same length as the integration_time")            
    all_motors=[]
    all_motors_names=[]
    for mot in trajectory["trajectory"]:
        all_motors.append(mot["motor"])
        all_motors_names.append(whois(mot["motor"]))
#Start setup
    glob  = get_ipython().user_ns
    shell = IPython.core.getipython.get_ipython()
    if "setSTEP" in glob.keys():
        glob["setSTEP"]()
    __time_at_start = cputime()
    if channel == None: channel = 1
    __no_scans = n
    time_scan = False
    if scaler in glob:
        cpt = glob[scaler]
    else:
        raise Exception("Timebase not defined or wrong timebase name.")
    if name == None:
        name = "nscan_out"
    ext = "txt"
    if graph >=0:
        w = speck_plot.speck_figure(fign=graph, title=name, grid=(1,1))
    for scan_number in range(__no_scans):
        x = []
        y = []
        full = []
        current_name = findNextFileName(name, ext, file_index = scan_number + 1)
        ###################### FULL MCA FILES! #####################################
        if fullmca:
            dirname = current_name[:current_name.rfind(".")]+".d"
            mca_files = {}
        if fullmca:
            os.mkdir(dirname,0o777)
            for mca_channel in cpt.read_mca().keys():
                mca_files[mca_channel] = file(dirname + os.sep + current_name[:current_name.rfind(".")]+"_"+mca_channel+".txt","a")
                print(dirname + os.sep+name + "." + mca_channel)
        ###################### FULL MCA FILES! #####################################
        f=file(current_name, "w")
        print("Saving in file: ",current_name)
        shell.logger.log_write("Saving data in: %s\n" % current_name, kind='output') 
        try:
            if "label" in dir(mot):    f.write("#ascan over motor: "+mot.label+"\n")
        except (KeyboardInterrupt,SystemExit) as tmp:
            print("Scan finished on user request")
            raise tmp
        except:
            pass
        try:
            motname = whois(trajectory["main_axis"])
            f.write("#main_axis  = %s\n"%(motname))
            if graph >=0:
                w.set_axis_labels(motname,"ct[%i]"%channel,0)
        except (KeyboardInterrupt,SystemExit) as tmp:
            print("Scan finished on user request")
            f.close()
            __backup_data()
            raise tmp
        except Exception as tmp:
            motname="None"
            print(tmp)
            pass
        print("main axis : ", motname)
        f.write("#Following line is a comment:")
        f.write("#"+comment+"\n")
        #Call pre scan function:
        pre_scan(handler=f)
        #
        no_channels=len(cpt.read())
        #Mark Header with a special card
        f.write("#HEADER\n")
        #f.write("#"+motname+"\t"+"\t".join(map(lambda x:"Chan%02i"%x,range(no_channels)))+"\tTimeFromEpoch\n")
        header="#"\
        + "\t".join(all_motors_names)\
        + "\t".join(map(lambda x:x.label,cpt.user_readconfig))\
        + "\t".join(map(lambda x:x["name"],cpt.posts))\
        + "\tTimeFromEpoch\n"
        f.write(header)
        try:
            for m_back in trajectory["trajectory"]:
                if "backlash" in m_back.keys():
                    m_back["motor"].go(m_back["points"][0]-abs(backlash))
            wait_motor(all_motors,verbose=False)
            for m_back in trajectory["trajectory"]:
                m_back["motor"].go(m_back["points"][0])
            wait_motor(all_motors,verbose=False)
            if "extra_backlash" in trajectory.keys():
                for m_back in trajectory["extra_backlash"]:
                    mvr(m_back["motor"],m_back["value"])
                #Workaround for resetting motors after extra backlash (keep in mind monochromator...)
                for m_back in trajectory["trajectory"]:
                    m_back["motor"].go(m_back["points"][0])
                wait_motor(all_motors,verbose=False)
            if delay0>0: sleep(delay0)
            
            if "dummy_points" in trajectory.keys() and trajectory["dummy_points"] > 0:
                dummies = trajectory["dummy_points"]
                for istep in range(trajectory["dummy_points"]):
                    if istep>0:
                        for mot in trajectory["trajectory"]:
                            mot["motor"].go(mot["points"][istep])
                        wait_motor(all_motors,verbose=False)
            else :
                dummies = 0
            for istep in range(dummies,len(trajectory["integration_time"])):
                if istep>0:
                    for mot in trajectory["trajectory"]:
                        mot["motor"].go(mot["points"][istep])
                    wait_motor(all_motors,verbose=False)
                    if delay>0: sleep(delay)
                    
                x_all=[x.pos() for x in all_motors]
                x.append(xall[0])
                __cts=cpt.count(trajectory["integration_time"][istep])
                y.append(__cts[channel])
                if fulldata:
                    full.append(array(__cts))
                for j in x_all:
                    f.write("%14.13e\t"%(j))
                for j in __cts:
                    f.write("%10.8e\t"%(numpy.nan_to_num(j)))
                f.write("%14.13e"%(cputime()))
                f.write("\n")
                ######################################################################################
                #            Write to Full MCA files
                ######################################################################################
                if fullmca:
                    __fullmca=cpt.read_mca()
                    for mca_channel in mca_files.keys():
                        __fullmca_line=__fullmca[mca_channel]
                        __fullmca_line_format="%d\t"*(len(__fullmca_line)-1)+"%d\n"
                        mca_files[mca_channel].write(__fullmca_line_format%tuple(__fullmca_line))
                ######################################################################################
                if graph >=0 and len(mod(x,5)==0):
                    w.plot(x,y,curve=0,update=True,marker=".",linestyle="--",linewidth=2,color="b")
            if graph >= 0:
                w.plot(x,y,curve=0,update=True,marker=".",linestyle="--",linewidth=2,color="b")

        except (KeyboardInterrupt,SystemExit) as tmp:
            print("Scan finished on user request")
            cpt.stop()
            f.close()
            __backup_data()
            raise tmp
        except Exception as tmp:
            f.close()
            raise tmp
        f.close()
        ##################### CLOSE MCA FILES ##################
        if fullmca:
            for mca_channel in mca_files.keys():
                mca_files[mca_channel].close()
        ########################################################

        try:
            __backup_data()
        except (KeyboardInterrupt,SystemExit) as tmp:
            print("Scan finished on user request")
            raise tmp
        except:
            pass
        #You could use this if persist=1 does not work:
        print("Elapsed Time: %8.6fs" % (cputime() - __time_at_start))
    #
    ml=min(len(x),len(y))
    #Call statistisc calculation
    if "ScanStats" in glob: 
        ascan_statistics(x[:ml], y[:ml], glob)
        print(BOLD + "\nScanStats:\n---------------------------" + RESET)
        print(glob["ScanStats"]())
        print("")
    #
    print("Total Elapsed Time: %8.6fs" % (cputime() - __time_at_start))
    #
    if returndata == True:
        if fulldata:
            full = array(full[:ml])
            return array([x[:ml], full.transpose()])
        else:
            return array([x[:ml], y[:ml]])
    return 


