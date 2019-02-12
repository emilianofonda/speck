# -*- coding: utf-8 -*-
import dentist
import thread
import tables
import os
import string
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
    print "Warning from ecscan: Tkinter not installed."
    NoTk=True

print mycurses.RED+"Using FTP version of ecscan"+mycurses.RESET


# WARNING This script version uses the global object ct from speck to import XIA cards.
# Ths whois function maybe used too to name the xia cards by their speck names.
# This version has been written for the replacement of the Canberra 36 pixels with the 
# Vortex ME4 detctor, but it is intended to be a scalable version for any number of xia cards/devices
# The object mostab is called too with the name "mostab".

cardCT = DeviceProxy("d09-1-c00/ca/cpt.3")
cardAI = DeviceProxy("d09-1-c00/ca/sai.1")

cardXIA = ct.mca_units

#cardXIA1 = DeviceProxy("d09-1-cx1/dt/dtc-mca_xmap.1")
#cardXIA2 = DeviceProxy("d09-1-cx1/dt/dtc-mca_xmap.2")
#cardXIA1Channels = range(1,20) #remember the range stops at N-1: 19
#cardXIA2Channels = range(0,16) #remember the range stops at N-1: 15

def stopscan(shutter=False):
    try:
        if shutter:
            sh_fast.close()
    except:
        pass
    print "Wait... Stopping Devices...",
    sys.stdout.flush()
    cardAI.stop()
    cardCT.stop()
    for xia in cardXIA:
        xia.stop()
    #cardXIA1.stop()
    #cardXIA2.stop()
    dcm.stop()
    myTime.sleep(3)
    dcm.velocity(60)
    while(DevState.RUNNING in [i.state() for i in cardXIA]):
        myTime.sleep(2)
    setMAP()
    wait_motor(dcm)
    print "Scan Stopped: OK"
    sys.stdout.flush()
    return

class CPlotter:
    def h_init__(self):
        return


__CPlotter__ = CPlotter()

def ecscan(fileName,e1,e2,n=1,dt=0.04,velocity=10, e0=-1, mode="",shutter=False,beamCheck=True,backlash=100):
    try:
        for i in range(n):
	  ecscanActor(fileName,e1,e2,1,dt,velocity, e0, mode,shutter, beamCheck,backlash=backlash)
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


