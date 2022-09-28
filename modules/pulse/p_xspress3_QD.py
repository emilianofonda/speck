from __future__ import print_function
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


class xspress3:
    def __init__(self,label="", channels=None, user_readconfig=[],
    timeout=30., deadtime=0.1, 
    FTPclient="", FTPserver="",
    spoolMountPoint="", specificDevice="",
    config={}, identifier="",detector_details={"detector_name":"","real_pixels_list":"","comment":""}):
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
        self.label=label
        self.deadtime=deadtime
        self.timeout=timeout
        self.DP=DeviceProxy(label)
        self.DPspecific = DeviceProxy(specificDevice)
        self.DP.set_timeout_millis(int(self.timeout*1000))
        self.config = config
        self.init_user_readconfig=user_readconfig

        #self.numChan = int(self.DPspecific.get_property("nbChans")["nbChans"][0])
        self.numChan = self.DPspecific.numChan

        if identifier == "":
            raise Exception("Identifier not specified !")
        self.identifier=identifier
        self.detector_details=detector_details

        if FTPclient != "":
            self.FTPclient = DeviceProxy(FTPclient)
        else:
            self.FTPclient = None
        if FTPserver != "":
            self.FTPserver = DeviceProxy(FTPserver)
        else:
            self.FTPserver = None
        self.spoolMountPoint=spoolMountPoint
        
        self.rois,self.ocrs,self.icrs,self.dts=[],[],[],[]
        self.channels=[]
        self.channels_labels=[]
        self.DP.set_timeout_millis(int(self.timeout*1000))
        for i in range(self.numChan):
            self.channels.append("channel%i"%i)
            self.channels_labels.append(self.identifier+"channel%i"%i)
            self.rois.append(self.identifier+"roi%i"%i)
            self.icrs.append(self.identifier+"icrs%i"%i)
            self.ocrs.append(self.identifier+"ocrs%i"%i)
            self.dts.append(self.identifier+"dts%i"%i)
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
        #self.currentStep = -1
        self.NbFrames = 1
        return

    def init(self):
        self.DP.set_timeout_millis(int(self.timeout*1000))
        sleep(1)
        self.DP.command_inout("Init")
        while(self.state() in [DevState.UNKNOWN, DevState.DISABLE]):
            sleep(self.deadtime)
        return

    def reinit(self):
        self.numChan = int(self.DPspecific.get_property("nbChans")["nbChans"][0])

        self.rois,self.ocrs,self.icrs,self.dts=[],[],[],[]
        self.channels=[]
        self.channels_labels=[]
        for i in range(self.numChan):
            self.channels.append("channel%i"%i)
            self.channels_labels.append(self.identifier+"_channel%i"%i)
            self.rois.append(self.identifier+"_roi%i"%i)
            self.icrs.append(self.identifier+"_icrs%i"%i)
            self.ocrs.append(self.identifier+"_ocrs%i"%i)
            self.dts.append(self.identifier+"_dts%i"%i)
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
        return

    def __repr__(self):
        repr =  "Device name = %s\n" % self.label
        repr += "ROI         = [%i, %i]\n" % tuple(self.getROIs())
        repr += "State       = %s\n"%self.DP.state()
        return repr
                    
    def __call__(self,x=None):
        print(self.__repr__())
        return self.state()                              

    def state(self):
        if self.DP.acq_status == "Running" or not self.DP.ready_for_next_acq or self.DPspecific.acqRunning:
            return DevState.RUNNING
        else:
            return self.DP.state()
        #return self.DP.state()

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

    def prepare(self,dt=1.,NbFrames=1,nexusFileGeneration=False,stepMode=False,upperDimensions=()):
        #Order of the following attributes seems to matter!
        
