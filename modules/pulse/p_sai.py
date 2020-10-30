import PyTango
from PyTango import DevState, DeviceProxy,DevFailed
from time import sleep
import time
import numpy, tables
import numpy as np

class sai:
    def __init__(self,label="",user_readconfig=[],
    timeout=3.,deadtime=0.1, 
    FTPclient="",FTPserver="",
    spoolMountPoint="", config={},identifier="",
    GateDownTime=2
    ):
        """
        this class interface with sai cards
        some of the parameters are set by default and cannot be changed.

        GateDownTime is a time in microseconds (let it equal to two) than reduces the total integration time,
        it is very useful to interleave average periods and should fit with the GateDownTime
        of the PulseGenerator 
        dt=1s ==>  GateUpTime=0.999 998 ms  and GateDownTime=2 microseconds on PulseGenerator

        config is a dictionary containing the following kw informations, name of kw must correspond to existing attributes:

        configurationId: integer
        frequency: value of the sampling frequency
        integrationTime: used for calculating averages (Beware: I use seconds, card use ms)
        nexusFileGeneration: False or True
        nexusTargetPath: path to spool as '\\\\srv5\\spool1\\sai' remark double backlashes if on windows...
        nexusNbAcqPerFile: self explaining
        dataBufferNumber: how many points you want to read
        statHistoryBufferDepth: useful in our case for reading data from buffer, so set it equal to dataBufferNumber
        if this is reasonably small (some thousands is OK)

        Specify identifier!  If more than one sai is used in speck it can be wise to use a non empty identifier to tell which is which 
        when doing a scan or a ct. identifier is a string. It is used when saving in HDF fiiles !!!
        

        example:
        config={"configurationId":3,"frequency":10000,"integrationTime":1,"nexusFileGeneration":False,
        "nexusTargetPath":'\\\\srv5\\spool1\\sai',"nexusNbAcqPerFile":1000,"dataBufferNumber":1,
        "statHistoryBufferDepth":1000}

        """
        self.config = config
        #The following line is used to adapt frequency to card capabilities
        #Contextual data may be affected, to be verified.
        try:
            self.stored_frequency = self.config["frequency"]
        except:
            self.stored_frequency = 1e5
        self.init_user_readconfig=user_readconfig
        self.label=label
        self.DP=DeviceProxy(label)
        if identifier <> "":
            self.identifier = identifier
        else:
            self.identifier = "ADC"
        self.GateDownTime=GateDownTime
        if FTPclient <> "":
            self.FTPclient = DeviceProxy(FTPclient)
        else:
            self.FTPclient = None
        if FTPserver <> "":
            self.FTPserver = DeviceProxy(FTPserver)
        else:
            self.FTPserver = None
        self.spoolMountPoint = spoolMountPoint
        self.channels = []
        self.channels_labels = []
        self.deadtime = deadtime
        self.timeout = timeout
        self.DP.set_timeout_millis(int(self.timeout*1000))
        self.channels = [i for i in self.DP.get_attribute_list() if i.startswith("averagechannel")]
        self.bufferedChannels = [i for i in self.DP.get_attribute_list() if i.startswith("historizedchannel")]
        self.user_readconfig = [self.DP.get_attribute_config(i) for i in self.channels]
        self.numChan = len(self.user_readconfig)
        for i in range(self.numChan):
            self.user_readconfig[i].label = self.identifier + "_" + self.user_readconfig[i].label
            self.user_readconfig[i].name = self.identifier + "_" + self.user_readconfig[i].name

        self.dark = self.readDark()
           
