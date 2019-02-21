# -*- coding: utf-8 -*-
import dentist
import thread
import tables
import os
import string
import numpy
import time as myTime
from time import sleep, asctime
from spec_syntax import wait_motor
from GracePlotter import GracePlotter
from spec_syntax import dark as ctDark
from wait_functions import checkTDL, wait_injection
import mycurses

#The following works with module version 2 that should be renamed and moved from scripts to modules/detectors.
from changePeakingTime import setMAP, setSTEP 

try:
    import Tkinter
    NoTk=False
except:
    print "Warning from ecscan: Tkinter not installed."
    NoTk=True

print mycurses.RED+"Using FTPv2 version of ecscan"+mycurses.RESET


#A global object of the counter_class called ct MUST exist 

class CPlotter:
    def h_init__(self):
        return

__CPlotter__ = CPlotter()

class ecscanFTP:
    def __init__(cardCT=DeviceProxy("d09-1-c00/ca/cpt.3"),cardAI=DeviceProxy("d09-1-c00/ca/sai.1")):
        self.shell=get_ipython()
        self.FE = self.shell.user_ns["FE"]
        self.obxg = self.shell.user_ns["obxg"]
        self.sh_fast = self.shell.user_ns["sh_fast"]
        self.cardAI = cardAI
        self.cardCT = cardCT
        self.cardCTsavedAttributes = ["totalNbPoint","integrationTime","continuous","bufferDepth"]
        self.cardAIsavedAttributes = ["configurationId","frequency","integrationTime","dataBufferNumber"]
        self.cardXIA = self.shell.user_ns["ct"].mca_units
        self.ct = self.shell.user_ns["ct"]
        self.dcm = self.shell.user_ns["dcm"]
        return

    def stopscan(self,shutter=False):
        try:
            if shutter:
                self.sh_fast.close()
        except:
            pass
        print "Wait... Stopping Devices...",
        sys.stdout.flush()
        self.cardAI.stop()
        self.cardCT.stop()
        for xia in self.cardXIA:
            xia.stop()
        self.dcm.stop()
        myTime.sleep(3)
        self.dcm.velocity(60)
        while(DevState.RUNNING in [i.state() for i in self.cardXIA]):
            myTime.sleep(2)
        setMAP()
        wait_motor(self.dcm)
        print "Scan Stopped: OK"
        sys.stdout.flush()
        return


    def update_graphs(self, CP, XIAfilesList, fluoXIA):
        
        #cardAI_dark0,cardAI_dark1,cardAI_dark2,cardAI_dark3 =\
        #map(float, self.cardAI.get_property(["SPECK_DARK"])["SPECK_DARK"])
     
        LastPoint = self.cardAI.dataCounter
        I0 = self.cardAI.historizedchannel0[:LastPoint] - self.cardAI_dark0
        I1 = self.cardAI.historizedchannel1[:LastPoint] - self.cardAI_dark1
        I2 = self.cardAI.historizedchannel2[:LastPoint] - self.cardAI_dark2
        xmu = numpy.nan_to_num(log(1.0*I0/I1))
        std = numpy.nan_to_num(log(1.0*I1/I2))
        ene = self.dcm.theta2e(self.cardCT.Theta)
        ll = min(len(ene), len(xmu))
        CP.GraceWin.GPlot(ene[:ll],xmu[:ll], gw=0, graph=0, curve=0, legend="",color=1, noredraw=True)
        CP.GraceWin.GPlot(ene[:ll], I0[:ll], gw=0, graph=1, curve=0, legend="", color=2, noredraw=True)
        CP.GraceWin.wins[0].command('with g0\nautoscale\nredraw\n')
        CP.GraceWin.GPlot(ene[:ll], I1[:ll], gw=0, graph=1, curve=1, legend="", color=3, noredraw=True)
        CP.GraceWin.wins[0].command('with g1\nautoscale\nredraw\n')
        CP.GraceWin.GPlot(ene[:ll], std[:ll], gw=0, graph=3, curve=1, legend="", color=1, noredraw=True)
        CP.GraceWin.wins[0].command('with g3\nautoscale\nredraw\n')
        tmp = []
        for xia in zip(self.cardXIA, self.XIANexusPath):
            __tmp = os.listdir(xia[1])
            __tmp.sort()
            #print __tmp
            for i in list(__tmp):
                #if not str(i).startswith(xia[0].DP.streamTargetFile) or str(i).startswith("."):
                if not str(i).startswith(xia[0].DP.streamTargetFile):
                    __tmp.remove(i)
            tmp.append(__tmp)
        if len(tmp[0]) > len(XIAfilesList[0]):
            for xiaN in range(len(self.cardXIA)):
                for name in tmp[xiaN][len(XIAfilesList[xiaN]):]:
                    XIAfilesList[xiaN].append(name)
                    try:
                        f = tables.openFile(self.XIANexusPath[xiaN] + os.sep + name, "r")
                        #fluoSeg=zeros([shape(eval("f.root.entry.scan_data.channel%02i"%cardXIAChannels[xiaN][0]))[0],cardXIA[xiaN].DP.streamNbDataPerAcq],numpy.float32)
                        #for ch in range(len(cardXIAChannels[xiaN])):
                        #    fluoSeg += eval("f.root.entry.scan_data.channel%02i"%ch).read()
                        fluoSeg=zeros(len(eval("f.root.entry.scan_data.channel%02i"%cardXIAChannels[xiaN][0])),numpy.float32)
                        for ch in range(len(self.cardXIAChannels[xiaN])):
                            fluoSeg += sum(eval("f.root.entry.scan_data.channel%02i[:,roiStart:roiEnd]"%ch),axis=1)\
                            /(1.-eval("f.root.entry.scan_data.deadtime%02i"%ch).read()*0.01)
                    finally:
                        try:
                            f.close()
                        except:
                            pass
                    #fluoSeg = sum(fluoSeg[:,roiStart:roiEnd],axis=1) 
                    fluoXIA[xiaN] += list(fluoSeg)
            ll = min([len(i) for i in fluoXIA])
            if len(I0) >= ll and ll > 2:
                fluoTrace = sum(array([i[:ll] for i in fluoXIA],"f"),axis=0)
                CP.GraceWin.GPlot(ene[:ll],numpy.nan_to_num(fluoTrace/I0[:ll]),\
                gw=0, graph=2, curve=0, legend="", color=1, noredraw=False)
                CP.GraceWin.wins[0]('with g2\nautoscale\nredraw\n')
        return


    def dark(self,dt=10.):
        #Configure cards
        NumberOfPoints = 1000
        #Card CT
        self.cardCT.totalNbPoint = NumberOfPoints
        self.cardCT.nexusNbAcqPerFile = NumberOfPoints
        self.cardCT.integrationTime = dt / float(NumberOfPoints)
        self.cardCT.bufferDepth = int(float(NumberOfPoints)/dt)
        self.cardCT.continuous = False
        self.cardCT.nexusFileGeneration = False
        self.cardCT.set_timeout_millis(30000)

        #Card AI
        if self.cardAI.configurationId <> 3:
            self.cardAI.configurationId = 3
            myTime.sleep(5)
        self.cardAI.integrationTime = dt -1.
        self.cardAI.nexusFileGeneration = False
        self.cardAI.nexusNbAcqPerFile = NumberOfPoints
        self.cardAI.dataBufferNumber = NumberOfPoints
        self.cardAI.statHistoryBufferDepth = NumberOfPoints
        self.cardAI.set_timeout_millis(30000)

        shell=get_ipython()
        shclose=shell.user_ns["shclose"]
        shopen=shell.user_ns["shopen"]
        shstate=shell.user_ns["shstate"]
        if dt == 0:
            self.ct.clearDark()
        else:
            previous = shstate()
            shclose(1)
            myTime.sleep(1)
            self.ct.count(dt)
            self.ct.writeDark()
            self.cardAI.start()
            myTime.sleep(1)
            self.cardCT.start()
            while(self.cardCT.state() == DevState.RUNNING):
                myTime.sleep(0.1)
            self.cardAI.stop()
            darkAI0 = numpy.average(self.cardAI.historizedchannel0)
            darkAI1 = numpy.average(self.cardAI.historizedchannel1)
            darkAI2 = numpy.average(self.cardAI.historizedchannel2)
            darkAI3 = numpy.average(self.cardAI.historizedchannel3)
            self.cardAI.put_property({"SPECK_DARK":[darkAI0,darkAI1,darkAI2,darkAI3]})
            print "Dark values:"
            print "I_0(AnalogInput) = %6.5fV" % darkAI0
            print "I_1(AnalogInput) = %6.5fV" % darkAI1
            print "I_2(AnalogInput) = %6.5fV" % darkAI2
            shopen(previous)
        print self.ct.readDark()
        return


    def AlarmBeep(self):
        """Uses Tkinter to alert user that the run is finished... just in case he was sleeping..."""
        try:
            a=Tkinter.Tk()
            for j in range(5):
                for i in range(3):
                    a.bell()
                    myTime.sleep(0.025)
                myTime.sleep(0.35)
            a.destroy()
        except:
            try:
                a.destroy()
            except:
                pass
        return


    def ecscanPrepare(self,fileName,e1,e2,dt,velocity, e0, mode,shutter,beamCheck,backlash):
        #CheckFilename first
        if fileName == None: 
            raise Exception("filename and limits must be specified")
        fileName = fileName.replace(" ","_")
        if string.whitespace in fileName:
            raise Exception("ecscan does not accept tabulations and other special spacings in filenames. Aborting.",fileName)
        for ch in fileName:
            if ch not in string.letters+string.digits+"_./\\+-@":
                raise Exception("ecscan does not accept special characters in filenames. Aborting.",fileName)
        self.filename = filename
        #
        if velocity <= 0.:
            raise Exception("Monochromator velocity too low!")
        if velocity > 100.:
            raise Exception("Monochromator velocity exceeded!")
        
        #Configure cards
        TotalTime = float(abs(e2-e1)) / velocity
        print "Expected time = %g s" % TotalTime
        self.NumberOfPoints = int (float(abs(e2-e1)) / velocity / dt)
        print "Number of points: ",self.NumberOfPoints
        print "One point every %4.2feV." % (velocity * dt)
        
        #Card CT
        self.cardCT.totalNbPoint = self.NumberOfPoints
        self.cardCT.nexusNbAcqPerFile = self.NumberOfPoints
        self.cardCT.integrationTime = dt
        self.cardCT.bufferDepth = int(1./dt)
        self.cardCT.continuous = False
        self.cardCT.nexusFileGeneration = False
        self.cardCT.set_timeout_millis(30000)

        #Card AI
        if self.cardAI.configurationId <> 3:
            self.cardAI.configurationId = 3
            myTime.sleep(5)
        self.cardAI.integrationTime = dt * 1000 -2.
        self.cardAI.nexusFileGeneration = False
        self.cardAI.nexusNbAcqPerFile = self.NumberOfPoints
        self.cardAI.dataBufferNumber = self.NumberOfPoints
        self.cardAI.statHistoryBufferDepth = self.NumberOfPoints
        self.cardAI.set_timeout_millis(30000)
        self.cardAI_dark0,self.cardAI_dark1,self.cardAI_dark2,self.cardAI_dark3 =\
        map(float, self.cardAI.get_property(["SPECK_DARK"])["SPECK_DARK"])

        #Set Mapping mode if needed
        try:
            setMAP()
            myTime.sleep(1)
        except:
            try:
                myTime.sleep(1)
                setMAP()
                myTime.sleep(1)
            except:
                print "The setMAP function does not work!!! Try again and/or check with local contact!!!"
        #Cards XIA
        #Rois are defined only on the first channel of the first card
        try:
            self.roiStart, self.roiEnd = self.cardXIA[0].getROIs()
        except:
            print "Please wait... I cannot find ROI limits, checking configuration...",
            setSTEP()
            myTime.sleep(1)
            setMAP()
            try:
                self.roiStart, self.roiEnd = self.cardXIA[0].getROIs()
                print " done. OK."
            except Exception, tmp:
                print "\nRegion Of Interest has not been defined? uAnatase_newPellet_phi20_macrose setroi(start,end) command please."
                raise tmp
        print "ROI limits are [%4i:%4i]" % (self.roiStart, self.roiEnd)
        cardXiaDataShape = []
        XIANexusPath = []
        cardXIAChannels = []
        __Nch = 0
        for xia in self.cardXIA:
            print "Setting XIA card:",xia.label
            cardXIAChannels.append(range(__Nch,__Nch + len(xia.channels)))
            #Line below should work for non overlapping output channels
            __Nch += len(xia.channels)
            xia.DP.nbpixels = NumberOfPoints
            xia.DP.streamNbAcqPerFile = 250
            xia.DP.set_timeout_millis(30000)
            cardXiaDataShape.append([ NumberOfPoints,xia.DP.streamNbDataPerAcq ])
            if xia.FTPclient:
                XIANexusPath.append(xia.spoolMountPoint)
                #Clean Up the mess (if any) in the source disk
                try:
                    xia.FTPclient.DeleteRemainingFiles()
                except:
                    print "Failed to delete remaining files from %s" % xia.FTPclient.name
                if xia.FTPclient.state() <> DevState.STANDBY:
                    if xia.FTPclient.state() == DevState.RUNNING:
                        xia.FTPclient.stop()
                        sleep(1)
                    else:
                        xia.FTPclient.init()
                        sleep(1)
                for retryFTPdelete in xrange(5):
                    try:
                        xia.FTPclient.DeleteRemainingFiles()
                        break
                    except:
                        xia.FTPclient.init()
                        sleep(1)
                xia.FTPclient.start()
            else:
                XIANexusPath.append("/nfs" + xia.DP.streamTargetPath.replace("\\","/")[1:])
            #Reset Nexus index and cleanup spool
            xia.DP.streamresetindex()
            map(lambda x: x.startswith(xia.DP.streamTargetFile) and os.remove(XIANexusPath[-1] +os.sep + x), os.listdir(XIANexusPath[-1]))
        NumberOfXIAFiles = int(cardXIA[0].DP.nbpixels / cardXIA[0].DP.streamNbAcqPerFile)
        if numpy.mod(cardXIA[0].DP.nbpixels, cardXIA[0].DP.streamNbAcqPerFile):
            NumberOfXIAFiles += 1
        
        self.cardXiaDataShape = cardXiaDataShape
        self.XIANexusPath = XIANexusPath
        self.cardXIAChannels = cardXIAChannels
        self.NumberOfXIAFiles = NumberOfXIAFiles
        #DCM Setup
        if self.dcm.state() == DevState.DISABLE:
            self.dcm.DP.on()
            myTime.sleep(1)
        for i in range(5):
            try:
                self.dcm.mode(1)
                break
            except:
                myTime.sleep(3)
        return

    def ecscanActor(self,e1,e2,dt=0.04,velocity=10, e0=-1, mode="",shutter=False,beamCheck=True,backlash=100,CurrentScan=1,NofScans=1):
        #Start graphic windows    
        try:
            CP = __CPlotter__
            CP.GraceWin = GracePlotter()
            #Calculate name of last data buffer file to wait (XIA)
            LastXIAFileName = ["%s_%06i.nxs" % (xia.DP.streamTargetFile, self.NumberOfXIAFiles) for xia in cardXIA]
            if beamCheck and not(checkTDL(self.FE)):
                wait_injection(self.FE,[self.obxg,])
                myTime.sleep(10.)
            ActualFileNameData = findNextFileName(self.fileName,"txt")
            shell.logger.log_write("Saving data in: %s\n" % ActualFileNameData, kind='output')
            ActualFileNameInfo = ActualFileNameData[:ActualFileNameData.rfind(".")] + ".info"
            f=file(ActualFileNameData,"w")
            f.close()
            #Configure and move mono
            if self.dcm.state() == DevState.MOVING:
                wait_motor(self.dcm)
            myTime.sleep(1)
            self.dcm.velocity(60)
            if self.dcm.pos() > e1 - backlash:
                self.dcm.pos(e1-backlash)
                #self.dcm.pos(e1-backlash, wait=False)
            #Print Name:
            print "Measuring : %s\n"%ActualFileNameData

            #Start Measurement
            CP.GraceWin.wins[0].command('ARRANGE(4,1,0.1,0.1,0.25)\nREDRAW\n')
            CP.GraceWin.wins[0].command('with g0\nxaxis ticklabel char size 0.7\n')
            CP.GraceWin.wins[0].command('with g0\nyaxis ticklabel char size 0.7\n')
            CP.GraceWin.wins[0].command('with g0\nyaxis label char size 0.7\nyaxis label "XMU"')
            CP.GraceWin.wins[0].command('with g1\nxaxis ticklabel char size 0.7\n')
            CP.GraceWin.wins[0].command('with g1\nyaxis ticklabel char size 0.7\n')
            CP.GraceWin.wins[0].command('with g1\nyaxis label char size 0.7\nyaxis label "I0, I1"')
            CP.GraceWin.wins[0].command('with g2\nxaxis ticklabel char size 0.7\n')
            CP.GraceWin.wins[0].command('with g2\nyaxis ticklabel char size 0.7\n')
            CP.GraceWin.wins[0].command('with g2\nyaxis label char size 0.7\nyaxis label "FLUO"')
            CP.GraceWin.wins[0].command('with g3\nxaxis ticklabel char size 0.7\n')
            CP.GraceWin.wins[0].command('with g3\nyaxis ticklabel char size 0.7\n')
            CP.GraceWin.wins[0].command('with g3\nyaxis label char size 0.7\nyaxis label "STD"')
            timeAtStart = myTime.asctime()
            self.cardAI.start()
            for xia in self.cardXIA:
                #xia.DP.snap()
                xia.start()
            myTime.sleep(1)
            self.dcm.mode(1)
            myTime.sleep(0.5)
            self.dcm.velocity(velocity)
            myTime.sleep(0.5)
            self.dcm.pos(e1)
            myTime.sleep(0.5)
            try:
                pass
                if shutter:
                    sh_fast.open()
            except KeyboardInterrupt:
                stopscan(shutter)
                raise
            except:
                pass
            self.cardCT.start()
            self.dcm.pos(e2, wait=False)
            myTime.sleep(2)
            XIAfilesList=[[],]*len(self.cardXIA)
            fluoXIA=[[],]*len(self.cardXIA)
            actualRunningStart = myTime.time()
            while(self.dcm.state() == DevState.MOVING):
                try:
                    if DevState.FAULT in [xia.state() for xia in self.cardXIA]:
                        shell.logger.log_write(mycurses.RED+mycurses.BOLD + "XIA Card FAULT." + mycurses.RESET, kind='output')
                        print mycurses.RED+mycurses.BOLD +"XIA Card FAULT" + mycurses.RESET
                        break
                    update_graphs(CP, XIAfilesList, fluoXIA)
                    pass
                except KeyboardInterrupt:
                    raise
                except Exception, tmp:
                    print tmp
                myTime.sleep(5)
            try:
                if shutter:
                    sh_fast.close()
            except KeyboardInterrupt:
                raise
            except:
                pass

            if CurrentScan < (NofScans-1): 
                print myTime.asctime(), " : sending self.dcm back to starting point."
                self.dcm.velocity(60)
                myTime.sleep(0.2)
                self.dcm.pos(e1-backlash, wait=False)
            else:
                print "Scan %i of %i"%(CurrentScan,NofScans)
                
            if DevState.FAULT in [xia.state() for xia in self.cardXIA]:
                self.cardCT.stop()
                self.cardAI.stop()
                setSTEP()
                myTime.sleep(1)
                setMAP()
                myTime.sleep(1)
            else:
                while(DevState.RUNNING in [self.cardCT.state(),]):
                    myTime.sleep(1.)
                timeAtStop = asctime()
                timeout0 = myTime.time()
                while(DevState.RUNNING in [self.cardAI.state(),] and myTime.time()-timeout0 < 3):
                    myTime.sleep(1)
                if myTime.time()-timeout0 > 6:
                    print "self.cardAI of ecscan failed to stop!"
                self.cardAI.stop()
                theta = self.cardCT.Theta
                
                #Begin of new block: test for I0 data, sometimes nan are returned .... why?
                I0 = array(self.cardAI.historizedchannel0,"f")
                if all(I0 <> numpy.nan_to_num(I0)):
                    shell.logger.log_write(mycurses.RED+mycurses.BOLD + ActualFileNameData + ": file is corrupt." + mycurses.RESET, kind='output')
                    print mycurses.RED+mycurses.BOLD + ActualFileNameData +": file is corrupt." + mycurses.RESET
                    CorruptData = True
                else:
                    CorruptData = False
                # End of new block
                
                I0 = numpy.nan_to_num((I0) - self.cardAI_dark0)
                I1 = numpy.nan_to_num(array(self.cardAI.historizedchannel1,"f") - self.cardAI_dark1)
                I2 = numpy.nan_to_num(array(self.cardAI.historizedchannel2,"f") - self.cardAI_dark2)
                I3 = numpy.nan_to_num(array(self.cardAI.historizedchannel3,"f") - self.cardAI_dark3)
                xmu = numpy.nan_to_num(log(I0/I1))
                fluoXP = numpy.nan_to_num(I3/I0)
                ene = numpy.nan_to_num(self.dcm.theta2e(theta))
                print myTime.asctime(), " : Saving Data..."

        #Wait for XIA files to be saved in spool
                XIAt0=myTime.time()
                while(DevState.RUNNING in [i.state() for i in self.cardXIA]):
                    myTime.sleep(1)
                    if myTime.time() - XIAt0 > 60.:
                        print "Time Out waiting for XIA self.cards to stop! Waited more than 60s... !"
                        for i in self.cardXIA:
                            i.stop()
                        setSTEP()
                        raise Exception("Time Out waiting for XIA self.cards to stop! Waited more than 60s... !")
                        shell.logger.log_write("Time Out waiting for XIA self.cards to stop! Waited more than 60s... !", kind='output')
                while(True in [i[0] not in os.listdir(i[1]) for i in zip(LastXIAFileName, XIANexusPath)]):
                    myTime.sleep(1)
                    #        os.system("cd %s&&ls"%i)
                    if myTime.time()-XIAt0>300:
                        print "Waited more than 300s. Exception Raised!"
                        raise Exception("XIA did not provided files in less than 300s!!!!!! Halt.")
                XIAtEnd = myTime.time()-XIAt0
                print "XIA needed additional %3.1f seconds to provide data files."%(XIAtEnd)
                shell.logger.log_write("XIA needed additional %3.1f seconds to provide data files."%(XIAtEnd) + ".hdf", kind='output')
        
        #Additional time to wait (?)
                myTime.sleep(0.2)
        #Measure time spent for saving data
                DataSavingTime = myTime.time()
        #Define filter to be used for writing big data into the HDF file
                HDFfilters = tables.Filters(complevel = 1, complib='zlib')
        #XIA prepare
                XIAfilesNames=[]
                for i in zip(self.cardXIA,XIANexusPath):
                    XIAfilesNames.append([j for j in os.listdir(i[1]) if j.startswith(i[0].DP.streamTargetFile)])
                XIAfilesNames = [numpy.sort(i) for i in XIAfilesNames]                  
                XIAfiles=[]
                for path in zip(XIANexusPath,XIAfilesNames):
                    XIAfiles.append([tables.openFile(path[0] +os.sep + x, "r") for x in path[1]])
            #Common
                outtaName = filename2ruche(ActualFileNameData)
                outtaHDF = tables.openFile(outtaName[:outtaName.rfind(".")] + ".hdf","w")
                outtaHDF.createGroup("/","XIA")
        #Superpose all XIA matrices and make one to avoid exploding the TeraByte/week limits and keep on a USB stick (actually, this changes with compression)
                outtaHDF.createCArray(outtaHDF.root.XIA, "mcaSum", title="McaSum", shape=self.cardXiaDataShape[0], atom = tables.UInt32Atom(), filters=HDFfilters)
                mcaSum = numpy.zeros(self.cardXiaDataShape[0],numpy.uint32)
                #outtaHDF.createArray("/XIA", "mcaSum", numpy.zeros(self.cardXIA1dataShape, numpy.uint32))
        
        #XIA1 read / write
        
        #Declare a RAM buffer for a single MCA
                bCmca = numpy.zeros(self.cardXiaDataShape[0],numpy.uint32)
                Breaked=False
                for xiaN in range(len(self.cardXIA)):
                    outChannels = iter(self.cardXIAChannels[xiaN])                    
                    for ch in range(len(self.cardXIA[xiaN].channels)):
                        if Breaked:
                            break
                        outCh = outChannels.next()
                        #print "outCh = ",outCh
        #Single Channel MCA CArray creation
                        outtaHDF.createCArray(outtaHDF.root.XIA, "mca%02i"%outCh, title="mca%02i"%outCh,\
                        shape=self.cardXiaDataShape[0], atom = tables.UInt32Atom(), filters=HDFfilters)
        #Get pointer to a Channel MCA on disk
                        pCmca = outtaHDF.getNode("/XIA/mca%02i"%outCh)
        #Fluo Channel ROI values                
                        outtaHDF.createArray("/XIA", "fluo%02i"%outCh, numpy.zeros(NumberOfPoints, numpy.uint32))
        #ICR line comment out if required
                        outtaHDF.createArray("/XIA", "inputCountRate%02i"%outCh, numpy.zeros(NumberOfPoints, numpy.float32))
        #OCR line comment out if required
                        outtaHDF.createArray("/XIA", "outputCountRate%02i"%outCh, numpy.zeros(NumberOfPoints, numpy.float32))
        #DT line comment out if required
                        outtaHDF.createArray("/XIA", "deadtime%02i"%outCh, numpy.zeros(NumberOfPoints, numpy.float32))
                        block = 0
                        blockLen = self.cardXIA[xiaN].DP.streamNbAcqPerFile
                        pointerCh = eval("outtaHDF.root.XIA.fluo%02i"%outCh)
        #ICR line comment out if required
                        pointerIcr = eval("outtaHDF.root.XIA.inputCountRate%02i"%outCh)
        #OCR line comment out if required
                        pointerOcr = eval("outtaHDF.root.XIA.outputCountRate%02i"%outCh)
        #DT line comment out if required
                        pointerDt = eval("outtaHDF.root.XIA.deadtime%02i"%outCh)
                        for XFile in XIAfiles[xiaN]:
                            try:
                                __block = eval("XFile.root.entry.scan_data.channel%02i"%ch).read()
        #ICR line comment out if required
                                __blockIcr = eval("XFile.root.entry.scan_data.icr%02i"%ch).read()
        #OCR line comment out if required
                                __blockOcr = eval("XFile.root.entry.scan_data.ocr%02i"%ch).read()

        #DT line comment out if required
                                __blockDT = eval("XFile.root.entry.scan_data.deadtime%02i"%ch).read()
                            except:
                                print "Cannot read ch = %i in XIA card #%i (first card is card 0)"%(ch,xiaN)
                                Breaked = True
                                break
                            actualBlockLen = shape(__block)[0]
        #Feed RAM buffers with MCA values
                            bCmca[block * blockLen: (block * blockLen) + actualBlockLen,:] = __block
                            mcaSum[block * blockLen: (block * blockLen) + actualBlockLen,:] += __block
                            #pointerCh[block * blockLen: (block + 1) * blockLen] = sum(__block[:,self.roiStart:self.roiEnd], axis=1)
                            pointerCh[block * blockLen: (block * blockLen) + actualBlockLen] = sum(__block[:,self.roiStart:self.roiEnd], axis=1)
        #ICR line comment out if required
                            pointerIcr[block * blockLen: (block * blockLen) + actualBlockLen] = __blockIcr
        #OCR line comment out if required
                            pointerOcr[block * blockLen: (block * blockLen) + actualBlockLen] = __blockOcr
        #DT line comment out if required
                            pointerDt[block * blockLen: (block * blockLen) + actualBlockLen] = __blockDT
                            block += 1
        #Write Single MCA to Disk
                        pCmca[:] = bCmca
                    print "XIA%i: OK"%(xiaN+1)

        #Finalize derived quantities
                fluoXraw = numpy.nan_to_num(array( sum(mcaSum[:,self.roiStart:self.roiEnd], axis=1), "f") / I0)
                fluoX = numpy.nan_to_num(sum(\
                [eval("outtaHDF.root.XIA.fluo%02i[:]"%nch)/(1.-eval("outtaHDF.root.XIA.deadtime%02i[:]"%nch)*0.01)\
                for nch in range(self.cardXIAChannels[-1][-1])]\
                ,axis=0)/I0)
                #
                outtaHDF.root.XIA.mcaSum[:] = mcaSum
                del mcaSum
                xmuS = numpy.nan_to_num(log(I1/I2))
                outtaHDF.createGroup("/","Spectra")
                outtaHDF.createArray("/Spectra", "xmuTransmission", xmu)
                outtaHDF.createArray("/Spectra", "xmuStandard", xmuS)
                outtaHDF.createArray("/Spectra", "xmuFluo", fluoX)
                outtaHDF.createArray("/Spectra", "xmuFluoRaw", fluoXraw)
                outtaHDF.createArray("/Spectra", "xmuFluoXP", fluoXP)
                outtaHDF.createGroup("/","Raw")
                outtaHDF.createArray("/Raw", "Energy", ene)
                outtaHDF.createArray("/Raw", "I0", I0)
                outtaHDF.createArray("/Raw", "I1", I1)
                outtaHDF.createArray("/Raw", "I2", I2)
                outtaHDF.createArray("/Raw", "I3", I3)
        #Stop feeding the monster. Close HDF
                outtaHDF.close()
                print "HDF closed."
                shell.logger.log_write("Saving data in: %s\n" % (outtaName[:outtaName.rfind(".")] + ".hdf"), kind='output')
        #Now that data are saved try to plot it for the last time
                try:
                   update_graphs(CP,XIAfilesList, fluoXIA)
                   print "Graph Final Update OK"
                   pass
                except KeyboardInterrupt:
                   raise
                except Exception, tmp:
                   print tmp
        #Clean up the mess in the spool 
        #XIA close and wipe
                for i in XIAfiles:
                    for j in i:
                        for ret in xrange(3):
                            try:
                                j.close()
                                break
                            except:
                                sleep(1)
                for i in zip(self.cardXIA,XIANexusPath):
                    for j in os.listdir(i[1]):
                        if j.startswith(i[0].DP.streamTargetFile):
                            os.remove(i[1] + os.sep + j)

        #Local data saving
                dataBlock = array([ene,theta,xmu,fluoX,xmuS,fluoXraw,\
                I0,I1,I2,I3],"f")
                numpy.savetxt(ActualFileNameData, transpose(dataBlock))
                FInfo = file(ActualFileNameInfo,"w")
                FInfo.write("#.txt file columns content is:\n")
                FInfo.write("# 1) Energy\n")
                FInfo.write("# 2) Angle\n")
                FInfo.write("# 3) Transmission\n")
                FInfo.write("# 4) Fluorescence\n")
                FInfo.write("# 5) Standard\n")
                FInfo.write("# 6) RawFluorescence\n")
                FInfo.write("# 7) I0\n")
                FInfo.write("# 8) I1\n")
                FInfo.write("# 9) I2\n")
                FInfo.write("#10) I3\n")
                FInfo.write("#TimeAtStart = %s\n" % (timeAtStart))
                FInfo.write("#TimeAtStop  = %s\n" % (timeAtStop))
                FInfo.write("#Scan from %g to %g at velocity= %g eV/s\n" % (e1, e2, velocity))
                FInfo.write("#Counter Card Config\n")
                for i in self.cardCTsavedAttributes:
                    FInfo.write("#%s = %g\n" % (i,self.cardCT.read_attribute(i).value))
                FInfo.write("#Analog  Card Config\n")
                #Report in file Info dark currents applied
                FInfo.write("#Dark_I0= %9.8f\nDark_I1= %9.8f\nDark_I2= %9.8f\nDark_I3= %9.8f\n"\
                %(self.cardAI_dark0,self.cardAI_dark1,self.cardAI_dark2,self.cardAI_dark3,))
                #
                for i in self.cardAIsavedAttributes:
                    FInfo.write("#%s = %g\n" % (i, self.cardAI.read_attribute(i).value))
        
                #XIA self.cards
                for xia in self.cardXIA:
                    FInfo.write("#DxMap Card Config: %s\n"%xia.label)
                    FInfo.write("#Config File: %s\n" %(xia.DP.currentConfigFile))
                    FInfo.write("#Mode : %s\n" %(xia.DP.currentMode))
                    FInfo.write("#ROI(s) : \n")
                    for i in xia.DP.getrois():
                        FInfo.write("#%s\n" % i)

                #DCM Config follows:
                try:
                    FInfo.write("#Monochromator Status:\n")
                    for __self.dcmStatusBit in tuple(["#%s\n"%i for i in self.dcm.status().split("\n")]):
                        FInfo.write("#%s" % __self.dcmStatusBit)
                except:
                    print self.dcm.status()
                    print "Error reporting monochromator status."

                #MOSTAB Config follows:
                try:
                    FInfo.write("#MOSTAB Status:\n")
                    for __mostabStatusBit in tuple(["#%s\n"%i for i in mostab.status().split("\n")]):
                        FInfo.write("#%s" % __mostabStatusBit)
                except:
                    print mostab.status()
                    print "Error reporting MOSTAB status."
               
                #Where All Info follow
                for i in wa(returns=True, verbose=False):
                    FInfo.write("#" + i + "\n")
                FInfo.close()
        
                os.system("cp " + ActualFileNameData +" " +filename2ruche(ActualFileNameData))
                os.system("cp " + ActualFileNameInfo +" " +filename2ruche(ActualFileNameInfo))            
                print myTime.asctime(), " : Data saved to backup."
                shell.logger.log_write("Data saved in %s at %s\n" % (ActualFileNameData, myTime.asctime()), kind='output')
                #Measure time spent for saving data
                print "Time spent for data saving, backup and refresh plots: %3.2fs" % (myTime.time()-DataSavingTime)
                try:
                    if e1 < e0 <e2:
                        #thread.start_new_thread(dentist.dentist, (ActualFileNameData,), {"e0":e0,})
                        if mode.startswith("f"):
                            dentist.dentist(ActualFileNameData, e0 =e0, mode="f")
                        else:
                            dentist.dentist(ActualFileNameData, e0 =e0, mode=mode)
                except KeyboardInterrupt:
                    raise
                except Exception, tmp:
                    print tmp
        except Exception, tmp:
            try:
                outtaHDF.close()
            except:
                raise tmp
            try:
                for __i in XIAfiles:
                    for __j in __i:
                        try:
                            __j.close()
                            myTime.sleep(0.25)
                        except:
                            pass
            except:
                pass
            print tmp
        finally:
            try:
                outtaHDF.close()
            except:
                pass
            try:
                for __i in XIAfiles:
                    for __j in __i:
                        try:
                            __j.close()
                            myTime.sleep(0.25)
                        except:
                            pass
            except:
                pass
            if self.dcm.state() <> DevState.MOVING:
                self.dcm.velocity(60)
        #Finally stop FTPclients
        for xia in self.cardXIA:
            xia.FTPclient.stop()
        
        
        #Write END of the Story
        shell.logger.log_write("Total Elapsed Time = %i s" % (myTime.time() - TotalScanTime), kind='output')
        print "Total Elapsed Time = %i s" % (myTime.time() - TotalScanTime) 
        
        AlarmBeep()
        return
    


    def ecscan(self,fileName,e1,e2,n=1,dt=0.04,velocity=10, e0=-1, mode="",shutter=False,beamCheck=True,backlash=100):
        """Start from e1 (eV) to e2 (eV) and count over dt (s) per point.
        velocity: Allowed velocity doesn't exceed 40eV/s.
        The backup folder MUST be defined for the code to run.
        Global variables: FE and obxg must exist and should point to Front End and Shutter
        The filename: the only acceptable characters are [a-Z][0-9] + - . _ @ failing to do so will cause an exception
        """
        
        ecscanPrepare(self,fileName,e1,e2,dt,velocity, e0, mode,shutter,beamCheck,backlash):

        try:
            for i in range(n):
                #function arguments are: fileName, e1, e2 ,dt, velocity, e0, mode, shutter, beamCheck, backlash, CurrentScan, NofScans
                ecscanActor(self,e1,e2,dt,velocity, e0, mode,shutter, beamCheck,backlash,i,n)
        except KeyboardInterrupt:
            shell.logger.log_write("ecscan halted on user request: Ctrl-C\n", kind='output')
            print "Halting on user request."
            sys.stdout.flush()
            stopscan(shutter)
            print "ecscan halted. OK."
            print "Raising KeyboardInterrupt as requested."
            sys.stdout.flush()
            raise KeyboardInterrupt
        except Exception, tmp:
            shell.logger.log_write("Error during ecscan:\n %s\n\n" % tmp, kind='output')
            print tmp
            stopscan(shutter)
            #raise
        return 

