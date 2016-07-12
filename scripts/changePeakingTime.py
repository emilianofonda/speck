#This is a macro that depends on the SAMBA environment defined in speck_config...
#This code works on global objects like mca1 and mca2, it is strictly... volatile.

__XIA_files = {
0:{"PeakingTime":"0.48us",
"mca1": '\\\\deviceservers\\configFiles\\XIA-XMAP\\Canberra36\\Canberra36_pcih_048_EF4.ini',
"mca2": '\\\\deviceservers\\configFiles\\XIA-XMAP\\Canberra36\\Canberra36_pcib_048_EF4.ini'},
1:{"PeakingTime":"1.00us",
"mca1": '\\\\deviceservers\\configFiles\\XIA-XMAP\\Canberra36\\Canberra36_pcih_100_EF4.ini',
"mca2": '\\\\deviceservers\\configFiles\\XIA-XMAP\\Canberra36\\Canberra36_pcib_100_EF4.ini'},
2:{"PeakingTime":"2.00us",
"mca1": '\\\\deviceservers\\configFiles\\XIA-XMAP\\Canberra36\\Canberra36_pcih_200_EF4.ini',
"mca2": '\\\\deviceservers\\configFiles\\XIA-XMAP\\Canberra36\\Canberra36_pcib_200_EF4.ini'},
3:{"PeakingTime":"6.00us",
"mca1": '\\\\deviceservers\\configFiles\\XIA-XMAP\\Canberra36\\Canberra36_pcih_600_EF4.ini',
"mca2": '\\\\deviceservers\\configFiles\\XIA-XMAP\\Canberra36\\Canberra36_pcib_600_EF4.ini'},
}


def getMCAconfig():
    for i in sort(__XIA_files.keys()):
        print "Config (%i)  --> Peaking Time %s" % (i, __XIA_files[i]["PeakingTime"])
        print "                 mca1 --> %s" % ( __XIA_files[i]["mca1"])
        print "                 mca2 --> %s" % ( __XIA_files[i]["mca2"])
    cfg1 = mca1.DP.get_property("ConfigFile")["ConfigFile"][0]
    cfg2 = mca2.DP.get_property("ConfigFile")["ConfigFile"][0]
    print "Current config files are:"
    print "mca1 --> ", cfg1
    print "mca2 --> ", cfg2
    return


def setMCAconfig(config=-1):
    if config == -1:
        return getMCAconfig()
    elif config in __XIA_files.keys():
        mca1.DP.put_property({"ConfigFile":[__XIA_files[config]["mca1"]]})
        mca2.DP.put_property({"ConfigFile":[__XIA_files[config]["mca2"]]})
        print "Please wait, it may take long time...",
        sys.stdout.flush()
        try:
            mca1.DP.init()
        except Exception, tmp:
            print tmp
        sleep(3)
        while(mca1.state() not in [DevState.STANDBY, DevState.FAULT]):
            sleep(0.25)
        print "OK 1/2... ",
        sys.stdout.flush()
        try:
            mca2.DP.init()
        except Exception, tmp:
            print tmp
        sleep(3)
        while(mca2.state() not in [DevState.STANDBY, DevState.FAULT]):
            sleep(0.25)
        print "OK 2/2"
        sys.stdout.flush()
    else:
        print "Choice number %i is not allowed." % config
        return getMCAconfig()
    return getMCAconfig()


def setMAP():
    try:
        changeMode = mca1.DP.currentMode <> 'MAPPING' or mca2.DP.currentMode <> 'MAPPING'
        rois1 = mca1.DP.getrois()
        rois2 = mca2.DP.getrois()
    except:
        changeMode = True
    if changeMode:
        mca1.DP.set_timeout_millis(30000)
        mca2.DP.set_timeout_millis(30000)
        mca1.DP.loadconfigfile("MAP")
        mca2.DP.loadconfigfile("MAP")
        while(mca1.state() == DevState.DISABLE or mca2.state() == DevState.DISABLE):
            sleep(1)
        if rois1 <> mca1.DP.getrois():
            mca1.DP.setroisfromlist(rois1)
        if rois2 <> mca2.DP.getrois():
            mca2.DP.setroisfromlist(rois2)
        while(mca1.state() in [DevState.DISABLE,DevState.UNKNOWN] or mca2.state() in [DevState.DISABLE,DevState.UNKNOWN]):
            sleep(1)
        ct.reinit()
    return

def setSTEP():
    try:
        changeMode = mca1.DP.currentMode <> 'MCA' or mca2.DP.currentMode <> 'MCA'
        rois1 = mca1.DP.getrois()
        rois2 = mca2.DP.getrois()
    except:
        changeMode = True
    if changeMode:
        mca1.DP.set_timeout_millis(30000)
        mca2.DP.set_timeout_millis(30000)
        mca1.DP.loadconfigfile("STEP")
        mca2.DP.loadconfigfile("STEP")
        while(mca1.state() == DevState.DISABLE or mca2.state() == DevState.DISABLE):
            sleep(1)
        if rois1 <> mca1.DP.getrois():
            mca1.DP.setroisfromlist(rois1)
        if rois2 <> mca2.DP.getrois():
            mca2.DP.setroisfromlist(rois2)
        while(mca1.state() in [DevState.DISABLE,DevState.UNKNOWN] or mca2.state() in [DevState.DISABLE,DevState.UNKNOWN]):
            sleep(1)
        ct.reinit()
    return
