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
        #Careful ! modification to be checked, it was =1 and working last week
            self.config["sequenceLength"] = 2 
        else:
            self.config["sequenceLength"] = NbFrames + 1 
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


class udp_sampler:
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



