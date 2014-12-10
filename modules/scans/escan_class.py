import os,sys
from time import clock,sleep,asctime,time
from numpy import cos, sin, pi, log, mod, array, zeros, mean, float32,float64, float16, sqrt, average, arange
import PyTango
from PyTango import DeviceProxy, DevState
import exceptions
#import thread

import Gnuplot

from mycurses import *
from wait_functions import checkTDL, wait_injection
#from motor_class import wait_motor
from GetPositions import GetPositions
from spec_syntax import wa, wait_motor

try:
    import Tkinter
    NoTk=False
except:
    print "Warning from escan: Tkinter not installed."
    NoTk=True

import grace_np

#
# Nota: todo copy of files to ruche
# A temporary and a storage default data folders should be defined. 
# If one is missing the backup copy in storage is not performed. 
# Properties: 
##    __DefaultDataFolder_Temporary=None means use current folder
##   __DefaultDataFolder_Storage=None means no storage copy

def ReadScanForm(filename):
    """Read the file and return the correct values for the usebender flag and the grid. 
       Other keys can be easily added. If no bender key is specified None is returned.
       If insufficient data is obtained for the scan grid an exception is raised. 
       The default counting time is 1 s per point. The counting time can be omitted.
       Default kscan parameters follow:
       kscan 16. 0.05 2. 6. 3.
       maximumk=16 k-step=0.05 initial counting time=2s, final counting time=6s and kweight=3"""
    #
    #Define tuple of known keywords
    #
    keys=["bend","nobend","tun","notun","detune","fluo","sexafs","e0","kscan","settling",\
    "plot","noplot","tey","roi","fast","backup","nobackup","roll","notz2","almostfast",
    "vortex","fullmca","attribute","pitch"]
    #
    #Define default values:
    #
    #PlotSetting can be kinetic or integral (kin or int actually).
    defaultPlotSetting="kinetic"
    #roll syntax is: roll energy1,roll1,energy2,roll2
    defaultServoRollParameters=[]
    defaultServoPitchParameters=[]
    defaultSettlingTime=0.0
    defaultDegree=1
    defaultFocus=15.88
    defaultDetune=1
    defaultDetectionMode="absorption"
    defaultkscan=False
    defaultkmax=16.
    defaultdk=0.05
    defaultt0=2.
    defaultt1=6.
    defaultkw=3.
    default_roi=[]
    default_notz2=False
    default_notz2_auto_limit=0.01
    #scanModes in ["step","fast"]
    default_scanMode="step"
    default_backup=True
    default_fullmca=False
    #
    #
    #
    try: 
        f=file(filename,'r')
    except:
        raise exceptions.Exception("File: "+filename+" not found!")
    raw=[]
    raw=f.readlines()
    res=[]
    #print "Raw data:"
    #for i in raw: print i
    #print "################### End raw data ######################"
    for i in raw:
        tmp=i.strip().expandtabs()
        if(not(tmp.startswith("#"))):
            if(tmp.find("#")==-1):
                res.append(tmp.lower())
            elif(tmp<>""): 
                res.append(tmp.lower()[:tmp.find("#")])
    #print "Cleaned data:"
    #for i in res: print i
    #print "################### End cleaned data ######################"
    #
    #Initialize parameters with default values
    #
    raw=res
    res=[]
    usebender=None
    plotSetting=defaultPlotSetting
    tuning=False
    degree=1
    detune=None
    detectionMode=None
    SettlingTime=defaultSettlingTime
    e0=None
    kscan=False
    kgrid=[]
    roi=default_roi
    scanMode=default_scanMode
    backup=default_backup
    notz2=False
    notz2_auto_limit=default_notz2_auto_limit
    ServoRollParameters=defaultServoRollParameters
    ServoPitchParameters=defaultServoPitchParameters
    fullmca=default_fullmca
    attributes=[]
    #print "First pass on data:"
    for i in raw:
        if(i.startswith("bend")):
            usebender=True
        elif(i.startswith("attribute")):
            j=i.replace("="," ")
            j=j.split()
            if len(j)==1:
                raise Exception("Error parsing line: missing attribute name on line.\n ---> %s"%i)
            elif len(j)==2:
                attributes.append([j[1],j[1]])
            elif len(j)==3:
                attributes.append([j[1],j[2]])
            else:
                raise Exception("Error parsing line: too many arguments on line.\n ---> %s"%i)
        elif(i.startswith("nobackup")):
            backup=False
        elif(i.startswith("backup")):
            backup=True
        elif(i.startswith("fast")):
            scanMode="fast"
        elif(i.startswith("almostfast")):
            scanMode="almostfast"
        elif(i.startswith("notz2")):
            j=i.replace("="," ")
            j=j.split()
            if len(j)==1:
                notz2=True
            else:
                try:
                    notz2_auto_limit=float(j[1])
                    print "Auto Limit for tz2 set to %g"%(notz2_auto_limit)
                except:
                    raise Exception("Error parsing line:\n %s\n"%i)
        elif(i.startswith("noplot")):
            plotSetting=None
        elif(i.startswith("plot")):
            j=i.replace("="," ")
            j=j.split()
            if(len(j)==1):
                plotSetting=defaultPlotSetting
            else:
                plotSetting=j[1]
                if (plotSetting[0:3]=="kin"):
                    plotSetting="kinetic"
                elif (plotSetting[0:3]=="ave"):
                    plotSetting="average"
                else:
                        plotSetting=defaultPlotSetting
                        print "Unknown plot mode :",j[1]
                        print "Plot modes are kinetic (kin) or average (ave)"
        elif(i.startswith("nobend")):
            usebender=False
        elif(i.startswith("tun")):
            tuning=True
            j=i.replace("="," ")
            j=j.split()
            #Default degree is 1 and no modification is allowed
            degree=defaultDegree
            if len(j)>=1: 
                print "No options allowed for tuning. Refer to the new handbook."
            #if(len(j)==1):
            #    degree=defaultDegree
            #else:
            #    try:
            #        degree=int(float(j[1]))
            #    except:
            #        exceptions.SyntaxError("Tuning points number not understandable",i)
        elif(i.startswith("e0")):
            j=i.replace("="," ")
            j=j.split()
            if(len(j)==1):
                e0=None
            else:
                try:
                    e0=float(j[1])
                except:
                    exceptions.SyntaxError("E0 value is not understandable",i)
        elif(i.startswith("roll")):
            j=i.replace("="," ")
            j=i.replace(","," ")
            j=j.split()
            print "Roll parameters are:",j[1:]
            if(len(j)<>5):
                ServoRollParameters=defaultServoRollParameters
                print "Error specifying roll parameters! Defaulting to no roll correction!"
            else:
                try:
                    for i in j[1:]: ServoRollParameters.append(float(i))
                except:
                    print "Error specifying roll parameters! Defaulting to no roll correction!"
                    ServoRollParameters=defaultServoRollParameters
        elif(i.startswith("pitch")):
            j=i.replace("="," ")
            j=i.replace(","," ")
            j=j.split()
            print "Pitch parameters are:",j[1:]
            if(len(j)<>5):
                ServoPitchParameters=defaultServoPitchParameters
                print "Error specifying pitch parameters! Defaulting to no pitch correction!"
            else:
                try:
                    for i in j[1:]: ServoPitchParameters.append(float(i))
                except:
                    print "Error specifying pitch parameters! Defaulting to no pitch correction!"
                    ServoPitchParameters=defaultServoPitchParameters
                    
        elif(i.startswith("notun")):
            tuning=False
            tuningpoints=0
        elif(i.startswith("sex")):
            detectionMode="sexafs"
        elif(i.startswith("fluo")):
            detectionMode="fluo"
        elif(i.startswith("tey")):
            detectionMode="tey"
        elif(i.startswith("vortex")):
            detectionMode="vortex"
        elif (i.startswith("roi")):
            j=((i.replace("="," ")).replace(","," ").split())[1:]
            for __chk in j:
                try:
                    roi[0]==True
                except:
                    roi=[]
                roi.append(float(__chk))
            if mod(len(roi),2)<>0:
                raise Exception("Wrong number of parameters for ROI!",roi)
        elif(i.startswith("detune")):
            j=i.replace("="," ")
            j=j.split()
            if(len(j)==1):
                detune=defaultDetune
            else:
                try:
                    detune=float(j[1])
                except:
                    exceptions.SyntaxError("detune value not understandable",i)
        elif(i.startswith("settling")):
            j=i.replace("="," ")
            j=j.split()
            if(len(j)==1):
                settlingTime=defaultSettlingTime
            else:
                try:
                    SettlingTime=float(j[1])
                except:
                    exceptions.SyntaxError("settling value not understandable",i)
                    SettlingTime=defaultSettlingTime
        elif(i.startswith("kscan")):
            j=i.replace("="," ")
            j=i.replace(","," ")
            j=j.split()
            kk=[]
            kscan=True
            kgrid=[defaultkmax,defaultdk,defaultt0,defaultt1,defaultkw]
            for jj in j[1:]: kk.append(float(jj))
            kgrid=kk+kgrid[len(kk):]
        elif(i.startswith("fullmca")):
            fullmca=True
    if plotSetting<>None:
        print "Plotter:",plotSetting
    else:
        print "Plotter: no graphic output."
    print "Using bender=",usebender
    if(tuning): print "Tuning degree is ",degree
    if(detune==None): 
        detune=defaultDetune
    print "Detuning crystals at ",detune,"*maximum" 
    if detectionMode==None: detectionMode=defaultDetectionMode
    print "Detection mode: ",detectionMode
    print "SettlingTime (movement-->SettlingTime-->counts)=",SettlingTime
    if kscan: 
        print "kscan active: parameters are kmax, deltak, t0, t1, kweight"
        print "kscan :",kgrid
    res=raw
    raw=[]
    for i in res:
        not_key=True
        for j in keys:
            if(i.find(j)<>-1): 
                not_key=False
                break
        if(not_key): 
            raw.append(i)
    res=[]
    for i in raw:
        tmp=i.split(",")
        tmp2=[]
        for j in tmp:
            for k in (j.split()): tmp2.append(k)
        res.append(tmp2)
    #for i in res: print i
    #print "################### End First pass on data ######################"
    raw=res
    res=[]
    for i in raw:
        tmp=[]
        for j in i:
            try:
                tmp.append(float(j))
            except:
                print "Spurious characters on line!"
                print "Line ---> ",j
                
        if(tmp<>[]): res.append(tmp)
    if len(res)<2:
        raise exceptions.SyntaxError("Too few usefull lines. Error in input file. Abort.")
    res.sort()
    #print "Second pass on data:"
    #for i in res: print i
    #print "################### End Second pass on data ######################"
    raw=res
    res=[]
    for i in raw:
        if (len(i)==1):
            res.append(i)
            break
        if (len(i)==2):
            res.append(i+[1.,])
        if (len(i)>=3):
            res.append(i[0:3])
    if len(res)<2:
        raise exceptions.SyntaxError("Too few usefull lines. Error in input file. Abort.")
    #print "Truncation on data:"
    print "Scan over:"
    for i in res: print i
    if kscan==True:
        if e0==None: e0=0.5*(res[-1][0]+res[-2][0])
        print "E0=",e0
    #print "################### End Truncation on data ######################"    
    return {"usebender":usebender,"tuning":tuning,"degree":degree,"res":res,\
    "detune":detune,"detectionMode":detectionMode,"e0":e0,"kgrid":kgrid,"kscan":kscan,"SettlingTime":SettlingTime,\
    "plotSetting":plotSetting,"roi":roi,"scanMode":scanMode,"backup":backup,\
    "ServoRollParameters":ServoRollParameters,"ServoPitchParameters":ServoPitchParameters,\
    "notz2":notz2,"notz2_auto_limit":notz2_auto_limit,"fullmca":fullmca,"attributes":attributes}




