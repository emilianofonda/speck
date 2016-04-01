import dentist
import thread
import tables
import os
import numpy
import time as myTime
from time import sleep
from spec_syntax import wait_motor
from GracePlotter import GracePlotter

cardCT = DeviceProxy("d09-1-c00/ca/cpt.3_old")
cardAI = DeviceProxy("d09-1-c00/ca/sai.1")
cardXIA1 = DeviceProxy("tmp/test/xiadxp.test")
cardXIA2 = DeviceProxy("tmp/test/xiadxp.test.2")
cardXIA1Channels = range(1,20) #remember the range stops at N-1: 19
cardXIA2Channels = range(0,16) #remember the range stops at N-1: 15

cardAI_dark0 = 0.#0038477007482805828
cardAI_dark1 = 0.#0089698445429353627
cardAI_dark2 = 0.#0036175041211772164
cardAI_dark3 = 0.0

def stopscan():
    cardAI.stop()
    cardCT.stop()
    cardXIA1.stop()
    cardXIA2.stop()
    wait_motor(dcm)
    return

class CPlotter:
    def __init__(self):
        return


__CPlotter__ = CPlotter()

def ecscan(fileName,e1,e2,n=1,dt=0.04,velocity=20, e0=-1, mode=""):
    """Start from e1 (eV) to e2 (eV) and count over dt (s) per point.
    velocity: Allowed velocity doesn't exceed 40eV/s.
    The backup folder MUST be defined for the code to run."""
    NofScans = n
    cardCTsavedAttributes = ["totalNbPoint","integrationTime","continuousAcquisition","bufferDepth"]
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

    #Card CT
    cardCT.totalNbPoint = NumberOfPoints
    cardCT.nexusNbAcqPerFile = NumberOfPoints
    cardCT.integrationTime = dt
    cardCT.bufferDepth = 1
    cardCT.continuousAcquisition = False
    cardCT.nexusFileGeneration = False
    cardCT.set_timeout_millis(30000)

    #Card AI
    cardAI.integrationTime = dt * 1000 -1.
    cardAI.nexusFileGeneration = False
    cardAI.nexusNbAcqPerFile = NumberOfPoints
    cardAI.dataBufferNumber = NumberOfPoints
    cardAI.statHistoryBufferDepth = NumberOfPoints
    cardAI.set_timeout_millis(30000)

    #Card XIA1
    #Rois are defined only on one channel of XIA1 and used for XIA2
    roiStart, roiEnd = map(int, cardXIA1.getrois()[1].split(",")[1:])

    cardXIA1.nbPixels = NumberOfPoints
    cardXIA1.streamNbAcqPerFile = 250
    cardXIA1.set_timeout_millis(10000)
    cardXIA1dataShape = [NumberOfPoints,cardXIA1.streamNbDataPerAcq ]    
    XIA1NexusPath = "/nfs" + cardXIA1.streamTargetPath.replace("\\","/")[1:]
    #Reset Nexus index and cleanup spool
    cardXIA1.streamresetindex()
    map(lambda x: x.startswith(cardXIA1.streamTargetFile) and os.remove(XIA1NexusPath +os.sep + x), os.listdir(XIA1NexusPath))

    #Card XIA2
    cardXIA2.nbPixels = NumberOfPoints
    cardXIA2.streamNbAcqPerFile = 250
    cardXIA2.set_timeout_millis(10000)
    cardXIA2dataShape = [NumberOfPoints,cardXIA2.streamNbDataPerAcq ]
    XIA2NexusPath = "/nfs" + cardXIA2.streamTargetPath.replace("\\","/")[1:]
    #Reset Nexus index and cleanup spool
    cardXIA2.streamresetindex()
    map(lambda x: x.startswith(cardXIA2.streamTargetFile) and os.remove(XIA2NexusPath +os.sep + x), os.listdir(XIA2NexusPath))

    #DCM Setup
    if dcm.state() == DevState.DISABLE:
        dcm.DP.on()

    #Start graphic windows    
    try:
        CP = __CPlotter__
        CP.GraceWin = GracePlotter()
        ##GnuWin = Gnuplot.Gnuplot()
        #GnuWin2 = Gnuplot.Gnuplot()
        #GnuWin3 = Gnuplot.Gnuplot()
        for CurrentScan in xrange(NofScans):
            ActualFileNameData = findNextFileName(fileName,"txt")
            ActualFileNameInfo = findNextFileName(fileName,"info")
            f=file(ActualFileNameData,"w")
            f.close()
            #Configure and move mono
            if dcm.state() == DevState.MOVING:
                wait_motor(dcm)
            dcm.DP.velocity = 60
            dcm.mode(1)
            dcm.pos(e1-1., wait=False)
        
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
            ##GnuWin('set xlabel "Energy (eV)"')
            #GnuWin2('set xlabel "Energy (eV)"')
            #GnuWin3('set xlabel "Energy (eV)"')
            ##GnuWin('set ylabel "XMU"')
            #GnuWin2('set ylabel "Currents"')
            #GnuWin3('set ylabel "Fluo"')
            ##GnuWin('set style data l')
            #GnuWin2('set style data l')
            #GnuWin3('set style data l')
            while(dcm.state() == DevState.MOVING):
                sleep(0.02)
            while(dcm.state() == DevState.MOVING):
                sleep(0.02)
            timeAtStart = asctime()
            cardAI.start()
            cardXIA1.snap()
            cardXIA2.snap()
            sleep(1)
            dcm.mode(1)
            dcm.DP.velocity = velocity
            dcm.pos(e1)
            sleep(1)
            cardCT.start()
            dcm.pos(e2, wait=False)
            sleep(2)
            XIA1filesList=[]
            XIA2filesList=[]
            fluoXIA1=[]
            fluoXIA2=[]
            while(dcm.state() == DevState.MOVING):
                try: 
                    update_graphs(CP, dcm, cardAI, cardCT, cardXIA1, cardXIA2, roiStart, roiEnd, XIA1NexusPath, XIA2NexusPath, XIA1filesList, XIA2filesList, fluoXIA1, fluoXIA2)
