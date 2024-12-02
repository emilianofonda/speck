from __future__ import print_function
import PyTango
from PyTango import DevState, DeviceProxy,DevFailed
from time import sleep
import time
import numpy, tables

class pandabox_timebase:
    def __init__(self,label="",user_readconfig=[],timeout=10.,deadtime=0.1,config={}, identifier=""):
        """
        this class interface with pandabox for the timebase part.
        This version consider only one timebase triggers out.
        
        Some of the parameters are set by default and cannot be changed.

        firstPulseDelay has to be >0. It is set to 0.001 by default, but it may be modified.

        pulsePeriod must be larger than pulseWidth
        
        (pulsePeriod-pulseWidth) is a time in ms that should fit with the GateDownTime in SAI and other slave cards
        it is a time when gate goes down between gates up. Hint: use it close to 2ms.

        dt=1s ==>  GateUpTime=0.998 ms  and GateDownTime=2 ms on PulseGenerator.

        config is a dictionary containing the following kw informations, name of kw must correspond to existing attributes:
        
        Channels are named from 0 to 7.

        mode: 0 or 1 (they stand for "TIME","POSITION")
        inputCoder : a number 1 to 4 for encoder inputs 1,2,3,and 4.
        firstPulseDelay : first delay in train of pulses (ms or axis units) >0
        pulsePeriod : is the integration time (ms or axis units)
        gateDownTime : the actual gateUpTime is pulsePeriod-gateDownTime (hint: use 2ms as gate down time) 
        sequenceLength: number of pulses (set it to +1 respect to what you would like to measure...)

        example:
        config={"mode":0,"inputCoder":1,"firstPulseDelay":0.001,"pulsePeriod":1000,
        "gateDownTime":2}

        """
        self.config = config
        self.init_user_readconfig=[]
        self.user_readconfig=[]
        self.label=label
        self.DP=DeviceProxy(label)
        self.deadtime=deadtime
        self.timeout=timeout
        self.DP.set_timeout_millis(int(self.timeout*1000))
        if identifier =="":
            self.identifier = "pandabox_timebase_0"
        else:
            self.identifier = identifier
        return

    def init(self):
        self.DP.set_timeout_millis(int(self.timeout*1000))
        sleep(1)
        self.DP.command_inout("Init")
        while(self.state() in [DevState.UNKNOWN, DevState.DISABLE]):
            sleep(self.deadtime)
        return

    def reinit(self):
        return

    def __repr__(self):
        repr =  "Device name = %s\n" % self.label
        repr += "State       = %s\n"%self.DP.state()
        return repr
                    
    def __call__(self,x=None):
        print(self.__repr__())
        return self.state()                              

    def state(self):
        return self.DP.state()

    def status(self):
        return self.DP.status()
        
    def prepare(self,dt=1,NbFrames=1,nexusFileGeneration=False,stepMode=False,upperDimensions=()):
        cKeys = self.config.keys()
        if stepMode:
#Careful ! modification to be checked, it was =1 and working last week :-(
#           self.config["sequenceLength"] = 2
#Works again as it should: 26/10/2023 :-)
            self.config["sequenceLength"] = 1 
        else:
# the +10 comes as a workaround for pulsecounting cpt3
            self.config["sequenceLength"] = NbFrames + 1 + 10
        #Remove GateDownTime:
        self.config["pulseWidth"] = dt * 1000. - self.config["gateDownTime"]
        self.config["pulsePeriod"] = dt * 1000.
        for i in [j for j in cKeys if j not in ["gateDownTime",]]:
            try:
                if i in cKeys and self.config[i]!=self.DP.read_attribute(i).value:
                    self.DP.write_attribute(i,self.config[i])
            except:
                raise
        return self.DP.prepare()

    def prepareHDF(self, handler, HDFfilters = tables.Filters(complevel = 1, complib='zlib')):
        """the handler is an already opened file object"""
