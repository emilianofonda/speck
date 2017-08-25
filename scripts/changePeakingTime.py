#This is a macro that depends on the SAMBA environment defined in speck_config...
#This code works on global objects like mca1 and mca2, it is strictly... volatile... but essential!!!!

#Employs the global object ct to retrieve the list of mca units

def XIAgetConfigFiles():
    return [i.DP.get_property("ConfigurationFiles")["ConfigurationFiles"] for i in ct.mca_units]
    #ll1 = mca1.DP.get_property("ConfigurationFiles")["ConfigurationFiles"]
    #ll2 = mca2.DP.get_property("ConfigurationFiles")["ConfigurationFiles"]
    #return ll1, ll2

def XIAviewConfigFiles():
    labels = iter([whois(i) for i in ct.mca_units])
    for cfg in XIAgetConfigFiles():
        print "\n%s:"%labels.next()
        for i in cfg:
            i3 = i.split(";")
            print "Label = %6s Mode = %8s\n    File = %s"%tuple(i3)
    return

def XIAgetConfigNumber():
    return [int(i.DP.get_property("SPECK_ConfigurationFileNumber")["SPECK_ConfigurationFileNumber"][0]) for i in ct.mca_units]
    #cfg1 = int(mca1.DP.get_property("SPECK_ConfigurationFileNumber")["SPECK_ConfigurationFileNumber"][0])
    #cfg2 = int(mca2.DP.get_property("SPECK_ConfigurationFileNumber")["SPECK_ConfigurationFileNumber"][0])
    #return cfg1, cfg2


def XIAsetConfigNumber(config):
    for i in ct.mca_units:
        i.DP.put_property({"SPECK_ConfigurationFileNumber":config})
    #mca1.DP.put_property({"SPECK_ConfigurationFileNumber":config})
    #mca2.DP.put_property({"SPECK_ConfigurationFileNumber":config})
    return XIAgetConfigNumber()


###Code below is used for EXAFS hutch continuous scans

def setMAP(recursive = 0):
    return setMODE(recursive, mode="MAP")

def setSTEP(recursive = 0):
    return setMODE(recursive, mode="STEP")

def setMODE(recursive = 0, mode=""):
    """Only one unique ROI is supported
    MAP corrensponds to MAPPING
    STEP corresponds to MCA"""
    if mode not in ["MAP", "STEP"]:
        raise Exception("setMODE: Wrong XIA mode specified!")
    if mode == "MAP":
        cMode = 'MAPPING'
    else:
        cMode = 'MCA'
    cfgNumbers = XIAgetConfigNumber()
    configs = [mode + "%i"%i for i in cfgNumbers]
    fault = False
    changeMode = False
    for i in ct.mca_units:
        if i.state() == DevState.FAULT:
            changeMode = True
            fault = True
            i.init()
    if changeMode:
        sleep(0.25)
        while(True in [i.state() in [DevState.DISABLE,DevState.UNKNOWN] for i in ct.mca_units]):
            sleep(1)
    try:
        changeMode = True in [i.DP.currentMode <> cMode for i in ct.mca_units] or \
        True in [i[0].DP.currentAlias <> i[1] for i in zip(ct.mca_units,configs)]
    except:
        changeMode = True
        fault = True
        print RED + "Fault: mode" + RESET
        #print RED + "Cannot retrieve current XIA mode. Note: ROIs will not be transferred from STEP to MAP." + RESET
    if changeMode:
        try:
            #Nasty! only first card gives roi to all others
            roi1,roi2 = ct.mca_units[0].getROIs()
            #print roi1, roi2
        except:
            print RED + "Fault: rois" + RESET
            #print RED + "Cannot retrieve ROIs. Note: ROIs will not be transferred from STEP to MAP." + RESET
            fault = True
        print "Setting %s  mode" % mode
        if fault:
            for i in ct.mca_units:
                i.init()
            sleep(1)
            while(True in [i.state() == DevState.DISABLE for i in ct.mca_units]):
                sleep(1)
        for i in ct.mca_units:
            i.DP.set_timeout_millis(60000)
        sleep(0.25)
        for i in zip(ct.mca_units,configs):
            i[0].DP.loadconfigfile(i[1])
        sleep(0.25)
        while(True in [i.state() in [DevState.DISABLE,DevState.UNKNOWN] for i in ct.mca_units]):
            sleep(1)
        if fault:
            roi1,roi2 = ct.mca_units[0].getROIs()
        sleep(0.25)
        for i in ct.mca_units:
            i.setROIs(roi1, roi2)
        sleep(1)
        ct.reinit()
    while(True in [i.state() in [DevState.DISABLE,DevState.UNKNOWN] for i in ct.mca_units]):
        sleep(1)
    if True in [i.state() == DevState.FAULT for i in ct.mca_units] and recursive <=3:
        setMODE(recursive = recursive + 1, mode = mode)
    else:
        #print "DxMap Ready for service."
        pass
    return


