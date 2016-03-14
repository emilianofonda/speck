from time import sleep,time
import PyTango
from PyTango import DeviceProxy, DevState
from exceptions import Exception
import exceptions
import numpy, scipy
from numpy import sin,cos,tan,arcsin,pi,arange,sign,array,nan,sqrt
from scipy import interpolate
import thread

from motor_class import *
from counter_class import counter
import moveable
from spec_syntax import move_motor

class sagittal_bender:
    def __init__(self,bender1_name="",bender2_name="",DataViewer="",deadtime=0.01,timeout=.0):
        """ Help to come.
        bender.c1=A1_1*1/R+A0_1
        bender.c2=A1_2*1/R+A0_2"""
        
        self.label="Bender :"+bender1_name+" + "+bender2_name
        self.c1 = moveable.moveable(bender1_name,"position")
        self.c2 = moveable.moveable(bender2_name,"position")
        self.DataViewer = DeviceProxy(DataViewer)
        self.timeout = timeout
        self.deadtime = deadtime
        return
        
    def __str__(self):
        return "MOTOR"
        
    def __repr__(self):
        return self.label+" at %10.6f"%(self.pos())
    
    def subtype(self):
        return "SAGITTAL BENDER"
    
    def compute_state(self):
        """State returns MOVING if one of the benders is moving, in any other case combined state with (state of 1) OR (state of 2) is returned. 
        This is a workaround since OFF has priority over MOVING and the code must follow motors movement even if one is OFF."""
        s1=self.c1.state()
        s2=self.c2.state()
        s12=[s1,s2]
        if DevState.MOVING in s12: 
            return DevState.MOVING
        if s12==[DevState.STANDBY,DevState.STANDBY]: 
            return DevState.STANDBY
        if s12==[DevState.UNKNOWN,DevState.UNKNOWN]: 
            return DevState.UNKNOWN
        if DevState.OFF in s12: 
            return DevState.OFF
        if DevState.DISABLE in s12: 
            return DevState.DISABLE
        if DevState.ALARM in s12: 
            return DevState.ALARM
        else:
            return s1 and s2

    def offset(self,dest=None):
        """Set an offset over C1 and C2 motors in motor steps.
        If you have to increase the value of the bender.pos od DX, 
        you have to type bender.offset(DX) and this function will set 
        a -DX offset on the two motors."""
        oc1=self.c1.offset()
        oc2=self.c2.offset()
        if dest<>None:
            self.c1.offset(oc1-dest)
            self.c2.offset(oc2-dest)
        return {"Old offsets":[oc1,oc2],"New offsets":[self.c1.offset(),self.c2.offset()]}
    
    def stop(self):
        self.c1.stop()
        self.c2.stop()
        return self.state()

    def on(self):
        self.c1.on()
        self.c2.on()
        return self.state()

    def off(self):
        self.c1.off()
        self.c2.off()
        return self.state()

    
    def r(self,dest=None,wait=True):
        """Radius in meters. Can send the bender to a curvature radius if specified.
        The actual calibration has been made on the curvature: 1/R which is linear with energy or sin(theta)"""
        if dest==None:
            return 1./self.curv()
        else:
            return 1./self.curv(1./dest,wait=wait)

    def calculate_steps_for_r(self,dest):
        """Radius in meters. Returns the bender steps for the specified r in m.
        The actual calibration has been made on the curvature: 1/R which is linear with energy or sin(theta)"""
        return self.calculate_steps_for_curv(1./dest)
        

    def curv(self,dest=None,wait=True):
        """The calibration is in the A1_1,A0_1... constants. C1=A1_1/R+A0_1, C2=...
        curv=0.5*(C1-A0_1)/A1_1+0.5*(C2-A0_2)/A1_2
        The position is returned in 1/m or the bender is sent to that value."""
        if dest==None:
            return ((self.c1.pos()-self.DataViewer.A10)/self.DataViewer.A11+(self.c2.pos()-self.DataViewer.A20)/self.DataViewer.A21)*0.5
        else:
            self.c1.go(dest*self.DataViewer.A11+self.DataViewer.A10)
            self.c2.go(dest*self.DataViewer.A21+self.DataViewer.A20)
            if not wait: return dest
            wait_motor(self.c1,self.c2)
            return self.curv()

    def calculate_steps_for_curv(self,dest=None):
        """Curvature in 1/m. Returns the C1 and C2 bender motors steps for the specified 1/r in 1/m.
        The calibration is in the A1_1,A0_1... constants. C1=A1_1/R+A0_1, C2=..."""
        return [dest*self.DataViewer.A11+self.DataViewer.A10,dest*self.DataViewer.A21+self.DataViewer.A20]
    
    def pos(self,dest=None,wait=True):
        if(dest==None):
            return 0.5*(self.c1.pos()+self.c2.pos())
        ss=self.state()
        if(ss in [DevState.DISABLE,DevState.OFF,DevState.UNKNOWN]):
            print "At least one motor is in Off,Unknown or Disable state!!!"
            self.stop()
            raise Exception("Bender in bad state")
        dest1=dest-self.pos()+self.c1.pos()
        #dest1=dest+self.asy_value*0.5
        dest2=dest-self.pos()+self.c2.pos()
        #dest2=dest-self.asy_value*0.5
        try:
            if(not(wait)):
                self.c1.go(dest1)
                self.c2.go(dest2)
                return dest
            self.c1.go(dest1)
            self.c2.go(dest2)
            t=time()
            while((self.state()<>DevState.MOVING) and (time()-t<self.timeout)):
                sleep(self.deadtime)
            while(self.state()==DevState.MOVING): 
                sleep(self.deadtime)
                pass
                #print "Bender=%8.3f\r"%(self.pos(dest=None)),
                
        except (KeyboardInterrupt,SystemExit), tmp:
            self.stop()
            print ""
            raise tmp                                
        except Exception, tmp:
            self.stop()
            #if(self.MotOff):
            #    self.mo()
            #    print ""
            #    print "Motors OFF"
            print "Stopped over exception"
            print  self.pos()
            raise tmp
        #print ""
        return self.pos()
        
    def go(self,dest):
        return self.pos(dest, wait=False)
        
    def fire(self,dest=None):
        """Legacy, to be dropped."""
        if dest==None:
                    return self.go()
        return self.go(dest)
                                                            
    def asy(self,dest=None,wait=True):
        """Asymmetry is defined as bender1-bender2, this is a signed value: positive means bender1>bender2."""
        if(dest==None):
            print "Last memorised value=%g This will be applied to next bender movement"%(self.asy_value)
            return (self.c1.pos()-self.c2.pos())
        ss=self.state()
        if(ss==DevState.MOVING):
            raise Exception("Motors are already moving !!!")
        if(ss in [DevState.DISABLE,DevState.OFF,DevState.UNKNOWN]):
            print "At least one motor is in Off,Unknown or Disable state!!!"
            self.stop()
            raise Exception("Bender: at least one motor is in Off,Unknown or Disable state!!!")
        dest1=self.c1.pos()+0.5*(dest-(self.c1.pos()-self.c2.pos()))
        dest2=self.c2.pos()-0.5*(dest-(self.c1.pos()-self.c2.pos()))
        try:
            self.c1.go(dest1)
            self.c2.go(dest2)
            self.asy_value=dest
            if(not(wait)):
                return dest
            t=0.
            while(((self.c1.state()<>DevState.MOVING) and (self.c2.state()<>DevState.MOVING)) and (t<self.timeout)):
                sleep(self.deadtime)
                t+=self.deadtime
            while((self.c1.state()==DevState.MOVING) or (self.c2.state()==DevState.MOVING)): 
                sleep(self.deadtime)
                #print "Asy=%8.3f\r"%(self.c1.pos()-self.c2.pos()),
        except (KeyboardInterrupt,SystemExit), tmp:
                self.stop()
                self.asy_value=self.c1.pos()-self.c2.pos()
                raise tmp                                
        except Exception, tmp:
            print "Stopped on exception"
            self.stop()
            self.asy_value=self.c1.pos()-self.c2.pos()
            print ""
            #if(self.MotOff):
            #    self.mo()
            #    print "Motors OFF"
            raise tmp
        #print ""
        return self.asy()

    def status(self):
        return "Status does not exist for this bender."

    def state(self):
        """The state function of the bender do not incorporate a check of the bender anymore.""" 
        try:
            s=self.compute_state()
        except (KeyboardInterrupt,SystemExit), tmp:
            self.c1.stop()
            self.c2.stop()
            raise tmp                                
        except Exception, tmp:
            self.c1.stop()
            self.c2.stop()
            print self.label," stopped over exception"
            print  self.pos()
            raise tmp
        return s
    