#                   I0 = cardAI.historizedchannel0 - cardAI_dark0
#                   I1 = cardAI.historizedchannel1 - cardAI_dark1
#                   I2 = cardAI.historizedchannel2 - cardAI_dark2
#                   xmu = log(1.0*I0/I1)
#                   std = log(1.0*I1/I2)
#                   ene = dcm.theta2e(cardCT.Theta)
#                   ll = min(len(ene), len(xmu))
#                   ##GnuWin.plot(Gnuplot.Data(ene[:ll],xmu[:ll]))
#                   ##GnuWin2.plot(Gnuplot.Data(ene[:ll],I0[:ll], title="I0"),Gnuplot.Data(ene[:ll],I1[:ll], title="I1"))
#                   CP.GraceWin.GPlot(ene[:ll],xmu[:ll], gw=0, graph=0, curve=0, legend="",color=1, noredraw=True)
#                   CP.GraceWin.GPlot(ene[:ll], I0[:ll], gw=0, graph=1, curve=0, legend="", color=2, noredraw=True)
#                   CP.GraceWin.wins[0].command('with g0\nautoscale\nredraw\n')
#                   CP.GraceWin.GPlot(ene[:ll], I1[:ll], gw=0, graph=1, curve=1, legend="", color=3, noredraw=True)
#                   CP.GraceWin.wins[0].command('with g1\nautoscale\nredraw\n')
#                   CP.GraceWin.GPlot(ene[:ll], std[:ll], gw=0, graph=3, curve=1, legend="", color=1, noredraw=True)
#                   CP.GraceWin.wins[0].command('with g3\nautoscale\nredraw\n')
#                   tmp = os.listdir(XIA1NexusPath)
#                   tmp.sort()
#                   for i in tuple(tmp):
#                       if not i.startswith(cardXIA1.streamTargetFile):
#                           tmp.remove(i)
#                   tmp2 = os.listdir(XIA2NexusPath)
#                   tmp2.sort()
#                   for i in tuple(tmp2):
#                       if not i.startswith(cardXIA2.streamTargetFile):
#                           tmp2.remove(i)
#                   if len(tmp) > len(XIA1filesList):
#                       #print tmp
#                       for name in tmp[len(XIA1filesList):]:
#                           XIA1filesList.append(name)
#                           #print "New XIA1 file found: ", name, " --> Fluo graph update."
#                           f = tables.openFile(XIA1NexusPath + os.sep + name,"r")
#                           fluoSeg=zeros([cardXIA1.streamNbAcqPerFile,cardXIA1.streamNbDataPerAcq],numpy.float32)
#                           for ch in cardXIA1Channels:
#                               fluoSeg += eval("f.root.entry.scan_data.channel%02i"%ch).read()
#                           f.close()
#                           fluoSeg = sum(fluoSeg[:,roiStart:roiEnd],axis=1) 
#                           fluoXIA1 += list(fluoSeg)
#                       for name in tmp2[len(XIA2filesList):]:
#                           XIA2filesList.append(name)
#                           #print "New XIA2 file found: ", name, " --> Fluo graph update."
#                           f = tables.openFile(XIA2NexusPath + os.sep + name,"r")
#                           fluoSeg=zeros([cardXIA2.streamNbAcqPerFile,cardXIA2.streamNbDataPerAcq],numpy.float32)
#                           for ch in cardXIA2Channels:
#                               fluoSeg += eval("f.root.entry.scan_data.channel%02i"%ch).read()
#                           f.close()
#                           fluoSeg = sum(fluoSeg[:,roiStart:roiEnd],axis=1) 
#                           fluoXIA2 += list(fluoSeg)
#                       ll = min(len(fluoXIA1),len(fluoXIA2))
#                       if len(I0) >= ll:
#                           CP.GraceWin.GPlot(ene[:ll],(array(fluoXIA1,"f")[:ll] + array(fluoXIA2,"f")[:ll])/I0[:ll],\
#                           gw=0, graph=2, curve=0, legend="", color=1, noredraw=False)
#                           
#                           CP.GraceWin.wins[0].command('with g2\nautoscale\nredraw\n')
#                           #GnuWin3.plot(Gnuplot.Data(ene[:ll],\
#                           #(array(fluoXIA1,"f")[:ll] + array(fluoXIA1,"f")[:ll])/I0[:ll]))
                except Exception, tmp:
                    print tmp
                    pass
                sleep(1)
            while(DevState.RUNNING in [cardCT.state(),]):
                sleep(0.1)
            timeAtStop = asctime()
            timeout0 = time()
            while(DevState.RUNNING in [cardAI.state(),] and time()-timeout0 < 3):
                sleep(0.1)
            if time()-timeout0 > 3:
                print "cardAI of ecscan failed to stop!"
            cardAI.stop()
            theta = cardCT.Theta
            I0 = array(cardAI.historizedchannel0,"f") - cardAI_dark0
            I1 = array(cardAI.historizedchannel1,"f") - cardAI_dark1
            I2 = array(cardAI.historizedchannel2,"f") - cardAI_dark2
            xmu = log(I0/I1)
            ene = dcm.theta2e(theta)
            #
            if NofScans >= 1: 
                print myTime.asctime(), " : sending dcm back to starting point."
                dcm.DP.velocity = 60
                dcm.mode(1)
                dcm.pos(e1-1., wait=False)
            #
            print myTime.asctime(), " : Saving Data..."
            XIAt0=time()
            while(cardXIA1.state() == DevState.RUNNING or cardXIA2.state() == DevState.RUNNING):
                sleep(0.2)
                if time() - XIAt0 > 60:
                    raise Exception("Time Out waiting for XIA cards to stop! Waited more than 60s... !")
            #Additional time to wait for last file to appear in spool
            myTime.sleep(3)
            try:
                update_graphs(CP, dcm, cardAI, cardCT, cardXIA1, cardXIA2, roiStart, roiEnd, XIA1NexusPath, XIA2NexusPath, XIA1filesList, XIA2filesList, fluoXIA1, fluoXIA2)
                #GnuWin.plot(Gnuplot.Data(ene[:ll],xmu[:ll]))
            except KeyboardInterrupt, tmp:
                raise tmp
            except Exception, tmp:
                print tmp
                pass
            
