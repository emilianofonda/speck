from time import time, sleep
ControlSystem = DeviceProxy("tango/devadmin/ControlSystemMonitor.1")

def StopServer(speckInstance, timeOut=10,delay=5):
    """There is a time for joy and a time for sorrow,
    There is a time to live and a time to die
    ... this is the time to kill ... a DeviceServer
    """
    if "label" in dir(speckInstance):
        label = speckInstance.label
    elif "name" in dir(speckInstance):
        label = speckInstance.name()
    else:
        raise Exception("Error: trying StartServer on non compatible object.")
    ControlSystem.killDevices([label,])
    t0=time()
    while(time()-t0<timeOut):
        try:
            sleep(0.1)
            st = speckInstance.state()
        except:
            break
    sleep(delay)
    return

def StartServer(speckInstance, timeOut=10,delay=0,retry=True):
    """Use the TANGO database to start a speckInstance that died."""
    if "label" in dir(speckInstance):
        label = speckInstance.label
    elif "name" in dir(speckInstance):
        label = speckInstance.name()
    else:
        raise Exception("Error: trying StartServer on non compatible object.")
    ControlSystem.startDevices([label,])
    t0=time()
    while(time()-t0<timeOut):
        try:
            sleep(0.1)
            st = speckInstance.state()
            break
        except:
            pass
    try:
        st = speckInstance.state()
    except:
        if retry:
            StartServer(speckInstance, timeOut=timeOut, delay=delay,retry=False)
        else:
            raise Exception("StartServer: %s can't start."%label)
    sleep(delay)
    return

#def StartServer(speckInstance):
#    """Use the TANGO database to start a speckInstance that died."""
#    if "label" in dir(speckInstance):
#        label = speckInstance.label
#    elif "name" in dir(speckInstance):
#        label = speckInstance.name()
#    else:
#        raise Exception("Error: trying StartServer on non compatible object.")
#    db=PyTango.Database()
#    SId = db.get_device_info(label).ds_full_name
#    for server in db.get_host_list():
#        if SId in db.get_host_server_list(server).value_string:
#            SHost = server
#    WeAdmin = DeviceProxy("tango/admin/"+SHost)
#    WeAdmin.DevStart(SId)
#    return

#def StopServer(speckInstance):
#    """Use the TANGO database to gently stop a speckInstance."""
#    if "label" in dir(speckInstance):
#        label = speckInstance.label
#    elif "name" in dir(speckInstance):
#        label = speckInstance.name()
#    else:
#        raise Exception("Error: trying StartServer on non compatible object.")
#    db=PyTango.Database()
#    SId = db.get_device_info(label).ds_full_name
#    for server in db.get_host_list():
#        if SId in db.get_host_server_list(server).value_string:
#            SHost = server
#    WeAdmin = DeviceProxy("tango/admin/"+SHost)
#    WeAdmin.DevStop(SId)
#    return

#def HardKillServer(speckInstance):
#    """There is a time for joy and a time for sorrow,
#    There is a time to live and a time to die
#    ... this is the time to kill ... a DeviceServer
#    HardKillServer() needs a DeviceProxy or a speck standard object"""
#    if "label" in dir(speckInstance):
#        label = speckInstance.label
#    elif "name" in dir(speckInstance):
#        label = speckInstance.name()
#    else:
#        raise Exception("Error: trying StartServer on non compatible object.")
#    db=PyTango.Database()
#    SId = db.get_device_info(label).ds_full_name
#    SClass = db.get_device_info(label).class_name
#    Spid = db.get_device_info(label).pid
#    for server in db.get_host_list():
#        if SId in db.get_host_server_list(server).value_string:
#            SHost = server
#    WeSysAdmin = DeviceProxy("tango/sysadmin/"+SHost)
#    WeSysAdmin.KillProcessByPID(Spid)
#    return

#def StartServer(speckInstance):
#    """Use the TANGO database to start a speckInstance that died."""
#    if "label" in dir(speckInstance):
#        label = speckInstance.label
#    elif "name" in dir(speckInstance):
#        label = speckInstance.name()
#    else:
#        raise Exception("Error: trying StartServer on non compatible object.")
#    db=PyTango.Database()
#    SId = db.get_device_info(label).ds_full_name
#    for server in db.get_host_list():
#        if SId in db.get_host_server_list(server).value_string:
#            SHost = server
#    WeAdmin = DeviceProxy("tango/admin/"+SHost)
#    WeAdmin.DevStart(SId)
#    return

#def StopServer(speckInstance):
#    """Use the TANGO database to gently stop a speckInstance."""
#    if "label" in dir(speckInstance):
#        label = speckInstance.label
#    elif "name" in dir(speckInstance):
#        label = speckInstance.name()
#    else:
#        raise Exception("Error: trying StartServer on non compatible object.")
#    db=PyTango.Database()
#    SId = db.get_device_info(label).ds_full_name
#    for server in db.get_host_list():
#        if SId in db.get_host_server_list(server).value_string:
#            SHost = server
#    WeAdmin = DeviceProxy("tango/admin/"+SHost)
#    WeAdmin.DevStop(SId)
#    return

