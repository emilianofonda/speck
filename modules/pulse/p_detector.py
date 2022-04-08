from __future__ import print_function
import PyTango
from PyTango import DevState, DeviceProxy,DevFailed
from time import sleep
import time
from numpy import array
import os
import tables


# This is a template for writing a detector module

class detector:
    def __init__(self,label="",channels=None,user_readconfig=[],
    timeout=30.,deadtime=0.1, 
    FTPclient="",FTPserver="",
    spoolMountPoint="", specificDevice="",
    config={},identifier=""):
        """
        This is an example class and an example init to be modified for every detector type
        
        This class it's intended for slave devices (can be used in master mode with modifications)

        identifier is a string.
        The identifier is used in the output hdf tree
        """
        self.config = config
        self.init_user_readconfig=user_readconfig
        self.label=label
        self.DP=DeviceProxy(label)
        if self.DPspecific != "":
            self.DPspecific = DeviceProxy(specificDevice)
        self.numChan = self.DPspecific.numChan
        self.identifier = identifier
        failure=False
        if FTPclient != "":
            self.FTPclient = DeviceProxy(FTPclient)
        else:
            self.FTPclient = None
        if FTPserver != "":
            self.FTPserver = DeviceProxy(FTPserver)
        else:
            self.FTPserver = None
        self.spoolMountPoint=spoolMountPoint
        if failure: print(self.label+": Failed setting one or more user_readconfig!")
        self.rois,self.ocrs,self.icrs,self.dts=[],[],[],[]
        self.channels=[]
        self.channels_labels=[]
        self.bufferedChannels = []
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

    def prepare(self,dt=1,NbFrames=1,nexusFileGeneration=False):
        cKeys = self.config.keys()
        for i in [k for k in cKeys if self.config[k]!=self.DP.read_attribute(k).value]:
            self.DP.write_attribute(i,self.config[i])
        sleep(self.deadtime)
        return

    def start(self,dt=1):
        if self.state()!=DevState.RUNNING:
            if self.FTPclient and self.FTPclient.state()!=DevState.RUNNING:
                self.FTPclient.start()
            self.DP.command_inout("start")
        else:
            raise Exception("Trying to start %s when already in RUNNING state"%self.label)
        return self.state()
        
    def stop(self):
        if self.state()==DevState.RUNNING:
            try:
                self.DP.command_inout("stop")
            except DevFailed:
                self.DP.command_inout("abort")
        if self.FTPclient and self.FTPclient.state() == DevState.RUNNING:
            self.FTPclient.stop()
        return self.state()

    def wait(self):
        while self.state()==DevState.RUNNING:
            sleep(self.deadtime)
        return

    def read_mca(self, channels=None):
        return

    def read(self):
        """returns a list of data like in the order of userReadConfig
        attributes from self.channels. Should subtract dark."""
        return

    def readBuffer(self):
        """returns buffered data: list of arrays of values like in userReadConfig
        attributes from self.bufferedChannels. Should subtract dark."""
        return 

    def computeRois(self):
        return

    def preCount(self, dt=1):
        return

    def postCount(self, dt=1):
        return

    def count(self,dt=1):
        """This is a slave device, but it can be useful to test it with a standalone count
        This count function is used for debug only"""
        self.prepare(dt,NbFrames=1,nexusFileGeneration=False)
        self.preCount(dt)
        self.start()
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
        gottenROIS = map(int, self.DP.get_property(["SPECK_roi"])["SPECK_roi"])
        if gottenROIS == []:
            print("Cannot get ROI from SPECK property. Defaulting to full range", end=' ')
            Ch1 = 0
            Ch2 = self.DP.image_width-9 #This is a trick of xspress3: last points of the image line are used for scalers (9 of them)
            self.DP.put_property({"SPECK_roi":[int(Ch1), int(Ch2)]})
            gottenROIS = [int(Ch1), int(Ch2)]
            print("OK")
        return gottenROIS
        

    def prepareHDF(self, handler, HDFfilters = tables.Filters(complevel = 1, complib='zlib')):
        """the handler is an already opened file object"""
        return

    def saveData2HDF(self, handler, wait=True):
        """the handler is an already opened file object
        The function will not open nor close the file to be written."""
        return
    


        
        
