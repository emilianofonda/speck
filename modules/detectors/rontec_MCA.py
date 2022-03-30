from __future__ import print_function
from string import lower
import PyTango
from PyTango import DeviceProxy, DevState
from time import sleep,time,asctime
from numpy import mean,std,mod,average,sum

class rontec_MCA:
    """Rontec MCA model 2.2"""

    def __init__(self,devicename,deadtime=.025,delay=0.7,timeout=0.,verbose=True,chunckSize=256,energy_ranges=[10000,20000,40000]):
        try:
            self.DP=DeviceProxy(devicename)
        except PyTango.DevFailed as tmp:
            print("Error when defining :",motorname," as a rontec detector.\n")
            print(tmp.args)
            raise tmp
        self.deadtime=deadtime
        self.delay=delay
        self.timeout=timeout
        self.label=devicename
        self.verbose=verbose
        self.chunckSize=int(chunckSize)
        self.movingState=DevState.RUNNING
        self.__energy_ranges=energy_ranges
        return

        def __str__(self):
                return "MCA"

        def __repr__(self):
                return self.label+" at %10.6f"%(self.icr())

        def subtype(self):
                return "RONTEC"

    def wait(self):
        try:
            t0=time()
            while(self.state()!=self.movingState and time()-t0<self.timeout):
                sleep(self.deadtime)
            while(self.state()==self.movingState):
                sleep(self.deadtime)
            return self.state()
        except (KeyboardInterrupt, SystemExit) as tmp:
            self.stop()
            raise tmp
        except Exception as tmp:
            raise tmp
        
    def state(self):
                """No arguments, return the state as a string"""
        return self.DP.state()

    def status(self):
                """No arguments, return the status as a string"""
        #State bug workaround!
        self.state()
        return self.DP.status()

    def abort(self):
        return self.stop()

    def stop(self):
        """Just stop it: asynchronous command is used... watch out!"""
        if self.state()==self.movingState:
            #self.DP.command_inout_asynch("Abort",0)
            self.DP.command_inout_asynch("Abort")
        return
        
    def command(self,cmdstr,arg=""):
        """For adventurous users only: send a command_inout string, optionally with arguments"""
        if(arg==""):
            return self.DP.command_inout(cmdstr)
        else:
            return self.DP.command_inout(cmdstr,arg)
        return

    def init(self):
        self.state()
        self.command("Init")
        return

    def rontec(self,cmd_string):
        """Send a command string to rontec via SendRontecMessage"""
        return self.DP.command_inout("SendRontecMessage",cmd_string)

    def setROIs(self,*args):
        """Set multiple ROIs at the same time. Refer to detector documents."""
        if args==():
            return self.DP.read_attribute("roisStartsEnds").value
        if mod(len(args),2)!=0:
            raise Exception("rontec_MCA setROIs: Odd number of parameters provided!")
        args_str=[]    
        for i in args:
            args_str.append(str(i))
        self.command("SetROIs",args_str)
        sleep(self.delay)
        return self.setROIs()

    def setROI(self,*args):
        """Set a single ROI. Actually, it is most used to set just the first one. Device should be properly 
        configured to allow several ROIs to be defined.
        Syntax: setROI(start,end,channel=1) this syntax is reversed for confort of use with respect to the device
        command SetSingleROI which expect roi_number,start,end. The ROI number starts at 1."""
        if args==():
            return self.setROIs()
        if len(args)>3 and len(args)<2: 
            raise Exception("rontec_MCA setROI: wrong number of parameters provided!")
        if len(args)==2:
            channel=1
        if len(args)==3:
            channel=args[2]
            roi1,roi2=args[0:2]
        args_str=[str(channel),str(roi1),str(roi2)]    
        self.command("SetSingleROI",args_str)
        sleep(self.delay)
        return self.setROIs()
    
    def ATKautoReadDataSpectrum(self,flag=None):
        """This is a severe handicap in term of performance. 
        Please set this to false when scanning or working in pySamba."""
        if flag==None:
            return self.DP.read_attribute("readDataSpectrum")
        else:
            f=self.DP.read_attribute("readDataSpectrum").value
            if f!=flag:
                self.DP.write_attribute("readDataSpectrum",flag)
                sleep(self.delay)
                return self.ATKautoReadDataSpectrum()
    
    def icr(self):
        """Input count rate"""
        return self.DP.read_attribute("countRate").value
    
    def start(self,dt=None):
        """Start the MCA readout over time dt. Current time is used when not supplied."""
        if dt!=None and dt!=self.integrationTime():
            self.integrationTime(dt)
        self.command("Start")
        return
        
    def count(self,dt=None,l1=None,l2=None):
        """For integrationTime equal to zero it does not wait 
        since integration time is set to infinite!
        Just start the counting. If l1 or l2 are defined 
        return the MCA values between the limits."""
        try:
            self.ATKautoReadDataSpectrum(False)
            self.start(dt)
            if dt>0:
                self.wait()
            else:
                return []
            if l1!=None or l2!=None:
                if l1==None: l1=0
                if l2==None: l2=self.nbChannels()
                return self.readMCA(l1,l2)
            else:
                return []
        except (KeyboardInterrupt, SystemExit) as tmp:
            self.stop()
            raise tmp
        except Exception as tmp:
            raise tmp
            
    def readMCA(self,l1=0,l2=None):
        """Get the spectrum and returns it in a tuple. It can return just the part
        you desire, provide l1 and l2 limits in this case. Since it is time consuming, 
        get the minimum part that fits your needs."""
        if l2==None:
            l2=self.nbChannels()-1
        mca=[]
        l1=int(l1)
        l2=int(l2)
        l1,l2=min(l1,l2),max(l1,l2)
        if l2-l1<=self.chunckSize:
            return self.command("GetPartOfSpectrum",[str(l1),str(l2+1)])
        else:
            n=(l2+1-l1)/self.chunckSize
            r=(l2+1-l1)-n*self.chunckSize
            #print n,r
            for i in range(n):
                try:
                    #print l1+i*self.chunckSize,l1+(i+1)*self.chunckSize-1
                    mca+=self.readMCA(l1+i*self.chunckSize,l1+(i+1)*self.chunckSize-1)
                except Exception as tmp:
                    raise tmp
            if r>0:
                try:
                    #print l1+n*self.chunckSize,l1+n*self.chunckSize-1+r
                    mca+=self.readMCA(l1+n*self.chunckSize,l1+n*self.chunckSize-1+r)
                except Exception as tmp:
                    raise tmp
        return mca

    def saveMCA(self,filename="RontecMCA_output.txt",l1=0,l2=None,comment=""):
        """Save a two columns file containing the channel index and the MCA values."""
        if l2==None:
            l2=self.nbChannels()-1
        y=self.readMCA(l1,l2)
        handler=open(filename,'a')
        handler.write("#START data block. Timestamp is: "+asctime()+"\n")
        handler.write("#Comment string is: "+comment+"\n")
        
        for i in range(l1,l2+1):
            handler.write("%8i\t%8i\n"%(i,y[i-l1]))
        handler.write("#END data block.   Timestamp is: "+asctime()+"\n\n\n")
        handler.close()

    def nbChannels(self,nb=None):
        return self.DP.read_attribute("nbChannels").value

    def integrationTime(self,dt=None):
        if dt==None:
            return self.DP.read_attribute("integrationTime").value
        else:
            it=self.DP.read_attribute("integrationTime").value
            if dt!=it:
                self.DP.write_attribute("integrationTime",dt)
            sleep(self.delay)
            return self.integrationTime()
    def energyRange(self,energy=None):
        if energy==None:
            return self.DP.read_attribute("energy")
        energy=int(energy)
        if energy in [10000,20000,40000]:
            new_en=self.DP.read_attribute("energy").value
            if new_en!=energy:
                self.DP.write_attribute("energy",energy)
                sleep(self.delay)
        else:
            print("Energy ranges allowed are:",self.__energy_ranges)
            raise Exception("Rontec_MCA energy_range: the required energy limit is not authorized")
        return self.energyRange()

    def peltier(self,mode=1):
        """Set peltier mode:
            0: OFF
            1: thermostat (default mode, T=-14.4 C)
            2: maximum current (T can be as low as -25 C)"""
        self.rontec("$DK "+str(mode))
        sleep(self.delay)
        reply=self.rontec("$DF")
        return int(float(reply[4:5]))
        

    def temperature(self):
        """Return the Peltier temperature"""
        return self.DP.read_attribute("detectorTemperature").value
    
    
        
    def cycleTime(self,dt=None):
        if dt==None:
            return self.DP.read_attribute("cycleTime").value
        else:
            ct=self.DP.read_attribute("cycleTime").value
            if ct!=dt:
                self.DP.write_attribute("cycleTime",dt)
                sleep(self.delay)
            return self.cycleTime()
    
    def strobe(self,n=None):
        """n is the period in 10microsec base of the strobe."""
        if(n==None):
            s=self.rontec("$FN")
            #print self.rontec("$FN")
            return float(s.split()[1])
        s="$NP "+str(int(n))
        self.rontec(s)
        sleep(self.delay)
        return self.strobe()