#XIA1 prepare
            XIA1filesNames = os.listdir(XIA1NexusPath)
            XIA1filesNames.sort()
            for i in tuple(XIA1filesNames):
                if not i.startswith(cardXIA1.streamTargetFile):
                    XIA1filesNames.remove(i)
            #print XIA1filesNames
            XIA1files = map(lambda x: tables.openFile(XIA1NexusPath +os.sep + x, "r"), XIA1filesNames)
#XIA2 prepare
            XIA2filesNames = os.listdir(XIA2NexusPath)
            XIA2filesNames.sort()
            for i in tuple(XIA2filesNames):
                if not i.startswith(cardXIA2.streamTargetFile):
                    XIA2filesNames.remove(i)
            #print XIA2filesNames
            XIA2files = map(lambda x: tables.openFile(XIA2NexusPath +os.sep + x, "r"), XIA2filesNames)
#Common
            outtaName = filename2ruche(ActualFileNameData)
            outtaHDF = tables.openFile(outtaName[:outtaName.rfind(".")] + ".hdf","w")
            outtaHDF.createGroup("/","XIA")
#Superpose all XIA matrices and make one to avoid exploding the TeraByte/week limits and keep on a USB stick
            outtaHDF.createArray("/XIA", "mcaSum", numpy.zeros(cardXIA1dataShape, numpy.uint32))
