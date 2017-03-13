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


cardCT = DeviceProxy("d09-1-c00/ca/cpt.3_old")
cardAI = DeviceProxy("d09-1-c00/ca/sai.1")
cardXIA1 = DeviceProxy("d091-1-cx2/dt/dtc-mca_xmap.1")
cardXIA1Channels = [0,] #remember the range stops at N-1: 19

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
    cardXIA1.stop()
    dcm.stop()
    myTime.sleep(3)
    #cardXIA1.init()
    #myTime.sleep(2)
    while(cardXIA1.state() == DevState.RUNNING):
        myTime.sleep(2)
    setMAP()
    wait_motor(dcm)
    print "OK"
    sys.stdout.flush()
    return

class CPlotter:
    def h_init__(self):
        return


__CPlotter__ = CPlotter()

def ecscan(fileName,e1,e2,n=1,dt=0.04,velocity=10, e0=-1, mode="f",shutter=False,beamCheck=True):
    try:
        ecscanActor(fileName,e1,e2,n,dt,velocity, e0, mode,shutter, beamCheck)
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
        stopscan(shutter)
        raise tmp
    return 

def ecscanActor(fileName,e1,e2,n=1,dt=0.04,velocity=10, e0=-1, mode="f",shutter=False,beamCheck=True):
    """Start from e1 (eV) to e2 (eV) and count over dt (s) per point.
    velocity: Allowed velocity doesn't exceed 40eV/s.
    The backup folder MUST be defined for the code to run.
    Global variables: FE and obxg must exist and should point to Front End and Shutter
    """
    shell=get_ipython()
    FE = shell.user_ns["FE"]
    obxg = shell.user_ns["obxg"]
    obx = shell.user_ns["obx"]
    TotalScanTime = myTime.time()
    NofScans = n
    cardCTsavedAttributes = ["totalNbPoint","integrationTime","continuousAcquisition","bufferDepth"]
    cardAIsavedAttributes = ["configurationId","frequency","integrationTime","dataBufferNumber"]
    if fileName == None: 
        raise Exception("filename and limits must be specified")
    if velocity <= 0.1:
        raise Exception("Monochromator velocity too low!")
    if velocity > 60.:
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
    cardCT.bufferDepth = 1
    cardCT.continuousAcquisition = False
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
    #Card XIA1
    try:
        roiStart, roiEnd = map(int, cardXIA1.getrois()[1].split(";")[1:])
    except:
        print "Please wait... I cannot find ROI limits, checking configuration...",
        setSTEP()
        myTime.sleep(1)
        setMAP()
        try:
            roiStart, roiEnd = map(int, cardXIA1.getrois()[1].split(";")[1:])
            print " done. OK."
        except Exception, tmp:
            print "\nRegion Of Interest has not been defined? use setroi(start,end) command please."
            raise tmp
    print "ROI limits are [%4i:%4i]" % (roiStart, roiEnd)
    cardXIA1.nbpixels = NumberOfPoints
    cardXIA1.streamNbAcqPerFile = 250
    cardXIA1.set_timeout_millis(30000)
    cardXIA1dataShape = (NumberOfPoints,cardXIA1.streamNbDataPerAcq )    
    XIA1NexusPath = "/nfs" + cardXIA1.streamTargetPath.replace("\\","/")[1:]
    #Reset Nexus index and cleanup spool
    cardXIA1.streamresetindex()
    map(lambda x: x.startswith(cardXIA1.streamTargetFile) and os.remove(XIA1NexusPath +os.sep + x), os.listdir(XIA1NexusPath))
    NumberOfXIAFiles = int(cardXIA1.nbpixels / cardXIA1.streamNbAcqPerFile) 
    if numpy.mod(cardXIA1.nbpixels, cardXIA1.streamNbAcqPerFile):
        NumberOfXIAFiles += 1
    
    #DCM Setup
    if dcm.state() == DevState.DISABLE:
        dcm.DP.on()
    for i in range(5):
        try:
            dcm.mode(1)
            break
        except:
            myTime.sleep(1)
    #Start graphic windows    
    try:
        CP = __CPlotter__
        CP.GraceWin = GracePlotter()
        for CurrentScan in xrange(NofScans):
            #Calculate name of last data buffer file to wait (XIA)
            LastXIA1FileName = "%s_%06i.nxs" % (cardXIA1.streamTargetFile, NumberOfXIAFiles * (CurrentScan+1))
            if beamCheck and not(checkTDL(FE)):
                wait_injection(FE,[obxg,obx])
                myTime.sleep(10.)
            ActualFileNameData = findNextFileName(fileName,"txt")
            shell.logger.log_write("Saving data in: %s\n" % ActualFileNameData, kind='output')
            ActualFileNameInfo = ActualFileNameData[:ActualFileNameData.rfind(".")] + ".info"
            f=file(ActualFileNameData,"w")
            f.close()
            #Configure and move mono
            if dcm.state() == DevState.MOVING:
                wait_motor(dcm)
            myTime.sleep(0.2)
            #dcm.DP.velocity = 60
            #myTime.sleep(0.2)
            dcm.mode(0)
            myTime.sleep(0.2)
            dcm.pos(e1-1., wait=False)
            
            #Print Name:
            print "Measuring : %s\n"%ActualFileNameData
            #Start Measurement
            CP.GraceWin.wins[0].command('ARRANGE(3,1,0.1,0.1,0.25)\nREDRAW\n')
            CP.GraceWin.wins[0].command('with g0\nxaxis ticklabel char size 0.7\n')
            CP.GraceWin.wins[0].command('with g0\nyaxis ticklabel char size 0.7\n')
            CP.GraceWin.wins[0].command('with g0\nyaxis label char size 0.7\nyaxis label "TEY"')
            CP.GraceWin.wins[0].command('with g1\nxaxis ticklabel char size 0.7\n')
            CP.GraceWin.wins[0].command('with g1\nyaxis ticklabel char size 0.7\n')
            CP.GraceWin.wins[0].command('with g1\nyaxis label char size 0.7\nyaxis label "I0, I1"')
            CP.GraceWin.wins[0].command('with g2\nxaxis ticklabel char size 0.7\n')
            CP.GraceWin.wins[0].command('with g2\nyaxis ticklabel char size 0.7\n')
            CP.GraceWin.wins[0].command('with g2\nyaxis label char size 0.7\nyaxis label "FLUO"')
            while(dcm.state() == DevState.MOVING):
                sleep(0.5)
            while(dcm.state() == DevState.MOVING):
                sleep(0.5)
            timeAtStart = asctime()
            cardAI.start()
            cardXIA1.snap()
            myTime.sleep(1)
            dcm.mode(1)
            sleep(0.2)
            dcm.DP.velocity = velocity
            myTime.sleep(0.5)
            dcm.pos(e1)
            sleep(1)
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
            XIA1filesList=[]
            fluoXIA1=[]
            while(dcm.state() == DevState.MOVING):
                try: 
                    update_graphs(CP, dcm, cardAI, cardCT, cardXIA1,\
                    roiStart, roiEnd, XIA1NexusPath, XIA1filesList,\
                    fluoXIA1)
                except KeyboardInterrupt:
                    raise
                except Exception, tmp:
                    print tmp
                    pass
                myTime.sleep(4)
            try:
                if shutter:
                    sh_fast.close()
            except KeyboardInterrupt:
                raise
            except:
                pass
            timeout0 = time()
            while(DevState.RUNNING in [cardCT.state(), cardAI.state(),] and time()-timeout0 < 6.):
                myTime.sleep(0.2)
            if time()-timeout0 > 6:
                if cardCT.state() == DevState.RUNNING:
                    shell.logger.log_write("cardCT of ecscan failed to stop!", kind='output')
                    print "cardCT of ecscan failed to stop!"
                    cardCT.stop()
                if cardAI.state() == DevState.RUNNING:
                    shell.logger.log_write("cardAI of ecscan failed to stop!", kind='output')
                    print "cardAI of ecscan failed to stop!"
                    cardAI.stop()
            timeAtStop = asctime()
            timeout0 = time()
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
            xmu = numpy.nan_to_num(I1/I0)
            ene = numpy.nan_to_num(dcm.theta2e(theta))
            #
            if NofScans >= 1: 
                print myTime.asctime(), " : sending dcm back to starting point."
                #dcm.DP.velocity = 60
                try:
                    dcm.state()
                except:
                    myTime.sleep(1)
                dcm.mode(0)
                myTime.sleep(1)
                dcm.pos(e1-1., wait=False)
            #
            print myTime.asctime(), " : Saving Data..."