#use of Step and currentStep is odd... obsolete option ?
        self.currentStep = -1
        
        self.upperDimensions = upperDimensions
        #try:
        #    if not self.DPspecific.read_attribute("useDtc").value:
        #        self.DPspecific.write_attribute("useDtc",True)
        #except Exception as tmp:
        #    print(tmp)
            
        #Verify stream items
        #self.stream_items = [lower(i) for i in self.DP.get_property("StreamItems")["StreamItems"]]

        cKeys = self.config.keys()
        self.config["acq_nb_frames"] = NbFrames
        #Multi file option needs to be studied... usefull?
        #Saving HDF code has to be debugged for multi file support
        #self.config["saving_frame_per_file"] = min(5000,NbFrames)
        self.config["saving_frame_per_file"] = NbFrames

        #self.config["nbframes"] = NbFrames
        #self.config["filenbframes"] = NbFrames
        if nexusFileGeneration:
            self.config["saving_mode"]="Auto_Frame"
            #Auto delete remaining files!!! this avoids aborting, but it is a potential risk.
            if [i for i in os.listdir(self.spoolMountPoint) if i.endswith(self.DP.saving_suffix)] != []:
                os.system("rm %s/*%s"%(self.spoolMountPoint,self.DP.saving_suffix))
        else:
            self.config["saving_mode"]="Manual"
        self.config["saving_managed_mode"]="SOFTWARE"
        self.config["acq_expo_time"]=dt
        #self.config["exposureTime"]=dt
        
        self.DP.write_attribute("saving_next_number",0)
        for i in [k for k in cKeys if self.config[k]!=self.DP.read_attribute(k).value]:
            self.DP.write_attribute(i,self.config[i])
        self.DP.prepareAcq()
        #self.DP.prepare()
        sleep(self.deadtime)
        return self.start()

    def start(self,dt=1):
        if self.state()!=DevState.RUNNING:
            if self.FTPclient and self.FTPclient.state()!=DevState.RUNNING:
                self.FTPclient.start()
            self.DP.command_inout("startAcq")
            #self.DP.command_inout("snap")
        else:
            raise Exception("Trying to start %s when already in RUNNING state"%self.label)
        t0 = time.time()
        while(self.state() != DevState.RUNNING and time.time()-t0 < self.timeout):
            sleep(self.deadtime)
        return self.state()
        
    def stop(self):
        #Version change: Abort becomes Abort. kept for compatibility 5/9/2014
        if self.state()==DevState.RUNNING:
            try:
                self.DP.command_inout("stopAcq")
                #self.DP.command_inout("stop")
            except DevFailed as tmp:
                self.DP.command_inout("abortAcq")
                #raise tmp               
        if self.FTPclient and self.FTPclient.state() == DevState.RUNNING:
            self.FTPclient.stop()
        return self.state()

    def wait(self):
        #while self.state()==DevState.RUNNING and self.DPspecific.acqrunning:
        t0 = time.time()
        while time.time() - t0 < self.timeout * 2 and (self.state()==DevState.RUNNING or self.DP.last_image_ready + 1 < self.DP.acq_nb_frames):
            sleep(self.deadtime)
        return

    
    #def stepWait(self):
    #    """This function is used to wait for an intermediate image during a step scan with the new ct from spec_syntax"""
    #    while(not self.DP.last_base_image_ready > self.currentStep):
    #        sleep(self.deadtime)
    #    self.currentStep += 1
    #    return

    def postCount(self):
        t0 = time.time()
        while time.time() - t0 < self.timeout * 2 and (self.state()==DevState.RUNNING or self.DP.last_image_ready + 1 < self.DP.acq_nb_frames):
            sleep(self.deadtime)
        return

    def read_mca(self, channels=None):
        for i in range(5):
            try:
                lastFrame = self.DP.last_image_ready
                return [self.DPspecific.readHistogram([lastFrame,i]) for i in range(self.numChan)]
                break
            except Exception as tmp:
                print(tmp)
                sleep(0.1)
        return [self.DPspecific.readHistogram([lastFrame,i]) for i in range(self.numChan)]

#       if self.state() == DevState.ON:
#read histogram needs (frame,channel) to read, the frame is intended to be the last one
#the last one is specified by the last_image_ready attribute
#           lastFrame = self.DP.last_image_ready
#           return [self.DPspecific.readHistogram([lastFrame,i]) for i in range(self.numChan)]
#       else:
#           raise Exception("%s: attempt to read histogram data when not in ON state"%self.DP.name)

#   def read_mca(self, channels=None):
#       if channels==None: 
#           channels=self.channels
#           auto=True
#       else:
#           auto=False
#       try:
#           mca=self.DPspecific.read_attributes(channels)
#           mca=map(lambda x: x.value, mca)
#       except DevFailed, tmp:
#           if tmp.args[0].reason=='API_AttrNotFound':
#               print "Reiniting mca"
#               self.reinit()
#               mca=self.DP.read_attributes(channels)
#               mca=map(lambda x: x.value, mca)
#           else:
#               raise tmp
#       return mca

    def read(self):
        for i in range(5):
            try:
                lastFrame = self.DP.last_image_ready
                reads = array([self.DPspecific.readscalers([lastFrame,i]) for i in range(self.numChan)])
                break
            except Exception as tmp:
                print(tmp)
                sleep(0.1)

        dts=100.*(1-reads[:,4]/reads[:,3])