#XIA1 read / write
            for ch in cardXIA1Channels:
                outtaHDF.createArray("/XIA", "fluo%02i"%ch, numpy.zeros(NumberOfPoints, numpy.uint32))
                block = 0
                blockLen = cardXIA1.streamNbAcqPerFile
                pointerCh = eval("outtaHDF.root.XIA.fluo%02i"%ch)
                for XFile in XIA1files:
                    __block = eval("XFile.root.entry.scan_data.channel%02i"%ch).read()
                    actualBlockLen = shape(__block)[0]
                    outtaHDF.root.XIA.mcaSum[block * blockLen: (block * blockLen) + actualBlockLen,:] += __block
                    pointerCh[block * blockLen: (block + 1) * blockLen] = sum(__block[:,roiStart:roiEnd], axis=1)
                    block += 1
            print "XIA1: OK"
#XIA2 read / write NOTA: these channels names are shifted of +20 in output
            for ch in cardXIA2Channels:
                outtaHDF.createArray("/XIA", "fluo%02i" % (ch+20), numpy.zeros(NumberOfPoints, numpy.uint32))
                block = 0
                blockLen = cardXIA2.streamNbAcqPerFile
                pointerCh = eval("outtaHDF.root.XIA.fluo%02i" % (ch+20))
                for XFile in XIA2files:
                    __block = eval("XFile.root.entry.scan_data.channel%02i"%ch).read()
                    actualBlockLen = shape(__block)[0]
                    outtaHDF.root.XIA.mcaSum[block * blockLen: (block * blockLen) + actualBlockLen,:] += __block
                    pointerCh[block * blockLen: (block + 1) * blockLen] = sum(__block[:,roiStart:roiEnd], axis=1)
                    block += 1
            print "XIA2: OK"
