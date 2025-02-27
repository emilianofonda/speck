# -*- coding: utf-8 -*-
from __future__ import print_function
import tables
import os,sys
import numpy as np
import time as myTime
from time import sleep,asctime
from p_spec_syntax import wait_motor,whois
from GracePlotter import GracePlotter
from p_spec_syntax import dark as ctDark
from wait_functions import checkTDL, wait_injection
import mycurses
from PyTango import DevState, DeviceProxy
import pylab

try:
    import Tkinter
    NoTk=False
except:
    print("Tkinter not installed.")
    NoTk=True

print(mycurses.PINK+"Using alpha version of cscan"+mycurses.RESET)



def stop_cscan(shutter=False,cmot=None,cmot_previous_velocity=None):
    shell=get_ipython()
    ct = shell.user_ns["ct"]
    try:
        if shutter:
            sh_fast.close()
    except:
        pass
    print("Wait... Stopping Devices...", end=' ')
    sys.stdout.flush()
    ct.stop()
    try:
        ct.handler.close()
    except:
        pass
    cmot.stop()
    myTime.sleep(3)
    cmot.velocity = cmot_previous_velocity
    print("Scan Stopped: OK")
    sys.stdout.flush()
    return

def stop_tcscan(shutter=False):
    shell=get_ipython()
    ct = shell.user_ns["ct"]
    try:
        if shutter:
            sh_fast.close()
    except:
        pass
    print("Wait... Stopping Devices...", end=' ')
    sys.stdout.flush()
    ct.stop()
    try:
        ct.handler.close()
    except:
        pass
    print("Scan Stopped: OK")
    sys.stdout.flush()
    return

class CPlotter:
    def __init__(self):
        return


__CPlotter__ = CPlotter()

def cscan(cmot,p1,p2,velocity=None,n=1,dt=0.1, channel=1,shutter=False,beamCheck=True,filename="cscan_out"):
    cmot_previous_velocity = cmot.velocity
    cmot_previous_position = cmot.pos()
    print("motor %s was at %f"%(whois(cmot),cmot_previous_position))
    shell=get_ipython()
    try:
        for i in range(n):
            #Previous speed to record
            cscanActor(cmot,p1,p2,velocity=velocity,n=1,dt=dt, channel=channel,shutter=shutter,beamCheck=beamCheck,filename=filename)
            #Previous speed to restore
    except KeyboardInterrupt:
        shell.logger.log_write("ecscan halted on user request: Ctrl-C\n", kind='output')
        print("Halting on user request.")
        sys.stdout.flush()
        stop_cscan(shutter, cmot, cmot_previous_velocity)
        print("ecscan halted. OK.")
        print("Raising KeyboardInterrupt as requested.")
        sys.stdout.flush()
        raise KeyboardInterrupt
    except Exception as tmp:
        shell.logger.log_write("Error during ecscan:\n %s\n\n" % tmp, kind='output')
        print(tmp)
        stop_cscan(shutter, cmot, cmot_previous_velocity)
        raise tmp
    return 

def cscanActor(cmot,p1,p2,velocity=None,n=1,dt=0.1, channel=1,shutter=False,beamCheck=True,filename="cscan_out"):
    """Start from p1 to p2 and count over dt (s) per point.
    velocity: if None currenty is used.
    The backup folder MUST be defined for the code to run.
    Global variables: FE and obxg must exist and should point to Front End and Shutter
    """
    if velocity==None:
        try:
            velocity=cmot.velocity
        except:
            raise("Velocity cannot be retrieved or set on motor.")
    shell=get_ipython()
    FE = shell.user_ns["FE"]
    obxg = shell.user_ns["obxg"]
    ct = shell.user_ns["ct"]
    dcm = shell.user_ns["dcm"]
    mostab = shell.user_ns["mostab"]
    TotalScanTime = myTime.time()
    NofScans = n
    if not "associated_counter" in dir(cmot.DP):
        raise Exception("associated_counter not specified for %s. Impossible to proceed." % cmot.label)
    #
    if filename == None: 
        raise Exception("filename and limits must be specified")
    if velocity <= 0.:
        raise Exception("Invalid velocity!")
    #Calculate acceleration overhead:
    accel_space = float(0.5 * velocity**2 / cmot.acceleration+ 0.5 * velocity**2 / cmot.deceleration)
    delta_time_acceleration = float(0.5 * velocity / cmot.acceleration + 0.5 * velocity / cmot.deceleration)
    
    TotalTime = float(abs(p2-p1)) / velocity + delta_time_acceleration
    print("Expected time = %g s" % TotalTime)
    
    NumberOfPoints =  int(TotalTime / dt + 1)
    print("Number of points: ",NumberOfPoints)
    print("One point every %8.6f motor units." % (velocity * dt))
    
    if beamCheck and not(checkTDL(FE)):
        wait_injection(FE,[obxg,])
        myTime.sleep(10.)
    
    # Store the where_all_before
    wa_before = shell.user_ns["wa"](verbose=False,returns=True)
    #
    cmot_previous_velocity = cmot.velocity * 1
    #Send motor to start position
    cmot.pos(p1)
    #Prepare recording (and acquire first point position... this prevents preparing AND moving)
    print("Preparing acquisition ... ", end=' ')
    ct.prepare(dt=dt,NbFrames = NumberOfPoints, nexusFileGeneration = True)
    print("OK")
    handler = ct.openHDFfile(filename)