#Wait for XIA files to be saved in spool
            XIAt0=myTime.time()
            ttt = myTime.asctime()
            sOut = "XIA waiting for last file since: %s" % ttt
            print sOut
            shell.logger.log_write(sOut, kind='output')
            while(cardXIA1.state() == DevState.RUNNING or (LastXIA1FileName not in os.listdir(XIA1NexusPath))):
                myTime.sleep(0.2)
                if time() - XIAt0 > 1200:
                    raise Exception("Time Out waiting for XIA cards to stop! Waited more than 20minutes... !")
            XIAtEnd = myTime.time()-XIAt0
            print "XIA needed additional %3.1f seconds to provide all data files."%(XIAtEnd)
            shell.logger.log_write("XIA needed additional %3.1f seconds to provide all data files."%(XIAtEnd) + ".hdf", kind='output')

#Additional time to wait (?)
            myTime.sleep(0.2)
#Measure time spent for saving data
            DataSavingTime = myTime.time()
#Define filter to be used for writing big data into the HDF file
            HDFfilters = tables.Filters(complevel = 1, complib='zlib')
#XIA1 prepare
            XIA1filesNames = os.listdir(XIA1NexusPath)
            XIA1filesNames.sort()
            for i in tuple(XIA1filesNames):
                if not i.startswith(cardXIA1.streamTargetFile):
                    XIA1filesNames.remove(i)
            #print XIA1filesNames
            XIA1files = map(lambda x: tables.openFile(XIA1NexusPath +os.sep + x, "r"), XIA1filesNames)