#Write down contextual data
        ll = numpy.array(["%s = %s"%(i,str(self.config[i])) for i in self.config.keys()])
        outGroup = handler.create_group("/context",self.identifier)
        outGroup = handler.get_node("/context/"+self.identifier)
        handler.create_carray(outGroup, "config", title = "config",\
        shape = numpy.shape(ll), atom = tables.Atom.from_dtype(ll.dtype), filters = HDFfilters)
        outNode = handler.get_node("/context/"+self.identifier+"/config")
        outNode[:] = ll
        return


    def start(self,dt=1):
        if self.state()!=DevState.RUNNING:
            self.DP.command_inout("Start")
        else:
            raise Exception("Trying to start %s when already in RUNNING state"%self.label)
        return self.state()
        
    def stop(self):
        if self.state()==DevState.RUNNING:
            self.DP.command_inout("Abort")
        return self.state()

    def wait(self):
        t0=time.time()
        while self.state() != DevState.RUNNING and time.time()-t0 < self.timeout:
            sleep(self.deadtime)
        while self.state() == DevState.RUNNING:
            sleep(self.deadtime)
        return

    def read(self):
        return []

    def count(self,dt=1):
        """This is a master device without output. A pure time base."""
        self.prepare(dt,NbFrames=1,nexusFileGeneration=False)
        self.start(dt)
        self.wait()
        return 

class pandabox_udp_timebase:
    def __init__(self,label="",user_readconfig=[],timeout=10.,deadtime=0.1,config={}, identifier=""):
        """
        this class interface with pandabox for the udp timebase part.
        
        there is no configuration needed apart the number of events expected.
        
        The first run after a device complete restart may report one lost count (the first)

        example:
        config={}

        """
        self.config = config
        self.init_user_readconfig=[]
        self.user_readconfig=[]
        self.label=label
        self.DP=DeviceProxy(label)
        self.deadtime=deadtime
        self.timeout=timeout
        self.DP.set_timeout_millis(int(self.timeout*1000))
        if identifier =="":
            self.identifier = "pandabox_udp_timebase_0"
        else:
            self.identifier = identifier
        return

    def init(self):
        self.DP.set_timeout_millis(int(self.timeout*1000))
        sleep(1)
        self.DP.command_inout("Init")
        while(self.state() in [DevState.UNKNOWN, DevState.DISABLE]):
            sleep(self.deadtime)
        return

    def reinit(self):
        return

    def __repr__(self):
        repr =  "Device name = %s\n" % self.label
        repr += "State       = %s\n"%self.DP.state()
        return repr
                    
    def __call__(self,x=None):
        print(self.__repr__())
        return self.state()                              

    def state(self):
        return self.DP.state()

    def status(self):
        return self.DP.status()
        
    def prepare(self,dt=1,NbFrames=1,nexusFileGeneration=False,stepMode=False,upperDimensions=()):
        self.DP.start(NbFrames)
        sleep(self.deadtime)
        return self.state()

    def prepareHDF(self, handler, HDFfilters = tables.Filters(complevel = 1, complib='zlib')):
        """the handler is an already opened file object"""
#Write down contextual data
        ll = numpy.array(["%s = %s"%(i,str(self.config[i])) for i in self.config.keys()])
        outGroup = handler.create_group("/context",self.identifier)
        outGroup = handler.get_node("/context/"+self.identifier)
        handler.create_carray(outGroup, "config", title = "config",\
        shape = numpy.shape(ll), atom = tables.Atom.from_dtype(ll.dtype), filters = HDFfilters)
        outNode = handler.get_node("/context/"+self.identifier+"/config")
        outNode[:] = ll
        return

    def start(self,dt=1):
        """ This is a slave device, the start command does nothing, make it ready with the prepare command"""
        return self.state()
        
    def stop(self):
        if self.state()==DevState.RUNNING:
            self.DP.command_inout("Abort")
        return self.state()

    def wait(self):
        t0=time.time()
        while self.state() != DevState.RUNNING and time.time()-t0 < self.timeout:
            sleep(self.deadtime)
        while self.state() == DevState.RUNNING:
            sleep(self.deadtime)
        return