#Warning: using the handler out of ct and directly has to be avoided, problems arise when scans are aborted and resumed. 
    #Create coordinates links and arrays in file
    handler.create_soft_link('/coordinates', 'X1', target='/data/'+cmot.DP.associated_counter.replace(".","/"))
    #Set scan speed
    cmot.velocity = velocity
    myTime.sleep(0.1)
    
    timeAtStart = asctime()
    #Start acquisition?
       #Print Name:
    print("Measuring : %s\n"%ct.handler.filename)
    try:
        pass
        if shutter:
            sh_fast.open()
    except KeyboardInterrupt:
        stop_cscan(shutter, cmot, cmot_previous_velocity)
        raise
    except:
        pass
    #Start Acquisition
    ct.start(dt)
    #myTime.sleep(0.5)
    #Start  Motor
    cmot.pos(p2, wait=False)
    myTime.sleep(0.1)
    while(cmot.state() == DevState.MOVING):
        myTime.sleep(0.1)
    try:
        if shutter:
            sh_fast.close()
    except KeyboardInterrupt:
        raise
    except:
        pass
    ct.wait()
    ct.saveData2HDF()
    #
    #Insert here specific data saving in ct.handler at position root.post? root.spectra?....
    #
    graph_x = eval("ct.handler.root.data.%s.read()"%cmot.DP.associated_counter.replace("/","."))
    #
    #Save CONTEXT
    #
#Context can be saved to an approriate dictionary like post.
#This will make scan procedures much more flexible and general
    ct.savePost2HDF("where_all_before", np.array(wa_before), 
    group = "", wait = True, HDFfilters = tables.Filters(complevel = 1, complib='zlib'), domain="context")
    try:
        ct.savePost2HDF("where_all_after", np.array(shell.user_ns["wa"](verbose=False,returns=True)), 
        group = "", wait = True, HDFfilters = tables.Filters(complevel = 1, complib='zlib'), domain="context")
    except:
        print("Cannot save where_all_after.")
    # MOSTAB and Mono Configs
    try:
        ct.savePost2HDF("mostab", np.array(mostab.status().split("\n")), 
        group = "", wait = True, HDFfilters = tables.Filters(complevel = 1, complib='zlib'), domain="context")
    except:
        print("Cannot save mostab status.")
    try:
        ct.savePost2HDF("dcm", np.array(dcm.status().split("\n")), 
        group = "", wait = True, HDFfilters = tables.Filters(complevel = 1, complib='zlib'), domain="context")
    except:
        print("Cannot save dcm status.")
    #
    #
    ct.closeHDFfile()
    print("Saving actions over!")
    timeAtStop = asctime()
    timeout0 = myTime.time()
    #The plotting, once finalised a reasonable code, could be generalised via a generic function and a dictionary listing plot items 
    try:
        f=tables.open_file(ct.final_filename,"r")
        fig1 = pylab.figure(3,figsize=(8,11),edgecolor="white",facecolor="white",)
        fig1.clear()
        pylab.subplot(4,1,1)
        pylab.ylabel("$\mu$x")
        try:
            pylab.plot(graph_x, f.root.post.MUX.read())
        except:
            pass
        pylab.subplot(4,1,2)
        pylab.ylabel("Fluo")
        try:
            pylab.plot(graph_x, f.root.post.FLUO.read(),label="DTC on")
        except:
            pass
        try:
            pylab.plot(graph_x, f.root.post.FLUO_RAW.read(),label="DTC off")
        except:
            pass
        pylab.legend(frameon=False)    
        pylab.subplot(4,1,3)
        pylab.ylabel("$\mu$x Reference")
        pylab.plot(graph_x, f.root.post.REF.read())
        pylab.subplot(4,1,4)
        pylab.ylabel("$I_0,I_1,I_2$ Counts")
        try:
            pylab.xlabel("%s (%s)"%(whois(cmot),cmot.DP.get_attribute_config(x.att_name).unit))
        except:
            pylab.xlabel("%s"%(cmot.att_name))
        pylab.plot(graph_x, f.root.post.I0.read(),"r",label="$I_0$")
        pylab.plot(graph_x, f.root.post.I1.read(),"k",label="$I_1$")
        pylab.plot(graph_x, f.root.post.I2.read(),"g",label="$I_2$")
        pylab.legend(frameon=False)    
        pylab.draw()
    except Exception as tmp:
        print("No Plot! Bad Luck!")
        print(tmp)
    finally:
        f.close()
    shell.logger.log_write("Total Elapsed Time = %i s" % (myTime.time() - TotalScanTime), kind='output')
    print("Total Elapsed Time = %i s" % (myTime.time() - TotalScanTime)) 
    #AlarmBeep()
    cmot.velocity = cmot_previous_velocity
    return
    
