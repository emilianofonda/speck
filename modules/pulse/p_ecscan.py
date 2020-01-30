# -*- coding: utf-8 -*-
import dentist
import thread
import tables
import os
import numpy
import time as myTime
from time import sleep
from spec_syntax import wait_motor
from GracePlotter import GracePlotter
from spec_syntax import dark as ctDark
from wait_functions import checkTDL, wait_injection
import mycurses

try:
    import Tkinter
    NoTk=False
except:
    print "Warning from escan: Tkinter not installed."
    NoTk=True

print mycurses.RED+"Using FTP version of ecscan"+mycurses.RESET


# WARNING This script version uses the global object ct from speck to import XIA cards.
# Ths whois function maybe used too to name the xia cards by their speck names.
# This version has been written for the replacement of the Canberra 36 pixels with the 
# Vortex ME4 detctor, but it is intended to be a scalable version for any number of xia cards/devices
# The object mostab is called too with the name "mostab".

#cardCT = DeviceProxy("d09-1-c00/ca/cpt.3")
#cardAI = DeviceProxy("d09-1-c00/ca/sai.1")
#cardXIA = ct.xia_units
#cardAI = sai0.DP
#cardCT = cpt.DP

def stopscan(shutter=False):
    try:
        if shutter:
            sh_fast.close()
    except:
        pass
    print "Wait... Stopping Devices...",
    sys.stdout.flush()
    ct.stop()
    dcm.stop()
    myTime.sleep(3)
    dcm.velocity(60)
    #while(DevState.RUNNING in [i.state() for i in cardXIA]):
    #    myTime.sleep(2)
    wait_motor(dcm)
    print "Scan Stopped: OK"
    sys.stdout.flush()
    return

class CPlotter:
    def h_init__(self):
        return


__CPlotter__ = CPlotter()

def ecscan(fileName,e1,e2,n=1,dt=0.04,velocity=10, e0=-1, mode="",shutter=False,beamCheck=True):
    try:
        for i in range(n):
	        ecscanActor(fileName=fileName,e1=e1,e2=e2,dt=dt,velocity=velocity, e0=e0, mode=mode,shutter=shutter, beamCheck=beamCheck, n=1)
    except KeyboardInterrupt:
        shell.logger.log_write("ecscan halted on user request: Ctrl-C\n", kind='output')
        print "Halting on user request."
        sys.stdout.flush()
        stopscan(shutter)
        print "ecscan halted. OK."
        print "Raising KeyboardInterrupt as requested."
        sys.stdout.flush()
        raise KeyboardInterrupt
    except Exception, tmp:
        shell.logger.log_write("Error during ecscan:\n %s\n\n" % tmp, kind='output')
        print tmp
        stopscan(shutter)
        #raise
    return 