#                   rois,               icrs,                                   ocrs,                               dts
        return self.computeRois() + list(reads[:,3]/reads[:,0]*8.0e7) + list(reads[:,4]/reads[:,0]*8.0e7) + list(dts)
#       if self.state() == DevState.ON:
#           #The order matters: rois, icrs, ocrs, dts
#           #out=self.DP.read_attributes(self.rois+self.icrs+self.ocrs+self.dts)
#           lastFrame = self.DP.last_image_ready
#           reads = array([self.DPspecific.readscalers([lastFrame,i]) for i in range(self.numChan)])
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
        #self.start()
        self.wait()
        for i in zip(self.user_readconfig,self.read()):
            print(i[0].name+"="+i[0].format%i[1] + "%s"%i[0].display_unit)
        return

    def setROIs(self,*args):
        """the command is self.setROIs(ROImin,ROImax)
        This implementation is very limited: only one roi for the whole card"""
        self.DP.put_property({"SPECK_roi":[args[0],args[1]]})
        return
        
    def getROIs(self,channel=-1):
        """This implementation is very limited: only one roi for the whole card"""
        gottenROIS = [int(i) for i in self.DP.get_property(["SPECK_roi"])["SPECK_roi"]]
        if gottenROIS == []:
            print("Cannot get ROI from SPECK property. Defaulting to full range", end=' ')
            Ch1 = 0
            Ch2 = self.DP.image_width-10 #This is a trick of xspress3: last points of the image line are used for scalers (10 of them)
            self.DP.put_property({"SPECK_roi":[int(Ch1), int(Ch2)]})
            gottenROIS = [int(Ch1), int(Ch2)]
            print("OK")
        return gottenROIS
        
    def prepareHDF(self, handler, HDFfilters = tables.Filters(complevel = 1, complib='zlib'),upperIndex=()):
        """the handler is an already opened file object"""
        ShapeArrays = (self.DP.acq_nb_frames,) + tuple(self.upperDimensions)
        ShapeMatrices = (self.DP.acq_nb_frames, self.DP.image_width - 9)+ tuple(self.upperDimensions)

        handler.create_group("/data/", self.identifier)
        outNode = handler.get_node("/data/" + self.identifier)

        for i in range(self.numChan):
            handler.create_carray(outNode, "mca%02i" % i, title = "mca%02i" % i,\
            shape = ShapeMatrices, atom = tables.UInt32Atom(), filters = HDFfilters)

        for i in range(self.numChan):
            handler.create_carray(outNode, "icr%02i" % i, title = "icr%02i" % i,\
            shape = ShapeArrays, atom = tables.Float32Atom(), filters = HDFfilters)
            handler.create_carray(outNode, "ocr%02i" % i, title = "ocr%02i" % i,\
            shape = ShapeArrays, atom = tables.Float32Atom(), filters = HDFfilters)
            handler.create_carray(outNode, "roi%02i" % i, title = "roi%02i" % i,\
            shape = ShapeArrays, atom = tables.Float32Atom(), filters = HDFfilters)
            handler.create_carray(outNode, "deadtime%02i" % i, title = "deadtime%02i" % i,\
            shape = ShapeArrays, atom = tables.Float32Atom(), filters = HDFfilters)

        handler.create_array("/data/"+self.identifier, "roiLimits", array(self.getROIs(),"i"))

