import PyTango
from PyTango import DevState, DeviceProxy,DevFailed
from time import sleep
import time

class dxmap:
    def __init__(self,label="",channels=None,user_readconfig=[],timeout=10.,deadtime=0., FTPclient="",FTPserver="",spoolMountPoint=""):
        self.init_user_readconfig=user_readconfig
        self.label=label
        self.DP=DeviceProxy(label)
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
        if self.init_user_readconfig<>[]:
            for i in self.init_user_readconfig:
                #ac=self.DP.get_attribute_config_ex([i[0],])[0]
                try:
                    ac=self.DP.get_attribute_config([i[0],])[0]
                    ac.label=i[1]
                    ac.format=i[2]
                    ac.unit=i[3]
                    #self.DP.set_attribute_config_ex([ac,])
                    self.DP.set_attribute_config([ac,])
                except:
                    failure=True
                    pass
        if failure: print self.label+": Failed setting one or more user_readconfig!"
        self.rois,self.ocrs,self.icrs,self.dts=[],[],[],[]
        self.channels=[]
        self.channels_labels=[]
        self.deadtime=deadtime
        self.timeout=timeout
        self.DP.set_timeout_millis(int(self.timeout*3000))
        for i in self.DP.get_attribute_list(): 
            if i[:7]=="channel" and int(i[-2:])>=0 and int(i[-2:])<=99:
                self.channels.append(i)
            if i[:3]=="roi" and i[5]=="_": self.rois.append(i)
            if i[:14]=="inputCountRate" and int(i[-2:])>=0 and int(i[-2:])<=99:
                self.icrs.append(i)
            if i[:len("outputCountRate")]=="outputCountRate" and int(i[-2:])>=0 and int(i[-2:])<=99:
                self.ocrs.append(i)
            if i[:len("deadTime")]=="deadTime" and int(i[-2:])>=0 and int(i[-2:])<=99:
                self.dts.append(i)
        self.user_readconfig=[]
        for i in self.rois+self.icrs+self.ocrs+self.dts:
            self.user_readconfig.append(self.DP.get_attribute_config(i))
        for i in self.channels:
            self.channels_labels.append(self.DP.get_attribute_config(i).label)
        return

    def init(self):
        self.DP.set_timeout_millis(int(self.timeout*1000))
        sleep(1)
        self.DP.command_inout("Init")
        while(self.state() in [DevState.UNKNOWN, DevState.DISABLE]):
            sleep(1)
        return

    def reinit(self):
        for prova in range(5):
            try:
                if self.init_user_readconfig<>[]: 
                    for i in self.init_user_readconfig:
                        #ac=self.DP.get_attribute_config_ex([i[0],])[0]
                        ac=self.DP.get_attribute_config([i[0],])[0]
                        ac.label=i[1]
                        ac.format=i[2]
                        ac.unit=i[3]
                        #self.DP.set_attribute_config_ex([ac,])
                        self.DP.set_attribute_config([ac,])
                break
            except:
                pass
                #print self.label+": Failed setting user_readconfig! Trial no: %i"%prova
        self.rois,self.ocrs,self.icrs,self.dts=[],[],[],[]
        self.channels=[]
        self.channels_labels=[]
        self.DP.set_timeout_millis(int(self.timeout*1000))
        for i in self.DP.get_attribute_list(): 
            if i[:7]=="channel" and int(i[-2:])>=0 and int(i[-2:])<=99:
                self.channels.append(i)
            if i[:3]=="roi" and i[5]=="_": self.rois.append(i)
            if i[:14]=="inputCountRate" and int(i[-2:])>=0 and int(i[-2:])<=99:
                self.icrs.append(i)
            if i[:len("outputCountRate")]=="outputCountRate" and int(i[-2:])>=0 and int(i[-2:])<=99:
                self.ocrs.append(i)
            if i[:len("deadTime")]=="deadTime" and int(i[-2:])>=0 and int(i[-2:])<=99:
                self.ocrs.append(i)
        self.user_readconfig=[]
        for i in self.rois+self.icrs+self.ocrs+self.dts:
            self.user_readconfig.append(self.DP.get_attribute_config(i))
        for i in self.channels:
            self.channels_labels.append(self.DP.get_attribute_config(i).label)
        #sleep(1)
        return

    def __repr__(self):
        repr =  "Device name = %s\n" % self.label
        repr += "ROI         = [%i, %i]\n" % tuple(self.getROIs())
        repr += "Config File = %s\n"%self.DP.currentConfigFile
        repr += "Mode        = %s\n"%self.DP.currentMode
        repr += "State       = %s\n"%self.DP.state()
        #gotten=self.getROIs(-1)
        #ii=1
        #kk = gotten.keys()
        #kk.sort()
        #for i in kk:
        #    repr+="%s"%i+":"
        #    for j in range(len(gotten[i]))[::2]:
        #        repr+="[%i:%i] "%(gotten[i][j],gotten[i][j+1])
        #    if not(ii%4): repr+="\n"
        #    ii+=1
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

    def start(self,dt=1):
        if self.state()<>DevState.RUNNING:
            if self.FTPclient and self.DP.currentMODE=="MAPPING" and self.FTPclient.state()<>DevState.RUNNING:
                self.FTPclient.start()
            try:
                self.DP.command_inout("Snap")
            except:
                try:
                    self.DP.command_inout("Start")
                except Exception, tmp:
                    print "Cannot Start"
                    raise tmp
        else:
            raise Exception("Trying to start %s when already in RUNNING state"%self.label)
        return self.state()
        
    def stop(self):
        #Version change: Abort becomes Abort. kept for compatibility 5/9/2014
        if self.state()==DevState.RUNNING:
            try:
                self.DP.command_inout("Stop")
            except DevFailed:
                self.DP.command_inout("Abort")
        #if self.FTPclient and self.DP.currentMODE=="MAPPING" and self.FTPclient.state() == DevState.RUNNING:
        #    self.FTPclient.stop()
        return self.state()
    
    def read_mca(self, channels=None):
        if channels==None: 
            channels=self.channels
            auto=True
        else:
            auto=False
        try:
            mca=self.DP.read_attributes(channels)
            mca=map(lambda x: x.value, mca)
            if (None in mca) and auto:
                print "Reiniting mca"
                self.reinit()
                mca=self.DP.read_attributes(channels)
                mca=map(lambda x: x.value, mca)
            elif None in mca:
                raise Exception("Wrong channel")
        except DevFailed, tmp:
            if tmp.args[0].reason=='API_AttrNotFound':
                print "Reiniting mca"
                self.reinit()
                mca=self.DP.read_attributes(channels)
                mca=map(lambda x: x.value, mca)
            else:
                raise tmp
        return mca

    def read(self):
        try:
            out=self.DP.read_attributes(self.rois+self.icrs+self.ocrs+self.dts)
            out=map(lambda x: x.value, out)
            if None in out:
                print "MCA modified... reinit required...",
                self.reinit()
                print "OK"
                out=self.DP.read_attributes(self.rois+self.icrs+self.ocrs+self.dts)
                out=map(lambda x: x.value, out)
        except DevFailed, tmp:
            if tmp.args[0].reason=='API_AttrNotFound':
                print "MCA modified... reinit required...",
                self.reinit()
                print "OK"
                out=self.DP.read_attributes(self.rois+self.icrs+self.ocrs+self.dts)
                out=map(lambda x: x.value, out)
            else:
                raise tmp
        return out
        
    def count(self,dt=1):
        """Not working, this is designed for a slave XIA device"""
        return

    def setROIs(self,*args):
        """the command is self.setROIs(ROImin,ROImax)"""
        #try:
        #    ##att=self.DP.read_attribute("selectedChannelForSetRois")
        #    #self.DP.write_attribute("selectedChannelForSetRois",args[0])
        #    #self.DP.command_inout("SetROIs",args[1:])
        #    #sleep(2)
        #    #self.reinit()
        #    pass
        #except:
        #roi=[]
        #print time.asctime()
        #for i in xrange(len(self.channels)):
        #    fmtS = "%i; " * len(args[1:]) + "%i"
        #    roi.append(fmtS % ((i,) + args[1:]))
        #print roi
        #print time.asctime()
        self.DP.setroisfromlist(["-1;%i;%i" % (args[0],args[1]),])
        self.DP.put_property({"SPECK_roi":[args[0],args[1]]})
        #print time.asctime()
        return
        
    def getROIs(self,channel=-1):
        gottenROIS={}
        #try:
        #    self.DP.write_attribute("selectedChannelForSetRois",0)
        #    if channel==-1:
        #        for i in range(len(self.rois)):
        #            self.DP.write_attribute("selectedChannelForSetRois",i)
        #            gottenROIS["channel%02i"%i]=self.DP.roisStartsEnds
        #    elif channel in range(len(self.rois)):
        #        gottenROISi["channel%02i"%channel]=self.DP.roisStartsEnds
        #    else:
        #        raise Exception("dxmap","roi limits requested for wrong channel","channel="+str(channel))
        #except:
        try:
            gottenROIS = map(int, self.DP.get_property(["SPECK_roi"])["SPECK_roi"])
        except:
            print "Cannot get ROI from SPECK property. Loading from device...",
            for i in self.DP.getrois():
                Ch = i.split(";")
                gottenROIS[ "channel%02i" % int(Ch[0]) ] = map(int, Ch[1:])
            print "set SPECK property from last gotten values..."
            self.DP.put_property({"SPECK_roi":[int(Ch[1]), int(Ch[2])]})
            gottenROIS = [int(Ch[1]), int(Ch[2])]
            print "OK"
        return gottenROIS
        
        
        