def dcscan(cmot,p1,p2,velocity=None,n=1,dt=0.1, channel=1,shutter=False,beamCheck=True,filename="cscan_out"):
    cmot_previous_velocity = cmot.velocity
    shell=get_ipython()
    cmot_previous_position = cmot.pos()
    print("motor %s was at %f"%(whois(cmot),cmot_previous_position))
    try:
        for i in range(n):
            #Previous speed to record
            cscanActor(cmot,cmot_previous_position + p1,cmot_previous_position + p2,\
            velocity=velocity,n=1,dt=dt, channel=channel,shutter=shutter,beamCheck=beamCheck,filename=filename)
            #Previous speed to restore
    
    except KeyboardInterrupt:
        shell.logger.log_write("ecscan halted on user request: Ctrl-C\n", kind='output')
        print("Halting on user request.")
        sys.stdout.flush()
        stop_cscan(shutter, cmot, cmot_previous_velocity)
        print("ecscan halted. OK.")
        print("Raising KeyboardInterrupt as requested.")
        sys.stdout.flush()
        raise KeyboardInterrupt
    except Exception as tmp:
        shell.logger.log_write("Error during ecscan:\n %s\n\n" % tmp, kind='output')
        print(tmp)
        stop_cscan(shutter, cmot, cmot_previous_velocity)
    finally:
        cmot.pos(cmot_previous_position)
    return 