class pandabox_udp_sampler:
    def __init__(self,label="",user_readconfig=[],timeout=10.,deadtime=0.1,config={}, identifier=""):
        """
        this class interface with the sampler device that receives triggers from the udp timebase.
        Several attibutes may be sampled over a udp trigger.
        
        There is no configuration needed at the beginning, but attributes to be sampled require
        specification at start.
        
        example:
        config={"attribute_names":{"energy":"d03-1-c03/op/mono1/energy",}, "read_error_threshold" : 10.}
        
        The attribute_names dictionary has nx_names as keys and attribute Tango adresses as values

        pandabox_udp_timebase.start()

        The device expects a configuration message at start that is provided by the class.
        The raw config is:
        
        [sampler]
        attribute:
        name = d03-1-c03/op/mono1/energy
        nx_name = energy
        nx_sampling_name = energy_sampling_time
        read_error_threshold = 10.000000
        -
        other attributes may be chainded below separated with a dash and the sequence ends with a dash

        Data is saved in NX files to be read and transferred to output.
        """
        self.config = config
        self.init_user_readconfig=[]
        self.user_readconfig=[]
        self.label=label
        self.DP=DeviceProxy(label)
        self.deadtime=deadtime
        self.timeout=timeout
        self.DP.set_timeout_millis(int(self.timeout*1000))
        self.attribute = {"attribute":"","nx_name":"","read_error_threshold":10.0}
        if identifier =="":
            self.identifier = "sampler_udp_0"
        else:
            self.identifier = identifier
        return

    def init(self):
        self.DP.set_timeout_millis(int(self.timeout*1000))
        sleep(1)
        self.DP.command_inout("Init")
        while(self.state() in [DevState.UNKNOWN, DevState.DISABLE]):
            sleep(self.deadtime)
        return

    def reinit(self):
        return

    def __repr__(self):
        repr =  "Device name = %s\n" % self.label
        repr += "State       = %s\n"%self.DP.state()
        return repr
                    
    def __call__(self,x=None):
        print(self.__repr__())
        return self.state()                              

    def state(self):
        return self.DP.state()

    def status(self):
        return self.DP.status()
        
    def prepare(self,dt=1,NbFrames=1,nexusFileGeneration=False,stepMode=False,upperDimensions=()):
        """This first version is made for one single attribute, but several can be sampled together"""
        if self.attribute["attribute"] != "" and NbFrames>1:
            __start_string = ("[sampler]","attribute:")
            __start_string += ("name = %s" % (self.attribute["attribute"]),)
            __start_string += ("nx_name = %s" % (self.attribute["nx_name"]),)
            __start_string += ("nx_sampling_name = %s_sampling_time" % (self.attribute["nx_name"]),)
            __start_string += ("read_error_threshold = %8.6f" % (self.attribute["read_error_threshold"]),)
            __start_string += ("-",)
            self.DP.configuration = __start_string
            sleep(self.deadtime)
            self.DP.start(NbFrames)
            sleep(self.deadtime)
        return self.state()

    def prepareHDF(self, handler, HDFfilters = tables.Filters(complevel = 1, complib='zlib')):
        """the handler is an already opened file object"""
#Write down contextual data
        ll = numpy.array(["%s = %s"%(i,str(self.config[i])) for i in self.config.keys()])
        outGroup = handler.create_group("/context",self.identifier)
        outGroup = handler.get_node("/context/"+self.identifier)
        handler.create_carray(outGroup, "config", title = "config",\
        shape = numpy.shape(ll), atom = tables.Atom.from_dtype(ll.dtype), filters = HDFfilters)
        outNode = handler.get_node("/context/"+self.identifier+"/config")
        outNode[:] = ll
        return

        
    def stop(self):
        if self.state()==DevState.RUNNING:
            self.DP.command_inout("Abort")
        return self.state()

    def wait(self):
        t0=time.time()
        while self.state() != DevState.RUNNING and time.time()-t0 < self.timeout:
            sleep(self.deadtime)
        while self.state() == DevState.RUNNING:
            sleep(self.deadtime)
        return


class pandabox_dataviewer:
    def __init__(self,label="",user_readconfig=[],
    timeout=3.,deadtime=0.1, 
    FTPclient="",FTPserver="",
    spoolMountPoint="", config={},identifier=""
    ):
        """
        This class interfaces with the PandaBox DataViewer at the sole intent of recording encoder values.
        Its purpose is to replace the bufferedCounter module (aka the underlying NI6602 card) in the pulse type data recording.
        The unit is slave, the triggering mode must be a priori set correctly. In this implementation the card has the same pandabox as a trigger generator.

        The FTPclient and FTPserver are maintained for backward compatibility but they are not used.
        Let them as blank strings and expect them to be removed.

        config is a dictionary containing the following kw informations, name of kw must correspond to existing attributes:

        GateDownTime: this value in ms (not seconds!) is used to correct the integration time to the real live time (integrationTime-GateDownTime*1000)
        
        integrationTime: used for calculating averages (Beware: I use seconds, card use ms) 
        Beware : the GateDownTime is removed from this value so the 10ms acquisition with a 0.1ms gatedowntime results in a 9.99ms integration every 10ms
        
        nexusFileGeneration: False or True
        nexusTargetPath: path to spool as '\\\\srv5\\spool1\\sai' remark double backlashes if on windows...
        nexusNbAcqPerFile: self explaining
        totalNbPoint: how many points you want to read it's the captureFrameNumber attribute
        bufferDepth: usually 100, it's the infinite mode buffer depth, you arrange to empty it about every second max(1,int(1/delta_t))

        identifier is a string, it is used in final nexus files

        the enables of the encoders must be set by hand or via the config as below for cod1

###################
        
        Two special config keywords deserve description and are NECESSARY in the config:
        
        The first determine the command to be used to set the device in the good triggering mode:
        
        set_trigger_source_command:"AcqFromFlyscan"

        The second is the value expected for the good triggering mode. 
        If this is not the case and only in this case the command above is executed at prepare.
        
        trigger_source:"PULSE1.OUT"

        The values of these two parameters (one an attribute, the other a dynamically defined command) 
        are subject to modifications depending on the configuration and cannot be determined in advance.

###################

        The encoder names are guessed from the GetCaptureInfo command, but the fact they are in enable or disable state
        is let as it is unless explicitly stated in the config. You may want to enforce an encoder to be active or inactive via the config.
        Disabled encoders are not recorded nor taken into account at any level.

        example:
        config={"integrationTime":0.01,"nexusFileGeneration":False,
        "nexusTargetPath":'\\\\srv5\\spool1\\panda_dataviewer',"nexusNbAcqPerFile":1000,"totalNbPoint":1000,
        "bufferDepth":100,enableDatasetcod1:True,set_trigger_source_command:"AcqFromFlyscan",trigger_source:"PULSE1.OUT"}

        """
        self.config = config