#Finalize derived quantities
            fluoX = array( sum(outtaHDF.root.XIA.mcaSum[:,roiStart:roiEnd], axis=1), "f") / I0
            xmuS = log(I1/I2)
            outtaHDF.createGroup("/","Spectra")
            outtaHDF.createArray("/Spectra", "xmu_sample", xmu)
            outtaHDF.createArray("/Spectra", "xmu_standard", xmuS)
            outtaHDF.createArray("/Spectra", "xmu_fluo", fluoX)
            outtaHDF.createGroup("/","Raw")
            outtaHDF.createArray("/Raw", "Energy", ene)
            outtaHDF.createArray("/Raw", "I0", I0)
            outtaHDF.createArray("/Raw", "I1", I1)
            outtaHDF.createArray("/Raw", "I2", I2)
#Stop feeding the monster. Close HDF
            outtaHDF.close()
            print "HDF closed."
#Clean up the mess in the spool
#XIA1 close and wipe
            map(lambda x: x.close(), XIA1files)
            map(lambda x: x.startswith(cardXIA1.streamTargetFile)\
            and os.remove(XIA1NexusPath +os.sep + x), os.listdir(XIA1NexusPath))
#XIA2 close and wipe
            map(lambda x: x.close(), XIA2files)
            map(lambda x: x.startswith(cardXIA2.streamTargetFile)\
            and os.remove(XIA2NexusPath +os.sep + x), os.listdir(XIA2NexusPath))
#Local data saving
            dataBlock = array([ene,theta,xmu,fluoX,xmuS,\
            I0,I1,I2,cardAI.historizedchannel3],"f")
            numpy.savetxt(ActualFileNameData, transpose(dataBlock))
            FInfo = file(ActualFileNameInfo,"w")
            FInfo.write("#TimeAtStart = %s\n" % (timeAtStart))
            FInfo.write("#TimeAtStop  = %s\n" % (timeAtStop))
            FInfo.write("#Scan from %g to %g at velocity= %g eV/s\n" % (e1, e2, dcm.DP.velocity))
            FInfo.write("#Counter Card Config\n")
            for i in cardCTsavedAttributes:
                FInfo.write("#%s = %g\n" % (i,cardCT.read_attribute(i).value))
            FInfo.write("#Analog  Card Config\n")
            #Report in file Info dark currents applied
            FInfo.write("Dark_I0= %9.8f\nDark_I1= %9.8f\nDark_I2= %9.8f\nDark_I3= %9.8f\n"\
            %(cardAI_dark0,cardAI_dark0,cardAI_dark0,cardAI_dark0,))
            #
            for i in cardAIsavedAttributes:
                FInfo.write("#%s = %g\n" % (i, cardAI.read_attribute(i).value))
            for i in wa(returns=True, verbose=False):
                FInfo.write("#" + i + "\n")
            FInfo.close()
            os.system("cp " + ActualFileNameData +" " +filename2ruche(ActualFileNameData))
            os.system("cp " + ActualFileNameInfo +" " +filename2ruche(ActualFileNameInfo))            
            print myTime.asctime(), " : Data saved to backup."
            try:
                if e1 < e0 <e2:
                    #thread.start_new_thread(dentist.dentist, (ActualFileNameData,), {"e0":e0,})
                    if mode.startswith("f"):
                        dentist.dentist(ActualFileNameData, e0 =e0, mode="f")
                    else:
                        dentist.dentist(ActualFileNameData, e0 =e0, mode="")
            except Exception, tmp:
                print tmp
    except Exception, tmp:
        print "Acquisition Halted on Exception: wait for dcm to stop."
        stopscan()
        print "Halt"
        print tmp
        raise tmp
    return

