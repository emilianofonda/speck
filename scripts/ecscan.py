import dentist
import thread
import tables
import os
import numpy
import time as myTime

cardCT = DeviceProxy("d09-1-c00/ca/cpt.3_old")
cardAI = DeviceProxy("d09-1-c00/ca/sai.1")
cardXIA1 = DeviceProxy("tmp/test/xiadxp.test")
cardXIA1Channels = range(1,20) #remember the range stops at N-1: 19
cardXIA2Channels = range(0,16) #remember the range stops at N-1: 15

def stopscan():
    dcm.stop()
    cardAI.stop()
    cardCT.stop()
    return

def ecscan(fileName,e1,e2,n=1,dt=0.04,velocity=10, e0=-1):
    """Start from e1 (eV) to e2 (eV) and count over dt (s) per point.
    velocity: Allowed velocity doesn't exceed 40eV/s."""
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

    #Card XIA
    cardXIA1.nbPixels = NumberOfPoints
    cardXIA1.streamNbAcqPerFile = 250
    cardXIA1.set_timeout_millis(10000)
    cardXIA1dataShape = [NumberOfPoints,cardXIA1.streamNbDataPerAcq ]
    roiStart, roiEnd = map(int, cardXIA1.getrois()[1].split(",")[1:])
    XIA1NexusPath = "/nfs" + cardXIA1.streamTargetPath.replace("\\","/")[1:]
    #MIssing reset Nexus index and cleanup spool
    cardXIA1.streamresetindex()
    map(lambda x: os.remove(XIA1NexusPath +os.sep + x), os.listdir(XIA1NexusPath))
    if dcm.state() == DevState.DISABLE:
        dcm.on()
    try:
        for CurrentScan in xrange(NofScans):
            ActualFileNameData = findNextFileName(fileName,"txt")
            ActualFileNameInfo = findNextFileName(fileName,"info")
            #Configure and move mono
            if dcm.state() == DevState.MOVING:
                wait_motor(dcm)
            dcm.DP.velocity = 60
            dcm.mode(1)
            dcm.pos(e1-1., wait=False)
        
            #Print Name:
            print "Measuring : %s\n"%ActualFileNameData
            #Start Measurement
            #GWin = grace_np.GraceProcess()
            #GPL = GracePlotter()
            GnuWin = Gnuplot.Gnuplot()
            GnuWin2 = Gnuplot.Gnuplot()
            GnuWin3 = Gnuplot.Gnuplot()
            GnuWin('set xlabel "Energy (eV)"')
            GnuWin2('set xlabel "Energy (eV)"')
            GnuWin3('set xlabel "Energy (eV)"')
            GnuWin('set ylabel "XMU"')
            GnuWin2('set ylabel "Currents"')
            GnuWin3('set ylabel "Fluo"')
            GnuWin('set style data l')
            GnuWin2('set style data l')
            GnuWin3('set style data l')
            while(dcm.state() == DevState.MOVING):
                sleep(0.02)
            while(dcm.state() == DevState.MOVING):
                sleep(0.02)
            timeAtStart = asctime()
            cardAI.start()
            cardXIA1.snap()
            sleep(1)
            dcm.mode(1)
            dcm.DP.velocity = velocity
            dcm.pos(e1)
            sleep(1)
            cardCT.start()
            dcm.pos(e2, wait=False)
            sleep(2)
            XIA1filesList=[]
            fluoX=[]
            while(dcm.state() == DevState.MOVING):
                try: 
                    I0 = cardAI.historizedchannel0
                    I1 = cardAI.historizedchannel1
                    xmu = log(I0/I1)
                    ene = dcm.theta2e(cardCT.Theta)
                    ll = min(len(ene), len(xmu))
                    GnuWin.plot(Gnuplot.Data(ene[:ll],xmu[:ll]))
                    GnuWin2.plot(Gnuplot.Data(ene[:ll],I0[:ll], title="I0"),Gnuplot.Data(ene[:ll],I1[:ll], title="I1"))
                    tmp = os.listdir(XIA1NexusPath)
                    tmp.sort()
                    for i in tuple(tmp):
                        if not i.startswith(cardXIA1.streamTargetFile):
                            tmp.remove(i)
                    if len(tmp) > len(XIA1filesList):
                        #print tmp
                        for name in tmp[len(XIA1filesList):]:
                            XIA1filesList.append(name)
                            print "New XIA1 file found: ", name, " --> Fluo graph update."
                            f = tables.openFile(XIA1NexusPath + os.sep + name,"r")
                            fluoSeg=zeros([cardXIA1.streamNbAcqPerFile,cardXIA1.streamNbDataPerAcq],numpy.float32)
                            for ch in cardXIA1Channels:
                                fluoSeg += eval("f.root.entry.scan_data.channel%02i"%ch).read()
                            f.close()
                            fluoSeg = sum(fluoSeg[:,roiStart:roiEnd],axis=1) 
                            fluoX += list(fluoSeg)
                            ll = len(fluoX)
                            if len(I0) >= ll:
                                GnuWin3.plot(Gnuplot.Data(ene[:ll], array(fluoX)/I0[:ll]))
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
            try:
                xmu = log(cardAI.historizedchannel0/cardAI.historizedchannel1)
                ene = dcm.theta2e(cardCT.Theta)
                ll = min(len(ene), len(xmu))
                GnuWin.plot(Gnuplot.Data(ene[:ll],xmu[:ll]))
            except KeyboardInterrupt, tmp:
                raise tmp
            except Exception, tmp:
                #print tmp
                pass
            theta = cardCT.Theta
            I0 = array(cardAI.historizedchannel0,"f")
            I1 = array(cardAI.historizedchannel1,"f")
            I2 = array(cardAI.historizedchannel2,"f")
            xmu = log(I0/I1)
            ene = dcm.theta2e(theta)
            dataBlock = array([ene,theta,xmu,\
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
            for i in cardAIsavedAttributes:
                FInfo.write("#%s = %g\n" % (i,cardAI.read_attribute(i).value))
            for i in wa(returns=True, verbose=False):
                FInfo.write("#" + i + "\n")
            FInfo.close()
            print myTime.asctime(), " : Local Data saved."
            if NofScans >1: 
                dcm.DP.velocity = 60
                dcm.mode(1)
                dcm.pos(e1-1., wait=False)
            if __Default_Backup_Folder <> "":
                os.system("cp " + ActualFileNameData +" " +filename2ruche(ActualFileNameData))
                os.system("cp " + ActualFileNameInfo +" " +filename2ruche(ActualFileNameInfo))
                XIAt0=time()
                while(cardXIA1.state() == DevState.RUNNING):
                    sleep(0.2)
                    if time() - XIAt0 > 60:
                        raise Exception("Time Out waiting for XIA card to stop! Waited more than 60s... !")
                XIA1filesNames = os.listdir(XIA1NexusPath)
                for i in tuple(XIA1filesNames):
                    if not i.startswith(cardXIA1.streamTargetFile):
                        XIA1filesNames.remove(i)
                XIA1files = map(lambda x: tables.openFile(XIA1NexusPath +os.sep + x), XIA1filesNames)
                outtaName = filename2ruche(ActualFileNameData)
                outtaHDF = tables.openFile(outtaName[:outtaName.rfind(".")] + ".hdf","w")
                outtaHDF.createGroup("/","XIA")
                outtaHDF.createArray("/XIA", "mcaSum", numpy.zeros(cardXIA1dataShape, numpy.uint32))
                for ch in cardXIA1Channels:
                    outtaHDF.createArray("/XIA", "fluo%02i"%ch, numpy.zeros(NumberOfPoints, numpy.uint32))
                    block = 0
                    blockLen = cardXIA1.streamNbAcqPerFile
                    pointerCh = eval("outtaHDF.root.XIA.fluo%02i"%ch)
                    for XFile in XIA1files:
                        __block = eval("XFile.root.entry.scan_data.channel%02i"%ch).read()
                        outtaHDF.root.XIA.mcaSum[block * blockLen: (block + 1) * blockLen,:] += __block
                        block += 1
                        pointerCh[block * blockLen: (block + 1) * blockLen] = sum(__block[:,roiStart:roiEnd], axis=1)
                fluoX = sum(outtaHDF.root.XIA.mcaSum[:,roiStart:roiEnd], axis=1) / I0
                outtaHDF.createGroup("/","Spectra")
                outtaHDF.createArray("/Spectra", "xmu_sample", xmu)
                outtaHDF.createArray("/Spectra", "xmu_standard", log(I1/I2))
                outtaHDF.createArray("/Spectra", "xmu_fluo", fluoX)
                outtaHDF.createGroup("/","Raw")
                outtaHDF.createArray("/Raw", "Energy", ene)
                outtaHDF.createArray("/Raw", "I0", I0)
                outtaHDF.createArray("/Raw", "I1", I1)
                outtaHDF.createArray("/Raw", "I2", I2)
                outtaHDF.close()
                map(lambda x: x.close(), XIA1files)
                map(lambda x: os.remove(XIA1NexusPath +os.sep + x), os.listdir(XIA1NexusPath))
                print myTime.asctime(), " : HDF Data saved to backup."
            try:
                if e1 < e0 <e2:
                    #thread.start_new_thread(dentist.dentist, (ActualFileNameData,), {"e0":e0,})
                    dentist.dentist(ActualFileNameData, e0 =e0)
            except Exception, tmp:
                print tmp
    except Exception, tmp:
        #dcm.stop()
        cardCT.stop()
        cardAI.stop()
        cardXIA1.stop()
        print "Acquisition Halted on Exception!"
        print tmp
        raise tmp
    return


