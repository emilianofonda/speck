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
            ct.closeHDFfile()
            timeAtStop = asctime()
            timeout0 = time()
            dcm.velocity(60)
            try:
                f=tables.open_file(handler.filename,"r")
                fig1 = pylab.figure(1)
                fig1.clear()
                pylab.plot(dcm.theta2e(f.root.encoder_rx1.Theta.read()), pylab.log(f.root.cx2sai1.I0.read()/f.root.cx2sai1.I1.read()))
            except Exception, tmp:
                print "No Plot! Bad Luck!"
                print tmp
            finally:
                f.close()
    except Exception, tmp:
        raise tmp #?

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


#SaveData

#            theta = cardCT.Theta

#            #Begin of new block: test for I0 data, sometimes nan are returned .... why?
#            I0 = array(cardAI.historizedchannel0,"f")
#            if all(I0 <> numpy.nan_to_num(I0)):
#                shell.logger.log_write(mycurses.RED+mycurses.BOLD + ActualFileNameData + ": file is corrupt." + mycurses.RESET, kind='output')
#                print mycurses.RED+mycurses.BOLD + ActualFileNameData +": file is corrupt." + mycurses.RESET
#                CorruptData = True
#            else:
#                CorruptData = False
#            # End of new block
#            
#            I0 = numpy.nan_to_num((I0) - cardAI_dark0)
#            I1 = numpy.nan_to_num(array(cardAI.historizedchannel1,"f") - cardAI_dark1)
#            I2 = numpy.nan_to_num(array(cardAI.historizedchannel2,"f") - cardAI_dark2)
#            I3 = numpy.nan_to_num(array(cardAI.historizedchannel3,"f") - cardAI_dark3)
#            xmu = numpy.nan_to_num(log(I0/I1))
#            fluoXP = numpy.nan_to_num(I3/I0)
#            ene = numpy.nan_to_num(dcm.theta2e(theta))
#            #
#            #if CurrentScan < NofScans-1: 
#            #    print myTime.asctime(), " : sending dcm back to starting point."
#            #    dcm.velocity(60)
#            #    myTime.sleep(0.2)
#            #    dcm.praise Exception("Time Out waiting for XIA cards to stop! Waited more than 180s... !")
#            #    dcm.pos(e1-1., wait=False)
#            #
#            print myTime.asctime(), " : Saving Data..."

