from __future__ import print_function
import PyTango
from PyTango import DevState, DeviceProxy,DevFailed,AttributeInfoEx
from time import sleep
import time
import tables
#Why such a double import ?
import numpy
import numpy as np
import os

class dxmap:
    def __init__(self,label="",channels=None,user_readconfig=[],timeout=90.,deadtime=0.05, FTPclient="",FTPserver="",spoolMountPoint="",
    specificDevice="",config={},identifier="",detector_details={"detector_name":"","real_pixels_list":"","comment":""}):
       
        self.DP=DeviceProxy(label)
        self.label=label
        self.deadtime = deadtime
        self.timeout = timeout
        self.DP.set_timeout_millis(int(self.timeout*1000))
        self.config = config
        if identifier == "":
            raise Exception("Identifier not specified !")
        self.identifier = identifier

        
         
        self.detector_details = detector_details

        self.init_user_readconfig=user_readconfig
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

        if self.state() == DevState.FAULT:
            self.DP.init()
            t0 = time.time()
            while(self.state() != Devstate.OFF or time.time()-t0 < self.timeout):
                sleep(1)

        if self.state() == DevState.OFF:
            self.setMode(self.config["mode"])


        if self.init_user_readconfig!=[]:
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
        if failure: print(self.label+": Failed setting one or more user_readconfig!")
        self.rois,self.ocrs,self.icrs,self.dts=[],[],[],[]
        self.channels=[]
        self.channels_labels=[]
        self.numChan = self.DP.nbChannels
#The NbFrames internal variable is used for storing the total number of points
#of the requested acquisition. This is important for data storage
#the self.prepare method updates its value
        self.NbFrames = 1


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
            __lbl = self.DP.get_attribute_config(i).label
            self.channels_labels.append(self.identifier + __lbl)
            __AI = AttributeInfoEx()
            __AI.label = "roi_"+ __lbl
            __AI.format = "%6i"
            __AI.unit = ""
            self.user_readconfig += [__AI,]
 
        for i in range(len(self.user_readconfig)):
            self.user_readconfig[i].label = self.identifier + "_" + self.user_readconfig[i].label
        return

    def init(self):
        self.DP.set_timeout_millis(int(self.timeout*1000))
        sleep(1)
        self.DP.command_inout("Init")
        while(self.state() in [DevState.UNKNOWN, DevState.DISABLE]):
            sleep(self.deadtime)
        self.setMode(self.config["mode"])
        return

    def reinit(self):
        #for prova in range(5):
        #    try:
        #        if self.init_user_readconfig<>[]: 
        #            for i in self.init_user_readconfig:
        #                #ac=self.DP.get_attribute_config_ex([i[0],])[0]
        #                ac=self.DP.get_attribute_config([i[0],])[0]
        #                ac.label=i[1]
        #                ac.format=i[2]
        #                ac.unit=i[3]
        #                #self.DP.set_attribute_config_ex([ac,])
        #                self.DP.set_attribute_config([ac,])
        #        break
        #    except:
        #        print self.label+": Failed setting user_readconfig! Trial no: %i"%prova
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
                self.dts.append(i)
        self.user_readconfig=[]
        for i in self.rois+self.icrs+self.ocrs+self.dts:
            self.user_readconfig.append(self.DP.get_attribute_config(i))
        for i in self.channels:
            __lbl = self.DP.get_attribute_config(i).label
            self.channels_labels.append(self.identifier +"_"+ __lbl)
            __AI = AttributeInfoEx()
            __AI.label = "roi_"+ __lbl[-2:]
            __AI.format = "%6i"
            __AI.unit = ""
            self.user_readconfig += [__AI,]

        for i in range(len(self.user_readconfig)):
            self.user_readconfig[i].label = self.identifier + "_" + self.user_readconfig[i].label
        
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
        print(self.__repr__())
        return self.state()                              

    def state(self):
        return self.DP.state()

    def status(self):
        return self.DP.status()
       
    def startFTP(self, deleteRemainingFiles = False):
        if self.FTPclient:
            try:
                self.FTPclient.DeleteRemainingFiles()
            except:
                #print("%s : Cannot delete remaining files." % self.label)
                pass
            sleep(0.1)
            if self.FTPserver and self.FTPserver.state() != DevState.RUNNING:
                raise Exception("FTP server %s is not running. Starting client is useless. Please start it and retry.")%self.FTPserver.name
            if self.FTPclient.state() != DevState.RUNNING:
                return self.FTPclient.start()
            else:
                return
        else:
            pass

    def stopFTP(self):
        if self.FTPclient:
            return self.FTPclient.stop()
        else:
            pass

    def wait(self):
        while self.state() == DevState.RUNNING:
            sleep(self.deadtime)
        return

    def setMode(self, mode=""):
        """The mode is a string to be passed to the device for the command loadConfigFile """
        try:
            if self.DP.currentAlias != mode:
                gotROIs = True
                try:
                    rois = self.getROIs()
                except: 
                    gotROIs = False
                self.DP.loadConfigFile(mode)
            else:
                return
        except:
                gotROIs = False
                self.DP.loadConfigFile(mode)

        t0 = time.time()
        while(self.state() in [DevState.DISABLE,DevState.UNKNOWN] and time.time() - t0 < self.timeout):
            sleep(self.deadtime)

        if gotROIs:
            self.setROIs(rois)
        return

    def prepare(self, dt=1., NbFrames=1, nexusFileGeneration=False,stepMode=False, upperDimensions=()):
        self.upperDimensions = upperDimensions