def ecscanActor(fileName,e1,e2,n=1,dt=0.04,velocity=10, e0=-1, mode="",shutter=False,beamCheck=True,backlash=100):
    """Start from e1 (eV) to e2 (eV) and count over dt (s) per point.
    velocity: Allowed velocity doesn't exceed 40eV/s.
    The backup folder MUST be defined for the code to run.
    Global variables: FE and obxg must exist and should point to Front End and Shutter
    The filename: the only acceptable characters are [a-Z][0-9] + - . _ @ failing to do so will cause an exception
    """
    #CheckFilename first
    fileName = fileName.replace(" ","_")
    if string.whitespace in fileName:
        raise Exception("ecscan does not accept tabulations and other special spacings in filenames. Aborting.",fileName)
    for ch in fileName:
        if ch not in string.letters+string.digits+"_./\\+-@":
            raise Exception("ecscan does not accept special characters in filenames. Aborting.",fileName)
    #
    shell=get_ipython()
    FE = shell.user_ns["FE"]
    obxg = shell.user_ns["obxg"]
    TotalScanTime = myTime.time()
    NofScans = n
    cardCTsavedAttributes = ["totalNbPoint","integrationTime","continuous","bufferDepth"]
    cardAIsavedAttributes = ["configurationId","frequency","integrationTime","dataBufferNumber"]
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
    
    #Card CT
    cardCT.totalNbPoint = NumberOfPoints
    cardCT.nexusNbAcqPerFile = NumberOfPoints
    cardCT.integrationTime = dt
    cardCT.bufferDepth = int(1./dt)
    cardCT.continuous = False
    cardCT.nexusFileGeneration = False
    cardCT.set_timeout_millis(30000)

    #Card AI
    if cardAI.configurationId <> 3:
        cardAI.configurationId = 3
        myTime.sleep(5)
    cardAI.integrationTime = dt * 1000 -2.
    cardAI.nexusFileGeneration = False
    cardAI.nexusNbAcqPerFile = NumberOfPoints
    cardAI.dataBufferNumber = NumberOfPoints
    cardAI.statHistoryBufferDepth = NumberOfPoints
    cardAI.set_timeout_millis(30000)
    cardAI_dark0,cardAI_dark1,cardAI_dark2,cardAI_dark3 =\
    map(float, cardAI.get_property(["SPECK_DARK"])["SPECK_DARK"])

    #Set Mapping mode if needed
    try:
        setMAP()
        myTime.sleep(1)
    except:
        try:
            myTime.sleep(1)
            setMAP()
            myTime.sleep(1)
        except:
            print "The setMAP function does not work!!! Try again and/or check with local contact!!!"
    #Cards XIA
    #Rois are defined only on the first channel of the first card
    try:
        roiStart, roiEnd = cardXIA[0].getROIs()
    except:
        print "Please wait... I cannot find ROI limits, checking configuration...",
        setSTEP()
        myTime.sleep(1)
        setMAP()
        try:
            roiStart, roiEnd = cardXIA[0].getROIs()
            print " done. OK."
        except Exception, tmp:
            print "\nRegion Of Interest has not been defined? uAnatase_newPellet_phi20_macrose setroi(start,end) command please."
            raise tmp
    print "ROI limits are [%4i:%4i]" % (roiStart, roiEnd)
    cardXiaDataShape = []
    XIANexusPath = []
    cardXIAChannels = []
    __Nch = 0
    for xia in cardXIA:
        print "Setting XIA card:",xia.label
        cardXIAChannels.append(range(__Nch,__Nch + len(xia.channels)))
        #Line below should work for non overlapping output channels
        __Nch += len(xia.channels)
        xia.DP.nbpixels = NumberOfPoints
        xia.DP.streamNbAcqPerFile = 250
        xia.DP.set_timeout_millis(30000)
        cardXiaDataShape.append([ NumberOfPoints,xia.DP.streamNbDataPerAcq ])
        if xia.FTPclient:
            XIANexusPath.append(xia.spoolMountPoint)
            #Clean Up the mess (if any) in the source disk
            try:
                xia.FTPclient.DeleteRemainingFiles()
            except:
                print "Failed to delete remaining files from %s" % xia.FTPclient.name
            if xia.FTPclient.state() <> DevState.STANDBY:
                if xia.FTPclient.state() == DevState.RUNNING:
                    xia.FTPclient.stop()
                    sleep(1)
                else:
                    xia.FTPclient.init()
                    sleep(1)
            for retryFTPdelete in xrange(5):
                try:
                    xia.FTPclient.DeleteRemainingFiles()
                    break
                except:
                    xia.FTPclient.init()
                    sleep(1)
            xia.FTPclient.start()
        else:
            XIANexusPath.append("/nfs" + xia.DP.streamTargetPath.replace("\\","/")[1:])
        #print XIANexusPath
        #Reset Nexus index and cleanup spool
        xia.DP.streamresetindex()
        map(lambda x: x.startswith(xia.DP.streamTargetFile) and os.remove(XIANexusPath[-1] +os.sep + x), os.listdir(XIANexusPath[-1]))
    NumberOfXIAFiles = int(cardXIA[0].DP.nbpixels / cardXIA[0].DP.streamNbAcqPerFile) 
    if numpy.mod(cardXIA[0].DP.nbpixels, cardXIA[0].DP.streamNbAcqPerFile):
        NumberOfXIAFiles += 1

    #DCM Setup
    if dcm.state() == DevState.DISABLE:
        dcm.DP.on()
        sleep(1)
    for i in range(5):
        try:
            dcm.mode(1)
            #break
        except:
            myTime.sleep(3)
    #Start graphic windows    
    try:
        CP = __CPlotter__
        CP.GraceWin = GracePlotter()
        for CurrentScan in xrange(NofScans):
            #Calculate name of last data buffer file to wait (XIA)
            LastXIAFileName = ["%s_%06i.nxs" % (xia.DP.streamTargetFile, NumberOfXIAFiles * (CurrentScan+1)) for xia in cardXIA]
            if beamCheck and not(checkTDL(FE)):
                wait_injection(FE,[obxg,])
                myTime.sleep(10.)
            ActualFileNameData = findNextFileName(fileName,"txt")
            shell.logger.log_write("Saving data in: %s\n" % ActualFileNameData, kind='output')
            ActualFileNameInfo = ActualFileNameData[:ActualFileNameData.rfind(".")] + ".info"
            f=file(ActualFileNameData,"w")
            f.close()
            #Configure and move mono
            if dcm.state() == DevState.MOVING:
                wait_motor(dcm)
            myTime.sleep(1)
            dcm.velocity(60)
            if dcm.pos() > e1 - backlash:
                dcm.pos(e1-backlash, wait=False)
            
            #Print Name:
            print "Measuring : %s\n"%ActualFileNameData

            #Start Measurement
            CP.GraceWin.wins[0].command('ARRANGE(4,1,0.1,0.1,0.25)\nREDRAW\n')
            CP.GraceWin.wins[0].command('with g0\nxaxis ticklabel char size 0.7\n')
            CP.GraceWin.wins[0].command('with g0\nyaxis ticklabel char size 0.7\n')
            CP.GraceWin.wins[0].command('with g0\nyaxis label char size 0.7\nyaxis label "XMU"')
            CP.GraceWin.wins[0].command('with g1\nxaxis ticklabel char size 0.7\n')
            CP.GraceWin.wins[0].command('with g1\nyaxis ticklabel char size 0.7\n')
            CP.GraceWin.wins[0].command('with g1\nyaxis label char size 0.7\nyaxis label "I0, I1"')
            CP.GraceWin.wins[0].command('with g2\nxaxis ticklabel char size 0.7\n')
            CP.GraceWin.wins[0].command('with g2\nyaxis ticklabel char size 0.7\n')
            CP.GraceWin.wins[0].command('with g2\nyaxis label char size 0.7\nyaxis label "FLUO"')
            CP.GraceWin.wins[0].command('with g3\nxaxis ticklabel char size 0.7\n')
            CP.GraceWin.wins[0].command('with g3\nyaxis ticklabel char size 0.7\n')
            CP.GraceWin.wins[0].command('with g3\nyaxis label char size 0.7\nyaxis label "STD"')
            while(dcm.state() == DevState.MOVING):
                sleep(0.5)
            while(dcm.state() == DevState.MOVING):
                sleep(0.5)
            timeAtStart = asctime()
            cardAI.start()
            for xia in cardXIA:
                #xia.DP.snap()
                xia.start()
            myTime.sleep(1)
            dcm.mode(1)
            sleep(0.2)
            dcm.velocity(velocity)
            myTime.sleep(0.5)
            dcm.pos(e1)
            sleep(0.2)
            try:
                pass
                if shutter:
                    sh_fast.open()
            except KeyboardInterrupt:
                stopscan(shutter)
                raise
            except:
                pass
            dcm.pos(e2, wait=False)
            cardCT.start()
            myTime.sleep(2)
            XIAfilesList=[[],]*len(cardXIA)
            fluoXIA=[[],]*len(cardXIA)
            actualRunningStart = myTime.time()
            #while((myTime.time() - actualRunningStart) < (TotalTime -30.) and dcm.state() == DevState.MOVING):
            while(dcm.state() == DevState.MOVING):
                try:
                    if DevState.FAULT in [xia.state() for xia in cardXIA]:
                        shell.logger.log_write(mycurses.RED+mycurses.BOLD + "XIA Card FAULT." + mycurses.RESET, kind='output')
                        print mycurses.RED+mycurses.BOLD +"XIA Card FAULT" + mycurses.RESET
                        break
                    update_graphs(CP, dcm, cardAI, cardCT, cardXIA,\
                    roiStart, roiEnd, XIANexusPath, XIAfilesList, fluoXIA, cardXIAChannels)
                    pass
                except KeyboardInterrupt:
                    raise
                except Exception, tmp:
                    print tmp
                #myTime.sleep(10)
                myTime.sleep(5)
            try:
                if shutter:
                    sh_fast.close()
            except KeyboardInterrupt:
                raise
            except:
                pass
            if DevState.FAULT in [xia.state() for xia in cardXIA]:
                cardCT.stop()
                cardAI.stop()
                setSTEP()
                sleep(1)
                setMAP()
                sleep(1)
            else:
                while(DevState.RUNNING in [cardCT.state(),]):
                    myTime.sleep(0.1)
                timeAtStop = asctime()
                timeout0 = time()
                while(DevState.RUNNING in [cardAI.state(),] and time()-timeout0 < 3):
                    myTime.sleep(0.1)
                if time()-timeout0 > 3:
                    print "cardAI of ecscan failed to stop!"
                cardAI.stop()
                theta = cardCT.Theta

                #Begin of new block: test for I0 data, sometimes nan are returned .... why?
                I0 = array(cardAI.historizedchannel0,"f")
                if all(I0 <> numpy.nan_to_num(I0)):
                    shell.logger.log_write(mycurses.RED+mycurses.BOLD + ActualFileNameData + ": file is corrupt." + mycurses.RESET, kind='output')
                    print mycurses.RED+mycurses.BOLD + ActualFileNameData +": file is corrupt." + mycurses.RESET
                    CorruptData = True
                else:
                    CorruptData = False
                # End of new block
                
                I0 = numpy.nan_to_num((I0) - cardAI_dark0)
                I1 = numpy.nan_to_num(array(cardAI.historizedchannel1,"f") - cardAI_dark1)
                I2 = numpy.nan_to_num(array(cardAI.historizedchannel2,"f") - cardAI_dark2)
                I3 = numpy.nan_to_num(array(cardAI.historizedchannel3,"f") - cardAI_dark3)
                xmu = numpy.nan_to_num(log(I0/I1))
                fluoXP = numpy.nan_to_num(I3/I0)
                ene = numpy.nan_to_num(dcm.theta2e(theta))
                #
                if CurrentScan < NofScans-1: 
                    print myTime.asctime(), " : sending dcm back to starting point."
                    dcm.velocity(60)
                    myTime.sleep(0.2)
                    dcm.pos(e1-backlash, wait=False)
                #
                print myTime.asctime(), " : Saving Data..."

    #Wait for XIA files to be saved in spool
                XIAt0=time()
                while(DevState.RUNNING in [i.state() for i in cardXIA]):
                    myTime.sleep(0.1)
                    if myTime.time() - XIAt0 > 30.:
                        for i in XIANexusPath:
                            os.system("cd %s&&ls"%i)
                        print "Time Out waiting for XIA cards to stop! Waited more than 30s... !"
                        for i in cardXIA:
                            i.stop()
                        setSTEP()
                        raise Exception("Time Out waiting for XIA cards to stop! Waited more than 30s... !")
                        shell.logger.log_write("Time Out waiting for XIA cards to stop! Waited more than 30s... !", kind='output')
                #XIAt0=time()
                while(True in [i[0] not in os.listdir(i[1]) for i in zip(LastXIAFileName, XIANexusPath)]):
                    myTime.sleep(0.25)
                    if 3. > myTime.time() - XIAt0 > 1.:
                        for i in XIANexusPath:
                            os.system("cd %s&&ls"%i)
                    elif 15. > myTime.time() - XIAt0 > 3.:
                        for i in XIANexusPath:
                            os.system("cd %s&&ls"%i)
                        print "Time Out waiting for XIA cards files! Waited more than 3s... ! FileSystem Workaround Applied"
                        shell.logger.log_write("Time Out waiting for XIA files! Waited more than 3s... ! FileSystem Workaround Applied", kind='output')
                    elif myTime.time() - XIAt0 > 15.:
                        #for i in XIANexusPath:
                            #ll = os.listdir(i).sort()
                            #print ll
                        print "Time Out waiting for XIA cards files! Waited more than 15s... !"
                        shell.logger.log_write("Time Out waiting for XIA files! Waited more than 15s... !", kind='output')
                        break
                XIAtEnd = myTime.time()-XIAt0
                print "XIA needed additional %3.1f seconds to provide data files."%(XIAtEnd)
                shell.logger.log_write("XIA needed additional %3.1f seconds to provide data files."%(XIAtEnd) + ".hdf", kind='output')
    
    #Additional time to wait (?)
                myTime.sleep(0.2)
    #Measure time spent for saving data
                DataSavingTime = myTime.time()
    #Define filter to be used for writing big data into the HDF file
                HDFfilters = tables.Filters(complevel = 1, complib='zlib')
    #XIA prepare
                XIAfilesNames=[]
                for i in zip(cardXIA,XIANexusPath):
                    XIAfilesNames.append([j for j in os.listdir(i[1]) if j.startswith(i[0].DP.streamTargetFile)])
                XIAfilesNames = [numpy.sort(i) for i in XIAfilesNames]                  
                #print XIAfilesNames
                XIAfiles=[]
                for path in zip(XIANexusPath,XIAfilesNames):
                    XIAfiles.append([tables.openFile(path[0] +os.sep + x, "r") for x in path[1]])
        #Common
                outtaName = filename2ruche(ActualFileNameData)
                outtaHDF = tables.openFile(outtaName[:outtaName.rfind(".")] + ".hdf","w")
                outtaHDF.createGroup("/","XIA")
    #Superpose all XIA matrices and make one to avoid exploding the TeraByte/week limits and keep on a USB stick (actually, this changes with compression)
                outtaHDF.createCArray(outtaHDF.root.XIA, "mcaSum", title="McaSum", shape=cardXiaDataShape[0], atom = tables.UInt32Atom(), filters=HDFfilters)
                mcaSum = numpy.zeros(cardXiaDataShape[0],numpy.uint32)
                #outtaHDF.createArray("/XIA", "mcaSum", numpy.zeros(cardXIA1dataShape, numpy.uint32))
    
    #XIA1 read / write
    
    #Declare a RAM buffer for a single MCA
                bCmca = numpy.zeros(cardXiaDataShape[0],numpy.uint32)
                Breaked=False
                for xiaN in range(len(cardXIA)):
                    outChannels = iter(cardXIAChannels[xiaN])                    
                    for ch in range(len(cardXIA[xiaN].channels)):
                        if Breaked:
                            break
                        outCh = outChannels.next()
                        #print "outCh = ",outCh
    #Single Channel MCA CArray creation
                        outtaHDF.createCArray(outtaHDF.root.XIA, "mca%02i"%outCh, title="mca%02i"%outCh,\
                        shape=cardXiaDataShape[0], atom = tables.UInt32Atom(), filters=HDFfilters)
    #Get pointer to a Channel MCA on disk
                        pCmca = outtaHDF.getNode("/XIA/mca%02i"%outCh)
    #Fluo Channel ROI values                
                        outtaHDF.createArray("/XIA", "fluo%02i"%outCh, numpy.zeros(NumberOfPoints, numpy.uint32))
    #ICR line comment out if required
                        outtaHDF.createArray("/XIA", "inputCountRate%02i"%outCh, numpy.zeros(NumberOfPoints, numpy.float32))
    #OCR line comment out if required
                        outtaHDF.createArray("/XIA", "outputCountRate%02i"%outCh, numpy.zeros(NumberOfPoints, numpy.float32))
    #DT line comment out if required
                        outtaHDF.createArray("/XIA", "deadtime%02i"%outCh, numpy.zeros(NumberOfPoints, numpy.float32))
                        block = 0
                        blockLen = cardXIA[xiaN].DP.streamNbAcqPerFile
                        pointerCh = eval("outtaHDF.root.XIA.fluo%02i"%outCh)
    #ICR line comment out if required
                        pointerIcr = eval("outtaHDF.root.XIA.inputCountRate%02i"%outCh)
    #OCR line comment out if required
                        pointerOcr = eval("outtaHDF.root.XIA.outputCountRate%02i"%outCh)
    #DT line comment out if required
                        pointerDt = eval("outtaHDF.root.XIA.deadtime%02i"%outCh)
                        for XFile in XIAfiles[xiaN]:
                            try:
                                __block = eval("XFile.root.entry.scan_data.channel%02i"%ch).read()
    #ICR line comment out if required
                                __blockIcr = eval("XFile.root.entry.scan_data.icr%02i"%ch).read()
    #OCR line comment out if required
                                __blockOcr = eval("XFile.root.entry.scan_data.ocr%02i"%ch).read()
    #DT line comment out if required
                                __blockDT = eval("XFile.root.entry.scan_data.deadtime%02i"%ch).read()
                            except:
                                print "Cannot read ch = %i in XIA card #%i (first card is card 0)"%(ch,xiaN)
                                Breaked = True
                                break
                            actualBlockLen = shape(__block)[0]
    #Feed RAM buffers with MCA values
                            bCmca[block * blockLen: (block * blockLen) + actualBlockLen,:] = __block
                            mcaSum[block * blockLen: (block * blockLen) + actualBlockLen,:] += __block
                            #pointerCh[block * blockLen: (block + 1) * blockLen] = sum(__block[:,roiStart:roiEnd], axis=1)
                            pointerCh[block * blockLen: (block * blockLen) + actualBlockLen] = sum(__block[:,roiStart:roiEnd], axis=1)
    #ICR line comment out if required
                            pointerIcr[block * blockLen: (block * blockLen) + actualBlockLen] = __blockIcr
    #OCR line comment out if required
                            pointerOcr[block * blockLen: (block * blockLen) + actualBlockLen] = __blockOcr
    #DT line comment out if required
                            pointerDt[block * blockLen: (block * blockLen) + actualBlockLen] = __blockDT
                            block += 1
    #Write Single MCA to Disk
                        pCmca[:] = bCmca
                    print "XIA%i: OK"%(xiaN+1)

    #Finalize derived quantities
                fluoXraw = numpy.nan_to_num(array( sum(mcaSum[:,roiStart:roiEnd], axis=1), "f") / I0)
                fluoX = numpy.nan_to_num(sum(\
                [eval("outtaHDF.root.XIA.fluo%02i[:]"%nch)/(1.-eval("outtaHDF.root.XIA.deadtime%02i[:]"%nch)*0.01)\
                for nch in range(cardXIAChannels[-1][-1])]\
                ,axis=0)/I0)
                #
                outtaHDF.root.XIA.mcaSum[:] = mcaSum
                del mcaSum
                xmuS = numpy.nan_to_num(log(I1/I2))
                outtaHDF.createGroup("/","Spectra")
                outtaHDF.createArray("/Spectra", "xmuTransmission", xmu)
                outtaHDF.createArray("/Spectra", "xmuStandard", xmuS)
                outtaHDF.createArray("/Spectra", "xmuFluo", fluoX)
                outtaHDF.createArray("/Spectra", "xmuFluoRaw", fluoXraw)
                outtaHDF.createArray("/Spectra", "xmuFluoXP", fluoXP)
                outtaHDF.createGroup("/","Raw")
                outtaHDF.createArray("/Raw", "Energy", ene)
                outtaHDF.createArray("/Raw", "I0", I0)
                outtaHDF.createArray("/Raw", "I1", I1)
                outtaHDF.createArray("/Raw", "I2", I2)
                outtaHDF.createArray("/Raw", "I3", I3)
    #Stop feeding the monster. Close HDF
                outtaHDF.close()
                print "HDF closed."
                shell.logger.log_write("Saving data in: %s\n" % (outtaName[:outtaName.rfind(".")] + ".hdf"), kind='output')
    #Now that data are saved try to plot it for the last time
                try:
                    update_graphs(CP, dcm, cardAI, cardCT, cardXIA, roiStart, roiEnd,\
                    XIANexusPath, XIAfilesList, fluoXIA, cardXIAChannels)
                    print "Graph Final Update OK"
                    pass
                except KeyboardInterrupt:
                    raise
                except Exception, tmp:
                    print tmp
    #Clean up the mess in the spool 
    #XIA close and wipe
                for i in XIAfiles:
                    for j in i:
                        for ret in xrange(3):
                            try:
                                j.close()
                                break
                            except:
                                sleep(1)
                                pass
                for i in zip(cardXIA,XIANexusPath):
                    for j in os.listdir(i[1]):
                        if j.startswith(i[0].DP.streamTargetFile):
                            pass
                            os.remove(i[1] + os.sep + j)

    #Local data saving
                dataBlock = array([ene,theta,xmu,fluoX,xmuS,fluoXraw,\
                I0,I1,I2,I3],"f")
                numpy.savetxt(ActualFileNameData, transpose(dataBlock))
                FInfo = file(ActualFileNameInfo,"w")
                FInfo.write("#.txt file columns content is:\n")
                FInfo.write("# 1) Energy\n")
                FInfo.write("# 2) Angle\n")
                FInfo.write("# 3) Transmission\n")
                FInfo.write("# 4) Fluorescence\n")
                FInfo.write("# 5) Standard\n")
                FInfo.write("# 6) RawFluorescence\n")
                FInfo.write("# 7) I0\n")
                FInfo.write("# 8) I1\n")
                FInfo.write("# 9) I2\n")
                FInfo.write("#10) I3\n")
                FInfo.write("#TimeAtStart = %s\n" % (timeAtStart))
                FInfo.write("#TimeAtStop  = %s\n" % (timeAtStop))
                FInfo.write("#Scan from %g to %g at velocity= %g eV/s\n" % (e1, e2, velocity))
                FInfo.write("#Counter Card Config\n")
                for i in cardCTsavedAttributes:
                    FInfo.write("#%s = %g\n" % (i,cardCT.read_attribute(i).value))
                FInfo.write("#Analog  Card Config\n")
                #Report in file Info dark currents applied
                FInfo.write("#Dark_I0= %9.8f\nDark_I1= %9.8f\nDark_I2= %9.8f\nDark_I3= %9.8f\n"\
                %(cardAI_dark0,cardAI_dark1,cardAI_dark2,cardAI_dark3,))
                #
                for i in cardAIsavedAttributes:
                    FInfo.write("#%s = %g\n" % (i, cardAI.read_attribute(i).value))
    
                #XIA cards
                for xia in cardXIA:
                    FInfo.write("#DxMap Card Config: %s\n"%xia.label)
                    FInfo.write("#Config File: %s\n" %(xia.DP.currentConfigFile))
                    FInfo.write("#Mode : %s\n" %(xia.DP.currentMode))
                    FInfo.write("#ROI(s) : \n")
                    for i in xia.DP.getrois():
                        FInfo.write("#%s\n" % i)

                #DCM Config follows:
                try:
                    FInfo.write("#Monochromator Status:\n")
                    for __dcmStatusBit in tuple(["#%s\n"%i for i in dcm.status().split("\n")]):
                        FInfo.write("#%s" % __dcmStatusBit)
                except:
                    print dcm.status()
                    print "Error reporting monochromator status."

                #MOSTAB Config follows:
                try:
                    FInfo.write("#MOSTAB Status:\n")
                    for __mostabStatusBit in tuple(["#%s\n"%i for i in mostab.status().split("\n")]):
                        FInfo.write("#%s" % __mostabStatusBit)
                except:
                    print mostab.status()
                    print "Error reporting MOSTAB status."
                
                #Where All Info follow
                for i in wa(returns=True, verbose=False):
                    FInfo.write("#" + i + "\n")
                FInfo.close()
    
                os.system("cp " + ActualFileNameData +" " +filename2ruche(ActualFileNameData))
                os.system("cp " + ActualFileNameInfo +" " +filename2ruche(ActualFileNameInfo))            
                print myTime.asctime(), " : Data saved to backup."
                shell.logger.log_write("Data saved in %s at %s\n" % (ActualFileNameData, myTime.asctime()), kind='output')
    #Measure time spent for saving data
                print "Time spent for data saving, backup and refresh plots: %3.2fs" % (myTime.time()-DataSavingTime)
                try:
                    if e1 < e0 <e2:
                        #thread.start_new_thread(dentist.dentist, (ActualFileNameData,), {"e0":e0,})
                        if mode.startswith("f"):
                            dentist.dentist(ActualFileNameData, e0 =e0, mode="f")
                        else:
                            dentist.dentist(ActualFileNameData, e0 =e0, mode=mode)
                except KeyboardInterrupt:
                    raise
                except Exception, tmp:
                    print tmp
                #dcm.velocity(60)
                #if CurrentScan < NofScans-1: 
                #    print myTime.asctime(), " : sending dcm back to starting point."
                #    myTime.sleep(0.2)
                #    dcm.pos(e1-1.)
    except Exception, tmp:
        #print "Acquisition Halted on Exception: wait for dcm to stop."
        #stopscan(shutter)
        #print "Halt"
        #shell.logger.log_write("Error during ecscan:\n %s\n\n" % tmp, kind='output')
        try:
            outtaHDF.close()
        except:
            raise tmp
        try:
            for __i in XIAfiles:
                for __j in __i:
                    try:
                        __j.close()
                        myTime.sleep(0.25)
                    except:
                        pass
        except:
            pass
        print tmp
    finally:
        try:
            outtaHDF.close()
        except:
            pass
        try:
            for __i in XIAfiles:
                for __j in __i:
                    try:
                        __j.close()
                        myTime.sleep(0.25)
                    except:
                        pass
        except:
            pass
        if dcm.state() <> DevState.MOVING:
            dcm.velocity(60)
    #Finally stop FTPclients
    for xia in cardXIA:
        xia.FTPclient.stop()
    
    
    #Write END of the Story
    shell.logger.log_write("Total Elapsed Time = %i s" % (myTime.time() - TotalScanTime), kind='output')
    print "Total Elapsed Time = %i s" % (myTime.time() - TotalScanTime) 
    
    AlarmBeep()
    return
    