#If there are no attributes to save, user_readconfig is set to []
        self.init_user_readconfig=user_readconfig
        self.user_readconfig=user_readconfig
        self.label=label
        self.DP=DeviceProxy(label)
        self.identifier = identifier
        self.GateDownTime=GateDownTime
        
#FTP is not used. Values to be removed in future pulse versions
        self.FTPclient = None
        self.FTPserver = None

        self.spoolMountPoint=spoolMountPoint
        self.channels=[]
        self.channels_labels=[]
        self.deadtime=deadtime
        self.timeout=timeout
        self.DP.set_timeout_millis(int(self.timeout*1000))

        #encoders_properties = self.DP.get_property("CaptureRegisterConfig")["CaptureRegisterConfig"]
        encoders_properties = [i.split(";") for i in self.DP.GetCaptureInfo()]
        for i in encoders_properties:
            self.channels.append([j[j.find(":")+1:] for j in i if j.startswith("NAME")][0])

        return

    def init(self):
        self.DP.set_timeout_millis(int(self.timeout*1000))
        sleep(1)
        self.DP.command_inout("Init")
        while(self.state() in [DevState.UNKNOWN, DevState.DISABLE]):
            sleep(1)
        return

    def reinit(self):
        self.FTPclient = None
        self.FTPserver = None
        self.DP.set_timeout_millis(int(self.timeout*1000))

        encoders_properties = self.DP.get_property("CaptureRegisterConfig")["CaptureRegisterConfig"]
        
        self.channels=[i.split(":")[0] for i in encoders_properties]
        for i in countersProp:
            self.channels.append([j.split(":")[-1] for j in i if j.lower().startswith("name")][0])
        return

    def __repr__(self):
        repr =  "Device name = %s\n" % self.label
        repr += "State       = %s\n"%self.DP.state()
        fmtCh = "%s, "*len(self.channels)
        repr += "Channels are = " + fmtCh%tuple(self.channels) + "\n"
        return repr
                    
    def __call__(self,x=None):
        print(self.__repr__())
        return self.state()                              

    def state(self):
        return self.DP.state()

    def status(self):
        return self.DP.status()
        
    def startFTP(self):
        """Unused"""
        return

    def stopFTP(self):
        """Unused"""
        return

    def prepare(self,dt=1,NbFrames=1,nexusFileGeneration=False,stepMode=False,upperDimensions=()):
        self.upperDimensions=upperDimensions

        if self.DP.state() == DevState.FAULT:
            self.DP.init()

        cKeys = self.config.keys()

#Check triggering configuration
#       set_trigger_source_command:"AcqFromFlyscan"
#       trigger_source:"PULSE1.OUT"
        if self.DP.triggerSource != self.config["trigger_source"]:
            self.DP.command_inout(self.config["set_trigger_source_command"])
        self.wait()
        if nexusFileGeneration:
            self.config["nexusFileGeneration"] = True
            self.DP.NexusResetBufferIndex()
            #Auto delete remaining files!!! this avoids aborting, but it is a potential risk.
            os.system("rm %s/*.%s"%(self.spoolMountPoint,"nxs"))
        else:
            self.config["nexusFileGeneration"] = False