#Verify stream items
        self.stream_items = [i.lower() for i in self.DP.get_property("StreamItems")["StreamItems"]]
#Order of the following attributes seems to matter!
        cKeys = self.config.keys()
#The frame numbers is a concept that does not exists in DxMap
#so I store it in a variable that prepare updates. This is reused for saving data
        self.NbFrames = NbFrames
        self.config["nbpixels"] = NbFrames
        try:
            if self.DP.currentAlias != self.config["mode"]:
                self.setMode(self.config["mode"])
        except:
            self.DP.command_inout("Init")
            sleep(1)
            self.setMode(self.config["mode"])
        #The following setup must be supplied in original config
        #self.config["streamNbAcqPerFile"]=NbFrames
        ##If possible, to be replaced with write_attributes...
        attValues=[]
        if stepMode :
            dontTouch = ["mode", "nbpixelsperbuffer"]
            attValues.append(("nbpixelsperbuffer",1))
            #self.DP.write_attribute("nbpixelsperbuffer",1)
        else:
            dontTouch = ["mode"]
        for i in [k for k in cKeys if (not k in dontTouch) and (self.config[k] != self.DP.read_attribute(k).value)]:
            try:
                #attValues.append((i,self.config[i]))
                self.DP.write_attribute(i,self.config[i])
                #print i,self.config[i]
            except Exception as tmp:
                print(tmp)
        if nexusFileGeneration:
            #Auto delete remaining files!!! this avoids aborting, but it is a potential risk.
            sleep(self.deadtime)
            self.DP.write_attribute("filegeneration",True)
            self.startFTP(deleteRemainingFiles=True)
            self.DP.streamresetindex()
        else:
            sleep(self.deadtime)
            self.DP.write_attribute("filegeneration",False)
        #self.DP.write_attributes(attValues)
        #sleep(self.deadtime)

        return self.start()

    def start(self,dt=1):
        if self.state()!=DevState.RUNNING:
            if self.FTPclient and self.DP.currentMODE=="MAPPING" and self.FTPclient.state()!=DevState.RUNNING:
                self.FTPclient.start()
            try:
                self.DP.command_inout("Snap")
            except:
                try:
                    self.DP.command_inout("Start")
                except Exception as tmp:
                    print("Cannot Start")
                    raise tmp
        else:
            raise Exception("Trying to start %s when already in RUNNING state"%self.label)
        t0 = time.time()
        while(self.state() != DevState.RUNNING and time.time()-t0 < self.timeout):
            sleep(self.deadtime)
        return self.state()
        
    def stopAcq(self):
        try:
            self.DP.command_inout("Stop")
        except Exception as tmp:
            print(tmp)
            raise tmp
        return self.state()

    def stop(self):
        #Version change: Abort becomes Abort. kept for compatibility 5/9/2014
        if self.state()==DevState.RUNNING:
            try:
                self.DP.command_inout("Stop")
            except DevFailed:
                self.DP.command_inout("Abort")
        #Why stopping the client ? after all...
        #if self.FTPclient and self.DP.currentMODE=="MAPPING" and self.FTPclient.state() == DevState.RUNNING:
        #    self.FTPclient.stop()
        return self.state()

    def read(self):
        try:
            out=self.DP.read_attributes(self.rois+self.icrs+self.ocrs+self.dts)
            out=[x.value for x in out]+self.posts()
            if None in out:
                print("MCA modified... reinit required...", end=' ')
                self.reinit()
                print("OK")
                out=self.DP.read_attributes(self.rois+self.icrs+self.ocrs+self.dts)
                out = [x.value for x in out] + self.posts()
        except DevFailed as tmp:
            if tmp.args[0].reason=='API_AttrNotFound':
                print("MCA modified... reinit required...", end=' ')
                self.reinit()
                print("OK")
                out=self.DP.read_attributes(self.rois+self.icrs+self.ocrs+self.dts)
                out = [x.value for i in out] + self.posts()
            else:
                raise tmp
        return out
    

    def posts(self):
        """Returns values calculated after counting: here it is used for determining rois in map mode"""
        roi1,roi2 = self.getROIs()
        return list(numpy.sum(numpy.array(self.read_mca())[:,roi1:roi2],axis=1))

    def read_mca(self, channels=None):
        if channels==None: 
            channels=self.channels
            auto=True
        else:
            auto=False
        try:
            mca=self.DP.read_attributes(channels)
            mca = [x.value for x in mca]