class escan_class:
    def __init__(self,scan_form="",\
    Ts2_Moves=False,amplis=None):
        if(scan_form==""):
            raise exceptions.Exception("Missing scan file! Please provide one.")
        shell = get_ipython()
        self.dcm = shell.user_ns["energy"]
        cpt = shell.user_ns["ct"]
        obx = shell.user_ns["obx"]
        obxg = shell.user_ns["obxg"]
        self.FE = shell.user_ns["FE"]
        try:
            sh_fast = shell.user_ns["sh_fast"]
        except:
            sh_fast = None
        #List here defined x stoppers 
        exafsStoppers=[obxg,]
        sexafsStoppers=[obxg,obx]
        #Shutters
        self.shutters={"exafs":obxg,"sexafs":obx,"fast":sh_fast}
        #self.shutters={"exafs":sh_fast,"sexafs":obx,"fast":sh_fast}
        ##############################################################
        #
        #Define data and backup folders: backup only if
        #current folder is in data path
        #__Default_Data_Folder must be a GLOBAL variable!
        # MUST be declared outside this class and before the escan class!
        #
        try:
            #__Default_Data_Folder="/home/experiences/samba/com-samba/ExperimentalData/"
            #__Default_Backup_Folder="/nfs/ruche-samba/samba-soleil/com-samba/"
            __Default_Data_Folder = get_ipython().user_ns["__Default_Data_Folder"]
            __Default_Backup_Folder = get_ipython().user_ns["__Default_Backup_Folder"]
            self.currentDataFolder=os.getcwd()
            print "Data Folder is :",self.currentDataFolder
            if self.currentDataFolder.startswith(__Default_Data_Folder.rstrip("/")) and __Default_Backup_Folder <> "":
                self.currentBackupFolder=__Default_Backup_Folder+"/"+\
                self.currentDataFolder.lstrip(__Default_Data_Folder.rstrip("/"))
                cbf=self.currentBackupFolder
                self.currentBackupFolder=cbf[:cbf.rstrip("/").rfind("/")]
            else:
                self.currentBackupFolder=None
            print "Backup Folder is :",self.currentBackupFolder
        except:
            print RED,
            print "--------------------------------------------------------------------"
            print "WARNING:"
            print "Error defining backup folders... please, backup data files manually."
            print "--------------------------------------------------------------------"
            print RESET,
            self.currentBackupFolder=None
        #
        #Setup avec scan file
        #
        ###Rustine revoltante !!!!!
        ###Il faut definir un controlleur pour le machinestatus et le passer en argument...
        try:
            self.ms=DeviceProxy("ans/ca/machinestatus")
        except:
            print RED+"Cannot define a device proxy for the machinestatus ans/ca/machinestatus"+RESET
        ###
        thisform=ReadScanForm(scan_form)
        f=file(scan_form,"r")
        self.formtext=f.readlines()
        f.close()
        #
        attributes=thisform["attributes"]
        self.attributes=[]
        #Transforms attributes to attribute proxies
        for i in attributes:
            try:
                self.attributes.append(
                [PyTango.AttributeProxy(i[0]),i[1]]
                )
            except Exception, tmp:
                print "\n\nError while defining the AttributeProxy for an additional attribute, verify config file or attribute address.\n\n"
                raise tmp
        del attributes
        self.backup=thisform["backup"]
        bend=thisform["usebender"]
        tuning=thisform["tuning"]
        degree=thisform["degree"]
        self.grid=thisform["res"]
        self.TUNING=tuning
        print "Tuning is set to :",self.TUNING
        if(self.TUNING==None): 
            self.TUNING=True
            self.tuningdegree=1
        elif(self.TUNING==False):
            self.tuningdegree=0
        elif(self.TUNING==True):
            self.tuningdegree=degree
        else:
            raise exceptions.Exception("The tuning flag is not properly set. Verify scan file.",self.TUNING)
        #Pitch correction (Explicit, deactivates the tuning)
        self.ServoPitchParameters=thisform["ServoPitchParameters"]
        if self.ServoPitchParameters<>[]:
            self.PitchCorrection=True
            self.TUNING=False
            print RED+"Pitch correction explicitly specified: deactivating auto tuning of piezo."+RESET
        else:
            self.PitchCorrection=False
        #Roll correction
        self.ServoRollParameters=thisform["ServoRollParameters"]
        if self.ServoRollParameters<>[]:
            self.RollCorrection=True
        else:
            self.RollCorrection=False
        #
        self.notz2=thisform["notz2"]
        if self.notz2:
            print "notz2: TZ2 will not be used."
        self.notz2_auto_limit=thisform["notz2_auto_limit"]
        self.detune=thisform["detune"]
        self.detectionMode=thisform["detectionMode"]
        #################################################################
        #                                    #
        # Defining different parameters for CX1 and CX2: very delicate! #
        #                                    #
        #################################################################
        if self.detectionMode=="sexafs":
            self.stoppersList=sexafsStoppers
            self.timer_channel=6
        else:
            self.stoppersList=exafsStoppers
            self.timer_channel=14
        ################################################################
        self.kscan_e0=thisform["e0"]
        self.kscan=thisform["kscan"]
        self.kgrid=thisform["kgrid"]
        self.SettlingTime=thisform["SettlingTime"]
        self.plotSetting=thisform["plotSetting"]
        self.roi=thisform["roi"]
        self.scanMode=thisform["scanMode"]
        print BLUE+"Scan Mode is :"+RESET,self.scanMode
        self.almostMode=False
        if self.scanMode=="almostfast":
            self.almostMode=True
            self.scanMode="fast"
        self.AFTER_INJECTION=False
        self.fullmca=thisform["fullmca"]
        if(bend==None):
            self.BENDER=None
        elif(not(bend in [False, True])):
            raise exceptions.Exception("The bender flag is not properly set. Verify scan file.")
        else:
            self.BENDER=bend
        ######################################################################
        #  Load trajectory into two arrays in a dictionary                   #
        #  The dictionary can be expanded to host more motors, timescales... #
        ######################################################################
        self.trajectory={"energy":[],"time":[]}
        #Calculate kgrid
        if self.kscan:
            #k1=sqrt(0.2625*(self.grid[-1][0]-self.kscan_e0))+self.kgrid[1]
            k1=sqrt(0.2625*(self.grid[-1][0]+self.grid[-2][1]-self.kscan_e0))
            self.kscan_e=3.8095238095*arange(k1+self.kgrid[1],self.kgrid[0]+self.kgrid[1],self.kgrid[1])**2+self.kscan_e0
            #self.kscan_t=(arange(k1+self.kgrid[1],self.kgrid[0]+self.kgrid[1],self.kgrid[1])-k1+1.)**self.kgrid[3]*self.kgrid[2]
            if self.kgrid[4]==0:
                ck=0.
            else:
                ck=(self.kgrid[3]-self.kgrid[2])/((self.kgrid[0]+self.kgrid[1])**self.kgrid[4]-(k1+self.kgrid[1])**self.kgrid[4])
            self.kscan_t=self.kgrid[2]+\
            +ck*(arange(k1+self.kgrid[1],self.kgrid[0]+self.kgrid[1],self.kgrid[1])**self.kgrid[4]-k1**self.kgrid[4])
            #Calculate kscan iterators
            kscan_energy=iter(self.kscan_e)
            kscan_time=iter(self.kscan_t)
        ####
        self.e1=self.grid[0][0]
        self.e2=self.grid[-1][0]
        if self.kscan:
            self.e2=float(self.kscan_e[-1])
        #
        #Calculate egrid and append kgrid
        #
        ni=0
        en=self.e1
        while(en<self.e2):
            if en<=self.grid[-1][0]:
                if(ni+2<len(self.grid)):
                    en+=self.grid[ni][1]
                    tmeasure=float(self.grid[ni][2])
                    if(en>=self.grid[ni+1][0]): 
                        en=self.grid[ni+1][0]
                        tmeasure=float(self.grid[ni+1][2])
                        ni+=1
                elif(ni+2==len(self.grid)):
                    en+=self.grid[ni][1]
                    tmeasure=float(self.grid[ni][2])
                self.trajectory["energy"].append(en)
                self.trajectory["time"].append(tmeasure)
            elif self.kscan:
                try:
                    en=float(kscan_energy.next())
                    tmeasure=float(kscan_time.next())
                except exceptions.StopIteration, tmp:
                    break
                self.trajectory["energy"].append(en)
                self.trajectory["time"].append(tmeasure)
        #Calculate integral of time
        self.scanNumberOfPoints=len(self.trajectory["energy"])
        IntegrationTime=sum(self.trajectory["time"])
        MovingTime=self.scanNumberOfPoints*0.75
        print "---------------------------------------------"
        print "Extimated Scan Time: please, consider only the moving time in fast mode."
        print "Following values are calculated for ONE scan."
        print "---------------------------------------------"
        print "Extimated Moving time (minutes):",MovingTime/60.
        print "IntegrationTime (minutes)",IntegrationTime/60.
        print "Extimated Total (minutes):",(MovingTime+IntegrationTime)/60.
        print "Number of points:",self.scanNumberOfPoints
        print "Tuning could take 2 minutes if enabled"
        print "---------------------------------------------"
        ##############################################################
        #Calculate if TZ2 should move or not: TZ2 is calculated in mm
        if abs(self.dcm.tz2(self.dcm.e2theta(self.e1))-self.dcm.tz2(self.dcm.e2theta(self.e2)))<self.notz2_auto_limit:
            self.notz2=True
            print GREEN,
            print "############################ NEW FEATURE #################################################"
            print RESET,
            print "Auto limiting TZ2!"
            print "tz2 movement is below %4.2f mm."%(self.notz2_auto_limit)
            print "If you want to use tz2 even for smaller tz2 ranges set: notz2 -1 in the parameter file."
            print GREEN,
            print "##########################################################################################"
            print RESET
        #
        if self.notz2:
            self.previous_dcm_tz2_setting=self.dcm.usetz2()
            self.dcm.disable_tz2()
        self.cpt=cpt
        #self.cpt_header="\t".join(map(lambda x:x.label,self.cpt.user_readconfig))+"\t"
        self.cpt_header=""
        self.auto_fluo_channels=[]
        col=0
        for i in self.cpt.user_readconfig:
            self.cpt_header+=i.label+"\t"
            if i.label.startswith("roi") and i.label.endswith("_1"): self.auto_fluo_channels.append(col)
            col+=1
        print "Number of fluo channels="+RED+"%i"%(len(self.auto_fluo_channels))+RESET
        del col
        self.auto_fluo_mask=zeros(len(self.cpt.user_readconfig))
        for i in self.auto_fluo_channels:
            self.auto_fluo_mask[i]=1
        #self.tuning_points=[[0.,]*(self.tuningdegree+1),[0.,]*(self.tuningdegree+1)]
        self.tuning_points=[[0.,0.],[0.,0.]]
        #self.TUNING_OK=False
        self.Ts2_Moves=Ts2_Moves
        if self.detectionMode=="sexafs":
            try:
                self.temperature_DP=DeviceProxy("d09-1-cx2/ex/tc.1")
            except:
                print "No thermocouple readings... error on d09-1-cx2/ex/tc.1"
        else:
            try:
                self.temperature_DP=DeviceProxy("D09-1-CX1/EX/TC.1")
            except:
                print "No thermocouple readings... error on D09-1-CX1/EX/TC.1"
        #Graphic properties and variables:
        self.gracewins={}
        return
        
    def set_ts2(self):
        """Set Ts2 at the right position for this scan"""
        dest=self.dcm.ts2(self.dcm.e2theta((self.e1+self.e2)*0.5))
        return self.dcm.m_ts2.pos(dest)

    def set_tz2(self):
        """Set Tz2 at the right position for this scan: used only when notz2 is chosen"""
        dest=self.dcm.tz2(self.dcm.e2theta((self.e1+self.e2)*0.5))
        return self.dcm.m_tz2.pos(dest)

    def __fibonacci(self,n):
        "returns the first n terms (starting from 1, 0 is neglected)"
        S=[0,1,1,2,3,5,8,13]
        if n>8:
            for i in range(7,n+7):
                S.append(S[i]+S[i-1])    
        return S[0:n]
        
    def backlash_recovery(self,energy,de=None,dummypoints=3,deadtime=0.0):
        """Execute a backlash recovery for the monochromator and then set it to e-de:
        de=2, dummypoints=3;  moves to energy-de*2, energy-de*2, energy-de"""
        if de==None:
            de=max(self.trajectory["energy"][1]-self.trajectory["energy"][0],1.)
        points=array(self.__fibonacci(dummypoints+2)[-1:1:-1])*(-de)+energy
        print "Performing backlash recovery over: ",points
        for en in points:
            self.dcm.pos(en,Ts2_Moves=self.Ts2_Moves,Tz2_Moves=not(self.notz2))
            sleep(deadtime)
        return

    def scan_tuning(self,n=1):
        """Sample points evenly in space.  n is the polynome degree, default n is 1, that means 2 points."""        
        #"""Sample points accordingly to Gauss criterion. n is the polynome degree, default n is 1, that means 2 points."""
        n = 1
        #self.tuning_points=[[0.,]*(n+1),[0.,]*(n+1)]
        #for i in range(n+1):
        #    self.tuning_points[0][i]=-cos(0.5*pi*(2.*i+1.)/(n+1))*(self.e2-self.e1)*0.5+(self.e1+self.e2)*0.5
        #if n<=0:
        #    self.tuning_points[0][0]=(self.e2+self.e1)*0.5
        #    n=0
        for i in range(2):
            self.tuning_points[0][i]=self.e1+i*(self.e2-self.e1)/float(n)
        for i in range(n,-1,-1):
            #Backlash recovery
            #self.backlash_recovery(self.tuning_points[0][i])
            #
            self.dcm.pos(self.tuning_points[0][i],Ts2_Moves=self.Ts2_Moves,Tz2_Moves=not(self.notz2))
            print "Tuning point at E=",self.dcm.pos()
            if self.detune==1:
                self.tuning_points[1][i]=self.dcm.tune()
            else:
                self.tuning_points[1][i]=self.dcm.detune(self.detune)
                print "Detuned of ",self.detune*100,"%"
            print " "
        return self.tuning_points

    def usebender(self,flag=None):
        if(flag==None):
            return self.BENDER
        if(flag in [True,False]):
            self.BENDER=flag
            return self.BENDER
        else:
            raise exceptions.SyntaxError("Wrong value for usebender")
  
    def lin_interp(self,x,points=[[0.,],[0.,]]):
        return (points[1][1] - points[1][0]) / (points[0][1] - points[0][0]) * (x - points[0][0]) + points[1][0]
        #print "Lin_interp :",__pp
        #return __pp
        
    def lagrange(self,x,points=[[0.,],[0.,]]):
        P = 0.
        n = len(points[0])
        for i in range(n):
            p=1.0
            for j in range(n):
                if(j!=i):
                    p=p*(x-points[0][j])/(points[0][i]-points[0][j])
            P+=p*points[1][i]            
        return P
    
    
    def start_grace_processes(self):
        """Depending on detectionMode this function initialize the necessary grace windows and 
        return the graceprocess objects as a tuple in self.gracewins"""
        #!
        #!This code could be rewritten using a text file source or a big string and sending it to grace just once per process
        #!
        
        #
        #Just to be sure that at least one detction mode has been set. This obliges programmer 
        #to append the new detection mode in ReadScanForm (top declare it), here (to open windows)
        #and in the update_grace_windows (to plot)... that is quite obvious.
        #
        self.GRAPHICS_RESTART_NEEDED=False
        if not(self.detectionMode in ["absorption","fluo","tey","sexafs","vortex"]):
            self.detectionMode="absorption"
        #
        
        #If self.gracewins==[] the plotting will never work: but the checkout should be done
        #always on plotSetting for the rest of the code so we set it to none in case of error
        if self.plotSetting==None:
            return
        if ("__GRACE_FAULTY" in dir()):
            self.plotSetting=None
            return
        #Start three grace processes for the following modes:
        #absorption, rontec, fluo, tey
        #Start two grace processes for the sexafs mode
        #!
        #!Windows will be opened in reverse order to get last on top !
        #!
        try:
            #if self.detectionMode<>"sexafs":
            if self.detectionMode<>None:       
                if self.detectionMode in ["fluo","vortex","sexafs"]:
                    #Start gracewin3: fluo
                    gracewin3=grace_np.GraceProcess()
                    gracewin3("timestamp 0., 0.\ntimestamp char size 0.5\ntimestamp on")
                    gracewin3("default char size 0.75")
                    gracewin3.viewport={}
                    ncols=int(sqrt(len(self.auto_fluo_channels)))
                    nrows=ncols+int((len(self.auto_fluo_channels)-ncols**2)/ncols)
                    if mod((len(self.auto_fluo_channels)-ncols**2),ncols)>0:
                        nrows+=1
                    gracewin3('arrange(%i,%i,0.05,0.,0.)'%(ncols,nrows))
                    gracewin3('with g0;title "%s"'%self.filename)
                    for i in range(nrows*ncols):
                        gracewin3('with g%i'%(i))
                        gracewin3('world xmin %g'%(self.e1))
                        gracewin3('world xmax %g'%(self.e2))
                        gracewin3.viewport["graph%02i"%i]=\
                        {"xmin":self.e1,"xmax":self.e2,"ymin":None,"ymax":None}
                        majortick=max(1.,int((self.e2-self.e1)/5.))
                        gracewin3('xaxis tick major %g'%(majortick))
                        gracewin3('xaxis ticklabel char size 0.75')
                        gracewin3('xaxis ticklabel off')
                        gracewin3('world ymin 0')
                        gracewin3('world ymax 1e-5')
                        majortick=100
                        gracewin3('yaxis tick major %g'%(majortick))
                        gracewin3('yaxis ticklabel char size 0.5')
                        gracewin3('yaxis ticklabel off')
                        gracewin3('xaxis tick major off\nyaxis tick major off')
                        gracewin3('redraw')

                #Start gracewin2: absorption of reference foil and currents

                gracewin2=grace_np.GraceProcess()
                gracewin2("timestamp 0., 0.\ntimestamp char size 0.5\ntimestamp on")
                gracewin2("default char size 0.75")
                gracewin2('arrange(2,1,0.15,0.1,0.1)')
                gracewin2('with g0;title "%s"'%self.filename)
                gracewin2('with g0;legend 1.13,0.95;with g1;legend 0.9,0.1')
                gracewin2.viewport={}
                #Reference Absorption    
                i=0
                gracewin2("with g%i"%(i))
                gracewin2('yaxis label char size 0.75')
                gracewin2('yaxis label color 1')
                if self.detectionMode=="sexafs":
                    gracewin2('yaxis label "Electron Yield"')
                else:
                    gracewin2('yaxis label "Reference (Absorption)"')
                gracewin2('yaxis label "Reference (Absorption)"')
                gracewin2.viewport["graph%02i"%i]=\
                {"xmin":self.e1,"xmax":self.e2,"ymin":None,"ymax":None}
                gracewin2('world xmin %g'%(self.e1))
                gracewin2('world xmax %g'%(self.e2))
                majortick=max(1.,int((self.e2-self.e1)/5.))
                gracewin2('xaxis tick major %g'%(majortick))
                gracewin2('xaxis ticklabel char size 0.75')
                gracewin2('xaxis ticklabel color 2')
                gracewin2('world ymin -1e-6')
                gracewin2('world ymax 1e-6')
                majortick=0.2
                gracewin2('yaxis tick major %g'%(majortick))
                gracewin2('yaxis ticklabel char size 0.5')
                gracewin2('yaxis ticklabel color 2')
                gracewin2('xaxis tick minor off\nyaxis tick minor off')
                #Currents
                i=1
                gracewin2('with g%i'%(i))
                gracewin2('xaxis label char size 0.75')
                gracewin2('xaxis label color 2')
                gracewin2('xaxis label "Energy (eV)"')
                gracewin2('yaxis label char size 0.75')
                gracewin2('yaxis label color 8')
                if self.detectionMode=="sexafs":
                    gracewin2('yaxis label "Currents"')
                else:
                    gracewin2('yaxis label "Ion Chambers Currents"')
                gracewin2.viewport["graph%02i"%i]=\
                {"xmin":self.e1,"xmax":self.e2,"ymin":0,"ymax":1000}
                gracewin2('world xmin %g'%(self.e1))
                gracewin2('world xmax %g'%(self.e2))
                majortick=max(1.,int((self.e2-self.e1)/5.))
                gracewin2('xaxis tick major %g'%(majortick))
                gracewin2('xaxis ticklabel char size 0.75')
                gracewin2('xaxis ticklabel color 2')
                gracewin2('world ymin 0')
                gracewin2('world ymax 1000')
                majortick=200
                gracewin2('yaxis tick major %g'%(majortick))
                gracewin2('yaxis ticklabel char size 0.5')
                gracewin2('yaxis ticklabel color 2')
                gracewin2('xaxis tick minor off\nyaxis tick minor off')
                gracewin2('redraw')

                #Start gracewin1: absorption and fluorescence spectra
                #Absorption or TEY
                gracewin1=grace_np.GraceProcess()
                gracewin1('arrange(2,1,0.15,0.1,0.1)')
                gracewin1("timestamp 0., 0.\ntimestamp char size 0.5\ntimestamp on")
                gracewin1("default char size 0.75")
                gracewin1('with g0;title "%s"'%self.filename)
                gracewin1('with g0;legend 1.13,0.95;with g1;legend 0.9,0.1')
                gracewin1.viewport={}
                i=0
                gracewin1('with g%i'%(i))
                gracewin1.viewport["graph%02i"%i]=\
                {"xmin":self.e1,"xmax":self.e2,"ymin":None,"ymax":None}
                gracewin1('world xmin %g'%(self.e1))
                gracewin1('world xmax %g'%(self.e2))
                majortick=max(1.,int((self.e2-self.e1)/5.))
                gracewin1('xaxis tick major %g'%(majortick))
                gracewin1('xaxis ticklabel char size 0.75')
                gracewin1('xaxis ticklabel color 2')
                gracewin1('world ymin 0')
                gracewin1('world ymax 1')
                majortick=0.25
                gracewin1('yaxis tick major %g'%(majortick))
                gracewin1('yaxis ticklabel char size 0.5')
                gracewin1('yaxis ticklabel color 2')
                gracewin1('xaxis tick minor off\nyaxis tick minor off')
                gracewin1("with g%i"%(i))
                gracewin1('yaxis label char size 0.75')
                gracewin1('yaxis label color 4')
                if self.detectionMode=="tey":
                    gracewin1('yaxis label "Sample TEY"')
                else:
                    gracewin1('yaxis label "Sample Absorption"')
                #Fluo
                i=1 
                gracewin1('with g%i'%(i))
                gracewin1.viewport["graph%02i"%i]=\
                {"xmin":self.e1,"xmax":self.e2,"ymin":None,"ymax":None}
                gracewin1('world xmin %g'%(self.e1))
                gracewin1('world xmax %g'%(self.e2))
                majortick=max(1.,int((self.e2-self.e1)/5.))
                gracewin1('xaxis tick major %g'%(majortick))
                gracewin1('xaxis ticklabel char size 0.75')
                gracewin1('xaxis ticklabel color 2')
                gracewin1('world ymin 0')
                gracewin1('world ymax 1')
                majortick=0.25
                gracewin1('yaxis tick major %g'%(majortick))
                gracewin1('yaxis ticklabel char size 0.5')
                gracewin1('yaxis ticklabel color 2')
                gracewin1('xaxis tick minor off\nyaxis tick minor off')
                gracewin1("with g%i"%(i))
                gracewin1('xaxis label char size 0.75')
                gracewin1('xaxis label color 2')
                gracewin1('xaxis label "Energy (eV)"')
                gracewin1("with g%i"%(i))
                gracewin1('yaxis label char size 0.75')
                gracewin1('yaxis label color 2')
                gracewin1('yaxis label "Sample Fluorescence"')
                gracewin1('redraw')
                
                if self.detectionMode in ["fluo","vortex","sexafs"]:
                    self.gracewins={"exafs_1":gracewin1,\
                            "exafs_2":gracewin2,\
                            "exafs_3":gracewin3}
                else:
                    self.gracewins={"exafs_1":gracewin1,\
                            "exafs_2":gracewin2}

            else:
                #Start gracewin5: currents and multichannel (sexafs)
                gracewin5=grace_np.GraceProcess()
                gracewin5("timestamp 0., 0.\ntimestamp char size 0.5\ntimestamp on")
                gracewin5("default char size 0.75")
                gracewin5('arrange(4,2,0.08,0.15,0.)')
                gracewin5.viewport={}
                for i in range(8):
                    gracewin5('with g%i'%(i))
                    #gracewin5.viewport["graph%02i"%i]=\
                    #{"xmin":self.e1,"xmax":self.e2,"ymin":-1e-6,"ymax":1e-6}
                    gracewin5('world xmin %g'%(self.e1))
                    gracewin5('world xmax %g'%(self.e2))
                    #majortick=max(1.,int((self.e2-self.e1)/5.))
                    #gracewin5('xaxis tick major %g'%(majortick))
                    gracewin5('xaxis ticklabel char size 0.75')
                    gracewin5('xaxis ticklabel color 2')
                    gracewin5('world ymin -1e-6')
                    gracewin5('world ymax 1e-6')
                    majortick=0.25
                    gracewin5('yaxis tick major %g'%(majortick))
                    gracewin5('yaxis ticklabel char size 0.5')
                    gracewin5('yaxis ticklabel color 2')
                    gracewin5('xaxis tick minor off\nyaxis tick minor off')
                for i in range(6):
                    gracewin5('with g%i'%(i))
                    gracewin5('xaxis ticklabel off')
                for i in [6,7]:
                    gracewin5("with g%i"%(i))
                    gracewin5('xaxis label char size 0.75')
                    gracewin5('xaxis label color 2')
                    gracewin5('xaxis label "Energy (eV)"')
                for i in range(0,1):
                    gracewin5("with g%i"%(i))
                    gracewin5('yaxis label char size 0.6')
                    gracewin5('yaxis label color 4')
                    gracewin5('yaxis label "SEX_TEY"')
                for i in range(1,8):
                    gracewin5("with g%i"%(i))
                    gracewin5('yaxis label char size 0.6')
                    gracewin5('yaxis label color 2')
                    gracewin5('yaxis label "SEX_Fluo%i"'%(i))
                gracewin5('with g1;legend 0.7,0.1')
                gracewin5('redraw')

                #Start gracewin4: SEXAFS fluorescence and TEY spectra

                gracewin4=grace_np.GraceProcess()
                gracewin4('arrange(2,1,0.12,0.1,0.1)')
                gracewin4("timestamp 0., 0.\ntimestamp char size 0.5\ntimestamp on")
                gracewin4("default char size 0.75")
                gracewin4.viewport={}
                for i in range(2):
                    gracewin4('with g%i'%(i))
                    #gracewin4.viewport["graph%02i"%i]=\
                    #{"xmin":self.e1,"xmax":self.e2,"ymin":-1e-6,"ymax":1e-6}
                    gracewin4('world xmin %g'%(self.e1))
                    gracewin4('world xmax %g'%(self.e2))
                    #majortick=max(1.,int((self.e2-self.e1)/5.))
                    #gracewin4('xaxis tick major %g'%(majortick))
                    gracewin4('xaxis ticklabel char size 0.75')
                    gracewin4('xaxis ticklabel color 2')
                    gracewin4('world ymin -1e-6')
                    gracewin4('world ymax 1e-6')
                    majortick=0.25
                    #gracewin4('yaxis tick major %g'%(majortick))
                    gracewin4('yaxis ticklabel char size 0.5')
                    gracewin4('yaxis ticklabel color 2')
                    gracewin4('xaxis tick minor off\nyaxis tick minor off')
                #for i in range(1):
                #    gracewin4('with g%i'%(i))
                #    gracewin4('xaxis ticklabel off')
                for i in [1]:
                    gracewin4("with g%i"%(i))
                    gracewin4('xaxis label char size 0.75')
                    gracewin4('xaxis label color 2')
                    gracewin4('xaxis label "Energy (eV)"')
                for i in range(0,1):
                    gracewin4("with g%i"%(i))
                    gracewin4('yaxis label char size 0.75')
                    gracewin4('yaxis label color 4')
                    gracewin4('yaxis label "Sample Fluorescence"')
                for i in range(1,2):
                    gracewin4("with g%i"%(i))
                    gracewin4('yaxis label char size 0.75')
                    gracewin4('yaxis label color 2')
                    gracewin4('yaxis label "Sample Electron Yield"')
                gracewin4('with g0;legend 0.7,0.95')
                gracewin4('redraw')
            
                self.gracewins={"sexafs_1":gracewin4,\
                        "sexafs_2":gracewin5}
        except Exception, tmp:
            print "Error starting Grace processes: no plotting. Scan will continue."
            self.plotSetting=None
            print tmp
        return

