import PyTango
from PyTango import DevState, DeviceProxy,DevFailed
from time import sleep
import time
import numpy 
import numpy as np
from numpy import array
import os
import tables
#Xspress3Mini from detector pool
#ssh -X xspress3@172.19.9.174
#Password x5pr3553


class xspress3mini:
    def __init__(self,label="", channels=None, user_readconfig=[],
    timeout=30., deadtime=0.1, 
    FTPclient="", FTPserver="",
    spoolMountPoint="", specificDevice="",
    config={}, identifier=""):
        """
        this class interface with xspress3mini through the lima framework
        some of the parameters are set by default and cannot be changed.
        specificDevice: name of the specific associated device
        config is a dictionary containing the following kw informations, name of kw must correspond to existing attributes:
        acq_trigger_mode: internal_trigger or external_gate  (external is default, which corresponds to external_gate, 
                          internal corresponds to internal_trigger)
        saving_suffix: hdf
        saving_prefix: xsp3_
        saving_format: HDF5 
        saving_directory: folder on the remote xspress3 machine, not the local spool mount. ( /mnt/spoolSAMBA)
        saving_mode: auto_frame
        saving_overwrite_policy: abort/overwrite.

        example: 
        config={"acq_trigger_mode":"external_gate","saving_suffix":"hdf",
        "saving_prefix":"xsp3_","saving_format":"hdf5","saving_directory":"/mnt/spoolSAMBA","saving_mode":"auto_frame",
        "saving_overwrite_policy":"abort"}
        
        The identifier is necessary when saving hdf data. It must be specified and being strictly alphanumerical
        """
        self.config = config
        self.init_user_readconfig=user_readconfig
        self.label=label
        self.DP=DeviceProxy(label)
        self.DPspecific = DeviceProxy(specificDevice)
        self.numChan = self.DPspecific.numChan
        if identifier == "":
            print "Warning: an identifier has not been specified and the default is xspress3, if more than a xspress3 exists errors will occur!!!!!"
            self.identifier ="xspress3" 
        else:
            self.identifier = identifier
        failure=False
        if FTPclient <> "":
            self.FTPclient = DeviceProxy(FTPclient)
        else:
            self.FTPclient = None
        if FTPserver <> "":
            self.FTPserver = DeviceProxy(FTPserver)
        else:
            self.FTPserver = None
        self.spoolMountPoint=spoolMountPoint
        if failure: print self.label+": Failed setting one or more user_readconfig!"
        self.rois,self.ocrs,self.icrs,self.dts=[],[],[],[]
        self.channels=[]
        self.channels_labels=[]
        self.deadtime=deadtime
        self.timeout=timeout
        self.DP.set_timeout_millis(int(self.timeout*1000))
        for i in xrange(self.numChan):
            self.channels.append("channel%i"%i)
            self.channels_labels.append(self.identifier+"channel%i"%i)
            self.rois.append(identifier+"roi%i"%i)
            self.icrs.append(identifier+"icrs%i"%i)
            self.ocrs.append(identifier+"ocrs%i"%i)
            self.dts.append(identifier+"dts%i"%i)
        self.user_readconfig=[]
        for i in self.rois+self.icrs+self.ocrs:
            atcfg = PyTango.AttributeInfo()
            atcfg.data_format=PyTango._PyTango.AttrDataFormat.SCALAR
            atcfg.data_type=3 #Long
            atcfg.display_unit="cts"
            atcfg.format="%i"
            atcfg.label=i
            atcfg.name=i
            self.user_readconfig.append(atcfg)
        for i in self.dts:
            atcfg = PyTango.AttributeInfo()
            atcfg.data_format=PyTango._PyTango.AttrDataFormat.SCALAR
            atcfg.data_type=4 #Float
            atcfg.display_unit="%"
            atcfg.format="%6.4f"
            atcfg.label=i
            atcfg.name=i
            self.user_readconfig.append(atcfg)
        self.currentStep = -1
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
        repr += "ROI         = [%i, %i]\n" % tuple(self.getROIs())
        repr += "State       = %s\n"%self.DP.state()
        return repr
                    
    def __call__(self,x=None):
        print self.__repr__()
        return self.state()                              

    def state(self):
        if self.DP.acq_status == "Running" or not self.DP.ready_for_next_acq:
            return DevState.RUNNING
        else:
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

    def prepare(self,dt=1,NbFrames=1,nexusFileGeneration=False,stepMode=False):
        #Order of the following attributes seems to matter!
        self.currentStep = -1
        cKeys = self.config.keys()
        self.config["acq_nb_frames"] = NbFrames
        self.config["saving_frame_per_file"] = NbFrames
        if nexusFileGeneration:
            self.config["saving_mode"]="Auto_Frame"
            #Auto delete remaining files!!! this avoids aborting, but it is a potential risk.
            os.system("rm %s/*%s"%(self.spoolMountPoint,self.DP.saving_suffix))
        else:
            self.config["saving_mode"]="Manual"
        self.config["saving_managed_mode"]="SOFTWARE"
        self.config["acq_expo_time"]=dt

        for i in [k for k in cKeys if self.config[k]<>self.DP.read_attribute(k).value]:
            self.DP.write_attribute(i,self.config[i])
        self.DP.prepareAcq()
        #sleep(self.deadtime)
        return self.start()

    def start(self,dt=1):
        if self.state()<>DevState.RUNNING:
            if self.FTPclient and self.FTPclient.state()<>DevState.RUNNING:
                self.FTPclient.start()
            self.DP.command_inout("startAcq")
        else:
            raise Exception("Trying to start %s when already in RUNNING state"%self.label)
        return self.state()
        
    def stop(self):
        #Version change: Abort becomes Abort. kept for compatibility 5/9/2014
        if self.state()==DevState.RUNNING:
            try:
                self.DP.command_inout("stopAcq")
            except DevFailed:
                self.DP.command_inout("abortAcq")
        if self.FTPclient and self.FTPclient.state() == DevState.RUNNING:
            self.FTPclient.stop()
        return self.state()

    def wait(self):
        #while self.state()==DevState.RUNNING and self.DPspecific.acqrunning:
        t0 = time.time()
        while time.time() - t0 < self.timeout * 2 and (self.state()==DevState.RUNNING or self.DP.last_image_ready + 1 < self.DP.acq_nb_frames):
            sleep(self.deadtime)
        return

    def stepWait(self):
        """This function is used to wait for an intermediate image during a step scan with the new ct from spec_syntax"""
        while(not self.DP.last_base_image_ready > self.currentStep):
            sleep(self.deadtime)
        self.currentStep += 1
        return

    def postCount(self):
     #while self.state()==DevState.RUNNING and self.DPspecific.acqrunning:
        t0 = time.time()
        while time.time() - t0 < self.timeout * 2 and (self.state()==DevState.RUNNING or self.DP.last_image_ready + 1 < self.DP.acq_nb_frames):
            sleep(self.deadtime)
        return

    def read_mca(self, channels=None):
        lastFrame = self.DP.last_image_ready
        return [self.DPspecific.readHistogram([lastFrame,i]) for i in xrange(self.numChan)]