#Remove GateDownTime (this card works in seconds and GateDown is always in ms): 
        self.config["integrationTime"] = dt*1000 - self.GateDownTime 
        sleep(self.deadtime)
        self.DP.captureFrameNumber=NbFrames
        reloadAtts = self.DP.get_attribute_list()
#Some Attributes doesn't exist or exist depending on mode or external/internal time base
#So we protect checking the actual Atts list
        for kk in [i for i in cKeys if not i in ["nexusFileGeneration","triggerSource","integrationTime","captureFrameNumber"] \
            and i in reloadAtts and self.config[i]!=self.DP.read_attribute(i).value]:
            self.DP.write_attribute(kk,self.config[kk])

        return self.start()

    def start(self,dt=1):
        if self.state() not in [DevState.RUNNING,DevState.FAULT,DevSate.INIT]:
            self.DP.command_inout("StartCapture")
        else:
            raise Exception("Trying to start %s when in %s state"%(self.label,self.state())
        return self.state()
        
    def stop(self):
        if self.state()==DevState.RUNNING:
            try:
                self.DP.command_inout("StopCapture")
            except DevFailed:
                self.DP.command_inout("AbortCapture")
            finally:
                return self.state()
        else:
            return self.state()

    def wait(self):
        while self.state() in [DevState.RUNNING, DevState.UNKNOWN, DevState.INIT]:
            sleep(self.deadtime)
        return

    def read(self):
        """This returns the last read value of all encoders in attribute"""
        return []
        #return [i.value for i in self.DP.read_attributes(self.channels)]

    def readBuffer(self):
        """This returns an ordered matrix (following list of channels) of all encoders"""
#Please modify this to use read_attributes.
        return [self.DP.read_attribute(i).value for i in self.channels]

################# Worked until here down is not yet modified

    def count(self,dt=1):
        """This is a slave device, but it can be useful to test it with a standalone count
        This count function is used for debug only. It could work if the card does not need an external trigger"""
        self.prepare(dt,NbFrames=1,nexusFileGeneration=False)
        #self.start()
        self.wait()
        #for i in zip(self.user_readconfig,self.read()):
        #    print i[0].name+"="+i[0].format%i[1]
        return self.readBuffer()

    def prepareHDF(self, handler, HDFfilters = tables.Filters(complevel = 1, complib='zlib')):
        """the handler is an already opened file object"""
        ShapeArrays = (self.DP.totalnbpoint,) + tuple(self.upperDimensions)
        handler.create_group("/data/", self.identifier)
        outNode = handler.get_node("/data/" + self.identifier)
        for s in self.channels:
            handler.create_carray(outNode, "%s" % s, title = "%s" % s,\
            shape = ShapeArrays, atom = tables.Float32Atom(), filters = HDFfilters)
#Write down contextual data
        ll = numpy.array(["%s = %s"%(i,str(self.config[i])) for i in self.config.keys()])
        outGroup = handler.create_group("/context",self.identifier)
        outGroup = handler.get_node("/context/"+self.identifier)
        handler.create_carray(outGroup, "config", title = "config",\
        shape = numpy.shape(ll), atom = tables.Atom.from_dtype(ll.dtype), filters = HDFfilters)
        outNode = handler.get_node("/context/"+self.identifier+"/config")
        outNode[:] = ll
        return

    def saveData2HDF(self, handler, wait=True,upperIndex=(),reverse=1):
        """the handler is an already opened file object
        The function will not open nor close the file to be written.

        This version uses the buffered data through TANGO
        The upperIndex is used when storing data of nD maps, it has nD-1 elements
        reverse is used to save date reversed if in azigzag scan. Can be 1 or -1."""
#Calculate the number of files expected
        #NOfiles = self.NbFrames / self.DP.streamnbacqperfile
# Get the list of files to read and wait for the last to appear (?)
#One after the other: open, transfert data, close and delete
        if reverse not in [-1,1]:
            reverse = 1
        buffer = self.readBuffer()
        if upperIndex != ():
            fmt = "%i," * len(tuple(upperIndex))
            stringIndex = fmt % tuple(upperIndex)
        for i in range(len(buffer)):
            outNode = handler.get_node("/data/" + self.identifier + "/%s" % self.channels[i])
            if upperIndex == ():
                outNode[:] = buffer[i]
            else:
                exec("outNode[:,%s]=buffer[i][::reverse]"%(stringIndex))
        del buffer
        return