#    #Wait for files to be saved in spool
#            XIAt0=time()
#            while(DevState.RUNNING in [i.state() for i in cardXIA]):
#                myTime.sleep(1)
#                if myTime.time() - XIAt0 > 30.:
#                    for i in XIANexusPath:
#                        print i
#                        print os.listdir(i)
#                    print "Time Out waiting for XIA cards to stop! Waited more than 30s... !"
#                    for i in cardXIA:
#                        i.stop()
#                    setSTEP()
#                    raise Exception("Time Out waiting for XIA cards to stop! Waited more than 30s... !")
#                    shell.logger.log_write("Time Out waiting for XIA cards to stop! Waited more than 30s... !", kind='output')
#            while(True in [i[0] not in os.listdir(i[1]) for i in zip(LastXIAFileName, XIANexusPath)]):
#                myTime.sleep(0.25)
#                if 3. > myTime.time() - XIAt0 > 2.:
#                    for i in XIANexusPath:
#                        ll = os.listdir(i)
#                        ll.sort()
#                        print ll
#                        os.system("cd %s&&ls"%i)
#                    print "Time Out waiting for XIA cards files! Waited more than 10s... ! FileSystem Workaround Applied"
#                    shell.logger.log_write("Time Out waiting for XIA files! Waited more than 2s... ! FileSystem Workaround Applied", kind='output')
#                if myTime.time() - XIAt0 > 15.:
#                    for i in XIANexusPath:
#                        ll = os.listdir(i).sort()
#                        print ll
#                    print "Time Out waiting for XIA cards files! Waited more than 3s... !"
#                    shell.logger.log_write("Time Out waiting for XIA files! Waited more than 3s... !", kind='output')
#                    break
#            XIAtEnd = myTime.time()-XIAt0
#            print "XIA needed additional %3.1f seconds to provide all data files."%(XIAtEnd)
#            shell.logger.log_write("XIA needed additional %3.1f seconds to provide all data files."%(XIAtEnd) + ".hdf", kind='output')
#    
#    #Additional time to wait (?)
#            myTime.sleep(0.2)
#    #Measure time spent for saving data
#            DataSavingTime = myTime.time()
#    #Define filter to be used for writing big data into the HDF file
#            HDFfilters = tables.Filters(complevel = 1, complib='zlib')
#    #XIA prepare
#            XIAfilesNames=[]
#            for i in zip(cardXIA,XIANexusPath):
#                XIAfilesNames.append([j for j in os.listdir(i[1]) if j.startswith(i[0].DP.streamTargetFile)])
#            XIAfilesNames = [numpy.sort(i) for i in XIAfilesNames]                  
#            #print XIAfilesNames
#            XIAfiles=[]
#            for path in zip(XIANexusPath,XIAfilesNames):
#                XIAfiles.append([tables.openFile(path[0] +os.sep + x, "r") for x in path[1]])
#        #Common
#            outtaName = filename2ruche(ActualFileNameData)
#            outtaHDF = tables.openFile(outtaName[:outtaName.rfind(".")] + ".hdf","w")
#            outtaHDF.createGroup("/","XIA")
#    #Superpose all XIA matrices and make one to avoid exploding the TeraByte/week limits and keep on a USB stick (actually, this changes with compression)
#            outtaHDF.createCArray(outtaHDF.root.XIA, "mcaSum", title="McaSum", shape=cardXiaDataShape[0], atom = tables.UInt32Atom(), filters=HDFfilters)
#            mcaSum = numpy.zeros(cardXiaDataShape[0],numpy.uint32)
#            #outtaHDF.createArray("/XIA", "mcaSum", numpy.zeros(cardXIA1dataShape, numpy.uint32))
#    
#    #XIA1 read / write
#    
#    #Declare a RAM buffer for a single MCA
#            bCmca = numpy.zeros(cardXiaDataShape[0],numpy.uint32)
#            Breaked=False
#            for xiaN in range(len(cardXIA)):
#                outChannels = iter(cardXIAChannels[xiaN])                    
#                for ch in range(len(cardXIA[xiaN].channels)):
#                    if Breaked:
#                        break
#                    outCh = outChannels.next()
#    #Single Channel MCA CArray creation
#                    outtaHDF.createCArray(outtaHDF.root.XIA, "mca%02i"%outCh, title="mca%02i"%outCh,\
#                    shape=cardXiaDataShape[0], atom = tables.UInt32Atom(), filters=HDFfilters)
#    #Get pointer to a Channel MCA on disk
#                    pCmca = outtaHDF.getNode("/XIA/mca%02i"%outCh)
#    #Fluo Channel ROI values                
#                    outtaHDF.createArray("/XIA", "fluo%02i"%outCh, numpy.zeros(NumberOfPoints, numpy.uint32))
#    #ICR line comment out if required
#                    outtaHDF.createArray("/XIA", "inputCountRate%02i"%outCh, numpy.zeros(NumberOfPoints, numpy.float32))
#    #OCR line comment out if required
#                    outtaHDF.createArray("/XIA", "outputCountRate%02i"%outCh, numpy.zeros(NumberOfPoints, numpy.float32))
#    #DT line comment out if required
#                    outtaHDF.createArray("/XIA", "deadtime%02i"%outCh, numpy.zeros(NumberOfPoints, numpy.float32))
#                    block = 0
#                    blockLen = cardXIA[xiaN].DP.streamNbAcqPerFile
#                    pointerCh = eval("outtaHDF.root.XIA.fluo%02i"%outCh)
#    #ICR line comment out if required
#                    pointerIcr = eval("outtaHDF.root.XIA.inputCountRate%02i"%outCh)
#    #OCR line comment out if required
#                    pointerOcr = eval("outtaHDF.root.XIA.outputCountRate%02i"%outCh)
#    #DT line comment out if required
#                    pointerDt = eval("outtaHDF.root.XIA.deadtime%02i"%outCh)
#                    for XFile in XIAfiles[xiaN]:
#                        try:
#                            __block = eval("XFile.root.entry.scan_data.channel%02i"%ch).read()
#    #ICR line comment out if required
#                            __blockIcr = eval("XFile.root.entry.scan_data.icr%02i"%ch).read()
#    #OCR line comment out if required
#                            __blockOcr = eval("XFile.root.entry.scan_data.ocr%02i"%ch).read()
#    #DT line comment out if required
#                            __blockDT = eval("XFile.root.entry.scan_data.deadtime%02i"%ch).read()
#                        except:
#                            Breaked = True
#                            break
#                        actualBlockLen = shape(__block)[0]
#    #Feed RAM buffers with MCA values
#                        bCmca[block * blockLen: (block * blockLen) + actualBlockLen,:] = __block
#                        mcaSum[block * blockLen: (block * blockLen) + actualBlockLen,:] += __block
#                        #pointerCh[block * blockLen: (block + 1) * blockLen] = sum(__block[:,roiStart:roiEnd], axis=1)
#                        pointerCh[block * blockLen: (block * blockLen) + actualBlockLen] = sum(__block[:,roiStart:roiEnd], axis=1)
#    #ICR line comment out if required
#                        pointerIcr[block * blockLen: (block * blockLen) + actualBlockLen] = __blockIcr
#    #OCR line comment out if required
#                        pointerOcr[block * blockLen: (block * blockLen) + actualBlockLen] = __blockOcr
#    #DT line comment out if required
#                        pointerDt[block * blockLen: (block * blockLen) + actualBlockLen] = __blockDT
#                        block += 1
#    #Write Single MCA to Disk
#                    pCmca[:] = bCmca
#                print "XIA%i: OK"%xiaN