#def setMAP(recursive = 0):
#    "Only one unique ROI is supported"
#    cfgNumbers = XIAgetConfigNumber()
#    config1, config2 = "MAP%i"%cfgNumbers[0], "MAP%i"%cfgNumbers[1]
#    fault = False
#    changeMode = False
#    if mca1.state() == DevState.FAULT:
#        changeMode = True
#        fault = True
#        mca1.init()
#    if mca2.state() == DevState.FAULT:
#        changeMode = True
#        fault = True
#        mca2.init()
#    if changeMode:
#        sleep(0.25)
#        while(mca1.state() in [DevState.DISABLE,DevState.UNKNOWN] or mca2.state() in [DevState.DISABLE,DevState.UNKNOWN]):
#            sleep(1)
#    try:
#        changeMode = mca1.DP.currentMode <> 'MAPPING' or mca2.DP.currentMode <> 'MAPPING'\
#        or config1 <> mca1.DP.currentAlias or config2 <> mca1.DP.currentAlias 
#    except:
#        changeMode = True
#        fault = True
#        print RED + "Fault: mode" + RESET
#        #print RED + "Cannot retrieve current XIA mode. Note: ROIs will not be transferred from STEP to MAP." + RESET
#    if changeMode:
#        try:
#            rois1 = mca1.getROIs()
#            rois2 = mca2.getROIs()
#            roi1,roi2 = rois1
#            #print roi1, roi2
#        except:
#            print RED + "Fault: rois" + RESET
#            #print RED + "Cannot retrieve ROIs. Note: ROIs will not be transferred from STEP to MAP." + RESET
#            fault = True
#        print "Setting MAP mode"
#        if fault:
#            mca1.init()
#            mca2.init()
#            sleep(1)
#            while(mca1.state() == DevState.DISABLE or mca2.state() == DevState.DISABLE):
#                sleep(1)
#        mca1.DP.set_timeout_millis(60000)
#        mca2.DP.set_timeout_millis(60000)
#        sleep(0.25)
#        mca1.DP.loadconfigfile(config1)
#        mca2.DP.loadconfigfile(config2)
#        sleep(0.25)
#        while(mca1.state() in [DevState.DISABLE,DevState.UNKNOWN] or mca2.state() in [DevState.DISABLE,DevState.UNKNOWN]):
#            sleep(1)
#        if fault:
#            rois1 = mca1.getROIs()
#            rois2 = mca2.getROIs()
#            roi1,roi2 = rois1
#        sleep(0.25)
#        mca1.setROIs(roi1, roi2)
#        mca2.setROIs(roi1, roi2)
#        sleep(1)
#        ct.reinit()
#    while(mca1.state() in [DevState.DISABLE,DevState.UNKNOWN] or mca2.state() in [DevState.DISABLE,DevState.UNKNOWN]):
#        sleep(1)
#    if mca1.state() == DevState.FAULT or mca2.state() == DevState.FAULT and recursive <=3:
#        setMAP(recursive = recursive + 1)
#    else:
#        #print "DxMap Ready for service."
#        pass
#    return