class mono1:
    def __init__(self,\
        monoName="",DataViewer="",\
        rx1=None,\
        tz2=None,\
        ts2=None,\
        rx2=None,\
        rs2=None,\
        rx2fine=None,\
        rz2=None,\
        tz1=None,\
        bender=None,\
        timeout=.00,deadtime=0.01,delay=0.0,
        counter_label="d09-1-c00/ca/cpt.1",
        counter_channel=0,\
        emin=None,emax=None):
        """Experimental version: use galil and powerBrick moveables"""
        self.DP = DeviceProxy(monoName)
        self.DataViewer = DeviceProxy(DataViewer)
        self.label = monoName
        self.bender = bender
        try:
            self.counter=counter(counter_label)
        except:
            self.counter=None
            print "No usable counter: no tuning possible"
        self.counter_channel=counter_channel
        self.bender=bender
        self.timeout=timeout
        self.deadtime=deadtime
        self.delay=delay
        self.counter_channel=counter_channel
        self.emin=emin
        self.emax=emax
        self.motors=[]
        self.m_rx1=rx1
        self.m_tz2=tz2
        self.m_ts2=ts2
        self.m_rx2=rx2
        self.m_rz2=rz2
        self.m_rs2=rs2
        self.m_rx2fine=rx2fine
        self.m_tz1=tz1

        ##Section LocalTable. This part relies on the dcm device
        if list(self.DP.get_property("SPECK_UseLocalTable")["SPECK_UseLocalTable"]) ==[]:
            self.DP.put_property({"SPECK_UseLocalTable": False})
        if list(self.DP.get_property("SPECK_LocalTable")["SPECK_LocalTable"]) == []:
            self.DP.put_property({"SPECK_LocalTable": [0,"Energy","C1","C2","RS2"]})
            self.DP.put_property({"SPECK_UseLocalTable": False})
        print "\nmono1PBR: Reading LocalTable from database...",
        self.readTable()
        print "OK"
        return
        
    def __str__(self):
        return "MOTOR"
        
    def __repr__(self):
        print ""
        self.printTable()
        self.printEnables()
        return self.label+" at %10.6f"%(self.pos())
    
    def subtype(self):
        return "SAMBA MONOCHROMATOR"

    def init(self):
        return self.DP.init()

    def on(self):
        for i in self.motors: i.on()
        return self.state()
        
    def off(self):
        for i in self.motors: i.off()
        return self.state()
   
    def readTable(self):
        """This function reads the table from the database and prepare the interpolation.
        ADVANCED FEATURE: this function is for the code internal use only. """
        lt = list(self.DP.get_property("SPECK_LocalTable")["SPECK_LocalTable"])
        ult = list(self.DP.get_property("SPECK_UseLocalTable")["SPECK_UseLocalTable"])
        if ult == []:
            self.useLocalTable = False
        elif ult[0] == "False":
            self.useLocalTable = False
        elif ult[0] == "True":
            self.useLocalTable = True
        else:
            self.useLocalTable = False
        np = int(lt[0])
        self.LocalTable = {"Points":int(lt[0])}
        if self.LocalTable["Points"] == 0:
            self.useLocalTable = False
            for i in ["Energy","C1","C2","RS2"]:
                self.LocalTable[i] = array([],"f")
            #for i in ["Energy","C1","C2","RS2","RX2FINE"]:
            #    self.LocalTable[i + "_spline"] = []
            self.useLocalTable = False
            return
        for i in range(4): 
            #print array(lt[i * (np+1) + 2:(np+1) * (i+1) + 1],"f")
            self.LocalTable[lt[i * (np + 1) + 1]] = array(lt[i * (np+1) + 2:(np+1) * (i+1) + 1],"f")
        #print self.LocalTable
        if np == 1:
            self.useLocalTable = False
            #for i in ["Energy","C1","C2","RS2","RX2FINE"]:
            #    self.LocalTable[i + "_spline"] = []
            return
        #x = self.LocalTable["Energy"]
        #for i in ["C1","C2","RS2","RX2FINE"]:
        #    y = self.LocalTable[i]
        #    self.LocalTable[i + "_spline"] = interpolate.splrep(x,y,k=min(3,np-1))
        return

    def writeTable(self, fileName=""):
        """Code internal use only: advanced feature. Write in-memory table to database.
        If a fileName is specified the table is written to a file and to the database."""
        if self.LocalTable["Points"] < 1:
            print "Cannot Write Table to database for less than 2 points"
            return
        outList =[self.LocalTable["Points"],]
        for i in ["Energy","C1","C2","RS2","RX2FINE"]:
            outList += [i,] + list(self.LocalTable[i])
        self.DP.put_property({"SPECK_LocalTable": outList})
        if fileName == "":
            return
        else:
            fOut = file(fileName, "w")
            for i in outList:
                fOut.write(str(i)+"\n")
            fOut.close()
        return

    def readTableFile(self, fileName = ""):
        """This function reads the table from a file, puts it in the database and then re read it to memory
        Use setLocalTable or unsetLocalTable to activate or disable the table."""
        if fileName <> "":
            fIn = file(fileName, "r")
            ll = fIn.readlines()
            fIn.close()
            outList = map(lambda x: x.strip(), ll)
            self.DP.put_property({"SPECK_LocalTable": outList})
            self.readTable()
            self.setLocalTable()
        else:
            return

    def setLocalTable(self):
        """Turn on the local mode. The bender will follow a local interpolation.
        Use unsetLocalTable to turn this option off. If the table is not defined, 
        the useLocalTable flag will be set to False"""
        self.useLocalTable = True
        self.DP.put_property({"SPECK_UseLocalTable":True})
        self.readTable()
        return

    def unsetLocalTable(self):
        """Turn off the local mode. The bender will not follow a local interpolation.
        Use setLocalTable to turn this option on."""
        self.useLocalTable = False
        self.DP.put_property({"SPECK_UseLocalTable":False})
        return

    def takeValue(self, xtol=10):
        """Take current position and use it for LocalTable interpolation.
        The setLocalTable command must be used only after the table has been 
        completed (2 values at least).
        Before creating a new table the command clearLocalTable must be used 
        to remove the old table values.
        A value in energy closer than xtol is replaced"""
        pointValue = {"Energy": self.pos(), "C1": self.bender.c1.pos(),\
        "C2": self.bender.c2.pos(),"RS2": self.m_rs2.pos(),"RX2FINE": self.m_rx2fine.pos()}
        idx = self.LocalTable["Energy"].searchsorted(pointValue["Energy"])
        if numpy.any(abs(self.LocalTable["Energy"] - pointValue["Energy"]) < xtol ):
            #Replace Value
            print "Replacing Value in Table at position ",
            idx = min(self.LocalTable["Energy"].searchsorted(pointValue["Energy"]),\
            len(self.LocalTable["Energy"])-1)
            if (abs(self.LocalTable["Energy"][idx] - pointValue["Energy"]) > xtol):
                idx = max(idx-1, 0)
            print idx
            for i in ["Energy","C1","C2","RS2","RX2FINE"]:
                self.LocalTable[i][idx] = pointValue[i]
        else:
            self.LocalTable["Points"] += 1
            for i in ["Energy","C1","C2","RS2","RX2FINE"]:
                self.LocalTable[i] = array(list(self.LocalTable[i][:idx]) + [pointValue[i],]\
                + list(self.LocalTable[i][idx:]),"f")
        #Update database if possible
        if self.LocalTable["Points"] > 1:
            print "Syncing table to database...",
            self.writeTable()
            print "OK"
            print "Reading table from database...",
            self.readTable()
            print "OK"
            print "Activating table...",
            self.setLocalTable()
            print "OK"
        return
        
    def clearLocalTable(self):
        self.DP.put_property({"SPECK_LocalTable":[0,"Energy","C1","C2","RS2","RX2FINE"]})
        self.DP.put_property({"SPECK_UseLocalTable":False})
        self.readTable()
        self.unsetLocalTable()
        return
    
    def printTable(self):
        print "--------------------------"
        print "Using Table ?",
        if self.useLocalTable:
            print "Yes"
        else:
            print "No"
        print "--------------------------"
        cols= self.LocalTable.keys()
        cols.remove("Energy")
        cols.remove("Points")
        cols= ["Energy",]+cols
        #for i in list(cols):
        #    if i.endswith("_spline"):
        #        cols.remove(i)
        for i in cols:
            print "%-15s\t"%i,
        print ""
        for i in range(self.LocalTable['Points']):
            for j in cols:
                out ="%-15.5f\t" % (self.LocalTable[j][i])
                print out,
            print ""
        return
    
    def printEnables(self):
        print "Active Couplings"
        print "________________"
        for i in ["Ts2","Rz2","Rs2"]:
            print "%8s active ?"%i, bool(self.DataViewer.__getattr__("Enable"+i))
        return

    def calculateParametersFromTable(self):
        """Take the localTable and calculate the coeffs of equations.
        Write them in the dataviewer. The original coeffs can be restored with restoreDefaultValues
        Rs2 and Rz2 are hardcoded to be linearly interpolated."""
               
        return

    def restoreDefaultValues(self):
        """Use the DefaultValues stored as a property in DataViewer to reset the coeffs of equations.
        Values are written in the property SPECK_DefaultValues of DataViewer."""
        DefVal = self.DataViewer.get_property("SPECK_DefaultValues")['SPECK_DefaultValues']
        for i in DefVal:
            s = i.split("=")
            self.DataViewer.write_attribute(i[0].strip(),float(i[1]))
        return

    def disable_ts2(self):
        self.DataViewer.EnableTs2 = 0
        return
    def enable_ts2(self):
        self.DataViewer.EnableTs2 = 1
        return

    def enable_rs2(self):
        self.DataViewer.EnableRs2 = 1
        return
    def disable_rs2(self):
        self.DataViewer.EnableRs2 = 0
        return

    def enable_rz2(self):
        self.DataViewer.EnableRz2 = 1
        return
    def disable_rz2(self):
        self.DataViewer.EnableRz2 = 0
        return

    def sample_at(self,distance=None):
        if distance==None:
            return self.DataViewer.q
        else:
            if self.state()==DevState.MOVING:
                raise Exception("Trying to write q on dcm while dcm is moving!")
            self.DataViewer.q = float(distance)
            return self.sample_at()

    def status(self):
        return "Nothing yet"

    def state(self):
        """In the PBR setup of SAMBA if the combined axis is in DISABLE state, it doesn't mean that the mono is not MOVING.
        On the other hand if the combined state is MOVING the other axis may be in disable. The state machine differs from usual."""
        s = self.state() 
        if s == DevState.MOVING:
            return s
        elif s == DevState.OFF:
            return DevState.OFF
        j=[]
        for i in self.motors:
            tmp = i.state()
            if tmp == DevState.MOVING: return DevState.MOVING
            j.append(tmp)
        if j==[DevState.STANDBY,]*len(j):
            return DevState.STANDBY
        if j==[DevState.UNKNOWN,]*len(j):
            return DevState.UNKNOWN
        if j==[DevState.OFF,]*len(j):
            return DevState.OFF
        if DevState.DISABLE in j:
            return DevState.DISABLE
        if DevState.ALARM in j:
            return DevState.ALARM
        j=self.motors[0].state()
        for i in self.motors[1:]:
            j=(i.state() and j)
        return j

    def stop(self):
        self.DP.stop()
        for i in self.motors:
            try:
                i.stop()
            except:
                print i.label," is not responding!\n"
        return
        
    def e2theta(self,energy):
        """Calculate the energy for a given angle"""
        return arcsin(12398.41857/(2.*self.DataViewer.d*energy))/pi*180.

    def theta2e(self,theta):
        """Calculate the angle for a given energy"""
        return 12398.41857/(2.*self.DataViewer.d*sin(theta/180.*pi))

    def ts2(self,theta):
        """Calculate ts2 position for a given angle"""
        return max(35., self.DataVivewer.H*0.5/sin(theta/180.*pi))

    def tz2(self,theta):
        """Calculate tz2 position for a given angle"""
        return self.DataViewer.H*0.5/cos(theta/180.*pi)
    
    def calculate_curvature(self,theta):
        """The sample distance and source distance are referred to the center of rotation of the first crystal.
        This is not exact, but turns out to be a good approximation. The more accurate code is commented and ready for use."""
        th=theta/180.*pi
        rec_p1=1./self.DataViewer.q
        if self.sample_at()<>0.: 
            rec_q1=1./self.sample_at()
        else:    
            raise Exception("Monochromator "+self.label+" sample_at() == 0 ?!?")
        if th<=0.:
            raise Exception("Monochromator "+self.label+"Cannot compute curvature for theta<=0!")
        return 0.5 * (rec_p1 + rec_q1) / sin(th)
    
    def calculate_curvatureradius(self,theta):
        return 1./self.calculate_curvature(theta)

    def pos(self, energy=None, wait=True):
        """Move the mono at the desired energy, it uses current couplings and mode."""
        try:
            if(energy==None):
                ps=self.m_rx1.pos()
                if ps==0.: return 9.99e12
                return self.theta2e(ps)
            if self.emin <> None and energy < self.emin:
                raise Exception("Requested energy below monochromator limit: %7.2f"%self.emin)
            if self.emax <> None and energy > self.emax:
                raise Exception("Requested energy above monochromator limit: %7.2f"%self.emax)
            theta = self.e2theta(energy)
        #
        #Write movement code here 
        #
        except (KeyboardInterrupt,SystemExit), tmp:
            self.stop()
            raise tmp
        except PyTango.DevFailed, tmp:
            self.stop()
            raise tmp
        except PyTango.DevError, tmp:
            self.stop()
            raise tmp
        except Exception, tmp:
            self.stop()
            print "\nUnknown Error"
            print "Positions energy, theta=", self.pos(), self.m_rx1.pos()
            raise tmp
        return self.pos()

    def move(self,energy=None,wait=True):
        """Please use pos instead. Move is obsolete and subject ro removal in next future. """
        return self.pos(energy,wait)

    def go(self,energy=None,wait=False):
        """Go to energy and do not wait. This does not work with the mono1b class: use of galil_mulitaxis!"""
        return self.pos(energy,wait)    
        
    def theta(self,theta=None,wait=True):
        if(theta==None):
            return self.m_rx1.pos()
        return self.pos(self.theta2e(theta),wait)

    def calibrate(self,experiment_energy,true_energy):
        """This function applies a new offset to the main rotation rx1. 
        It requires the experimental energy position of the spectral feature as first argument
        and the true energy of the feature as second argument
        calibrate(Energy_I_See,Energy_From_Tables)"""
        print "Main goniometer offset was: %8.6f"%(self.m_rx1.offset())
        offset=self.m_rx1.offset()+self.e2theta(true_energy)-self.e2theta(experiment_energy)
        print "New goniometer offset is:   %8.6f"%(offset)
        oe=self.pos()
        self.m_rx1.offset(offset)
        return {"Old energy":oe,"New energy":self.pos()}


    def tune(self,piezomin=1.,piezomax=9.,np=20,tolerance=0.005,countingtime=0.2,nested=False):
        #try:
        #    return self.m_rx2fine.tune(p1=piezomin, p2= piezomax, np = 100, draw = False, offset = 0.)
        #except:
        #    return self.old_tune(self,piezomin=1.,piezomax=9.,np=20,tolerance=0.005,countingtime=0.2,nested=False)
        return self.old_tune(piezomin=1.,piezomax=9.,np=20,tolerance=0.005,countingtime=0.2,nested=False)

    def old_tune(self,piezomin=1.,piezomax=9.,np=20,tolerance=0.005,countingtime=0.2,nested=False):
        """Scan the mono.m_rx2fine motor to achieve maximum intensity in the desired counter/channel.
        Set the piezo to the position, returns the position in terms of voltage to apply.
        Feedback and control values differ on a piezo, the control value is always returned."""
        if self.counter==None:
            return
        cpt=self.counter
        channel=self.counter_channel
        #if(self.__userx2fine==False): 
        #    print "dcm setup excludes a piezo. Tuning is nonsense without the piezo."
        #    return 0.
        if(np<4):
            print "I use minimum 4 intervals (5 points). I set np=4."
            np=4
        piezomax=max(piezomin,piezomax)
        if (float(piezomax-piezomin)/np>1.): np=int((piezomax-piezomin)/1.)+1
        dp=float(piezomax-piezomin)/np
        if(dp==0): return "Invalid Range"
        p=float(piezomin)
        scan=[[0.]*np,[0.]*np]
        t=time()
        self.m_rx2fine.pos(max(piezomin-0.2,0.1))
        sleep(0.1)
        self.m_rx2fine.pos(max(piezomin-0.1,0.1))
        sleep(0.1)
        for i in range(np):
            self.m_rx2fine.pos(p)
            scan[0][i]=p
            if type(channel)==int:
                scan[1][i]=cpt.count(countingtime)[channel]
            elif type(channel) in [tuple,list]:
                scan[1][i]=0
                ccs=cpt.count(countingtime)
                for j in channel:
                    scan[1][i]+=ccs[j]
            p+=dp
        try:
            optimum= sum(array(scan[0],"f")*(array(scan[1],"f")-min(scan[1])))/sum(array(scan[1],"f")-min(scan[1]))
            if optimum==nan: 
                print "Tuning failed!"
                optimum=5.
        except Exception, tmp:
            print sum(array(scan[1],"f"))
            print "No tuning found!"
            print "Returning 5 Volts as result... check it again!"
            optimum=5.
            print tmp
        if not(nested):
            dp=0.75
            optimum=self.old_tune(max(optimum - dp * 2.,0.1),min(optimum + dp*2.,9.9),np=np,tolerance=tolerance,countingtime=countingtime,nested=True)
            self.m_rx2fine.pos(optimum)
            print "Tuning this point took: %5.2f seconds"%(time()-t)
        return optimum
    
    def ftune(self,piezomin=1.,piezomax=9.,np=20,tolerance=0.005,countingtime=0.2,nested=False):
        """Scan the mono.m_rx2fine motor to achieve maximum intensity in the desired counter/channel.
        Set the piezo to the position, returns the position in terms of voltage to apply.
        Feedback and control values differ on a piezo, the control value is always returned."""
        I0_average=moveable.sensor("d09-1-c00/ca/sai.1","averagechannel0")
        if self.counter==None:
            return
        cpt=self.counter
        channel=self.counter_channel
        #if(self.__userx2fine==False): 
        #    print "dcm setup excludes a piezo. Tuning is nonsense without the piezo."
        #    return 0.
        if(np<4):
            print "I use minimum 4 intervals (5 points). I set np=4."
            np=4
        piezomax=max(piezomin,piezomax)
        if (float(piezomax-piezomin)/np>1.): np=int((piezomax-piezomin)/1.)+1
        dp=float(piezomax-piezomin)/np
        if(dp==0): return "Invalid Range"
        p=float(piezomin)
        scan=[[0.]*np,[0.]*np]
        t=time()
        self.m_rx2fine.pos(max(piezomin-0.2,0.1))
        sleep(0.1)
        self.m_rx2fine.pos(max(piezomin-0.1,0.1))
        sleep(0.1)
        for i in range(np):
            self.m_rx2fine.pos(p)
            scan[0][i]=p
            if type(channel)==int:
                #scan[1][i]=cpt.count(countingtime)[channel]
                scan[1][i]=I0_average.pos()
            elif type(channel) in [tuple,list]:
                scan[1][i]=0
                ccs=cpt.count(countingtime)
                for j in channel:
                    scan[1][i]+=ccs[j]
            p+=dp
        try:
            optimum= sum(array(scan[0],"f")*(array(scan[1],"f")-min(scan[1])))/sum(array(scan[1],"f")-min(scan[1]))
            if optimum==nan: 
                print "Tuning failed!"
                optimum=5.
        except Exception, tmp:
            print sum(array(scan[1],"f"))
            print "No tuning found!"
            print "Returning 5 Volts as result... check it again!"
            optimum=5.
            print tmp
        if not(nested):
            dp=0.75
            optimum=self.tune(max(optimum-dp,0.1),min(optimum+dp,9.9),np=np,tolerance=tolerance,countingtime=countingtime,nested=True)
            self.m_rx2fine.pos(optimum)
            print "Tuning this point took: %5.2f seconds"%(time()-t)
        return optimum
    
    def detune(self,fraction):
        """Use the mono1.tune method and then detune the two crystals to get a fraction of the intensity. 
        Tha value of fraction must be in the [-1:0[ or ]0:1] bounds."""
        if self.counter==None:
            return
        cpt=self.counter
        channel=self.counter_channel
        if fraction <=-1. or fraction>=1. or fraction==0.: 
            raise exceptions.Exception("Illegal range","fraction value is out of bounds",fraction)
        print "Finding maximum..."
        p=self.tune()
        imax=cpt.count(.2)[channel]
        print "Maximum=",imax/0.2," Position=",p
        inow=imax
        dp=0.1*sign(fraction)
        tolerance=0.01
        while (abs(float(inow)/imax-abs(fraction)) >=tolerance):
            print "detuning... step=%5.3f"%(dp)
            while(inow>abs(imax*fraction)):
                p+=dp
                self.m_rx2fine.pos(p)
                inow=cpt.count(0.2)[channel]
            p=p-dp
            self.m_rx2fine.pos(p)
            inow=cpt.count(0.2)[channel]
            dp=dp*0.2
        print "Detuned=",inow/0.2," Position=",p
        return p
    

    def seten(self, energy=None):
        if energy == None:
            return self.pos(energy,Ts2_Moves=True)
        try:
            shell=get_ipython()
            shell.user_ns["mostab"].stop()
        except Exception, tmp:
            print tmp
        try:
            shell.user_ns["mostab"].lmset(1.,9.)
            shell.user_ns["mostab"].pos(5.)
        except Exception, tmp:
            print tmp
        print "Enabling Ts2 movement...",
        self.enable_ts2()
        print "OK"
        try:
            self.m_rx2fine.pos(5)
        except:
            pass
        #
        #Insert Move code here
        #
        print "Disabling Ts2 movement...",
        self.disable_ts2()
        print "OK"
        try:
            shell.user_ns["mostab"].start()
        except:
            pass
        return self.pos()

