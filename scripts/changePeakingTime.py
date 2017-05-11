#This is a macro that depends on the SAMBA environment defined in speck_config...
#This code works on global objects like mca1 and mca2, it is strictly... volatile... but essential!!!!


def XIAgetConfigFiles():
    ll1 = mca1.DP.get_property("ConfigurationFiles")["ConfigurationFiles"]
    ll2 = mca2.DP.get_property("ConfigurationFiles")["ConfigurationFiles"]
    return ll1, ll2

def XIAviewConfigFiles():
    ll1, ll2 = XIAgetConfigFiles()
    print "\nmca1:"
    for i in ll1:
        i3 = i.split(";")
        print "Label = %6s Mode = %8s\n    File = %s"%tuple(i3)
    print "\nmca2:"
    for i in ll2:
        i3 = i.split(";")
        print "Label = %6s Mode = %8s\n    File = %s"%tuple(i3)
    return

def XIAgetConfigNumber():
    cfg1 = int(mca1.DP.get_property("SPECK_ConfigurationFileNumber")["SPECK_ConfigurationFileNumber"][0])
    cfg2 = int(mca2.DP.get_property("SPECK_ConfigurationFileNumber")["SPECK_ConfigurationFileNumber"][0])
    #print "Current config numbers are:"
    #print "mca1 --> ", cfg1
    #print "mca2 --> ", cfg2
    return cfg1, cfg2


def XIAsetConfigNumber(config):
    mca1.DP.put_property({"SPECK_ConfigurationFileNumber":config})
    mca2.DP.put_property({"SPECK_ConfigurationFileNumber":config})
    return XIAgetConfigNumber()


###Code below is used for EXAFS hutch continuous scans

def setMODE(mode="",config="",mca=[]):
    fault = False
    if mca == []:
        return
    changeMode = False
    try:
        for i in mca:
            if i.DP.currentMode <> mode:
                changeMode = True
    except:
        changeMode = True
        fault = True
        #print RED + "Cannot retrieve current XIA mode. Note: ROIs will not be transferred from STEP to MAP." + RESET
    try:
        rois = []
        for i in mca:
            rois.append(i.DP.getrois())
    except:
        #print RED + "Cannot retrieve ROIs. Note: ROIs will not be transferred from STEP to MAP." + RESET
        changeMode = True
        fault = True
    if changeMode:
        if fault:
            for i in mca:
                i.init()
        for i in mca:
            i.DP.set_timeout_millis(30000)
        for i in mca:
            i.DP.loadconfigfile(config)
        sleep(0.25)
        notReady = True
        while(notReady):
            for i in mca:
                notReady =  False
                if i.state() in [DevState.UNKNOWN, DevState.DISABLE, DevState.OFF]:
                    notReady = True
                    break
            sleep(1)
        if fault:
            rois = []
            for i in mca:
                rois.append(i.DP.getrois())
        sleep(0.25)
        for i in range(len(mca)):
            if rois[i] <> mca[i].DP.getrois():
                mca[i].DP.setroisfromlist(rois[i])
        notReady = True
        while(notReady):
            for i in mca:
                notReady =  False
                if i.state() in [DevState.UNKNOWN, DevState.DISABLE, DevState.OFF]:
                    notReady = True
                    break
            sleep(1)
        ct.reinit()
    return