#The card needs a double of points in step mode !!!! to be investigated!!!
#this has to be managed in pulsegen and inside the sai module
#the effect on other cards has to be investigated
        self.stepMode=False
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
        
    def startFTP(self):
        if self.FTPclient:
            if self.FTPserver and self.FTPserver.state() <> DevState.RUNNING:
                raise Exception("FTP server %s is not running. Starting client is useless. Please start it and retry.")%self.FTPserver.name
            return self.FTPclient.start()
        else:
            raise Exception("%s: You should define an FTP client first."%self.DP.name)

    def stopFTP(self):
        if self.FTPclient:
            return self.FTPclient.stop()
        else:
            raise Exception("%s: You should define an FTP client first."%self.DP.name)

    def prepare(self,dt=1,NbFrames=1,nexusFileGeneration=False,stepMode=False,upperDimensions=()):
        self.upperDimensions = upperDimensions
        cKeys = self.config.keys()
        if self.DP.configurationId <> self.config["configurationId"]:
            self.DP.write_attribute("configurationId",self.config["configurationId"])
        self.wait()
        #if nexusFileGeneration:
        #    self.config["nexusFileGeneration"] = True
        #    self.DP.NexusResetBufferIndex()
        #    #Auto delete remaining files!!! this avoids aborting, but it is a potential risk.
        #    os.system("rm %s/*.%s"%(self.spoolMountPoint,"nxs"))
        #Use FTPclient cleanup instead!
        #else:
        #    self.config["nexusFileGeneration"] = False
        #Hard remove nexus files from ADC
        self.config["nexusFileGeneration"] = False
        #Remove GateDownTime: 
        self.config["integrationTime"]=dt * 1000 - self.GateDownTime
        if stepMode:
            self.stepMode = True
            self.config["dataBufferNumber"] = NbFrames 
            self.config["statHistoryBufferDepth"] = NbFrames 
        else:
            self.stepMode = False
            self.config["dataBufferNumber"] = NbFrames 
            self.config["statHistoryBufferDepth"] = NbFrames 
        #Taking into account hardware limits
        if dt * self.config["frequency"] > 1.0e5:
            self.stored_frequency = self.config["frequency"]
            self.config["frequency"] = 1.0e5/dt
        reloadAtts = self.DP.get_attribute_list()
        for kk in [i for i in cKeys if i<> "configurationId" and self.config[i]<>self.DP.read_attribute(i).value]:
            self.DP.write_attribute(kk,self.config[kk])
        self.start()
        return

    def start(self,dt=1):
        if self.state() <> DevState.RUNNING:
            if self.FTPclient and self.FTPclient.state()<>DevState.RUNNING:
                self.FTPclient.start()
            self.DP.command_inout("Start")
        else:
            raise Exception("Trying to start %s when already in RUNNING state"%self.label)
        return self.state()
        
    def stopAcq(self):
        self.config["frequency"] = self.stored_frequency
        if self.state()==DevState.RUNNING:
            try:
                self.DP.command_inout("Stop")
            except DevFailed:
                self.DP.command_inout("Abort")
        return self.state()

    def stop(self):
        #Version change: Abort becomes Abort. kept for compatibility 5/9/2014
        self.config["frequency"] = self.stored_frequency
        if self.state()==DevState.RUNNING:
            try:
                self.DP.command_inout("Stop")
            except DevFailed:
                self.DP.command_inout("Abort")
#It is not necessary to stop the FTP client, 
#since it will clean up the remote spool and this is fine
#Code below has been commented
        #if self.FTPclient and self.FTPclient.state() == DevState.RUNNING:
        #    self.FTPclient.stop()
        return self.state()
    
    def preCount(self, dt=1):
        if self.DP.integrationTime <> dt * 1000 - self.GateDownTime:
            self.DP.integrationTime = dt * 1000 - self.GateDownTime
        return