#Write down contextual data
        #ll = numpy.array(["%s = %s"%(i,str(self.config[i])) for i in self.config.keys()])
        #outGroup = handler.create_group("/context",self.identifier)
        #outGroup = handler.get_node("/context/"+self.identifier)
        #handler.create_carray(outGroup, "config", title = "config",\
        #shape = numpy.shape(ll), atom = tables.Atom.from_dtype(ll.dtype), filters = HDFfilters)
        #outNode = handler.get_node("/context/"+self.identifier+"/config")
        #outNode[:] = ll

        ll = np.array(["%s = %s"%(i,str(self.config[i])) for i in self.config.keys()])
        handler.create_group("/context",self.identifier)
        outGroup = handler.get_node("/context/"+self.identifier)
        handler.create_carray(outGroup, "config", title = "config",\
        shape = np.shape(ll), atom = tables.Atom.from_dtype(ll.dtype), filters = HDFfilters)
        outNode = handler.get_node("/context/"+self.identifier+"/config")
        outNode[:] = ll
        
        handler.create_group("/data/"+self.identifier,"detector_details","Detector description")
        outGroup = handler.get_node("/data/"+self.identifier+"/detector_details")

        handler.create_carray(outGroup, "detector_name", title = "name of detector used by fastosh",\
        shape = (1,), atom = tables.StringAtom(256,1))
        outNode = handler.get_node("/data/"+self.identifier+"/detector_details"+"/detector_name")
        outNode[:] = np.array(self.detector_details["detector_name"])

        handler.create_carray(outGroup, "real_pixels_list", title = "List of Real Pixels",\
        shape = (1,), atom = tables.StringAtom(256,1))
        outNode = handler.get_node("/data/"+self.identifier+"/detector_details"+"/real_pixels_list")
        outNode[:] = np.array(self.detector_details["real_pixels_list"])

        handler.create_carray(outGroup, "comment", title = "free user comment",\
        shape = (1,), atom = tables.StringAtom(256,1))
        outNode = handler.get_node("/data/"+self.identifier+"/detector_details"+"/comment")
        outNode[:] = np.array(self.detector_details["comment"])
        
        return

    def saveData2HDF(self, handler, wait=True, upperIndex=(),reverse=1):
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
        print("xsp3 files to read:", files2read)
#One after the other: open, transfert data, close and delete
        for Nfile in range(len(files2read)):
            sourceFile = tables.open_file(self.spoolMountPoint + os.sep + files2read[Nfile], "r")
            try:
                p0 = self.DP.saving_frame_per_file * Nfile 
                p1 = self.DP.saving_frame_per_file * (Nfile + 1)
                for i in range(self.numChan):
                    outNode = handler.get_node("/data/" + self.identifier + "/mca%02i" % i)
                    p0 = self.DP.saving_frame_per_file * Nfile 
                    p1 = self.DP.saving_frame_per_file * (Nfile + 1)
                    if upperIndex == ():
                        outNode[p0:p1] = sourceFile.root.entry_0000.measurement.xspress3.data[:,i,0:nBins+1]
                    else:    
                        outNode[p0:p1][upperIndex] = sourceFile.root.entry_0000.measurement.xspress3.data[::reverse,i,0:nBins+1]

                for i in range(self.numChan):
                    
                    outNode = handler.get_node("/data/" + self.identifier + "/icr%02i" % i)
                    if upperIndex == ():
                        outNode[p0:p1] = sourceFile.root.entry_0000.measurement.xspress3.data[:,i,nBins+4:nBins+5].transpose()[0]
                    else:
                        outNode[p0:p1][upperIndex] = sourceFile.root.entry_0000.measurement.xspress3.data[::reverse,i,nBins+4:nBins+5].transpose()[0]

                    outNode = handler.get_node("/data/" + self.identifier + "/ocr%02i" % i)
                    if upperIndex == ():
                        outNode[p0:p1] = sourceFile.root.entry_0000.measurement.xspress3.data[:,i,nBins+5:nBins+6].transpose()[0]
                    else:
                        outNode[p0:p1][upperIndex] = sourceFile.root.entry_0000.measurement.xspress3.data[::reverse,i,nBins+5:nBins+6].transpose()[0]
                    

            finally:
                sourceFile.close()
                os.system("rm %s" % (self.spoolMountPoint + os.sep + files2read[Nfile]))

        for i in range(self.numChan):
            dt = handler.get_node("/data/" + self.identifier + "/deadtime%02i" % i)
            ocr = handler.get_node("/data/" + self.identifier + "/ocr%02i" % i)
            icr = handler.get_node("/data/" + self.identifier + "/icr%02i" % i)
            dt[:] = np.nan_to_num(1.0 - (array(ocr[:],"f") / array(icr[:],"f")))*100.0
            roi = handler.get_node("/data/" + self.identifier + "/roi%02i" % i)
            mca = handler.get_node("/data/" + self.identifier + "/mca%02i" % i)
            roi[:] = np.sum(mca[:,Roi0:Roi1],axis=1)
        return
    

