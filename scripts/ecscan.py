cardCT = DeviceProxy("d09-1-c00/ca/cpt.3_old")
cardAI = DeviceProxy("d09-1-c00/ca/sai.1")


def ecscan(fileName,e0,e1,dt=0.05,velocity=10):
    """Start from e0 (eV) to e1 (eV) and count over dt (s) per point.
    velocity: Allowed velocity doesn't exceed 40eV/s."""
    cardCTsavedAttributes = ["totalNbPoint","integrationTime","continuousAcquisition","bufferDepth"]
    cardAIsavedAttributes = ["configurationId","frequency","integrationTime","dataBufferNumber"]
    if fileName == None: 
        raise Exception("filename and limits must be specified")
    ActualFileNameData = findNextFileName(fileName,"txt")
    ActualFileNameInfo = findNextFileName(fileName,"info")
    if velocity <= 0.:
        raise Exception("Monochromator velocity too low!")
    if velocity > 40.:
        raise Exception("Monochromator velocity exceeded!")

    #Configure and move mono
    dcm.DP.velocity = velocity
    dcm.mode(0)
    dcm.pos(e0, wait=False)
    
    #Configure cards
    TotalTime = float(abs(e1-e0)) / velocity
    print "Expected time = %g s" % TotalTime
    NumberOfPoints = int (float(abs(e1-e0)) / velocity / dt)

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

    #Start Measurement
    GnuWin = Gnuplot.Gnuplot()
    GnuWin('set xlabel "Energy (eV)"')
    GnuWin('set ylabel "XMU"')
    GnuWin('set style data l')
    while(dcm.state() == DevState.MOVING):
        sleep(0.02)
    while(dcm.state() == DevState.MOVING):
        sleep(0.02)
    timeAtStart = asctime()
    cardAI.start()
    sleep(0.1)
    dcm.mode(1)
    cardCT.start()
    dcm.pos(e1, wait=False)
    sleep(0.2)
    while(dcm.state() == DevState.MOVING):
        try:
            xmu = log(cardAI.historizedchannel0/cardAI.historizedchannel1)
            ene = dcm.theta2e(cardCT.Theta)
            ll = min(len(ene), len(xmu))
            GnuWin.plot(Gnuplot.Data(ene[:ll],xmu[:ll]))
        except Exception, tmp:
            #print tmp
            pass
        sleep(1)
    while(DevState.RUNNING in [cardCT.state(),cardAI.state()]):
        sleep(0.1)
    timeAtStop = asctime()
    try:
        xmu = log(cardAI.historizedchannel0/cardAI.historizedchannel1)
        ene = dcm.theta2e(cardCT.Theta)
        ll = min(len(ene), len(xmu))
        GnuWin.plot(Gnuplot.Data(ene[:ll],xmu[:ll]))
    except Exception, tmp:
        #print tmp
        pass
    theta = cardCT.Theta
    I0 = cardAI.historizedchannel0
    I1 = cardAI.historizedchannel1
    I2 = cardAI.historizedchannel2
    xmu = log(I0/I1)
    ene = dcm.theta2e(theta)
    dataBlock = array([ene,theta,xmu,\
    I0,I1,I2,cardAI.historizedchannel3],"f")
    numpy.savetxt(ActualFileNameData, transpose(dataBlock))
    FInfo = file(ActualFileNameInfo,"w")
    FInfo.write("#TimeAtStart = %s\n" % (timeAtStart))
    FInfo.write("#TimeAtStop  = %s\n" % (timeAtStop))
    FInfo.write("#Scan from %g to %g at velocity= %g eV/s\n" % (e0, e1, dcm.DP.velocity))
    FInfo.write("#Counter Card Config\n")
    for i in cardCTsavedAttributes:
        FInfo.write("#%s = %g\n" % (i,cardCT.read_attribute(i).value))
    FInfo.write("#Analog  Card Config\n")
    for i in cardAIsavedAttributes:
        FInfo.write("#%s = %g\n" % (i,cardAI.read_attribute(i).value))
    for i in wa(returns=True, verbose=False):
        FInfo.write("#" + i + "\n")
    FInfo.close()
    if __Default_Backup_Folder <> "":
        os.system("cp " + ActualFileNameData +" " +filename2ruche(ActualFileNameData))
        os.system("cp " + ActualFileNameInfo +" " +filename2ruche(ActualFileNameInfo))
    return