#       if self.state() == DevState.ON:
#read histogram needs (frame,channel) to read, the frame is intended to be the last one
#the last one is specified by the last_image_ready attribute
#           lastFrame = self.DP.last_image_ready
#           return [self.DPspecific.readHistogram([lastFrame,i]) for i in xrange(self.numChan)]
#       else:
#           raise Exception("%s: attempt to read histogram data when not in ON state"%self.DP.name)

    def read(self):
        lastFrame = self.DP.last_image_ready
        reads = array([self.DPspecific.readscalers([lastFrame,i]) for i in xrange(self.numChan)])
#       return self.computeRois() + list(reads[:,3]) + list(reads[:,4]) + list(reads[:,9])
        return self.computeRois() + list(reads[:,3]) + list(reads[:,4]) + list(100.-100.*reads[:,4]/reads[:,3])
#       if self.state() == DevState.ON:
#           #The order matters: rois, icrs, ocrs, dts
#           #out=self.DP.read_attributes(self.rois+self.icrs+self.ocrs+self.dts)
#           lastFrame = self.DP.last_image_ready
#           reads = array([self.DPspecific.readscalers([lastFrame,i]) for i in xrange(self.numChan)])
#           return self.computeRois() + list(reads[:,3]) + list(reads[:,4]) + list(reads[:,9])
#       else:
#           raise Exception("%s: attempt to read scalers data when not in ON state"%self.DP.name)
    
    def computeRois(self):
        ch1,ch2 = self.getROIs()
        return [np.sum(i[ch1:ch2]) for i in self.read_mca()]

    def count(self,dt=1):
        """This is a slave device, but it can be useful to test it with a standalone count
        This count function is used for debug only"""
        self.prepare(dt,NbFrames=1,nexusFileGeneration=False)
        self.start()
        self.wait()
        for i in zip(self.user_readconfig,self.read()):
            print i[0].name+"="+i[0].format%i[1] + "%s"%i[0].display_unit
        return

    def setROIs(self,*args):
        """the command is self.setROIs(ROImin,ROImax)
        This implementation is very limited: only one roi for the whole card"""
        self.DP.put_property({"SPECK_roi":[args[0],args[1]]})
        return
        
    def getROIs(self,channel=-1):
        """This implementation is very limited: only one roi for the whole card"""
        gottenROIS = map(int, self.DP.get_property(["SPECK_roi"])["SPECK_roi"])
        if gottenROIS == []:
            print "Cannot get ROI from SPECK property. Defaulting to full range",
            Ch1 = 0
            Ch2 = self.DP.image_width-10 #This is a trick of xspress3: last points of the image line are used for scalers (10 of them)
            self.DP.put_property({"SPECK_roi":[int(Ch1), int(Ch2)]})
            gottenROIS = [int(Ch1), int(Ch2)]
            print "OK"
        return gottenROIS
        
    def prepareHDF(self, handler, HDFfilters = tables.Filters(complevel = 1, complib='zlib')):
        """the handler is an already opened file object"""
        ShapeArrays = (self.DP.acq_nb_frames,)
        ShapeMatrices = (self.DP.acq_nb_frames, self.DP.image_width - 10)
        handler.createGroup("/data/", self.identifier)
        outNode = handler.getNode("/data/" + self.identifier)

        for i in xrange(self.numChan):
            handler.createCArray(outNode, "mca%02i" % i, title = "mca%02i" % i,\
            shape = ShapeMatrices, atom = tables.UInt32Atom(), filters = HDFfilters)

        for i in xrange(self.numChan):
            handler.createCArray(outNode, "icr%02i" % i, title = "icr%02i" % i,\
            shape = ShapeArrays, atom = tables.UInt32Atom(), filters = HDFfilters)
            handler.createCArray(outNode, "ocr%02i" % i, title = "ocr%02i" % i,\
            shape = ShapeArrays, atom = tables.UInt32Atom(), filters = HDFfilters)
            handler.createCArray(outNode, "roi%02i" % i, title = "roi%02i" % i,\
            shape = ShapeArrays, atom = tables.UInt32Atom(), filters = HDFfilters)
            handler.createCArray(outNode, "deadtime%02i" % i, title = "deadtime%02i" % i,\
            shape = ShapeArrays, atom = tables.Float32Atom(), filters = HDFfilters)

        handler.createArray("/data/"+self.identifier, "roiLimits", array(self.getROIs(),"i"))