#    def GPlot(self,gw,graph,curve,x,y,legend=None,color=1,noredraw=False):
#        """kills and replot a curve on a given graceprocess,graph,signal with an optional legend
#        Could be executed in a thread to kill scan deadtime"""
#        l=min(len(x),len(y))
#        color=int(max(0,color))
#        pipe_string="kill g%i.s%i"%(graph,curve)+"\n"+"with g%i\n"%(graph)
#        for i in range(l):
#            pipe_string+='g%i.s%i point %g,%g\n'%(graph,curve,x[i],y[i])
#        pipe_string+="autoscale\n"
#        if legend<>None:
#            pipe_string+='g%i.s%i legend "%s"\n'%(graph,curve,legend)
#        if color>0:
#            pipe_string+="g%i.s%i LINE COLOR %i\n"%(graph,curve,mod(color,24)+1)
#        else:
#            pipe_string+="g%i.s%i LINE COLOR 0\n"%(graph,curve)
#        if noredraw:
#            gw(pipe_string)
#        else:
#            gw(pipe_string+'redraw\n')
#        return

    def GPlot(self,gw,graph,curve,x,y,legend=None,color=1,noredraw=False,autoscale=False):
        """kills and replot a curve on a given graceprocess,graph,signal with an optional legend
        Could be executed in a thread to kill scan deadtime"""
        etol=1e-15
        scale_tol=0.1
        l=min(len(x),len(y))
        if len(x)<2 or len(y)<2:
            return
        xmax,xmin,ymax,ymin=max(x),min(x),max(y),min(y)
        if xmax-xmin<etol: xmax=xmin+etol
        if ymax-ymin<etol: ymax=ymin+etol
        color=int(max(0,color))
        #color==4 is yellow, almost invisible !
        if mod(color,4)==0: color+=1
        pipe_string="kill g%i.s%i"%(graph,curve)+"\n"+"with g%i\n"%(graph)
        #Send data
        for i in range(l):
            pipe_string+='g%i.s%i point %g,%g\n'%(graph,curve,x[i],y[i])
        #
        if "viewport" in dir(gw):
            if not("graph%02i"%graph in gw.viewport):
                gw.viewport["graph%02i"%graph]={
                "xmax":xmax,"xmin":xmin,"ymax":ymax,"ymin":ymin}
            if xmin<gw.viewport["graph%02i"%graph]["xmin"] or gw.viewport["graph%02i"%graph]["xmin"]==None:
                gw.viewport["graph%02i"%graph]["xmin"]=xmin
                pipe_string+='world xmin %g\n'%(xmin)
            if xmax>gw.viewport["graph%02i"%graph]["xmax"] or gw.viewport["graph%02i"%graph]["xmax"]==None:
                gw.viewport["graph%02i"%graph]["xmax"]=xmax
                pipe_string+='world xmax %g\n'%(xmax)
            if ymin<gw.viewport["graph%02i"%graph]["ymin"] or gw.viewport["graph%02i"%graph]["ymin"]==None:
                gw.viewport["graph%02i"%graph]["ymin"]=ymin
                pipe_string+='world ymin %g\n'%(ymin)
            if ymax>gw.viewport["graph%02i"%graph]["ymax"] or gw.viewport["graph%02i"%graph]["ymax"]==None:
                gw.viewport["graph%02i"%graph]["ymax"]=ymax
                pipe_string+='world ymax %g\n'%(ymax)
        else:
            gw.viewport={}
            gw.viewport["graph%02i"%graph]=\
            {"xmin":min(x),"xmax":max(x),"ymin":min(y),"ymax":max(y)}
            pipe_string+='world xmin %g\n'%(xmin)
            pipe_string+='world xmax %g\n'%(xmax)
            pipe_string+='world ymin %g\n'%(ymin)
            pipe_string+='world ymax %g\n'%(ymax)
        majortick=(gw.viewport["graph%02i"%graph]["xmax"]-gw.viewport["graph%02i"%graph]["xmin"])*0.1
        pipe_string+=('xaxis tick major %g\n'%(majortick))
        majortick=(gw.viewport["graph%02i"%graph]["ymax"]-gw.viewport["graph%02i"%graph]["ymin"])*0.1
        pipe_string+=('yaxis tick major %g\n'%(majortick))
        if legend<>None:
            pipe_string+='g%i.s%i legend "%s"\n'%(graph,curve,legend)
        if color>0:
            pipe_string+="g%i.s%i LINE COLOR %i\n"%(graph,curve,mod(color,24)+1)
        else:
            pipe_string+="g%i.s%i LINE COLOR 0\n"%(graph,curve)
        if autoscale: pipe_string+="autoscale\n"
        if noredraw:
            gw(pipe_string)
        else:
            gw(pipe_string+'redraw\n')
            #gw.flush()
        return
    
    def restart_grace_processes(self):
        """Kills living grace processes by PID with signal 15 and restart them."""
        #Kills by PID
        for i in self.gracewins:
            try:
                os.kill(self.gracewins[i].pid,15)
            except KeyboardInterrupt, tmp:
                raise tmp
            except:
                print "restart_grace_processes: cannot kill pid=",self.gracewins[i]," by signal 15"
        #Restart them
        self.start_grace_processes()
        return

    def update_grace_windows(self,iscan):
        """Append new points to the curves. This is a separate function, so that it can be easily executed in a separate thread.
        The iscan value is used to decide on which curve send data. Every iscan has a curve sor as to observe evolutions.
        I reserve the s0 curve for average even if not yet used."""
        #Verify that all arrays have same lenght: this is not necessary using my GPlot function!
        #
        #Shortcuts
        gws=self.gracewins
        gp=self.GPlot
        en=self.graph_data["energy"]
        en_ave=self.graph_data["energy_average"]
        gd=self.graph_data
        #current curve index
        iplot=iscan+1
        #
        for i in gws:
            if not(gws[i].is_open()):
                try:
                    self.restart_grace_processes()
                except:
                    print "Graphics cannot be restarted. Scan will continue without..."
                    self.GRAPHICS_RESTART_NEEDED=True
        try:
            if self.detectionMode in ["absorption","fluo","tey","vortex","sexafs"]:
                #
                #Window exafs_1
                #
                if self.plotSetting=="kinetic":
                    #    Many plots mode
                    gp(gws["exafs_1"],0,iplot,en,gd["mux"],legend="n=%i"%(iplot),color=iplot,noredraw=True)
                    gp(gws["exafs_1"],1,iplot,en,gd["fluochannels"][0],color=iplot)
                elif self.plotSetting=="average":
                    #    Average mode
                    gp(gws["exafs_1"],0,1,en,gd["mux"],legend="n=%i"%(iplot),color=3,noredraw=True)
                    gp(gws["exafs_1"],1,1,en,gd["fluochannels"][0],color=3,noredraw=True)
                    gp(gws["exafs_1"],0,0,en_ave,gd["mux_average"],legend="Average",color=1,noredraw=True)
                    if self.detectionMode=="sexafs":
                        gp(gws["exafs_1"],1,0,en_ave,gd["tey_average"],color=1)
                    else:
                        gp(gws["exafs_1"],1,0,en_ave,gd["fluo_average"],color=1)
                #
                #Window exafs_2
                #
                #For the currents always overwrite the same curve for short
                names=["i0","i1","i2","i_tey"]
                for i in range(len(names)):
                    gp(gws["exafs_2"],1,i,en,gd[names[i]],legend=names[i],color=i+1,noredraw=True)
                gp(gws["exafs_2"],0,iplot,en,gd["mux_ref"],legend=("n=%i"%(iplot)),color=iplot)
                #
                #Window exafs_3
                #
                #For the fluo counts always overwrite the same curve for short
                if self.detectionMode in ["fluo","vortex","sexafs"]:
                    for i in range(len(self.auto_fluo_channels)-1):
                        gp(gws["exafs_3"],i,1,en,gd["fluochannels"][i+1],color=1,noredraw=True)
                    gp(gws["exafs_3"],len(self.auto_fluo_channels)-1,1,en,gd["fluochannels"][len(self.auto_fluo_channels)],\
                    color=1)
                    #gp(gws["exafs_3"],0,1,en,gd["rontec"],color=3)
                    #
            elif self.detectionMode in ["sexafs",]:
                #
                #Window sexafs_1: reference data are TEY data when in sexafs (just to reuse variables)
                #
                if self.plotSetting=="kinetic":
                    #    Many plots mode
                    gp(gws["sexafs_1"],0,iplot,en,gd["mux"],\
                    legend=("n=%i"%(iplot)),color=iplot,noredraw=True)
                    gp(gws["sexafs_1"],1,iplot,en,gd["mux_ref"],color=iplot)
                elif self.plotSetting=="average":
                    #    Average mode
                    gp(gws["sexafs_1"],0,1,en,gd["mux"],legend=("n=%i"%(iplot)),color=3,noredraw=True)
                    gp(gws["sexafs_1"],1,1,en,gd["mux_ref"],color=3,noredraw=True)
                    gp(gws["sexafs_1"],0,0,en_ave,gd["mux_average"],legend="Average",color=1,noredraw=True)
                    gp(gws["sexafs_1"],1,0,en_ave,gd["tey_average"],color=1)
                #
                #Window sexafs_2
                #
                #For the fluo counts always overwrite the same curve for short
                for i in range(1,8):
                    gp(gws["sexafs_2"],i,1,en,gd["fluochannels"][i],noredraw=True)
                gp(gws["sexafs_2"],0,1,en,gd["i0"],color=1,legend="i0",noredraw=True)
                gp(gws["sexafs_2"],0,2,en,gd["i1"],color=2,legend="i1")
                #
            else:
                pass
        except KeyboardInterrupt, tmp:
            raise tmp
        except grace_np.Disconnected:
            print "One or more grace windows have been disconnected or closed !"
            print "Restarting windows...",
            self.restart_grace_processes()
            print "OK"
        except Exception, tmp:
            for i in gws:
                if not(gws[i].is_open()):
                    print "Restarting windows...",
                    self.restart_grace_processes()
                    print "OK"
                    return
            self.plotSetting=None
            print "Unknown error in update_grace_windows... no more plotting in grace"
            print tmp
            print tmp.args
        #cleanup namespace and then returns
        del gws,gp,gd,en        
        return
        
    
    def calculate_pitch(self,energy):
        """Calculate pitch for given energy..."""
        rp=self.ServoPitchParameters
        pitch=(rp[3]-rp[1])/(rp[2]-rp[0])*(energy-rp[0])+rp[1]
        return pitch
        
    def calculate_roll(self,energy):
        """Calculate roll for given energy..."""
        rp=self.ServoRollParameters
        roll=(rp[3]-rp[1])/(rp[2]-rp[0])*(energy-rp[0])+rp[1]
        return roll

    def backup_data(self):
        #NOTA:  This version make an integral backup of folder content
        # another strategy could be just to copy current data file.
        # but I prefer a complete backup including other files too.
        #Backup is performed in a separate shell by os.system
        try:
            if self.backup and not(self.currentBackupFolder in [None,""]):
                command="rsync --ignore-existing  -auv --temp-dir=/tmp '"+self.currentDataFolder+"' '"+self.currentBackupFolder+"'"
                os.system(command)
            else:
                print "Please do a manual backup of data files."
        except:
            print "Cannot make backup to ruche... do it manually!"
        return

    def start(self,filename="",nscans=1,nowait=False):
        self.filename = filename
        ####Hard coded parameters:####
        _UPDATE_GRAPHICS_EVERY=5
        __FLUSH_TO_DISK_EVERY=10
        extension="txt"
        #
        #    Initialize variables common to all scans
        #
        #Want to stop possible values: "EndOfScan", "Yes", "No"
        self.GRAPHICS_RESTART_NEEDED=False
        __WANT_TO_STOP="No"
        #
        mux_list=[None,]
        std_list=[None,]
        mus_total=[]
        mux_total=[]
        fluo_total=[]
        tey_total=[]

        if self.BENDER==True:
            self.__previous_dcm_bender_state=self.dcm.usebender()
            self.dcm.enable_bender()
        elif self.BENDER==False:
            self.dcm.disable_bender()
        else:
            #Do nothing is BENDER is None
            pass
        #Initialise iscan counter
        iscan=-1
        self.iscan=iscan
        ###
        ### Pre run procedure
        ###
        self.pre_run(nowait=nowait)
        #
        # Start graphic windows
        #
        self.start_grace_processes()
        #    
        #Start the real stuff
        #
        file_index=1
        #
        #Prepare graphics data
        #
        self.graph_data={
        "energy":[],
        "energy_average":[],
        "mux":[],
        "mux_ref":[],
        "i0":[],
        "i1":[],
        "i2":[],
        "i_tey":[],
        "fluochannels":[],
        "mux_average":[],
        "tey_average":[],
        "fluo_average":[],
        "rontec":[]
        }
        while (iscan<nscans-1):
            #This must be the first action
            iscan += 1
            self.iscan = iscan
            #
            #Prepare graphics data
            #
            self.graph_data["energy"]=[]
            self.graph_data["mux"]=[]
            self.graph_data["mux_ref"]=[]
            self.graph_data["i0"]=[]
            self.graph_data["i1"]=[]
            self.graph_data["i2"]=[]
            self.graph_data["i_tey"]=[]
            self.graph_data["fluochannels"]=[[] for i in range(len(self.auto_fluo_channels)+1)]
            self.graph_data["rontec"]=[]
            #fluopoint=array([0.,0.,0.,0.,0.,0.,0.,0.],"f")
            fluopoint=zeros(len(self.auto_fluo_channels)+1)
            #fluopoint=[0.,]*(len(self.auto_fluo_channels)+1)
            rontecpoint=array([0.,0.],"f")
            #
            #Prepare correct filename to avoid overwriting
            #
            psep=filename.find(os.sep)
            if(psep<>-1): 
                fdir=filename[:psep]
            else:
                fdir="."
            if(psep<>-1): filename=filename[psep+1:]
            fname=filename+"_"+("%4i"%(file_index)).replace(" ","0")+"."+extension
            dirname=filename+"_"+("%4i"%(file_index)).replace(" ","0")+".d"
            _dir=os.listdir(fdir)
            while(fname in _dir):
                file_index += 1
                dirname = filename + "_" + ("%4i"%(file_index)).replace(" ","0") + ".d"
                fname = filename + "_"+("%4i"%(file_index)).replace(" ","0") + "." + extension
            fname = fdir + os.sep + fname
            dirname = fdir + os.sep + dirname
            f = file(fname,"a")

            ###################### FULL MCA FILES! #####################################
            self.mca_files={}
            if self.fullmca:
                os.mkdir(dirname,0777)
                for mca_channel in self.cpt.read_mca().keys():
                    self.mca_files[mca_channel]=file(dirname+os.sep+fname+"."+mca_channel,"a")
            ###################### FULL MCA FILES! #####################################
            
            ##
            ##Pre scan: get header. The prescan returns the header to be buffered for backup
            ##
            file_buffer=self.pre_scan(f,nowait=nowait)
            ##
            ##
            #thisline="#Energy\tAngle\tmu\tmus\tI0\tI1\tI2\tTEY\tXBPM1\tXBPM2\tRontec_Zero\
            #\tRontec_ROI\tFluo1\tFluo2\tFluo3\tFluo4\tFluo5\tFluo6\tFluo7\
            #\tSEXI0\tSEXI\tSEXBPM1\tSEXBPM2\tEmpty4\tEmpty5\tEmpty6\tEmpty7\
            #\tSEXFluo1\tSEXFluo2\tSEXFluo3\tSEXFluo4\tSEXFluo5\tSEXFluo6\tSEXFluo7\tTimeMeasure(s)\
            #\tPIEZO_write(V)\tPIEZO_read(V)\tBender1\tBender2\tBender_AI1\tBender_AI2\
            #\tTime(count)\tTime(move)\tTemperature(C)\tRontec_DT_factor\
            #\tRs2\tTz2\n"
            #The card HEADER is set on a separate line before the header line
            thisline="#HEADER\n#Energy\tAngle\tmu\tmus\t"+\
                self.cpt_header\
            +"\tPIEZO_write(V)\tPIEZO_read(V)\tBender1\tBender2\tBender_AI1\tBender_AI2\
            \tTime(count)\tTime(move)\tTemperature(C)\tRontec_DT_factor\
            \tRs2\tTz2"

            #Add attributes labels
            for i in self.attributes: thisline+="\t%s"%(i[1])
            #Add newline
            thisline+="\n"
            #Move line to buffer and then write it to file
            file_buffer.append(thisline)
            f.write(thisline)
            file_index+=1
            print "Scanning file :",fname
            self.time_spent_for_scan=time()
            #
            #if self.TUNING: 
            #    p=self.lin_interp(self.trajectory["energy"][0],self.tuning_points)
            ##    p=self.lagrange(self.trajectory["energy"][0],self.tuning_points)
            #    #Set the piezo at the first point by Fibonacci approach
            #    for __backlash_piezo_pos in array(self.__fibonacci(5)[::-1])*(-0.01)+p:
            #        self.dcm.m_rx2fine.pos(__backlash_piezo_pos)
            #    p=__backlash_piezo_pos
            #
            #    Number of points recorded (for average purpose only)
            ave_point = 0
            #    Number of points recorded before next flush to disk and graphic update
            waitflush = 0
            waitplot = 0
            #    Buffer to be written to disk
            line_buffer = ""
            #    DeadTime correction factor (1. by default)
            #    used and modified by rontec mode.
            dt_correction = 1.
            #
            #Point index initialised here below
            #
            pointIndex = 0
            #
            dummy_point = (2 * self.trajectory["energy"][0]) - self.trajectory["energy"][1]
            if self.TUNING: 
                self.dcm.m_rx2fine.pos(self.lin_interp(dummy_point, self.tuning_points))
            self.dcm.pos(dummy_point, Ts2_Moves = self.Ts2_Moves, Tz2_Moves = not(self.notz2))
            sleep(1)
            while(pointIndex < len(self.trajectory["energy"])):
                try:    
                    motors_to_wait=[]
                    en = self.trajectory["energy"][pointIndex]
                    tmeasure = self.trajectory["time"][pointIndex]
                    t0 = time()
                    if self.TUNING: 
                        p = self.lin_interp(en, self.tuning_points)
                        #p = self.lagrange(en, self.tuning_points)
                        self.dcm.m_rx2fine.go(p)
                        motors_to_wait.append(self.dcm.m_rx2fine)
                    else:
                        p = self.dcm.m_rx2fine.pos()
                    if self.PitchCorrection: 
                        self.dcm.m_rx2fine.go(self.calculate_pitch(en))
                        motors_to_wait.append(self.dcm.m_rx2fine)
                    if self.RollCorrection: 
                        self.dcm.m_rs2.go(self.calculate_roll(en))
                        motors_to_wait.append(self.dcm.m_rs2)
                    if self.scanMode == "fast":
                        if self.almostMode:
                            self.cpt.start(tmeasure)
                        else:
                            self.cpt.start(10)
                    #Let's move..."
                    #if self.notz2:
                    #    self.dcm.disable_tz2()
                    #actual = self.dcm.go(en, Ts2_Moves = self.Ts2_Moves, Tz2_Moves = not(self.notz2))
                    #wait_motor([self.dcm,] + motors_to_wait, verbose=False)  #[self.dcm, self.dcm.m_rs2, self.dcm.m_rx2fine])
                    #actual = self.dcm.pos()
                    actual = self.dcm.pos(en, Ts2_Moves = self.Ts2_Moves, Tz2_Moves = not(self.notz2))
                    if motors_to_wait <>[]:
                        wait_motor(motors_to_wait, verbose=False)
                    actual = self.dcm.pos()
                    if self.SettlingTime >0:
                        sleep(self.SettlingTime)
                    tmove = time() - t0
                    if en <= self.grid[-1][0]:
                        print "%8.2f\r"%(actual),
                    elif self.kscan:
                        print "En=%8.2f k=%5.2f\r"%(actual, sqrt(0.2624 * (actual - self.kscan_e0))),
                    sys.stdout.flush()
                    #Read mono position BEFORE counting (step mode)
                    theta = self.dcm.m_rx1.pos()
                    etheta = self.dcm.theta2e(theta)
                    ##
                    ##Pre recording
                    ##
                    self.pre_recording(nowait=nowait)
                    ##
                    ##Counting section: different strategies depending on mode
                    ##
                    #tc=time()
                    if self.scanMode == "step":
                        cnts = array(self.cpt.count(tmeasure),dtype=float32)
                        #cnts[self.timer_channel] = cnts[self.timer_channel]/999984.
                    elif self.scanMode=="fast":
                        if self.almostMode:
                            self.cpt.wait()
                        else:
                            self.cpt.stop()
                        cnts=array(self.cpt.read(),dtype=float32)
                        #cnts[self.timer_channel]=cnts[self.timer_channel]/999984.
                    #
                    #Be careful to convert in float... mind the last dot!
                    #
                    #Counting now is finished: last corrections common to all modes follow
                    #
                    #print "Counting takes ", time()-tc," seconds."
                    i0, i1, i2 = cnts[0:3]
                    #
                    #Calculate the absorption depending on different detection schemes
                    #
                    
                    #Assertions valid for all modes:
                    fluopoint[0] = 0.
                    #This modification holds when using the XIA card as configured
                    #for SAMBA...
                    try:
                        for i in range(len(self.auto_fluo_channels)):
                            fluopoint[i+1] = cnts[self.auto_fluo_channels[i]]
                    except Exception, tmp:
                        print "No fluorescence channels!!!!!"
                        print tmp
                    #Assertions valid for specific modes
                    if self.detectionMode in ["absorption","fluo","tey","vortex"]:
                        if i1 * i0 > 0 :
                            mu = log(abs(i0 / i1))
                        else:
                            mu = 0.
                    if self.detectionMode == "tey":
                        if i0 <> 0:
                            mu = cnts[3]/i0
                        else:
                            mu = 0.
                    elif self.detectionMode=="fluo":
                        if i0 <> 0:
                            #This modification holds when using the XIA card as configured
                            #for SAMBA...
                            try:
                                fluopoint[0] = average(fluopoint[2:]) / i0
                            except Exception, tmp:
                                fluopoint[0] = 0.
                                print "Error calculating fluopoint[0]"
                                print tmp
                        else:
                            fluopoint[0] = 0.
                    elif self.detectionMode == "sexafs":
                        if i0 > 0:
                            #This modification holds when using the XIA card as configured
                            #for SAMBA...
                            try:
                                #The sexafs detector is connected from channel 0 to 7
                                #on the xia cards
                                #Fluo
                                fluopoint[0] = average(fluopoint[1:8]) / i0
                                #Tey
                                mu = cnts[2] / i0
                                #Reference foil (counters are apparently reversed in this case...)
                                if (i0 * i1 > 0.): 
                                    mus = log(i1 / i0)
                                else:
                                    mus = 0.
                            except:
                                print "Error calculating fluopoint[0]"
                                pass
                        else:
                            fluopoint[0] = 0.
                            mu = 0.
                            mus = 0.
                    elif self.detectionMode=="vortex":
                        #print "Calculating absorption for vortex"
                        if i0 <> 0:
                            fluopoint[0] = fluopoint[1] / i0
                        else:
                            fluopoint[0] = 0.
                        #dt_correction=cnts[47]/cnts[55]
                        #if dt_correction in [nan,inf]: dt_correction=0.0
                        dt_correction = 1.
                        rontecpoint[0] = fluopoint[1]
                        rontecpoint[1] = dt_correction
                    else:
                        if i0 * i1 <> 0:
                            mu = log(abs(i0/i1))
                        else: 
                            mu = 0.
                    if self.detectionMode<>"sexafs":
                        if i2 * i1 <> 0:
                            mus = log(abs(i1 / i2))
                        else:
                            mus = 0.
                    if self.detectionMode in ["fluo", "vortex"]:
                        line_buffer += ("%8.2f\t%8.6f\t%8.6f\t%8.6f\t" % (etheta, theta, fluopoint[0], mus))
                    elif self.detectionMode in ["sexafs",]:
                        line_buffer += ("%8.2f\t%8.6f\t%8.6f\t%8.6f\t" % (etheta, theta, fluopoint[0], mu))
                    else:
                        line_buffer += ("%8.2f\t%8.6f\t%8.6f\t%8.6f\t"%(etheta,theta,mu,mus))
                    #The user_readconfig should be used instead...
                    for i in cnts:
                        line_buffer += ("%g\t"%(i))
                    ###! WARNING:
                    ###! Les  thermocouples sont definies en durs !
                    ###! 
                    try:
                        temperature=self.temperature_DP.read_attribute("temperature").value
                        if temperature.__repr__() == 'nan': temperature = -1000.
                    except KeyboardInterrupt, tmp:
                        raise tmp
                    except:
                        #print "Invalid temperature reading..."
                        temperature = -1000.
                    
                    try:
                        bp1, bp2 = self.dcm.bender.c1.pos(),self.dcm.bender.c2.pos()
                    except:
                        bp1, bp2 = 0.,0.
                    try:
                        an1, an2 = self.dcm.bender.analog1(), self.dcm.bender.analog2()
                    except:
                        an1, an2 = 0., 0.
                    #line_buffer+=("%g\t%g\t%g\t%g\t%g\t%g\t%g\t%g\t%g\t%g\t%g\t%g\t%g"\
                    line_buffer+=("%g\t%g\t%g\t%g\t%g\t%g\t%g\t%g\t%g\t%g\t%g\t%g"\
                    % (p, self.dcm.m_rx2fine.pos(),\
                    bp1, bp2,\
                    an1, an2,\
                    tmeasure, tmove, temperature, dt_correction,\
                    self.dcm.m_rs2.pos(), self.dcm.m_tz2.pos()\
                    ))
                    #Append additional attributes
                    for i in self.attributes:
                        try:
                            line_buffer += "\t%g" % (i[0].read().value)
                        except Exception, tmp:
                            line_buffer += "\t%g" % (0)
                            print tmp
                    #Add newline
                    line_buffer += "\n"
                    #
                    # Write buffer to disk and reset it
                    #
                    try:
                        f.write(line_buffer)
                        ###The file buffer is update in case of no failure only to avoid double entries
                        file_buffer.append(line_buffer)
                        ###if there are no errors the line_buffer is reset.
                        line_buffer = ""
                        ###If, at the end of a scan, a line_buffer is not empty, it means it must be added to
                        ###the file_buffer.
                    except KeyboardInterrupt, tmp:
                        raise tmp
                    except:
                        print "Cannot write to file!!!!!!"
                        print "If this problem occurs often, call the Local Contact Please..."
                    pointIndex += 1
                    try:
                        if waitflush == __FLUSH_TO_DISK_EVERY:
                            f.flush()
                            waitflush = 0
                        else:
                            waitflush += 1
                    except KeyboardInterrupt, tmp:
                        raise tmp
                    except:
                        print "Cannot flush this data point to file ..."
                    ######################################################################################
                    #            Write to Full MCA files
                    ######################################################################################
                    if self.fullmca:
                        __fullmca = self.cpt.read_mca()
                        for mca_channel in self.mca_files.keys():
                            __fullmca_line = __fullmca[mca_channel]
                            __fullmca_line_format = "%d\t" * (len(__fullmca_line) - 1) + "%d\n"
                            self.mca_files[mca_channel].write(__fullmca_line_format % tuple(__fullmca_line))
                    ######################################################################################
                    self.graph_data["energy"].append(etheta)
                    if len(self.graph_data["energy_average"]) < len(self.graph_data["energy"]):
                        self.graph_data["energy_average"].append(etheta)
                    self.graph_data["mux"].append(mu)
                    self.graph_data["mux_ref"].append(mus)
                    t_nor = 1.
                    if self.cpt.clock_channel > -1 and cnts[self.cpt.clock_channel] <>0:
                        t_nor = float(cnts[self.cpt.clock_channel])
                    if self.detectionMode == "sexafs":
                        self.graph_data["i0"].append(cnts[0] / t_nor)
                        self.graph_data["i1"].append(cnts[1] / t_nor)
                        self.graph_data["i2"].append(cnts[2] / t_nor)
                    else:
                        self.graph_data["i0"].append(i0 / t_nor)
                        self.graph_data["i1"].append(i1 / t_nor)
                        self.graph_data["i2"].append(i2 / t_nor)
                    self.graph_data["fluochannels"][0].append(float(fluopoint[0]))
                    for i in range(1, len(fluopoint)):
                        self.graph_data["fluochannels"][i].append(float(fluopoint[i]) / t_nor)
                    self.graph_data["rontec"].append(rontecpoint[0] / t_nor)
                    #Start average calculation
                    # Average mux data
                    if len(self.graph_data["mux_average"]) < len(self.graph_data["mux"]):
                        mux_total.append(mu)
                        self.graph_data["mux_average"].append(mu)
                    else:
                        mux_total[ave_point] += mu
                        self.graph_data["mux_average"][ave_point] = mux_total[ave_point] / (iscan + 1)
                    # Average fluo data
                    if len(self.graph_data["fluo_average"]) < len(self.graph_data["mux"]):
                        fluo_total.append(fluopoint[0])
                        self.graph_data["fluo_average"].append(fluopoint[0])
                    else:
                        fluo_total[ave_point] += fluopoint[0]
                        self.graph_data["fluo_average"][ave_point] = fluo_total[ave_point] / (iscan + 1)
                    # Average SEXAFS TEY data
                    if self.detectionMode == "sexafs":
                        if len(self.graph_data["tey_average"]) < len(self.graph_data["mux_ref"]):
                            mus_total.append(mus)
                            self.graph_data["tey_average"].append(mus)
                        else:
                            mus_total[ave_point] += mus
                            self.graph_data["tey_average"][ave_point] = mus_total[ave_point] / (iscan + 1)
                    ave_point += 1
                    
                    # End of average calculation
                    #!
                    #!Call the graphics (thread) here 
                    #!
                    if self.plotSetting<>None:
                        if self.GRAPHICS_RESTART_NEEDED == False:
                            if mod(waitplot,_UPDATE_GRAPHICS_EVERY) == 0:
                                waitplot = 0
                                self.update_grace_windows(iscan)
                                #thread.start_new_thread(self.update_grace_windows, (iscan,))
                            else:
                                waitplot += 1
                        else:
                            self.update_grace_windows(iscan)
                    #
                    #END OF A SCAN CYCLE
                    #
                except (KeyboardInterrupt,SystemExit), tmp:
                    self.cpt.stop()
                    if tmp.__class__==KeyboardInterrupt:
                        print "Welcome on the Samba answering machine:"
                        print "---------------------------------------"
                        print "Type 1 to end this scan"
                        print "Type 2 to end at the end of this scan"
                        print "Type 3 to change the total number of scans"
                        print "Type 4 if you want to continue..."
                        print ""
                        mychoice=input("-->")
                        if mychoice=="" or type(mychoice)==str:
                            print "I ignore your command, sir."
                            mychoice=4
                        if mychoice==1:
                            print "Ending this can, sir"
                            self.dcm.stop()
                            if line_buffer:
                                file_buffer.append(line_buffer)
                                line_buffer=""
                            #Setting to False the TUNING option prevent the after_scan hook
                            #to perform a useless and time consuming scan_tuning
                            self.TUNING=False
                            self.after_scan(f,nowait,iscan,nscans,file_buffer,fname)
                            f.close()
                            print "Scan finished on user request."
                            try:
                                self.update_grace_windows(iscan)
                            except:
                                pass
                            try:
                                self.update_grace_windows(iscan)
                            except:
                                pass
                            self.after_run(handler=f,nowait=nowait)
                            raise tmp
                        if mychoice==2:
                            #Repeat last point... maybe this is idiot
                            if line_buffer<>"":
                                line_buffer=""
                            pointIndex-=1
                            __WANT_TO_STOP="EndOfScan"
                            self.GRAPHICS_RESTART_NEEDED=True
                        if mychoice==3:
                            print "Current scan is :",iscan
                            print "Total number of scans:",nscans
                            print "New total number of scans:",
                            new_nscans=input()
                            nscans=int(new_nscans)
                            print "Got new total number of scans:",nscans
                            #Repeat last point... maybe this is idiot
                            if line_buffer<>"":
                                line_buffer=""
                            pointIndex-=1
                            print "I am going back to work, sir"
                            self.GRAPHICS_RESTART_NEEDED=True
                        if mychoice==4:
                            #Repeat last point... maybe this is idiot
                            if line_buffer<>"":
                                line_buffer=""
                            pointIndex-=1
                            print "I am going back to work, sir"
                            self.GRAPHICS_RESTART_NEEDED=True
                    else:
                        self.dcm.stop()
                        if line_buffer:
                            file_buffer.append(line_buffer)
                            line_buffer=""
                        #Setting to False the TUNING option prevent the after_scan hook
                        #to perform a useless and time consuming scan_tuning
                        self.TUNING=False
                        self.after_scan(f,nowait,iscan,nscans,file_buffer,fname)
                        f.close()
                        print "Scan finished on user request."
                        raise tmp
                except PyTango.DevFailed, tmp:
                    raise tmp
                except Exception, tmp: 
                    print "Error during scan! trying to end well..."
                    self.dcm.stop()
                    #Setting to False the TUNING option prevent the after_scan hook
                    #to perform a useless and time consuming scan_tuning
                    self.TUNING=False
                    self.after_scan(f,nowait,iscan,nscans,file_buffer,fname)
                    f.close()
                    ##################### CLOSE MCA FILES ##################
                    for mca_channel in self.mca_files.keys():
                        self.mca_files[mca_channel].close()
                    ########################################################
                    self.after_run(handler=f,nowait=nowait)
                    raise tmp
            ##
            ##After scan
            ##
            
            #!
            #!Call the graphics update for the last few points 
            #!
            if self.plotSetting <> None:
                self.update_grace_windows(iscan)
                #thread.start_new_thread(self.update_grace_windows,(iscan,))
            #
            if line_buffer:
                #if the line buffer is not empty, it means that a problem occured...
                file_buffer.append(line_buffer)
                line_buffer = ""
            #
            #After scan will close file, no more data written after after_scan!
            #
            self.after_scan(f, nowait, iscan, nscans, file_buffer, fname)
            #
            #the file has been closed in after_scan        
            #f.close()
            #
            file_buffer = []
            print "Scan ",iscan+1,"out of ",nscans," scans finished."
            
            mux_list.append(None)
            std_list.append(None)
            if __WANT_TO_STOP == "EndOfScan": 
                print "WARNING: User requested to stop the run at the end of this scan.\n Run ends now."
                break
        
        ##
        ##After run
        ##
        self.after_run(handler=f,nowait=nowait)
        #Hello world!
        print "Series of scans finished, may the python be with you! :-)"
        return
    
    def pre_run(self,nowait=False):
        #
        #
        #!
        #! Set correct Ts2 and Tz2 before any other beam operation!
        #!
        #Following lines could considered obsolete. Keep them to track changes.
        #notz2: could it follow the same destiny?
        #if(not(self.Ts2_Moves)): 
        #    #    #print "Setting ts2..."
        #    #    self.set_ts2()
        #if self.notz2:
            #print "Setting tz2..."
        #    self.set_tz2()
        #
        # Wait for beam if necessary
        #
        #print "Checking for beam..."
        if(not(checkTDL(self.FE)) and not(nowait)):
            wait_injection(self.FE,self.stoppersList)
            sleep(10.)
        #
        #Execute total tuning just once for this run
        #
        #print "Tuning crystals... if necessary"
        if self.TUNING: 
            self.scan_tuning(self.tuningdegree)
        return

    def pre_scan(self,handler=None,nowait=False):
        """Execute all operations needed before every and each scan."""
        #Backlash recovery
        #if self.iscan>=1 or not(self.TUNING): self.backlash_recovery(self.e1)
        #
        if self.RollCorrection:
            try:
                self.dcm.m_rs2.pos(self.calculate_roll(self.e1-4))
            except:
                print "pre_scan: Error while moving dcm.m_rs2 to first point"
        #Wait for injection if necessary
        if(not(nowait)):
            if(not(checkTDL(self.FE))):
                wait_injection(self.FE,self.stoppersList)
                self.AFTER_INJECTION=True
                sleep(10.)
        if self.AFTER_INJECTION: 
            if self.TUNING:
                self.scan_tuning(self.tuningdegree)
            self.AFTER_INJECTION=False
            #Below we retune the first point if we are not at the first scan
        else:
            #The backlash has been perfomed few lines above
            if self.TUNING and self.iscan>=1:
#            if self.TUNING:
                print "Retuning first point..."
                self.dcm.pos(self.tuning_points[0][0], Ts2_Moves=self.Ts2_Moves, Tz2_Moves=not(self.notz2))
                if self.RollCorrection:
                    self.dcm.m_rs2.pos(self.calculate_roll(self.tuning_points[0][0]))
                if self.detune==1:
                    #__p=self.tuning_points[1][0]
                    #self.tuning_points[1][0]=self.dcm.tune(max(0.,__p-2),min(9.9,__p+2))
                    self.tuning_points[1][0]=self.dcm.tune()
                else:
                    self.tuning_points[1][0]=self.dcm.detune(self.detune)
                    print "Detuned of ",self.detune*100,"%"
        buffer=[]
        buffer.append("#"+handler.name+"\n")
        buffer.append("#Scan parameters follow:\n")
        for i in self.formtext:
            buffer.append("#"+i)
        #fname=GetPositions(fname="",hardcopy=False,verbose=0)
        #try:
        #    f=file(fname,'r')
        #    ll=f.readlines()
        #    for i in range(len(ll)): 
        #        ll[i]="#"+ll[i]
        #    buffer+=ll
        #except:
        #    pass
        try:
            GetPositions(verbose=0)
            for i in wa(verbose=False,returns=True):
                buffer.append("#"+i+"\n")
        except Exception, tmp:
            print "Error when getting motors positions!"
            print tmp
        buffer.append("#dcm is focusing at %6.3f m\n"%(self.dcm.sample_at()))
        buffer.append("#dcm  2d spacing is %8.6f m\n"%(self.dcm.d*2.))
        buffer.append("#2d spacing for common crystals [A]: 2d[Si(111)]=6.2712 2d[Si(220)]=3.8403 2d[Si(311)]=3.2749\n")
        try:
            buffer.append("#Machine Current = %g\n"%(self.ms.read_attribute("current").value))
        except:
            buffer.append("#Machine Current = nan\n")
        buffer.append("#"+asctime()+"\n")
        handler.writelines(buffer)
        return buffer
        
    def pre_recording(self,handler=None,nowait=False):
        if(not(nowait)):
            try:
                currentTooLow = (self.ms.read_attribute("current").value < 8.)
            except:
                currentTooLow = False
                pass
            if currentTooLow:
                self.FE.close()
                print RED + BOLD + "Beam Loss: current is below 8mA !" + RESET
                print "Waiting two minutes before checking Front End state: ",
                sys.stdout.flush()
                sleep(2*60.)
                print "done."
            if(not(checkTDL(self.FE)) or currentTooLow):
                wait_injection(self.FE,self.stoppersList)
                self.AFTER_INJECTION=True
                sleep(10.)
        return
    
    def after_scan(self,handler=None,nowait=False,iscan=1,nscans=1,file_buffer=None,fname=None):
        """After scan will perform a series of operations and finally CLOSE the data file and 
        request its backup."""
        print "WARNING: Ending scan operations, please, do not stop now."
        try:
            ll=["#Machine Current = %g\n"%(self.ms.read_attribute("current").value),]
        except:
            ll=["#Machine Current = nan\n",]
        ll.append("#"+asctime()+"\n")
        try:
            GetPositions(verbose=0)
            for i in wa(verbose=False,returns=True):
                ll.append("#"+i+"\n")
        except Exception, tmp:
            print "Error when getting motors positions!"
            print tmp
        handler.writelines(ll)
        if iscan < nscans - 1:
            if(not(nowait)):
                if(not(checkTDL(self.FE))):
                    wait_injection(self.FE,self.stoppersList)
                    self.AFTER_INJECTION=True
            #if self.TUNING:
            #    self.scan_tuning(self.tuningdegree)
            #Below we retune only the last point
            if self.TUNING:
                print "Retuning last point..."
                #print "Tuning at Energy=",self.tuning_points[0][-1]
                #self.dcm.pos(self.tuning_points[0][-1], Ts2_Moves=self.Ts2_Moves)
                self.tuning_points[0][-1]=self.dcm.pos()
                if self.detune==1:
                    #__p=self.tuning_points[1][-1]
                    #self.tuning_points[1][-1]=self.dcm.tune(max(0.5,__p-2),min(9.5,__p+2))
                    self.tuning_points[1][-1]=self.dcm.tune()
                else:
                    self.tuning_points[1][-1]=self.dcm.detune(self.detune)
                    print "Detuned of ",self.detune*100,"%"
        #Close file before backup
        handler.close()
        #Execute backup
        #thread.start_new_thread(self.backup_data,())
        self.backup_data()
        #
        print "OK, end of scan operations over."
        self.time_spent_for_scan=time()-self.time_spent_for_scan
        print "Time spent for the scan: %6.0fs or %6.2fmin"%(self.time_spent_for_scan,self.time_spent_for_scan/60.)
        return
        
    def after_run(self,handler=None,nowait=False):
        """All operations to be accomplished after an entire series of scans"""
        if self.notz2:
            self.dcm.usetz2(self.previous_dcm_tz2_setting)
        if(self.BENDER):
            self.dcm.usebender(self.__previous_dcm_bender_state)
        self.EndOfRunAlert()
        return
    

    def EndOfRunAlert(self):
        """Uses Tkinter to alert user that the run is finished... just in case he was sleeping..."""
        #try:
        #    pass
        #    Beep(5,0.1);Beep(5,0.2)
        #    Beep(5,0.1);Beep(5,0.2)
        #except:
        #    print "WARNING: Error alerting for end of scan... \n"
        #    print "BUT: Ignore this message if escan is working well,\n just report this to your local contact\n"
        try:
            a=Tkinter.Tk()
            for j in range(5):
                for i in range(3):
                    a.bell()
                    sleep(0.025)
                sleep(0.35)
            a.destroy()
        except:
            print "WARNING: Error alerting for end of scan... no Tkinter?\n"
            print "BUT: Ignore this message if escan is working well,\n just report this to your local contact\n"
        return
def escan(filename="",form="",n=1,nowait=False):
    """Provide the start of the filename for the data, the parameters file, the number of scans.
    If you do NOT want to check the presence of beam (injections, beam loss...) set nowait=True."""
    if(filename==""):
        if NoTk:
            raise Exception("escan:","Please provide prefix for output file name")
        else:
            filename=tkFileDialog.asksaveasfilename(title="Save scans as... Please omit extension",initialdir=".")
    if(form==""):
        if NoTk:
            raise Exception("escan:","Please provide a file with scan parameters")
        else:
            form=tkFileDialog.askopenfilename(title="Open Scan parameters file...",initialdir=".")
    if(n<1):
        return "No scans to do."
    if(form==""): 
        print "Missing parameter filename!"
        return 
    if(filename==""):
        print "Missing data filename!"
        return
    es=escan_class(form)
    es.start(filename,n,nowait=nowait)
    del es
    return 
    

def escan_test(filename="",form="",n=1):
    """Provide the start of the filename for the data, the parameters file, the number of scans.
    nowait=True all the time for tests without beam."""
    return escan(filename,form,n,nowait=True)
    

