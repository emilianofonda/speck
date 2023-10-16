# -*- coding: utf-8 -*-
from __future__ import print_function
from io import open as file
import dentist
import tables
import os
import numpy
numpy.seterr(all="ignore")
import time as myTime
from time import sleep
from spec_syntax import wait_motor
from GracePlotter import GracePlotter
from spec_syntax import dark as ctDark
from wait_functions import checkTDL, wait_injection
import mycurses
from p_dentist import dentist as p_dentist

print(mycurses.RED+"Using pulse ecscan"+mycurses.RESET)


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
    print("Wait... Stopping Devices...", end=' ')
    sys.stdout.flush()
    ct.stop()
    dcm.stop()
    myTime.sleep(3)
    dcm.velocity(60)
    #while(DevState.RUNNING in [i.state() for i in cardXIA]):
    #    myTime.sleep(2)
    wait_motor(dcm)
    print("Scan Stopped: OK")
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
        print("Halting on user request.")
        sys.stdout.flush()
        stopscan(shutter)
        print("ecscan halted. OK.")
        print("Raising KeyboardInterrupt as requested.")
        sys.stdout.flush()
        raise KeyboardInterrupt
    except Exception as tmp:
        print(tmp)
        shell.logger.log_write("Error during ecscan:\n %s\n\n" % tmp.args[0], kind='output')
        stopscan(shutter)
        #raise
    return 

def ecscan_debug(fileName,e1,e2,n=1,dt=0.04,velocity=10, e0=-1, mode="",shutter=False,beamCheck=False):
    for i in range(n):
	    ecscanActor(fileName=fileName,e1=e1,e2=e2,dt=dt,velocity=velocity, e0=e0, mode=mode,shutter=shutter, beamCheck=beamCheck, n=1)
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
    print("Expected time = %g s" % TotalTime)
    NumberOfPoints = int (float(abs(e2-e1)) / velocity / dt)
    print("Number of points: ",NumberOfPoints)
    print("One point every %4.2feV." % (velocity * dt))
    
    for i in range(5):
        try:
            dcm.mode(1)
        except:
            myTime.sleep(3)
    try:
         for CurrentScan in range(NofScans):
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
            
            if dcm.state() == DevState.MOVING:
                wait_motor(dcm)
                myTime.sleep(1)

            dcm.velocity(60)
            dcm.pos(e1-40.)
            #General bender backlash correction (bender 2 = 5000, bender 1 = 30000) to be generalised via Powerbrick
            mvr(dcm.bender,5000)
            myTime.sleep(0.2)
            mvr(dcm.bender,-5000)
            myTime.sleep(0.2)
            dcm.velocity(velocity)
            myTime.sleep(0.2)
            dcm.pos(e1)
            myTime.sleep(0.2)
            
            timeAtStart = asctime()
            # Store the where_all_before
            wa_before = wa(verbose=False,returns=True)
            #
            #Start acquisition?
            print("Preparing acquisition ... ", end=' ')
            ct.prepare(dt=dt,NbFrames = NumberOfPoints, nexusFileGeneration = True)