def update_graphs(CP, dcm, cardAI, cardCT, cardXIA, roiStart, roiEnd,\
XIANexusPath, XIAfilesList, fluoXIA, cardXIAChannels):
    
    cardAI_dark0,cardAI_dark1,cardAI_dark2,cardAI_dark3 =\
    map(float, cardAI.get_property(["SPECK_DARK"])["SPECK_DARK"])
 
    LastPoint = cardAI.dataCounter
    I0 = cardAI.historizedchannel0[:LastPoint] - cardAI_dark0
    I1 = cardAI.historizedchannel1[:LastPoint] - cardAI_dark1
    I2 = cardAI.historizedchannel2[:LastPoint] - cardAI_dark2
    xmu = numpy.nan_to_num(log(1.0*I0/I1))
    std = numpy.nan_to_num(log(1.0*I1/I2))
    ene = dcm.theta2e(cardCT.Theta)
    ll = min(len(ene), len(xmu))
    CP.GraceWin.GPlot(ene[:ll],xmu[:ll], gw=0, graph=0, curve=0, legend="",color=1, noredraw=True)
    CP.GraceWin.GPlot(ene[:ll], I0[:ll], gw=0, graph=1, curve=0, legend="", color=2, noredraw=True)
    CP.GraceWin.wins[0].command('with g0\nautoscale\nredraw\n')
    CP.GraceWin.GPlot(ene[:ll], I1[:ll], gw=0, graph=1, curve=1, legend="", color=3, noredraw=True)
    CP.GraceWin.wins[0].command('with g1\nautoscale\nredraw\n')
    CP.GraceWin.GPlot(ene[:ll], std[:ll], gw=0, graph=3, curve=1, legend="", color=1, noredraw=True)
    CP.GraceWin.wins[0].command('with g3\nautoscale\nredraw\n')
    tmp = []
    for xia in zip(cardXIA, XIANexusPath):
        __tmp = os.listdir(xia[1])
        __tmp.sort()
        #print __tmp
        for i in list(__tmp):
            #if not str(i).startswith(xia[0].DP.streamTargetFile) or str(i).startswith("."):
            if not str(i).startswith(xia[0].DP.streamTargetFile):
                __tmp.remove(i)
        tmp.append(__tmp)
    if len(tmp[0]) > len(XIAfilesList[0]):
        for xiaN in range(len(cardXIA)):
            for name in tmp[xiaN][len(XIAfilesList[xiaN]):]:
                XIAfilesList[xiaN].append(name)
                try:
                    f = tables.openFile(XIANexusPath[xiaN] + os.sep + name, "r")
                    #fluoSeg=zeros([shape(eval("f.root.entry.scan_data.channel%02i"%cardXIAChannels[xiaN][0]))[0],cardXIA[xiaN].DP.streamNbDataPerAcq],numpy.float32)
                    #for ch in range(len(cardXIAChannels[xiaN])):
                    #    fluoSeg += eval("f.root.entry.scan_data.channel%02i"%ch).read()
                    fluoSeg=zeros(len(eval("f.root.entry.scan_data.channel%02i"%cardXIAChannels[xiaN][0])),numpy.float32)
                    for ch in range(len(cardXIAChannels[xiaN])):
                        fluoSeg += sum(eval("f.root.entry.scan_data.channel%02i[:,roiStart:roiEnd]"%ch),axis=1)\
                        /(1.-eval("f.root.entry.scan_data.deadtime%02i"%ch).read()*0.01)
                finally:
                    try:
                        f.close()
                    except:
                        pass
                #fluoSeg = sum(fluoSeg[:,roiStart:roiEnd],axis=1) 
                fluoXIA[xiaN] += list(fluoSeg)
        ll = min([len(i) for i in fluoXIA])
        if len(I0) >= ll and ll > 2:
            fluoTrace = sum(array([i[:ll] for i in fluoXIA],"f"),axis=0)
            CP.GraceWin.GPlot(ene[:ll],numpy.nan_to_num(fluoTrace/I0[:ll]),\
            gw=0, graph=2, curve=0, legend="", color=1, noredraw=False)
            CP.GraceWin.wins[0]('with g2\nautoscale\nredraw\n')
    return