#def setSTEP(recursive = 0):
#    "Only one unique ROI is supported"
#    cfgNumbers = XIAgetConfigNumber()
#    config1, config2 = "STEP%i"%cfgNumbers[0], "STEP%i"%cfgNumbers[1]
#    fault = False
#    changeMode = False
#    if mca1.state() == DevState.FAULT:
#        changeMode = True
#        fault = True
#        mca1.init()
#    if mca2.state() == DevState.FAULT:
#        changeMode = True
#        fault = True
#        mca2.init()
#    if changeMode:
#        sleep(0.25)
#        while(mca1.state() in [DevState.DISABLE,DevState.UNKNOWN] or mca2.state() in [DevState.DISABLE,DevState.UNKNOWN]):
#            sleep(1)
#    try:
#        changeMode = mca1.DP.currentMode <> 'MCA' or mca2.DP.currentMode <> 'MCA'\
#        or config1 <> mca1.DP.currentAlias or config2 <> mca1.DP.currentAlias 
#    except KeyboardInterrupt, tmp:
#        raise tmp
#    except:
#        changeMode = True
#        fault = True
#        print RED + "Fault: mode" + RESET
#        #print RED + "Cannot retrieve current XIA mode. Note: ROIs will not be transferred from STEP to MAP." + RESET
#    if changeMode:
#        try:
#            rois1 = mca1.getROIs()
#            rois2 = mca2.getROIs()
#            roi1,roi2 = rois1
#            #print roi1, roi2
#        except:
#            print RED + "Fault: rois" + RESET
#            #print RED + "Cannot retrieve ROIs. Note: ROIs will not be transferred from STEP to MAP." + RESET
#            fault = True
#        print "Setting STEP mode"
#        if fault:
#            mca1.init()
#            mca2.init()
#            sleep(1)
#            while(mca1.state() == DevState.DISABLE or mca2.state() == DevState.DISABLE):
#                sleep(1)
#        mca1.DP.set_timeout_millis(60000)
#        mca2.DP.set_timeout_millis(60000)
#        sleep(0.25)
#        mca1.DP.loadconfigfile(config1)
#        mca2.DP.loadconfigfile(config2)
#        sleep(0.25)
#        while(mca1.state() in [DevState.DISABLE,DevState.UNKNOWN] or mca2.state() in [DevState.DISABLE,DevState.UNKNOWN]):
#            sleep(1)
#        if fault:
#            rois1 = mca1.getROIs()
#            rois2 = mca2.getROIs()
#            roi1,roi2 = rois1
#        sleep(0.25)
#        mca1.setROIs(roi1, roi2)
#        mca2.setROIs(roi1, roi2)
#        sleep(1)
#        ct.reinit()
#    while(mca1.state() in [DevState.DISABLE,DevState.UNKNOWN] or mca2.state() in [DevState.DISABLE,DevState.UNKNOWN]):
#        sleep(1)
#    if mca1.state() == DevState.FAULT or mca2.state() == DevState.FAULT and recursive <=3:
#        setMAP(recursive = recursive + 1)
#    else:
#        #print "DxMap Ready for service."
#        pass
#    return

def setSTEP_old(recursive = 0):
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
    except KeyboardInterrupt, tmp:
        raise tmp
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
    #if rois1 <> mca1.getROIs():
    #    #mca1.DP.setroisfromlist(rois1)
    #    mca1.setROIs(roi1, roi2)
    #if rois2 <> mca2.getROIs():
    #    mca2.setROIs(roi1, roi2)
    #    #mca2.DP.setroisfromlist(rois2)
    #2 lines below replace lines above for tests
    mca1.setROIs(roi1, roi2)
    mca2.setROIs(roi1, roi2)
    sleep(0.25)
    while(mca1.state() in [DevState.DISABLE,DevState.UNKNOWN] or mca2.state() in [DevState.DISABLE,DevState.UNKNOWN]):
        sleep(1)
    if mca1.state() == DevState.FAULT or mca2.state() == DevState.FAULT and recursive <=3:
        setSTEP(recursive = recursive + 1)
    else:
        pass
        #print "DxMap Ready for service."
    sleep(0.25)
    ct.reinit()
    return
