#This is a macro that depends on the SAMBA environment defined in speck_config...
#This code works on global objects like mca1 and mca2, it is strictly... volatile... but essential!!!!

#Employs the global object ct to retrieve the list of mca units

def XIAgetConfigFiles():
    return [i.DP.get_property("ConfigurationFiles")["ConfigurationFiles"] 
    for i in get_ipython().user_ns["ct"].mca_units]

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


def XIAsetConfigNumber(config):
    for i in ct.mca_units:
        i.DP.put_property({"SPECK_ConfigurationFileNumber":config})
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
    for i in ct.mca_units:
        try:
            i.DP.accumulate=False
        except:
            pass
    return