def dark(dt=10.):
    #Configure cards
    NumberOfPoints = 1000
    #Card CT
    cardCT.totalNbPoint = NumberOfPoints
    cardCT.nexusNbAcqPerFile = NumberOfPoints
    cardCT.integrationTime = dt / float(NumberOfPoints)
    cardCT.bufferDepth = int(float(NumberOfPoints)/dt)
    cardCT.continuous = False
    cardCT.nexusFileGeneration = False
    cardCT.set_timeout_millis(30000)

    #Card AI
    if cardAI.configurationId <> 3:
        cardAI.configurationId = 3
        myTime.sleep(5)
    cardAI.integrationTime = dt -1.
    cardAI.nexusFileGeneration = False
    cardAI.nexusNbAcqPerFile = NumberOfPoints
    cardAI.dataBufferNumber = NumberOfPoints
    cardAI.statHistoryBufferDepth = NumberOfPoints
    cardAI.set_timeout_millis(30000)

    shell=get_ipython()
    shclose=shell.user_ns["shclose"]
    shopen=shell.user_ns["shopen"]
    shstate=shell.user_ns["shstate"]
    ct=shell.user_ns["ct"]
    if dt == 0:
        ct.clearDark()
    else:
        previous = shstate()
        shclose(1)
        myTime.sleep(1)
        ct.count(dt)
        ct.writeDark()
        cardAI.start()
        myTime.sleep(1)
        cardCT.start()
        while(cardCT.state() == DevState.RUNNING):
            myTime.sleep(0.1)
        cardAI.stop()
        darkAI0 = numpy.average(cardAI.historizedchannel0)
        darkAI1 = numpy.average(cardAI.historizedchannel1)
        darkAI2 = numpy.average(cardAI.historizedchannel2)
        darkAI3 = numpy.average(cardAI.historizedchannel3)
        cardAI.put_property({"SPECK_DARK":[darkAI0,darkAI1,darkAI2,darkAI3]})
        print "Dark values:"
        print "I_0(AnalogInput) = %6.5fV" % darkAI0
        print "I_1(AnalogInput) = %6.5fV" % darkAI1
        print "I_2(AnalogInput) = %6.5fV" % darkAI2
        shopen(previous)
    print ct.readDark()
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