#Common
            outtaName = filename2ruche(ActualFileNameData)
            outtaHDF = tables.openFile(outtaName[:outtaName.rfind(".")] + ".hdf","w")
            outtaHDF.createGroup("/","XIA")
#Superpose all XIA matrices and make one
            outtaHDF.createCArray(outtaHDF.root.XIA, "mcaSum", title="McaSum", shape=cardXIA1dataShape, atom = tables.UInt32Atom(), filters=HDFfilters)
            mcaSum = numpy.zeros(cardXIA1dataShape,numpy.uint32)

#XIA1 read / write

#Declare a RAM buffer for a single MCA
            bCmca = numpy.zeros(cardXIA1dataShape,numpy.uint32)
            Breaked=False
            for ch in cardXIA1Channels:
                if Breaked:
                    break
#Single Channel MCA CArray creation
                outtaHDF.createCArray(outtaHDF.root.XIA, "mca%02i"%ch, title="Mca%02i"%ch,\
                shape=cardXIA1dataShape, atom = tables.UInt32Atom(), filters=HDFfilters)
#Get pointer to a Channel MCA on disk
                pCmca = outtaHDF.getNode("/XIA/mca%02i"%ch)
#Fluo Channel ROI values                
                outtaHDF.createArray("/XIA", "fluo%02i"%ch, numpy.zeros(NumberOfPoints, numpy.uint32))
#DT line comment out if required
                outtaHDF.createArray("/XIA", "deadtime%02i"%ch, numpy.zeros(NumberOfPoints, numpy.float32))
                block = 0
                blockLen = cardXIA1.streamNbAcqPerFile
                pointerCh = eval("outtaHDF.root.XIA.fluo%02i"%ch)
