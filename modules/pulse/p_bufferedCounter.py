from __future__ import print_function
import PyTango
from PyTango import DevState, DeviceProxy,DevFailed
from time import sleep
import time
import numpy, tables
from numpy import array


class bufferedCounter:
    def __init__(self,label="",user_readconfig=[],
    timeout=3.,deadtime=0.1, 
    FTPclient="",FTPserver="",
    spoolMountPoint="", config={},identifier="",
    GateDownTime=2
    ):
        """
        this class interface with counter NI6602 cards in buffered mode.
        A unified approach would be nice, but this is OK for me.
        The unit is slave, the prepare method starts the card.
        
        Some of the parameters are set by default and cannot be changed.

        GateDownTime is a time in microseconds (let it equal to two) than reduces the total integration time,
        it is very useful to interleave average periods and should fit with the GateDownTime
        of the PulseGenerator 
        dt=1s ==>  GateUpTime=0.999 998 ms  and GateDownTime=2 microseconds on PulseGenerator

        config is a dictionary containing the following kw informations, name of kw must correspond to existing attributes:

        frequency: value of the sampling frequency
        integrationTime: used for calculating averages (Beware: I use seconds, card use ms)
        nexusFileGeneration: False or True
        nexusTargetPath: path to spool as '\\\\srv5\\spool1\\sai' remark double backlashes if on windows...
        nexusNbAcqPerFile: self explaining
        totalNbPoint: how many points you want to read
        bufferDepth: usually int(1./integrationTime) or minimum 1

        identifier is a string but is unused at the moment... maybe can be used in final nexus files

        example:
        config={"frequency":100,"integrationTime":0.01,"nexusFileGeneration":False,
        "nexusTargetPath":'\\\\srv5\\spool1\\cpt',"nexusNbAcqPerFile":1000,"totalNbPoint":1000,
        "bufferDepth":100}

        """
        self.config = config
#If there are no attributes to save, user_readconfig is set to []
        self.init_user_readconfig=user_readconfig
        self.user_readconfig=user_readconfig
        self.label=label
        self.DP=DeviceProxy(label)
        self.identifier = identifier
        self.GateDownTime=GateDownTime
        if FTPclient != "":
            self.FTPclient = DeviceProxy(FTPclient)
        else:
            self.FTPclient = None
        if FTPserver != "":
            self.FTPserver = DeviceProxy(FTPserver)
        else:
            self.FTPserver = None
        self.spoolMountPoint=spoolMountPoint
        self.channels=[]
        self.channels_labels=[]
        self.deadtime=deadtime
        self.timeout=timeout
        self.DP.set_timeout_millis(int(self.timeout*1000))

        countersProp = [self.DP.get_property(i)[i] for i in self.DP.get_property_list("counter*")]
        self.channels=[]
        for i in countersProp:
            self.channels.append([j.split(":")[-1] for j in i if j.lower().startswith("name")][0])
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
        fmtCh = "%s, "*len(self.channels)
        repr += "Channes are = " + fmtCh%tuple(self.channels) + "\n"
        return repr
                    
    def __call__(self,x=None):
        print(self.__repr__())
        return self.state()                              

    def state(self):
        return self.DP.state()

    def status(self):
        return self.DP.status()
        
    def startFTP(self):
        if self.FTPclient:
            if self.FTPserver and self.FTPserver.state() != DevState.RUNNING:
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
#New attributes used for mapping purposes (to be used...)
        self.upperDimensions=upperDimensions

        if self.DP.state() == DevState.FAULT:
            self.DP.init()
        cKeys = self.config.keys()
#Force card to buffered mode if necessary.
        if self.DP.acquisitionMode != "BUFFERED":
            self.DP.write_attribute("acquisitionMode","BUFFERED")
        self.wait()
        #if nexusFileGeneration:
        #    self.config["nexusFileGeneration"] = True
        #    self.DP.NexusResetBufferIndex()
        #    #Auto delete remaining files!!! this avoids aborting, but it is a potential risk.
        #    os.system("rm %s/*.%s"%(self.spoolMountPoint,"nxs"))
        #else:
        #    self.config["nexusFileGeneration"] = False
#Hard remove nexus files from buffered card
        self.config["nexusFileGeneration"] = False
#Remove GateDownTime (this card works in seconds and GateDown is always in ms): 
        self.config["integrationTime"] = dt - self.GateDownTime/1000. 
        self.config["totalNbPoint"] = NbFrames
        self.config["bufferDepth"] = 1
        #min(NbFrames, max(int(1./dt), 1)) #Check with ECA ... this value is exotic...
        self.config["continuous"] = False
        sleep(self.deadtime)
        reloadAtts = self.DP.get_attribute_list()
#Some Attributes doesn't exist or exist depending on mode or external/internal time base
#So we protect checking the actual Atts list
        for kk in [i for i in cKeys if i!= "acquisitionMode" and i in reloadAtts and self.config[i]!=self.DP.read_attribute(i).value]:
            self.DP.write_attribute(kk,self.config[kk])

        return self.start()

    def start(self,dt=1):
        if self.state()!=DevState.RUNNING:
            if self.FTPclient and self.FTPclient.state()!=DevState.RUNNING:
                self.FTPclient.start()
            self.DP.command_inout("Start")
        else:
            raise Exception("Trying to start %s when already in RUNNING state"%self.label)
        return self.state()
        
    def stopAcq(self):
        try:
            self.DP.command_inout("Stop")
        except DevFailed:
            self.DP.command_inout("Abort")
        return self.state()

    def stop(self):
        #Version change: Abort becomes Abort. kept for compatibility 5/9/2014
        if self.state()==DevState.RUNNING:
            try:
                self.DP.command_inout("Stop")
            except DevFailed:
                self.DP.command_inout("Abort")
        return self.state()

    def wait(self):
        while self.state() in [DevState.RUNNING, DevState.UNKNOWN, DevState.INIT]:
            sleep(self.deadtime)
        return

    def read(self):
        return []
        #return [i.value for i in self.DP.read_attributes(self.channels)]

    def readBuffer(self):
        return [self.DP.read_attribute(i).value for i in self.channels]

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
        handler.createGroup("/data/", self.identifier)
        outNode = handler.getNode("/data/" + self.identifier)
        for s in self.channels:
            handler.createCArray(outNode, "%s" % s, title = "%s" % s,\
            shape = ShapeArrays, atom = tables.Float32Atom(), filters = HDFfilters)
#Write down contextual data
        ll = numpy.array(["%s = %s"%(i,str(self.config[i])) for i in self.config.keys()])
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
        for i in xrange(len(buffer)):
            outNode = handler.getNode("/data/" + self.identifier + "/%s" % self.channels[i])
            if upperIndex == ():
                outNode[:] = buffer[i]
            else:
                exec("outNode[:,%s]=buffer[i][::reverse]"%(stringIndex))
        del buffer
        return