#    #Finalize derived quantities
#            fluoX = numpy.nan_to_num(array( sum(mcaSum[:,roiStart:roiEnd], axis=1), "f") / I0)
#            outtaHDF.root.XIA.mcaSum[:] = mcaSum
#            del mcaSum
#            xmuS = numpy.nan_to_num(log(I1/I2))
#            outtaHDF.createGroup("/","Spectra")
#            outtaHDF.createArray("/Spectra", "xmuTransmission", xmu)
#            outtaHDF.createArray("/Spectra", "xmuStandard", xmuS)
#            outtaHDF.createArray("/Spectra", "xmuFluo", fluoX)
#            outtaHDF.createArray("/Spectra", "xmuFluoXP", fluoXP)
#            outtaHDF.createGroup("/","Raw")
#            outtaHDF.createArray("/Raw", "Energy", ene)
#            outtaHDF.createArray("/Raw", "I0", I0)
#            outtaHDF.createArray("/Raw", "I1", I1)
#            outtaHDF.createArray("/Raw", "I2", I2)
#            outtaHDF.createArray("/Raw", "I3", I3)
#    #Stop feeding the monster. Close HDF
#            outtaHDF.close()
#            print "HDF closed."
#            shell.logger.log_write("Saving data in: %s\n" % (outtaName[:outtaName.rfind(".")] + ".hdf"), kind='output')
#    #Now that data are saved try to plot it for the last time
#            try:
#                update_graphs(CP, dcm, cardAI, cardCT, cardXIA, roiStart, roiEnd,\
#                XIANexusPath, XIAfilesList, fluoXIA, cardXIAChannels)
#                print "Graph Final Update OK"
#                pass
#            except KeyboardInterrupt:
#                raise
#            except Exception, tmp:
#                print tmp
#    #Clean up the mess in the spool 
#    #XIA close and wipe
#            for i in XIAfiles:
#                for j in i:
#                    for ret in xrange(3):
#                        try:
#                            j.close()
#                            break
#                        except:
#                            sleep(1)
#                            pass
#            for i in zip(cardXIA,XIANexusPath):
#                for j in os.listdir(i[1]):
#                    if j.startswith(i[0].DP.streamTargetFile):
#                        pass
#                        os.remove(i[1] + os.sep + j)

#    #Local data saving
#            dataBlock = array([ene,theta,xmu,fluoX,xmuS,\
#            I0,I1,I2,I3],"f")
#            numpy.savetxt(ActualFileNameData, transpose(dataBlock))
#            FInfo = file(ActualFileNameInfo,"w")
#            FInfo.write("#.txt file columns content is:\n")
#            FInfo.write("#1) Energy\n")
#            FInfo.write("#2) Angle\n")
#            FInfo.write("#3) Transmission\n")
#            FInfo.write("#4) Fluorescence\n")
#            FInfo.write("#5) Standard\n")
#            FInfo.write("#6) I0\n")
#            FInfo.write("#7) I1\n")
#            FInfo.write("#8) I2\n")
#            FInfo.write("#9) I3\n")
#            FInfo.write("#TimeAtStart = %s\n" % (timeAtStart))
#            FInfo.write("#TimeAtStop  = %s\n" % (timeAtStop))
#            FInfo.write("#Scan from %g to %g at velocity= %g eV/s\n" % (e1, e2, velocity))
#            FInfo.write("#Counter Card Config\n")
#            for i in cardCTsavedAttributes:
#                FInfo.write("#%s = %g\n" % (i,cardCT.read_attribute(i).value))
#            FInfo.write("#Analog  Card Config\n")
#            #Report in file Info dark currents applied
#            FInfo.write("#Dark_I0= %9.8f\nDark_I1= %9.8f\nDark_I2= %9.8f\nDark_I3= %9.8f\n"\
#            %(cardAI_dark0,cardAI_dark1,cardAI_dark2,cardAI_dark3,))
#            #
#            for i in cardAIsavedAttributes:
#                FInfo.write("#%s = %g\n" % (i, cardAI.read_attribute(i).value))
#    
#            #XIA cards
#            for xia in cardXIA:
#                FInfo.write("#DxMap Card Config: %s\n"%xia.label)
#                FInfo.write("#Config File: %s\n" %(xia.DP.currentConfigFile))
#                FInfo.write("#Mode : %s\n" %(xia.DP.currentMode))
#                FInfo.write("#ROI(s) : \n")
#                for i in xia.DP.getrois():
#                    FInfo.write("#%s\n" % i)
#            #MOSTAB Config follows:
#            try:
#                FInfo.write("#MOSTAB Status:\n")
#                for __mostabStatusBit in tuple(["#%s\n"%i for i in mostab.status().split("\n")]):
#                    FInfo.write("#%s" % __mostabStatusBit)
#            except:
#                print mostab.status()
#                print "Error reporting MOSTAB status."
#            
#            #Where All Info follow
#            for i in wa(returns=True, verbose=False):
#                FInfo.write("#" + i + "\n")
#            FInfo.close()
#    
#            os.system("cp " + ActualFileNameData +" " +filename2ruche(ActualFileNameData))
#            os.system("cp " + ActualFileNameInfo +" " +filename2ruche(ActualFileNameInfo))            
#            print myTime.asctime(), " : Data saved to backup."
#            shell.logger.log_write("Data saved in %s at %s\n" % (ActualFileNameData, myTime.asctime()), kind='output')