def ecscanActor(fileName,e1,e2,n=1,dt=0.04,velocity=10, e0=-1, mode="",shutter=False,beamCheck=True):
    """Start from e1 (eV) to e2 (eV) and count over dt (s) per point.
    velocity: Allowed velocity doesn't exceed 40eV/s.
    The backup folder MUST be defined for the code to run.
    Global variables: FE and obxg must exist and should point to Front End and Shutter
    """
    shell=get_ipython()
    FE = shell.user_ns["FE"]
    obxg = shell.user_ns["obxg"]
    cpt = shell.user_ns["ct"]
    mostab = shell.user_ns["mostab"]
    TotalScanTime = myTime.time()
    NofScans = n
    #
    if fileName == None: 
        raise Exception("filename and limits must be specified")
    if velocity <= 0.:
        raise Exception("Monochromator velocity too low!")
    if velocity > 100.:
        raise Exception("Monochromator velocity exceeded!")
    
    #Configure cards
    TotalTime = float(abs(e2-e1)) / velocity
    print "Expected time = %g s" % TotalTime
    NumberOfPoints = int (float(abs(e2-e1)) / velocity / dt)
    print "Number of points: ",NumberOfPoints
    print "One point every %4.2feV." % (velocity * dt)
    
    for i in range(5):
        try:
            dcm.mode(1)
        except:
            myTime.sleep(3)
    try:
         for CurrentScan in xrange(NofScans):
            #Calculate name of last data buffer file to wait (XIA)
            if beamCheck and not(checkTDL(FE)):
                wait_injection(FE,[obxg,])
                myTime.sleep(10.)
            #ActualFileNameData = findNextFileName(fileName,"txt")
            #shell.logger.log_write("Saving data in: %s\n" % ActualFileNameData, kind='output')
            #ActualFileNameInfo = ActualFileNameData[:ActualFileNameData.rfind(".")] + ".info"
            #f=file(ActualFileNameData,"w")
            #f.close()
            #Configure and move mono
            
            # Store the where_all_before
            wa_before = wa(verbose=False,returns=True)
            #
            if dcm.state() == DevState.MOVING:
                wait_motor(dcm)
                myTime.sleep(1)

            dcm.velocity(60)
            dcm.pos(e1-50.)
            myTime.sleep(0.2)
            dcm.velocity(velocity)
            myTime.sleep(0.2)
            dcm.pos(e1)
            myTime.sleep(0.2)
            
            timeAtStart = asctime()
            #Start acquisition?
            print "Preparing acquisition ... ",
            ct.prepare(dt=dt,NbFrames = NumberOfPoints, nexusFileGeneration = True)
            print "OK"
            handler = ct.openHDFfile(fileName)
            #Print Name:
            print "Measuring : %s\n"%handler.filename
            try:
                pass
                if shutter:
                    sh_fast.open()
            except KeyboardInterrupt:
                stopscan(shutter)
                raise
            except:
                pass
            #Start Acqusiition
            ct.start(dt)
            myTime.sleep(0.5)
            #Start Mono
            dcm.pos(e2, wait=False)
            myTime.sleep(2)
            while(dcm.state() == DevState.MOVING):
                myTime.sleep(1)
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
            #The following is specific of the energy scan while the xmu not, it is defined in the postDictionary
            post_ene = dcm.theta2e(ct.handler.root.data.encoder_rx1.Theta.read())
            ct.savePost2HDF("energy", post_ene, group = "", wait = True, HDFfilters = tables.Filters(complevel = 1, complib='zlib'), domain="post")
            #
            #Save CONTEXT
            #
            ct.savePost2HDF("where_all_before", array(wa_before), 
            group = "", wait = True, HDFfilters = tables.Filters(complevel = 1, complib='zlib'), domain="context")
            ct.savePost2HDF("where_all_after", array(wa(verbose=False,returns=True)), 
            group = "", wait = True, HDFfilters = tables.Filters(complevel = 1, complib='zlib'), domain="context")
            # MOSTAB and Mono Configs
            ct.savePost2HDF("mostab", array(mostab.status().split("\n")), 
            group = "", wait = True, HDFfilters = tables.Filters(complevel = 1, complib='zlib'), domain="context")
            ct.savePost2HDF("dcm", array(dcm.status().split("\n")), 
            group = "", wait = True, HDFfilters = tables.Filters(complevel = 1, complib='zlib'), domain="context")
            #
            ct.closeHDFfile()
            timeAtStop = asctime()
            timeout0 = time()
            dcm.velocity(60)
            try:
                f=tables.open_file(handler.filename,"r")
                fig1 = pylab.figure(1)
                fig1.clear()
                pylab.subplot(3,1,1)
                pylab.plot(post_ene, log(f.root.data.cx2sai1.I0.read()/f.root.data.cx2sai1.I1.read()))
                try:
                    pylab.subplot(3,1,2)
                    pylab.plot(post_ene, f.root.post.FLUO.read())
                except:
                    pass
                pylab.subplot(3,1,3)
                pylab.plot(post_ene, f.root.data.cx2sai1.I0.read(),"r")
                pylab.plot(post_ene, f.root.data.cx2sai1.I1.read(),"k")
                pylab.draw()
            except Exception, tmp:
                print "No Plot! Bad Luck!"
                print tmp
            finally:
                f.close()
    except Exception, tmp:
        try:
            ct.closeHDFfile()
        except:
            pass
        raise tmp
    shell.logger.log_write("Total Elapsed Time = %i s" % (myTime.time() - TotalScanTime), kind='output')
    print "Total Elapsed Time = %i s" % (myTime.time() - TotalScanTime) 
    AlarmBeep()
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
        print "WARNING: Error alerting for end of scan... no Tkinter?\n"
        print "BUT: Ignore this message if escan is working well,\n just report this to your local contact\n"
    return