def setMAP(recursive = 0):
    "Only one unique ROI is supported"
    cfgNumbers = XIAgetConfigNumber()
    config1, config2 = "MAP%i"%cfgNumbers[0], "MAP%i"%cfgNumbers[1]
    fault = False
    changeMode = False
    if mca1.state() == DevState.FAULT:
        changeMode = True
        fault = True
        mca1.init()
    if mca2.state() == DevState.FAULT:
        changeMode = True
        fault = True
        mca2.init()
    if changeMode:
        sleep(0.25)
        while(mca1.state() in [DevState.DISABLE,DevState.UNKNOWN] or mca2.state() in [DevState.DISABLE,DevState.UNKNOWN]):
            sleep(1)
    try:
        changeMode = mca1.DP.currentMode <> 'MAPPING' or mca2.DP.currentMode <> 'MAPPING'\
        or config1 <> mca1.DP.currentAlias or config2 <> mca1.DP.currentAlias 
    except:
        changeMode = True
        fault = True
        print RED + "Fault: mode" + RESET
        #print RED + "Cannot retrieve current XIA mode. Note: ROIs will not be transferred from STEP to MAP." + RESET
    try:
        rois1 = mca1.getROIs()
        rois2 = mca2.getROIs()
        roi1,roi2 = rois1
        #print roi1, roi2
    except:
        print RED + "Fault: rois" + RESET
        #print RED + "Cannot retrieve ROIs. Note: ROIs will not be transferred from STEP to MAP." + RESET
        changeMode = True
        fault = True
    if changeMode:
        print "Setting MAP mode"
        if fault:
            mca1.init()
            mca2.init()
            sleep(1)
            while(mca1.state() == DevState.DISABLE or mca2.state() == DevState.DISABLE):
                sleep(1)
        mca1.DP.set_timeout_millis(60000)
        mca2.DP.set_timeout_millis(60000)
        sleep(0.25)
        mca1.DP.loadconfigfile("MAP1")
        mca2.DP.loadconfigfile("MAP1")
        sleep(0.25)
        while(mca1.state() == DevState.DISABLE or mca2.state() == DevState.DISABLE):
            sleep(1)
        if fault:
            rois1 = mca1.getROIs()
            rois2 = mca2.getROIs()
            roi1,roi2 = rois1
        sleep(0.25)
        if rois1 <> mca1.getROIs():
            #mca1.DP.setroisfromlist(rois1)
            mca1.setROIs(roi1, roi2)
        if rois2 <> mca2.getROIs():
            mca2.setROIs(roi1, roi2)
            #mca2.DP.setroisfromlist(rois2)
        sleep(0.25)
        ct.reinit()
        sleep(0.25)
    #if rois1 <> mca1.getROIs():
    #    #mca1.DP.setroisfromlist(rois1)
    #    mca1.setROIs(roi1, roi2)
    #if rois2 <> mca2.getROIs():
    #    mca2.setROIs(roi1, roi2)
    #    #mca2.DP.setroisfromlist(rois2)
    mca1.setROIs(roi1, roi2)
    mca2.setROIs(roi1, roi2)
    while(mca1.state() in [DevState.DISABLE,DevState.UNKNOWN] or mca2.state() in [DevState.DISABLE,DevState.UNKNOWN]):
        sleep(1)
    if mca1.state() == DevState.FAULT or mca2.state() == DevState.FAULT and recursive <=3:
        setMAP(recursive = recursive + 1)
    else:
        #print "DxMap Ready for service."
        pass
    return

def setSTEP(recursive = 0):
    cfgNumbers = XIAgetConfigNumber()
    config1, config2 = "STEP%i"%cfgNumbers[0], "STEP%i"%cfgNumbers[1]
    fault = False
    changeMode = False
    if mca1.state() == DevState.FAULT:
        changeMode = True
        fault = True
        mca1.init()
        sleep(1)
    if mca2.state() == DevState.FAULT:
        changeMode = True
        fault = True
        mca2.init()
        sleep(1)
    if changeMode:
        sleep(0.25)
        while(mca1.state() in [DevState.DISABLE,DevState.UNKNOWN] or mca2.state() in [DevState.DISABLE,DevState.UNKNOWN]):
            sleep(1)
    try:
        changeMode = mca1.DP.currentMode <> 'MCA' or mca2.DP.currentMode <> 'MCA'\
        or config1 <> mca1.DP.currentAlias or config2 <> mca1.DP.currentAlias 
    except:
        changeMode = True
        fault = True
        print RED + "Fault: mode" + RESET
        #print RED + "Cannot retrieve current XIA mode. Note: ROIs will not be transferred from STEP to MAP." + RESET
    try:
        rois1 = mca1.getROIs()
        rois2 = mca2.getROIs()
        roi1,roi2 = rois1
        #print roi1, roi2
    except:
        print RED + "Fault: rois" + RESET
        #print RED + "Cannot retrieve ROIs. Note: ROIs will not be transferred from STEP to MAP." + RESET
        changeMode = True
        fault = True
    if changeMode:
        print "Setting STEP mode"
        if fault:
            mca1.init()
            mca2.init()
            sleep(0.25)
            while(mca1.state() in [DevState.DISABLE,DevState.UNKNOWN] or mca2.state() in [DevState.DISABLE,DevState.UNKNOWN]):
                sleep(1)
        mca1.DP.set_timeout_millis(60000)
        mca2.DP.set_timeout_millis(60000)
        sleep(0.25)
        mca1.DP.loadconfigfile(config1)
        mca2.DP.loadconfigfile(config2)
        sleep(0.25)
        while(mca1.state() == DevState.DISABLE or mca2.state() == DevState.DISABLE):
            sleep(1)
        if fault:
            rois1 = mca1.getROIs()
            rois2 = mca2.getROIs()
            roi1,roi2 = rois1
        sleep(0.25)
        ct.reinit()
    #if rois1 <> mca1.getROIs():
    #    #mca1.DP.setroisfromlist(rois1)
    #    mca1.setROIs(roi1, roi2)
    #if rois2 <> mca2.getROIs():
    #    mca2.setROIs(roi1, roi2)
    #    #mca2.DP.setroisfromlist(rois2)
    #2 lines below replace lines above for tests
    mca1.setROIs(roi1, roi2)
    mca2.setROIs(roi1, roi2)
    while(mca1.state() in [DevState.DISABLE,DevState.UNKNOWN] or mca2.state() in [DevState.DISABLE,DevState.UNKNOWN]):
        sleep(1)
    if mca1.state() == DevState.FAULT or mca2.state() == DevState.FAULT and recursive <=3:
        setSTEP(recursive = recursive + 1)
    else:
        pass
        #print "DxMap Ready for service."
    return