#DT line comment out if required
                pointerDt = eval("outtaHDF.root.XIA.deadtime%02i"%ch)
                for XFile in XIA1files:
                    try:
                        __block = eval("XFile.root.entry.scan_data.channel%02i"%ch).read()
#DT line comment out if required
                        __blockDT = eval("XFile.root.entry.scan_data.deadtime%02i"%ch).read()
                    except:
                        print "Error reading XIA card. Break now!"
                        Breaked = True
                        break
                    actualBlockLen = shape(__block)[0]
#Feed RAM buffers with MCA values
                    bCmca[block * blockLen: (block * blockLen) + actualBlockLen,:] = __block
                    mcaSum[block * blockLen: (block * blockLen) + actualBlockLen,:] += __block
                    pointerCh[block * blockLen: (block + 1) * blockLen] = sum(__block[:,roiStart:roiEnd], axis=1)
#DT line comment out if required
                    pointerDt[block * blockLen: (block + 1) * blockLen] = __blockDT
                    block += 1
#Write Single MCA to Disk
                pCmca[:] = bCmca
            print "XIA1: OK"
#Finalize derived quantities
            fluoX = numpy.nan_to_num(array( sum(mcaSum[:,roiStart:roiEnd], axis=1), "f") / I0)
            outtaHDF.root.XIA.mcaSum[:] = mcaSum
            del mcaSum
            outtaHDF.createGroup("/","Spectra")
            outtaHDF.createArray("/Spectra", "xmuTEY", xmu)
            outtaHDF.createArray("/Spectra", "xmuFluo", fluoX)
            outtaHDF.createGroup("/","Raw")
            outtaHDF.createArray("/Raw", "Energy", ene)
            outtaHDF.createArray("/Raw", "I0", I0)
            outtaHDF.createArray("/Raw", "I1", I1)
#Stop feeding the monster. Close HDF
            outtaHDF.close()
            print "HDF closed."
            shell.logger.log_write("Saving data in: %s\n" % (outtaName[:outtaName.rfind(".")] + ".hdf"), kind='output')
#Now that data are saved try to plot it for the last time
            try:
                #thread.start_new_thread(update_graphs, (CP, dcm, cardAI, cardCT, cardXIA1, \
                #roiStart, roiEnd, XIA1NexusPath,  XIA1filesList, \
                #fluoXIA1))
                update_graphs(CP, dcm, cardAI, cardCT, cardXIA1, roiStart, roiEnd,\
                XIA1NexusPath, XIA1filesList, fluoXIA1 )
                print "Graph Final Update OK"
            except KeyboardInterrupt:
                raise
            except:
                pass
#Clean up the mess in the spool
#XIA1 close and wipe
            map(lambda x: x.close(), XIA1files)
            map(lambda x: x.startswith(cardXIA1.streamTargetFile)\
            and os.remove(XIA1NexusPath +os.sep + x), os.listdir(XIA1NexusPath))
