import PyTango
from PyTango import DevState, DeviceProxy,DevFailed
from time import sleep
import time
import numpy, tables

class pulseGen:
    def __init__(self,label="",user_readconfig=[],timeout=10.,deadtime=0.1,config={}, identifier=""):
        """
        this class interface with pulseGen cards
        some of the parameters are set by default and cannot be changed.
        for example the approach is very reductive in prepare: only onde integration time is considered for all channels

        delayCounter is a time in ms that should fit with the GateDownTime in SAI and other slave cards
        it is a time when gate goes down between gates up.

        dt=1s ==>  GateUpTime=0.998 ms  and GateDownTime=2 ms on PulseGenerator

        config is a dictionary containing the following kw informations, name of kw must correspond to existing attributes:
        
        Channels are named from 0 to 7.

        generationType: "FINITE","CONTINUOUS,"RETRIG"
        counter0Enable : counter0,1, 2, 3... Enable it or not.
        idleStateCounter0: LOW or HIGH (use LOW please)
        initialDelay0 : first delay in train of pulses (ms)
        pulseWidthCounter0: is the integration time - delayCounter0
        pulseNumber: number of pulses (set it to +1 respect to what you would like to measure...)

        example:
        config={"generationType":"FINITE","pulseNumber":1,"counter0Enable":True,
        "initialDelay0":0,"delayCounter0":2,"pulseWidthCounter0":998}

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
            self.identifier = "pulsegenerator_0"
        else:
            self.identifier = identifier
        return

    def init(self):
        self.DP.set_timeout_millis(int(self.timeout*1000))
        sleep(1)
        self.DP.command_inout("Init")
        while(self.state() in [DevState.UNKNOWN, DevState.DISABLE]):
            sleep(1)
        return

    def reinit(self):
        return

    def __repr__(self):
        repr =  "Device name = %s\n" % self.label
        repr += "State       = %s\n"%self.DP.state()
        return repr
                    
    def __call__(self,x=None):
        print self.__repr__()
        return self.state()                              

    def state(self):
        return self.DP.state()

    def status(self):
        return self.DP.status()
        
    def prepare(self,dt=1,NbFrames=1,nexusFileGeneration=False,stepMode=False):
        cKeys = self.config.keys()
        if stepMode:
            self.config["pulseNumber"] = 2 
        else:
            self.config["pulseNumber"] = NbFrames + 1 
        #Remove GateDownTime:
        for i in range(7):
            if "counter%iEnable"%i in self.config.keys() and self.config["counter%iEnable"%i]:
                self.config["pulseWidthCounter%i"%i] = dt * 1000 - self.config["delayCounter%i"%i]
        #Protect illegal writes, in fact it can happen that enables are not set and we would like to set a value for that counter
        for i in cKeys:
            try:
                if i in cKeys and self.config[i]<>self.DP.read_attribute(i).value:
                    self.DP.write_attribute(i,self.config[i])
            except:
                raise
        return

    def prepareHDF(self, handler, HDFfilters = tables.Filters(complevel = 1, complib='zlib')):
        """the handler is an already opened file object"""
#Write down contextual data
        ll = numpy.array(["%s = %s"%(i,str(self.config[i])) for i in self.config.keys()])
        outGroup = handler.createGroup("/context",self.identifier)
        outGroup = handler.getNode("/context/"+self.identifier)
        handler.createCArray(outGroup, "config", title = "config",\
        shape = numpy.shape(ll), atom = tables.Atom.from_dtype(ll.dtype), filters = HDFfilters)
        outNode = handler.getNode("/context/"+self.identifier+"/config")
        outNode[:] = ll
        return


    def start(self,dt=1):
        if self.state()<>DevState.RUNNING:
            self.DP.command_inout("Start")
        else:
            raise Exception("Trying to start %s when already in RUNNING state"%self.label)
        return self.state()
        
    def stop(self):
        if self.state()==DevState.RUNNING:
            self.DP.command_inout("Stop")
        return self.state()

    def wait(self):
        t0=time.time()
        while self.state() <> DevState.RUNNING and time.time()-t0<self.timeout:
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