#It is dangerous to address the handler out of the ct context
            print("OK")
            handler = ct.openHDFfile(fileName)
            #Print Name:
            print("Measuring : %s\n"%handler.filename)
            try:
                pass
                if shutter:
                    sh_fast.open()
            except KeyboardInterrupt:
                stopscan(shutter)
                raise
            except:
                pass
            print("Starting counters....", end=" ")
            #Start Acqusiition
            ct.start(dt)
            print("OK")
            myTime.sleep(0.1)
            #Start Mono
            dcm.pos(e2, wait=False)
            myTime.sleep(1.0)
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
            #Insert here specific data saving in ct.handler at position root.post
            #
            #The following is specific of the energy scan; everything could be moved directly in formulas but dcm.e2theta is not known at the evaluation
            #
            try:
                post_ene = ct.handler.root.post.energy.read()
                #post_ene = dcm.theta2e(ct.handler.root.post.Theta.read())
                #ct.savePost2HDF("energy", post_ene, group = "", wait = True, HDFfilters = tables.Filters(complevel = 1, complib='zlib'), domain="post")
            except Exception as tmp:
                print("Error reading energy from hdf file post group.")
                #print("Error converting angle to energy.")
                print(tmp)
            #
            #Save CONTEXT
            #
            try:
                ct.savePost2HDF("where_all_before", array(wa_before), 
                group = "", wait = True, HDFfilters = tables.Filters(complevel = 1, complib='zlib'), domain="context")
                ct.savePost2HDF("where_all_after", array(wa(verbose=False,returns=True)), 
                group = "", wait = True, HDFfilters = tables.Filters(complevel = 1, complib='zlib'), domain="context")
            except:
                print("No contextual data for where_all and/or where_after")
            # MOSTAB and Mono Configs
            try:
                ct.savePost2HDF("mostab", array(mostab.status().split("\n")), 
                group = "", wait = True, HDFfilters = tables.Filters(complevel = 1, complib='zlib'), domain="context")
            except:
                print("No contextual data for mostab")
            try:
                ct.savePost2HDF("dcm", array(dcm.status().split("\n")), 
                group = "", wait = True, HDFfilters = tables.Filters(complevel = 1, complib='zlib'), domain="context")
            except:
                print("No contextual data for dcm")

            #
            ct.closeHDFfile()
            timeAtStop = asctime()
            timeout0 = time()
            try:
                HDF2ASCII(ct.final_filename)
            except Exception as tmp:
                print(tmp)
                print("ASCII output failed")
            try:
                dcm.velocity(60)
            except:
                pass
            try:
                #The x axis should be joined together to improve readability
                f=tables.open_file(ct.final_filename,"r")
                fig1 = pylab.figure(1,figsize=(8,11),edgecolor="white",facecolor="white")
                fig1.clear()
                fig1.subplots_adjust(hspace=0)
                ax1 = pylab.subplot(4,1,1)
                ylabel("$\mu$x")
                pylab.plot(post_ene, f.root.post.MUX.read())
                pylab.setp(ax1.get_xticklabels(), visible=False)
                l1,l2 = ax1.get_ylim()
                red = abs(l1-l2)*0.05
                ax1.set_yticks(numpy.linspace(l1+red,l2-red,5))

                ax2 = pylab.subplot(4,1,2, sharex=ax1)
                ylabel("Fluo")
                try:
                    pylab.plot(post_ene, f.root.post.FLUO.read(),label="DTC on")
                    pylab.plot(post_ene, f.root.post.FLUO_RAW.read(),label="DTC off")
                    pylab.setp(ax2.get_xticklabels(), visible=False)
                    l1,l2 = ax2.get_ylim()
                    red = abs(l1-l2)*0.05
                    ax2.set_yticks(numpy.linspace(l1+red,l2-red,5))
                    legend(frameon=False)    
                except:
                    pass
                ax3 = pylab.subplot(4,1,3, sharex=ax1)
                ylabel("$\mu$x Reference")
                pylab.plot(post_ene, f.root.post.REF.read())
                pylab.setp(ax3.get_xticklabels(), visible=False)
                l1,l2 = ax3.get_ylim()
                red = abs(l1-l2)*0.05
                ax3.set_yticks(numpy.linspace(l1+red,l2-red,5))

                ax4 = pylab.subplot(4,1,4, sharex=ax1)
                ylabel("$I_0,I_1,I_2$ Counts")
                xlabel("Energy (eV)")
                pylab.plot(post_ene, f.root.post.I0.read(),"r",label="$I_0$")
                pylab.plot(post_ene, f.root.post.I1.read(),"k",label="$I_1$")
                pylab.plot(post_ene, f.root.post.I2.read(),"g",label="$I_2$")
                l1,l2 = ax4.get_ylim()
                red = abs(l1-l2)*0.05
                ax4.set_yticks(numpy.linspace(l1+red,l2-red,5))
                pylab.setp(ax4.get_xticklabels(),  visible=True)
                ax4.xaxis.set_major_formatter(FormatStrFormatter('%.1f')) 
                legend(frameon=False)                    
                pylab.draw()
            except Exception as tmp:
                print("No Plot! Bad Luck!")
                print(tmp)
            finally:
                try:
                    f.close()
                except:
                    pass
            try:
                if e0>0:
                    p_dentist(ct.final_filename,e0=e0,mode=mode,figN=2)
            except:
                pass
            pylab.pause(0.01)
    except Exception as tmp:
        try:
            ct.closeHDFfile()
            raise
        except:
            pass
        raise tmp
    shell.logger.log_write("Total Elapsed Time = %i s" % (myTime.time() - TotalScanTime), kind='output')
    print("Total Elapsed Time = %i s" % (myTime.time() - TotalScanTime)) 
    return
    


def HDF2ASCII(filename):
    """Filename is the complete path to file.
    The function is hard coded and looks for specific cards in post group.
    Energy, Theta, XMU, FLUO, REF, FLUO_RAW, I0, I1, I2, I3 
    
    Warning: in this version all values are read into RAM before being saved, the whole table!"""

    f=tables.open_file(filename, "r")
    try:
        filename_out = filename[:filename.rfind(".hdf")]+".txt"
        tab_out = []
        tab_out.append(f.root.post.energy[:])
        npoints = len(tab_out[0])
        for i in ["Theta", "MUX", "FLUO", "REF", "FLUO_RAW", "I0", "I1","I2","I3"]:
            try:
                tab_out.append(numpy.nan_to_num(eval("f.root.post."+i)[:]))
            except Exception as tmp:
                print(tmp)
                print("Missing %s in file.root.post, replacing with zero values."%i)
                tab_out.append(numpy.zeros(npoints))
        savetxt(filename_out, array(tab_out).transpose(),header="Energy, Theta, XMU, FLUO, REF, FLUO_RAW, I0, I1, I2, I3")
    finally:
        f.close()
    return