#    def postCount(self, dt=1)
#        return

    def wait(self):
        while self.state() in [DevState.RUNNING, DevState.UNKNOWN, DevState.INIT]:
            sleep(self.deadtime)
        return

    def read(self):
        return [i[0].value - i[1] for i in zip(self.DP.read_attributes(self.channels),self.dark)]

    def readBuffer(self):
        if self.stepMode:
            return [np.array(self.DP.read_attribute(i[0]).value[::2]) - i[1] for i in zip(self.bufferedChannels, self.dark)]
        else:
            return [np.array(self.DP.read_attribute(i[0]).value) - i[1] for i in zip(self.bufferedChannels, self.dark)]

    def count(self,dt=1):
        """This is a slave device, but it can be useful to test it with a standalone count
        This count function is used for debug only. It could work if the card does not need an external trigger"""
        self.prepare(dt,NbFrames=1,nexusFileGeneration=False)
        self.start()
        self.wait()
        for i in zip(self.user_readconfig,self.read()):
            print i[0].name+"="+i[0].format%i[1]
        return

    def writeDark(self):
        """Use it after one dark count to store dark counter values."""
        self.clearDark()
        dark = self.read()
        #print "dark values are:", dark
        self.DP.put_property({'SPECK_DARK_VALUES': map(str, dark)})
        return self.readDark()
        
    def readDark(self):
        """Reload dark values from device to python object and then return it."""
        dark = self.DP.get_property("SPECK_DARK_VALUES")["SPECK_DARK_VALUES"]
        #print dark
        if dark == []:
            self.DP.put_property({'SPECK_DARK_VALUES':['0',] * len(self.user_readconfig)})
            dark = ['0',] * len(self.user_readconfig)
        elif len(dark) > len(self.user_readconfig):
            print "%s WARNING: dark current stored in device has wrong length: tail is cut."%self.label
            dark = dark[:len(self.user_readconfig)]
        elif len(dark) < len(self.user_readconfig):
            print "%s WARNING: dark current stored in device has wrong length: adding zeros."%self.label
            dark = dark + ['0',] * (len(self.user_readconfig)-len(dark))
        elif len(dark) == len(self.user_readconfig):
            pass
            #print "dark values read from device %s"%self.label
        self.dark = map(float, dark)
        return self.dark

    def clearDark(self):
        self.DP.put_property({'SPECK_DARK_VALUES':['0',] * len(self.user_readconfig)})
        self.dark = ['0',] * len(self.user_readconfig)
        return self.readDark()
        
    def prepareHDF(self, handler, HDFfilters = tables.Filters(complevel = 1, complib='zlib'),upperIndex=()):
        """the handler is an already opened file object"""
        if self.stepMode:
            ShapeArrays = (self.DP.dataBufferNumber/2,)+ tuple(self.upperDimensions)
        else:
            ShapeArrays = (self.DP.dataBufferNumber,)+ tuple(self.upperDimensions)
        handler.createGroup("/data/", self.identifier)
        outNode = handler.getNode("/data/" + self.identifier)
        for i in xrange(self.numChan):
            handler.createCArray(outNode, "I%i" % i, title = "I%i" % i,\
            shape = ShapeArrays, atom = tables.Float32Atom(), filters = HDFfilters)
#Write down contextual data
        ll = np.array(["%s = %s"%(i,str(self.config[i])) for i in self.config.keys()])
        outGroup = handler.createGroup("/context",self.identifier)
        outGroup = handler.getNode("/context/"+self.identifier)
        handler.createCArray(outGroup, "config", title = "config",\
        shape = numpy.shape(ll), atom = tables.Atom.from_dtype(ll.dtype), filters = HDFfilters)
        outNode = handler.getNode("/context/"+self.identifier+"/config")
        outNode[:] = ll

        return

    def saveData2HDF(self, handler, wait=True,upperIndex=(),reverse=1):
        """the handler is an already opened file object
        The function will not open nor close the file to be written.

        This version uses the buffered data through TANGO
        The upperIndex is used when storing data of nD maps, it has nD-1 elements
        reverse is used to save date reversed if in a zigzag scan. Can be 1 or -1. """
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
        for i in xrange(self.numChan):
            outNode = handler.getNode("/data/" + self.identifier + "/I%i" % i)
            #outNode[:] = buffer[i]
            if upperIndex == ():
                outNode[:] = buffer[i]
            else:
                #exec("outNode[::,%s] = buffer[i][::reverse]"%(stringIndex))
                outNode[::][upperIndex] = buffer[i][::reverse]
        del buffer
        return