def c2scan(cmot,p1,p2,velocity,mot2,p21,p22,dp2,n=1,dt=0.1, channel=1,shutter=False,beamCheck=True,filename="c2scan_out"):
    """Start from p1 to p2 and count over dt (s) per point.
    Make a map over cmot2 position, this not being moved continuously.
    velocity: if None current is used.
    The backup folder MUST be defined for the code to run.
    Global variables: FE and obxg must exist and should point to Front End and Shutter
    """
    shell=get_ipython()
    FE = shell.user_ns["FE"]
    obxg = shell.user_ns["obxg"]
    ct = shell.user_ns["ct"]
    dcm = shell.user_ns["dcm"]
    mostab = shell.user_ns["mostab"]
    TotalScanTime = myTime.time()
    NofScans = n
    if not "associated_counter" in dir(cmot.DP):
        raise Exception("associated_counter not specified for %s. Impossible to proceed." % cmot.label)
    #
    if filename == None: 
        raise Exception("filename and limits must be specified")
    if velocity <= 0.:
        raise Exception("Invalid velocity!")
    #Calculate acceleration overhead:
    accel_space = float(0.5 * velocity**2 / cmot.acceleration+ 0.5 * velocity**2 / cmot.deceleration)
    delta_time_acceleration = float(0.5 * velocity / cmot.acceleration + 0.5 * velocity / cmot.deceleration)
    #Configure cards
    TotalTime = float(abs(p2-p1)) / velocity + delta_time_acceleration
    #NumberOfPoints = int (float(abs(p2-p1)) / velocity / dt)
    NumberOfPoints =  int(TotalTime / dt + 1)
    NumberOfLines = int(float(abs(p22 - p21))/dp2) + 1
    if p22 < p21: 
        dp2 = -abs(dp2)
    else:
        dp2 = abs(dp2)
    print("Expected time = %g s" % (TotalTime * NumberOfLines))
    print("Number of points: ",NumberOfPoints)
    print("Number of lines : ",NumberOfLines)
    print("One point every %8.6f motor units." % (velocity * dt))
    
    if beamCheck and not(checkTDL(FE)):
        wait_injection(FE,[obxg,])
        myTime.sleep(10.)
    
    # Store the where_all_before
    wa_before = shell.user_ns["wa"](verbose=False,returns=True)
    #
    cmot_previous_velocity = cmot.velocity * 1
    #Send motor to start position
    move_motor(cmot, p1, mot2, p21)
    #Prepare recording (and acquire first point position... this prevents preparing AND moving)
    print("Preparing acquisition ... ", end=' ')
    ct.prepare(dt=dt, NbFrames = NumberOfPoints, nexusFileGeneration = True, upperDimensions=(NumberOfLines,))
    print("OK")
    handler = ct.openHDFfile(filename)
#Create coordinates soft links and arrays in file
    handler.create_soft_link('/coordinates', 'X1', target='/data/'+cmot.DP.associated_counter.replace(".","/"))
#Create a soft link for a continuously encoded motor or an actaul matrix for a standard motor
    if "associated_counter" in dir(mot2.DP) and mot2.DP.associated_counter!="":
        handler.create_soft_link('/coordinates', 'X2', target='/data/'+mot2.DP.associated_counter.replace(".","/"))
    else:
        mot2_fake = np.array([arange(NumberOfLines,dtype="float32")*dp2 + p21]*NumberOfPoints,dtype="float32")
        outGroup = handler.get_node("/coordinates")
        handler.create_carray(outGroup, "X2", title = "X2",\
        shape =  (NumberOfPoints, NumberOfLines), atom = tables.Atom.from_dtype(mot2_fake.dtype))
        handler.root.coordinates.X2[:] = mot2_fake
        del mot2_fake
    ct.stop()
    #Set scan speed
    cmot.velocity = velocity
    myTime.sleep(0.1)
    timeAtStart = asctime()
    print("Measuring : %s\n"%handler.filename)
    for lineNumber in range(NumberOfLines): 
        mot2.pos(p21 + dp2 * lineNumber)
        print("                                                                       ")
        print(mycurses.UPNLINES%2)
        print("Progress = %2i\%  mot2 at %6.4f" % (float(lineNumber)/NumberOfLines*100.,mot2.pos()))
        print(mycurses.UPNLINES%2)
        if mod(lineNumber,2):
            zigzag = -1
        else:
            zigzag = 1
        try:
            pass
            if shutter:
                sh_fast.open()
        except KeyboardInterrupt:
            stop_cscan(shutter, cmot, cmot_previous_velocity)
            raise
        except:
            pass
        #Start Acquisition
#This part must be reworked soon: a new line concept has to be introduced instead of prepare/start at each line
        ct.prepare(dt=dt, NbFrames = NumberOfPoints, nexusFileGeneration = True, upperDimensions=(NumberOfLines,))
        ct.start(dt)
        #Start  Motor
        if zigzag==1:
            cmot.pos(p2, wait=False)
        else:
            cmot.pos(p1, wait=False)
        myTime.sleep(0.1)
        while(cmot.state() == DevState.MOVING):
            myTime.sleep(0.1)
        try:
            if shutter:
                sh_fast.close()
        except KeyboardInterrupt:
            raise
        except:
            pass
        ct.wait()
        ct.saveData2HDF(upperIndex=(lineNumber,),reverse=zigzag)
    #
    #Save CONTEXT
    #
    ct.savePost2HDF("where_all_before", np.array(wa_before), 
    group = "", wait = True, HDFfilters = tables.Filters(complevel = 1, complib='zlib'), domain="context")
    ct.savePost2HDF("where_all_after", np.array(shell.user_ns["wa"](verbose=False,returns=True)), 
    group = "", wait = True, HDFfilters = tables.Filters(complevel = 1, complib='zlib'), domain="context")
    # MOSTAB and Mono Configs
    ct.savePost2HDF("mostab", np.array(shell.user_ns["mostab"].status().split("\n")), 
    group = "", wait = True, HDFfilters = tables.Filters(complevel = 1, complib='zlib'), domain="context")
    ct.savePost2HDF("dcm", np.array(shell.user_ns["dcm"].status().split("\n")), 
    group = "", wait = True, HDFfilters = tables.Filters(complevel = 1, complib='zlib'), domain="context")
    #
    ct.closeHDFfile()
    timeAtStop = asctime()
    timeout0 = time()
    shell.logger.log_write("Total Elapsed Time = %i s" % (myTime.time() - TotalScanTime), kind='output')
    print("Total Elapsed Time = %i s" % (myTime.time() - TotalScanTime)) 
    #AlarmBeep()
    cmot.velocity = cmot_previous_velocity
    return