#           if (None in mca) and auto:
#               print "Reiniting mca"
#               self.reinit()
#               mca=self.DP.read_attributes(channels)
#               mca=map(lambda x: x.value, mca)
#           elif None in mca:
#               raise Exception("Wrong channel")
        except DevFailed as tmp:
            if tmp.args[0].reason=='API_AttrNotFound':
                print("Reiniting mca")
                self.reinit()
                mca=self.DP.read_attributes(channels)
                mca = [x.value for x in mca]
            else:
                raise tmp
        return mca
        
    
    #def postCount(self, dt=1):
    #    self.stop()
    #    sleep(self.deadtime)
    #    while(self.state() == DevState.RUNNING):
    #        sleep(self.deadtime)
    #    return

    
    def count(self,dt=1):
        """Not working, this code is designed for a slave XIA device not a master"""
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
        #for i in range(len(self.channels)):
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
            gottenROIS = [int(i) for i in self.DP.get_property(["SPECK_roi"])["SPECK_roi"]]
        except:
            print("Cannot get ROI from SPECK property. Loading from device...", end=' ')
            for i in self.DP.getrois():
                Ch = i.split(";")
                gottenROIS[ "channel%02i" % int(Ch[0]) ] = (int(i) for i in Ch[1:])
            print("set SPECK property from last gotten values...")
            self.DP.put_property({"SPECK_roi":[int(Ch[1]), int(Ch[2])]})
            gottenROIS = [int(Ch[1]), int(Ch[2])]
            print("OK")
        return gottenROIS
        
        
    def prepareHDF(self, handler, HDFfilters = tables.Filters(complevel = 1, complib='zlib'),upperIndex=()):
        """the handler is an already opened file object"""
        ShapeArrays = (self.NbFrames,) + tuple(self.upperDimensions)
        ShapeMatrices = (self.NbFrames, self.DP.nbBins) + tuple(self.upperDimensions)
        handler.create_group("/data", self.identifier)
        outNode = handler.get_node("/data/" + self.identifier)
       
         
        for i in range(self.numChan):
            handler.create_carray(outNode, "mca%02i" % i, title = "mca%02i" % i,\
            shape = ShapeMatrices, atom = tables.UInt32Atom(), filters = HDFfilters)

        for i in range(self.numChan):
            if 'icr' in self.stream_items:
                handler.create_carray(outNode, "icr%02i" % i, title = "icr%02i" % i,\
                shape = ShapeArrays, atom = tables.Float32Atom(), filters = HDFfilters)
            if 'ocr' in self.stream_items:
                handler.create_carray(outNode, "ocr%02i" % i, title = "ocr%02i" % i,\
                shape = ShapeArrays, atom = tables.Float32Atom(), filters = HDFfilters)
            if 'deadtime' in self.stream_items:
                handler.create_carray(outNode, "deadtime%02i" % i, title = "deadtime%02i" % i,\
                shape = ShapeArrays, atom = tables.Float32Atom(), filters = HDFfilters)
            elif 'icr' in self.stream_items and 'ocr' in self.stream_items:
                handler.create_carray(outNode, "deadtime%02i" % i, title = "deadtime%02i" % i,\
                shape = ShapeArrays, atom = tables.Float32Atom(), filters = HDFfilters)
            handler.create_carray(outNode, "roi%02i" % i, title = "roi%02i" % i,\
            shape = ShapeArrays, atom = tables.UInt32Atom(), filters = HDFfilters)

        handler.create_array("/data/"+self.identifier, "roiLimits", np.array(self.getROIs(),"i"))
