#This is a macro that depends on the SAMBA environment defined in speck_config...
#This code works on global objects like mca1 and mca2, it is strictly... volatile... but essential!!!!

#Employs the global object ct to retrieve the list of mca units


from PyTango import DevState, DeviceProxy
from time import sleep

def XIAgetConfigFiles():
    return [i.DP.get_property("ConfigurationFiles")["ConfigurationFiles"] 
    for i in get_ipython().user_ns["ct"].mca_units]

def XIAviewConfigFiles():
    labels = iter([whois(i) for i in get_ipython().user_ns["ct"].mca_units])
    for cfg in XIAgetConfigFiles():
        print "\n%s:"%labels.next()
        for i in cfg:
            i3 = i.split(";")
            print "Label = %6s Mode = %8s\n    File = %s"%tuple(i3)
    return

def XIAgetConfigNumber():
    return [int(i.DP.get_property("SPECK_ConfigurationFileNumber")["SPECK_ConfigurationFileNumber"][0]) for i in get_ipython().user_ns["ct"].mca_units]


def XIAsetConfigNumber(config):
    for i in get_ipython().user_ns["ct"].mca_units:
        i.DP.put_property({"SPECK_ConfigurationFileNumber":config})
    return XIAgetConfigNumber()


def setMAP(recursive = 0):
    return setMODE(recursive, mode="MAP")

def setSTEP(recursive = 0):
    return setMODE(recursive, mode="STEP")

def setMODE(recursive = 0, mode=""):
    """Only one unique ROI is supported
    MAP corrensponds to MAPPING
    STEP corresponds to MCA"""
    mca_units = get_ipython().user_ns["ct"].mca_units
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
    for i in mca_units:
        if i.state() == DevState.FAULT:
            changeMode = True
            fault = True
            i.init()
    if changeMode:
        sleep(0.25)
        while(True in [i.state() in [DevState.DISABLE,DevState.UNKNOWN] for i in mca_units]):
            sleep(1)
    try:
        changeMode = True in [i.DP.currentMode <> cMode for i in mca_units] or \
        True in [i[0].DP.currentAlias <> i[1] for i in zip(mca_units,configs)]
    except:
        changeMode = True
        fault = True
        print RED + "Fault: mode" + RESET
    if changeMode:
        try:
            #Only one roi is set for all... this is not really OK... but...
            roi1,roi2 = mca_units[0].getROIs()
        except:
            print RED + "Fault: rois" + RESET
            fault = True
        print "Setting %s  mode" % mode
        if fault:
            for i in mca_units:
                i.init()
            sleep(1)
            while(True in [i.state() == DevState.DISABLE for i in mca_units]):
                sleep(1)
        for i in mca_units:
            i.DP.set_timeout_millis(60000)
        sleep(0.25)
        for i in zip(mca_units,configs):
            i[0].DP.loadconfigfile(i[1])
        sleep(0.25)
        while(True in [i.state() in [DevState.DISABLE,DevState.UNKNOWN] for i in mca_units]):
            sleep(1)
        if fault:
            roi1,roi2 = mca_units[0].getROIs()
        sleep(0.25)
        for i in mca_units:
            i.setROIs(roi1, roi2)
        sleep(1)
        reinit()
    while(True in [i.state() in [DevState.DISABLE,DevState.UNKNOWN] for i in mca_units]):
        sleep(1)
    if True in [i.state() == DevState.FAULT for i in mca_units] and recursive <=3:
        setMODE(recursive = recursive + 1, mode = mode)
    else:
        #print "DxMap Ready for service."
        pass
    return