#Local data saving
            dataBlock = array([ene,theta,xmu,fluoX,\
            I0,I1],"f")
            numpy.savetxt(ActualFileNameData, transpose(dataBlock))
            FInfo = file(ActualFileNameInfo,"w")
            FInfo.write("#.txt file columns content is:\n")
            FInfo.write("#1) Energy\n")
            FInfo.write("#2) Angle\n")
            FInfo.write("#3) TEY\n")
            FInfo.write("#4) Fluorescence\n")
            FInfo.write("#5) I0\n")
            FInfo.write("#6) I1\n")
            FInfo.write("#TimeAtStart = %s\n" % (timeAtStart))
            FInfo.write("#TimeAtStop  = %s\n" % (timeAtStop))
            FInfo.write("#Scan from %g to %g at velocity= %g eV/s\n" % (e1, e2, velocity))
            FInfo.write("#Counter Card Config\n")
            for i in cardCTsavedAttributes:
                FInfo.write("#%s = %g\n" % (i,cardCT.read_attribute(i).value))
            FInfo.write("#Analog  Card Config\n")
            #Report in file Info dark currents applied
            FInfo.write("Dark_I0= %9.8f\nDark_I1= %9.8f\nDark_I2= %9.8f\nDark_I3= %9.8f\n"\
            %(cardAI_dark0,cardAI_dark1,cardAI_dark2,cardAI_dark3,))
            #
            for i in cardAIsavedAttributes:
                FInfo.write("#%s = %g\n" % (i, cardAI.read_attribute(i).value))
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
                        dentist.dentist(ActualFileNameData, e0 =e0, mode="")
            except KeyboardInterrupt:
                raise
            except Exception, tmp:
                print tmp
    except Exception, tmp:
        #print "Acquisition Halted on Exception: wait for dcm to stop."
        #stopscan(shutter)
        #print "Halt"
        #shell.logger.log_write("Error during ecscan:\n %s\n\n" % tmp, kind='output')
        try:
            outtaHDF.close()
        except:
            pass
        raise tmp
    shell.logger.log_write("Total Elapsed Time = %i s" % (myTime.time() - TotalScanTime), kind='output')
    print "Total Elapsed Time = %i s" % (myTime.time() - TotalScanTime) 
    AlarmBeep()
    return

def update_graphs(CP, dcm, cardAI, cardCT, cardXIA1, roiStart, roiEnd,\
XIA1NexusPath, XIA1filesList, fluoXIA1):
    
    cardAI_dark0,cardAI_dark1,cardAI_dark2,cardAI_dark3 =\
    map(float, cardAI.get_property(["SPECK_DARK"])["SPECK_DARK"])
 
    LastPoint = cardAI.dataCounter
    I0 = cardAI.historizedchannel0[:LastPoint] - cardAI_dark0
    I1 = cardAI.historizedchannel1[:LastPoint] - cardAI_dark1
    xmu = numpy.nan_to_num(I1/I0)
    ene = dcm.theta2e(cardCT.Theta)
    ll = min(len(ene), len(xmu))
    CP.GraceWin.GPlot(ene[:ll],xmu[:ll], gw=0, graph=0, curve=0, legend="",color=1, noredraw=True)
    CP.GraceWin.GPlot(ene[:ll], I0[:ll], gw=0, graph=1, curve=0, legend="", color=2, noredraw=True)
    CP.GraceWin.wins[0].command('with g0\nautoscale\nredraw\n')
    CP.GraceWin.GPlot(ene[:ll], I1[:ll], gw=0, graph=1, curve=1, legend="", color=3, noredraw=True)
    CP.GraceWin.wins[0].command('with g1\nautoscale\nredraw\n')
    tmp = os.listdir(XIA1NexusPath)
    tmp.sort()
    for i in tuple(tmp):
        if not i.startswith(cardXIA1.streamTargetFile):
            tmp.remove(i)
    if len(tmp) > len(XIA1filesList):
        #print tmp
        #print tmp2
        for name in tmp[len(XIA1filesList):]:
            XIA1filesList.append(name)
            #print "New XIA1 file found: ", name, " --> Fluo graph update."
            f = tables.openFile(XIA1NexusPath + os.sep + name,"r")
            fluoSeg=zeros([shape(eval("f.root.entry.scan_data.channel%02i"%cardXIA1Channels[0]))[0],cardXIA1.streamNbDataPerAcq],numpy.float32)
            for ch in cardXIA1Channels:
                fluoSeg += eval("f.root.entry.scan_data.channel%02i"%ch).read()
            f.close()
            fluoSeg = sum(fluoSeg[:,roiStart:roiEnd],axis=1) 
            fluoXIA1 += list(fluoSeg)
        ll = len(fluoXIA1)
        if len(I0) >= ll and ll > 2:
            pass
            CP.GraceWin.GPlot(ene[:ll],numpy.nan_to_num((array(fluoXIA1,"f")[:ll])/I0[:ll]),\
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
    cardCT.bufferDepth = 1
    cardCT.continuousAcquisition = False
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


