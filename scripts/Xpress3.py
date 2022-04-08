from __future__ import print_function
#ssh -X xspress3@172.19.9.17
# Xspress3 Test 1
# No file saving

import PyTango
import numpy
import time
import random
import string

X3dev = PyTango.DeviceProxy('xspress3/xspress3/xspress3.1-specific')
X3lima = PyTango.DeviceProxy('xspress3/xspress3/xspress3.1')

X3dev.set_timeout_millis(30000)

def X3ct(dt=1, n=1,deadtime =0.1,trigger="",saveData=False):
    """trigger can be:
        EXT or INT, default is INT.
        Corresponding device values are:
        EXTERNAL_TRIGGER or INTERNAL_TRIGGER"""
    # definitions
    nframes = n
    exp_time = dt # seconds

    # do not change the order of the saving attributes!
    #X3lima.write_attribute("saving_directory","/home/xspress3/data")
    X3lima.write_attribute("saving_directory","/mnt/spoolSAMBA/xsp3")
    X3lima.write_attribute("saving_format","HDf5")
    X3lima.write_attribute("saving_overwrite_policy","Abort")
    X3lima.write_attribute("saving_suffix", ".hdf")
    X3lima.write_attribute("saving_prefix","xsp3_")
    if saveData:
        X3lima.write_attribute("saving_mode","Auto_Frame")
    else:
        X3lima.write_attribute("saving_mode","Manual")
    X3lima.write_attribute("saving_managed_mode","SOFTWARE")
    X3lima.write_attribute("saving_frame_per_file", nframes)


    X3lima.write_attribute("acq_nb_frames",nframes)
    X3lima.write_attribute("acq_expo_time", exp_time)

    # INTERNAL = Internal trigger
    # EXTERNAL = TTL Veto (input TTL1)
    if string.upper(trigger) == "EXT":
        X3lima.write_attribute("acq_trigger_mode", "EXTERNAL_GATE")
    else:
        X3lima.write_attribute("acq_trigger_mode", "INTERNAL_TRIGGER")
    #X3dev.command_inout("Arm")
    #time.sleep(3)
    X3lima.command_inout("prepareAcq")
    time.sleep(deadtime)
    X3lima.command_inout("startAcq")

    lastFrame = -1
    #channel = 0
    currentFrame = -1

    while X3dev.read_attribute("acqRunning").value or currentFrame < nframes-1:
        try:
            time.sleep(deadtime)
            currentFrame=X3lima.read_attribute("last_image_ready").value
            #if currentFrame > lastFrame:
            #    lastFrame = currentFrame
            #    for channel in xrange(4):
            #        data = X3dev.command_inout("ReadScalers",[lastFrame, channel])
            #        print "Frame", lastFrame, "allevent" ,data[3],"allgood",data[4], "dt%", data[9], "dtf", data[10]
            #    #hdata = X3dev.command_inout("ReadHistogram",[lastFrame, channel])
            #    #print "hist data ",hdata
        except (KeyboardInterrupt, SystemExit) as tmp:
            print("Stopped on user request")
            X3lima.command_inout("stopAcq")
            raise tmp
        except Exception as tmp:
            print(tmp)
            
    print("Last Frame is ",lastFrame)