#Write down contextual data
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
        The function will not open nor close the file to be written.
        Files in spool will be DELETED after writing data in output file.
        upperIndex has to be a tuple, it can be an empty tuple."""
        Roi0, Roi1 = self.getROIs()[:2]
#Calculate the number of files expected
        NOfiles = int(self.NbFrames / self.DP.streamnbacqperfile)
        if np.mod(self.NbFrames, self.DP.streamnbacqperfile) :
            NOfiles += 1
# Get the list of files to read and wait for the last to appear (?)
        files2read = [i for i in os.listdir(self.spoolMountPoint) if i.startswith(self.DP.streamTargetFile)\
        and i.endswith("nxs")]
        #print(files2read)
        if wait:
            t0 = time.time()
            #This check loop maybe avoided if a partial save has to be performed
            while(NOfiles > len(files2read) and time.time() - t0 < self.timeout):
                files2read = [i for i in os.listdir(self.spoolMountPoint) if i.startswith(self.DP.streamTargetFile)\
                and i.endswith("nxs")]
                useless_file=open(self.spoolMountPoint+os.sep+"useless.txt","w")
                useless_file.write("\n")
                useless_file.close()
                sleep(self.deadtime)
                os.system("rm "+self.spoolMountPoint+os.sep+"useless.txt")
            #print("XIA files waited for %4.2fs" % (time.time()-t0))
            if time.time()-t0 > self.timeout:
                try:
                    ipy=get_ipython()
                    ipy.user_global_ns["resetFluo"]()
                except:
                    print("p_dxmap tried to reset fluo electronics calling ResetFluo: failure.")
        files2read.sort()
#check reverse value for upper dimensional scans
        if reverse not in [-1,1]:
            reverse = 1
#One after the other: open, transfert data, close and delete
        for Nfile in range(len(files2read)):
            for try_it_again_Sam in range(3):
                try:
                    sourceFile = tables.open_file(self.spoolMountPoint + os.sep + files2read[Nfile], "r")
                    break
                except Exception as tmp:
                    if try_it_again_Sam<3:
                        sleep(1)
                    else:
                        raise tmp
            
            try:
                p0 = self.DP.streamnbacqperfile * Nfile 
                #p1 = self.DP.streamnbacqperfile * (Nfile + 1)
#Get actual file length that can vary depending on number of points in scan
                actualBlockLen = np.shape(sourceFile.root.entry.scan_data.channel00)[0]
                p1 = p0 + actualBlockLen
                for i in range(self.numChan):
                    outNode = handler.get_node("/data/" + self.identifier + "/mca%02i" % i)
                    #p0 = self.DP.streamnbacqperfile * Nfile 
                    #p1 = self.DP.streamnbacqperfile * (Nfile + 1)
                    if upperIndex == ():
                        outNode[p0:p1] = eval("sourceFile.root.entry.scan_data.channel%02i" % i)[:]
                    else:
                        #exec("outNode[::,%s] = buffer[i][::reverse]"%(stringIndex))
                        outNode[p0:p1][upperIndex] = eval("sourceFile.root.entry.scan_data.channel%02i" % i)[::reverse]

                for i in range(self.numChan):
                    if 'icr' in self.stream_items:
                        outNode = handler.get_node("/data/" + self.identifier + "/icr%02i" % i)
                        if upperIndex == ():
                            outNode[p0:p1] = eval("sourceFile.root.entry.scan_data.icr%02i" % i)[:]
                        else:
                            outNode[p0:p1][upperIndex] = eval("sourceFile.root.entry.scan_data.icr%02i" % i)[::reverse]

                    if 'ocr' in self.stream_items:
                        outNode = handler.get_node("/data/" + self.identifier + "/ocr%02i" % i)
                        if upperIndex == ():
                            outNode[p0:p1] =  eval("sourceFile.root.entry.scan_data.ocr%02i" % i)[:]
                        else:
                            outNode[p0:p1][upperIndex] =  eval("sourceFile.root.entry.scan_data.ocr%02i" % i)[::reverse]
                    if 'deadtime' in self.stream_items:
                        outNode = handler.get_node("/data/" + self.identifier + "/deadtime%02i" % i)
                        if upperIndex == ():
                            outNode[p0:p1] =  eval("sourceFile.root.entry.scan_data.deadtime%02i" % i)[:]
                        else:
                            outNode[p0:p1][upperIndex] =  eval("sourceFile.root.entry.scan_data.deadtime%02i" % i)[::reverse]
                    elif 'icr' in self.stream_items and 'ocr' in self.stream_items:
                        outNode = handler.get_node("/data/" + self.identifier + "/deadtime%02i" % i)
                        if upperIndex == ():
                            outNode[p0:p1] =  np.nan_to_num(\
                            100.*(1.-eval("sourceFile.root.entry.scan_data.ocr%02i" % i)[:]/eval("sourceFile.root.entry.scan_data.icr%02i" % i)[:])\
                            )
                        else:
                            outNode[p0:p1][upperIndex] =  np.nan_to_num(\
                            100.*(1.-eval("sourceFile.root.entry.scan_data.ocr%02i" % i)[::reverse]\
                            /eval("sourceFile.root.entry.scan_data.icr%02i" % i)[::reverse])\
                            )
            except Exception as tmp:
                print("Error saving data from file %s"%sourceFile.filename)
                print(tmp)
                raise
            finally:
                sourceFile.close()
            #os.system("rm %s" % (self.spoolMountPoint + os.sep + files2read[Nfile]))

        for i in range(self.numChan):
            roi = handler.get_node("/data/" + self.identifier + "/roi%02i" % i)
            mca = handler.get_node("/data/" + self.identifier + "/mca%02i" % i)
            roi[:] = np.sum(mca[:,Roi0:Roi1],axis=1)
        try:
            sleep(0.3)
            self.FTPclient.deleteremainingfiles()
        except Exception as tmp:
            pass
            #print(tmp)
            #print("Timeout ==> Retry Once")
            #sleep(3)
            #self.FTPclient.deleteremainingfiles()
            #print("Timeout ==> OK")
        return
    