def update_graphs(CP, dcm, cardAI, cardCT, cardXIA1, cardXIA2, roiStart, roiEnd,\
XIA1NexusPath, XIA2NexusPath, XIA1filesList, XIA2filesList, fluoXIA1, fluoXIA2):
    I0 = cardAI.historizedchannel0 - cardAI_dark0
    I1 = cardAI.historizedchannel1 - cardAI_dark1
    I2 = cardAI.historizedchannel2 - cardAI_dark2
    xmu = log(1.0*I0/I1)
    std = log(1.0*I1/I2)
    ene = dcm.theta2e(cardCT.Theta)
    ll = min(len(ene), len(xmu))
    ##GnuWin.plot(Gnuplot.Data(ene[:ll],xmu[:ll]))
    ##GnuWin2.plot(Gnuplot.Data(ene[:ll],I0[:ll], title="I0"),Gnuplot.Data(ene[:ll],I1[:ll], title="I1"))
    CP.GraceWin.GPlot(ene[:ll],xmu[:ll], gw=0, graph=0, curve=0, legend="",color=1, noredraw=True)
    CP.GraceWin.GPlot(ene[:ll], I0[:ll], gw=0, graph=1, curve=0, legend="", color=2, noredraw=True)
    CP.GraceWin.wins[0].command('with g0\nautoscale\nredraw\n')
    CP.GraceWin.GPlot(ene[:ll], I1[:ll], gw=0, graph=1, curve=1, legend="", color=3, noredraw=True)
    CP.GraceWin.wins[0].command('with g1\nautoscale\nredraw\n')
    CP.GraceWin.GPlot(ene[:ll], std[:ll], gw=0, graph=3, curve=1, legend="", color=1, noredraw=True)
    CP.GraceWin.wins[0].command('with g3\nautoscale\nredraw\n')
    tmp = os.listdir(XIA1NexusPath)
    tmp.sort()
    for i in tuple(tmp):
        if not i.startswith(cardXIA1.streamTargetFile):
            tmp.remove(i)
    tmp2 = os.listdir(XIA2NexusPath)
    tmp2.sort()
    for i in tuple(tmp2):
        if not i.startswith(cardXIA2.streamTargetFile):
            tmp2.remove(i)
    if len(tmp) > len(XIA1filesList):
        #print tmp
        for name in tmp[len(XIA1filesList):]:
            XIA1filesList.append(name)
            #print "New XIA1 file found: ", name, " --> Fluo graph update."
            f = tables.openFile(XIA1NexusPath + os.sep + name,"r")
            fluoSeg=zeros([cardXIA1.streamNbAcqPerFile,cardXIA1.streamNbDataPerAcq],numpy.float32)
            for ch in cardXIA1Channels:
                fluoSeg += eval("f.root.entry.scan_data.channel%02i"%ch).read()
            f.close()
            fluoSeg = sum(fluoSeg[:,roiStart:roiEnd],axis=1) 
            fluoXIA1 += list(fluoSeg)
        for name in tmp2[len(XIA2filesList):]:
            XIA2filesList.append(name)
            #print "New XIA2 file found: ", name, " --> Fluo graph update."
            f = tables.openFile(XIA2NexusPath + os.sep + name,"r")
            fluoSeg=zeros([cardXIA2.streamNbAcqPerFile,cardXIA2.streamNbDataPerAcq],numpy.float32)
            for ch in cardXIA2Channels:
                fluoSeg += eval("f.root.entry.scan_data.channel%02i"%ch).read()
            f.close()
            fluoSeg = sum(fluoSeg[:,roiStart:roiEnd],axis=1) 
            fluoXIA2 += list(fluoSeg)
        ll = min(len(fluoXIA1),len(fluoXIA2))
        if len(I0) >= ll:
            CP.GraceWin.GPlot(ene[:ll],(array(fluoXIA1,"f")[:ll] + array(fluoXIA2,"f")[:ll])/I0[:ll],\
            gw=0, graph=2, curve=0, legend="", color=1, noredraw=False)
            
            CP.GraceWin.wins[0].command('with g2\nautoscale\nredraw\n')
            #GnuWin3.plot(Gnuplot.Data(ene[:ll],\
            #(array(fluoXIA1,"f")[:ll] + array(fluoXIA1,"f")[:ll])/I0[:ll]))
    return