def tcscan(total_time=1,integration_time=0.1,n=1,channel=1,shutter=False,beamCheck=True,filename="tcscan_out"):
    """
    Continuous time scan (missing time scale in coordinates!!! to be done)
    total_time: total scan time in seconds
    integration_time : time of one single gate or point
    channel to be drawn at the end of the scan
    shutter: use shutter_fast or not
    beamCheck: wait or not for the presence of x-ray beam (check shutters and machine current)
    filename: the first part of datafile (an hdf file is produced)
    """
    shell=get_ipython()
    no_failures=0
    total_failures=0
    for i in range(n):
        try:
            tcscanActor(total_time,integration_time, channel=channel,shutter=shutter,beamCheck=beamCheck,filename=filename)
            no_failures=0
        except KeyboardInterrupt:
            shell.logger.log_write("tcscan halted on user request: Ctrl-C\n", kind='output')
            print("Halting on user request.")
            sys.stdout.flush()
            stop_tcscan(shutter)
            print("tcscan halted. OK.")
            print("Raising KeyboardInterrupt as requested.")
            sys.stdout.flush()
            raise KeyboardInterrupt
        except Exception as tmp:
            shell.logger.log_write("Error during tcscan:\n %s\n\n" % tmp, kind='output')
            total_failures+=1
            no_failures+=1
            print(tmp)
            stop_tcscan(shutter)
            print("tcscan halted on exception. NOK.")
            if no_failures>3:
                print(tmp)
                break
    if total_failures>0:
        print("Total number of failed scans = %i"%total_failures)
    if no_failures>3:
        raise tmp
    return 

def tcscanActor(total_time=1,integration_time=0.1,n=1,channel=1,shutter=False,beamCheck=True,filename="cscan_out"):
    """
    no news
    """
    shell=get_ipython()
    FE = shell.user_ns["FE"]
    obxg = shell.user_ns["obxg"]
    ct = shell.user_ns["ct"]
    dcm = shell.user_ns["dcm"]
    mostab = shell.user_ns["mostab"]
    TotalScanTime = myTime.time()
    NofScans = n
    #
    if filename == None: 
        raise Exception("filename and limits must be specified")
    
    NumberOfPoints =  int(total_time / integration_time)
    print("Number of points: ",NumberOfPoints)
    
    if beamCheck and not(checkTDL(FE)):
        wait_injection(FE,[obxg,])
        myTime.sleep(10.)
    
    # Store the where_all_before
    wa_before = shell.user_ns["wa"](verbose=False,returns=True)
    #Prepare recording (and acquire first point position... this prevents preparing AND moving)
    print("Preparing acquisition ... ", end=' ')
    ct.prepare(dt=integration_time,NbFrames = NumberOfPoints, nexusFileGeneration = True)
    print("OK")
    handler = ct.openHDFfile(filename)
#Warning: using the handler out of ct and directly has to be avoided, problems arise when scans are aborted and resumed. 
    #Create coordinates links and arrays in file

    
    timeAtStart = asctime()
    #Start acquisition?
       #Print Name:
    print("Measuring : %s\n"%ct.handler.filename)
    try:
        pass
        if shutter:
            sh_fast.open()
    except KeyboardInterrupt:
        ct.stop()
        raise
    except:
        pass
    #Start Acquisition
    ct.start(integration_time)
    ct.wait()
    try:
        if shutter:
            sh_fast.close()
    except:
        print("tcscan: error closing fast shutter")
    ct.saveData2HDF()