#Write down contextual data
        ll = numpy.array(["%s = %s"%(i,str(self.config[i])) for i in self.config.keys()])
        outGroup = handler.createGroup("/context",self.identifier)
        outGroup = handler.getNode("/context/"+self.identifier)
        handler.createCArray(outGroup, "config", title = "config",\
        shape = numpy.shape(ll), atom = tables.Atom.from_dtype(ll.dtype), filters = HDFfilters)
        outNode = handler.getNode("/context/"+self.identifier+"/config")
        outNode[:] = ll

        return

    def saveData2HDF(self, handler, wait=True):
        """the handler is an already opened file object
        The function will not open nor close the file to be written."""
        Roi0, Roi1 = self.getROIs()[:2]
        nBins = self.DP.image_width - 10
#Calculate the number of files expected
        NOfiles = int(self.DP.acq_nb_frames / self.DP.saving_frame_per_file)
        if np.mod(self.DP.acq_nb_frames, self.DP.saving_frame_per_file):
            NOfiles +=1
# Get the list of files to read and wait for the last to appear (?)
        files2read = [i for i in os.listdir(self.spoolMountPoint) if i.startswith(self.DP.saving_prefix)\
        and i.endswith(self.DP.saving_suffix)]
        if wait:
            self.wait()
            t0 = time.time()
            #This check loop maybe avoided if a partial save has to be performed
            while(NOfiles > len(files2read) and time.time() - t0 < self.timeout):
                files2read = [i for i in os.listdir(self.spoolMountPoint) if i.startswith(self.DP.saving_prefix)\
                and i.endswith(self.DP.saving_suffix)]
                sleep(self.deadtime)
        files2read.sort()
        print "xsp3 files to read:", files2read
#One after the other: open, transfert data, close and delete
        for Nfile in xrange(len(files2read)):
            sourceFile = tables.open_file(self.spoolMountPoint + os.sep + files2read[Nfile], "r")
            try:
                p0 = self.DP.saving_frame_per_file * Nfile 
                p1 = self.DP.saving_frame_per_file * (Nfile + 1)
                for i in xrange(self.numChan):
                    outNode = handler.getNode("/data/" + self.identifier + "/mca%02i" % i)
                    p0 = self.DP.saving_frame_per_file * Nfile 
                    p1 = self.DP.saving_frame_per_file * (Nfile + 1)
                    outNode[p0:p1] = sourceFile.root.entry_0000.measurement.xspress3.data[:,i,0:nBins]

                for i in xrange(self.numChan):
                    outNode = handler.getNode("/data/" + self.identifier + "/icr%02i" % i)
                    outNode[p0:p1] = sourceFile.root.entry_0000.measurement.xspress3.data[:,i,nBins+4:nBins+5].transpose()[0]
                    outNode = handler.getNode("/data/" + self.identifier + "/ocr%02i" % i)
                    outNode[p0:p1] = sourceFile.root.entry_0000.measurement.xspress3.data[:,i,nBins+5:nBins+6].transpose()[0]
            finally:
                sourceFile.close()

            os.system("rm %s" % (self.spoolMountPoint + os.sep + files2read[Nfile]))

        for i in xrange(self.numChan):
            dt = handler.getNode("/data/" + self.identifier + "/deadtime%02i" % i)
            ocr = handler.getNode("/data/" + self.identifier + "/ocr%02i" % i)
            icr = handler.getNode("/data/" + self.identifier + "/icr%02i" % i)
            dt[:] = np.nan_to_num(1.0 - (array(ocr[:],"f") / array(icr[:],"f")))*100.0
            roi = handler.getNode("/data/" + self.identifier + "/roi%02i" % i)
            mca = handler.getNode("/data/" + self.identifier + "/mca%02i" % i)
            roi[:] = np.sum(mca[:,Roi0:Roi1],axis=1)
        return
    