#Replace X1 coordinate by theoretical time values
#handler.create_soft_link('/coordinates', 'X1', target='/data/'+cmot.DP.associated_counter.replace(".","/"))
    ct.savePost2HDF("X1", np.linspace(0,total_time,NumberOfPoints),\
    group = "", wait = True, HDFfilters = tables.Filters(complevel = 1, complib='zlib'),
    domain="data")
    #
    #Insert here specific data saving in ct.handler at position root.post? root.spectra?....
    #
    graph_x = np.linspace(0,total_time,NumberOfPoints)
    #
    #Save CONTEXT
    #
#Context can be saved to an approriate dictionary like post.
#This will make scan procedures much more flexible and general
    ct.savePost2HDF("where_all_before", np.array(wa_before), 
    group = "", wait = True, HDFfilters = tables.Filters(complevel = 1, complib='zlib'), domain="context")
    try:
        ct.savePost2HDF("where_all_after", np.array(shell.user_ns["wa"](verbose=False,returns=True)), 
        group = "", wait = True, HDFfilters = tables.Filters(complevel = 1, complib='zlib'), domain="context")
    except:
        print("Cannot save where_all_after.")
    # MOSTAB and Mono Configs
    try:
        ct.savePost2HDF("mostab", np.array(mostab.status().split("\n")), 
        group = "", wait = True, HDFfilters = tables.Filters(complevel = 1, complib='zlib'), domain="context")
    except:
        print("Cannot save mostab status.")
    try:
        ct.savePost2HDF("dcm", np.array(dcm.status().split("\n")), 
        group = "", wait = True, HDFfilters = tables.Filters(complevel = 1, complib='zlib'), domain="context")
    except:
        print("Cannot save dcm status.")
    #
    #
    ct.closeHDFfile()
    print("Saving actions over!")
    timeAtStop = asctime()
    timeout0 = myTime.time()
    #The plotting, once finalised a reasonable code, could be generalised via a generic function and a dictionary listing plot items 
    try:
        f=tables.open_file(ct.final_filename,"r")
        fig1 = pylab.figure(3,figsize=(8,11),edgecolor="white",facecolor="white",)
        fig1.clear()
        ax1=pylab.subplot(4,1,1)
        pylab.ylabel("$\mu$x")
        try:
            pylab.plot(graph_x, f.root.post.MUX.read())
        except:
            pass
        ax2=pylab.subplot(4,1,2,sharex=ax1)
        pylab.ylabel("Fluo")
        try:
            pylab.plot(graph_x, f.root.post.FLUO.read(),label="DTC on")
        except:
            pass
        try:
            pylab.plot(graph_x, f.root.post.FLUO_RAW.read(),label="DTC off")
        except:
            pass
        pylab.legend(frameon=False)    
        ax3=pylab.subplot(4,1,3,sharex=ax1)
        pylab.ylabel("$\mu$x Reference")
        pylab.plot(graph_x, f.root.post.REF.read())
        ax4=pylab.subplot(4,1,4,sharex=ax1)
        pylab.ylabel("$I_0,I_1,I_2$ Counts")
        pylab.xlabel("t (s)")
        pylab.plot(graph_x, f.root.post.I0.read(),"r",label="$I_0$")
        pylab.plot(graph_x, f.root.post.I1.read(),"k",label="$I_1$")
        pylab.plot(graph_x, f.root.post.I2.read(),"g",label="$I_2$")
        pylab.plot(graph_x, f.root.post.I3.read(),"b--",label="$I_3$")
        pylab.legend(frameon=False)    
        pylab.draw()
    except Exception as tmp:
        print("No Plot! Bad Luck!")
        print(tmp)
    finally:
        f.close()
    shell.logger.log_write("Total Elapsed Time = %i s" % (myTime.time() - TotalScanTime), kind='output')
    print("Total Elapsed Time = %i s" % (myTime.time() - TotalScanTime)) 
    #AlarmBeep()
    return
    
def AlarmBeep():
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
                myTime.sleep(0.025)
            myTime.sleep(0.35)
        a.destroy()
    except:
        try:
            a.destroy()
        except:
            pass
    return



