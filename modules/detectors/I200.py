from __future__ import print_function
#and now something completely different...
import time

import numpy
from pylab import plot

#import serial
import PyTango

from tango_serial import tango_serial

class I200_serial:

    def __init__(self, port=0, baudrate=115200, echo=1, deadtime=0.025):
        self.SerPort=serial.Serial(0)
        self.SerPort.baudrate=baudrate
        self.SerPort.timeout=0.4
        self.deadtime = deadtime
        self.label="I200_%i" % port
        if echo in [0, 1]: self.InOutS("SYST:COMM:TERM %1i"%echo)
        self.SerPort.flush()
        self.InOutS("*CLS")
        #Cleanup pending auto profile if active
        self.InOutS("PID:PROF 0")
        try:
            self.deadtime = min(0.2, max(0.025, 2*self.range()[1]))
            #if self.range()[1] >= self.deadtime:
            #    self.deadtime = self.range()[1]*2.
        except:
            pass
        print(self.version())
        return

    def __call__(self,arg = None):
        if arg != None:
            return self.InOutS(arg)
        print("I200 DAC is at ", self.pos())
        print("I0=%8.6e I1=%8.6e State=%s" % self.currents())
        print("mode = %s" % self.pid()["modename"])
        _i200_status = self.status()
        if _i200_status["PID_state"] == "Servo not running?":
            print("Servo not running?")
        else:
            print("DAC_write_0 = %s DAC_write = %s" % (_i200_status["DAC_write_0"], _i200_status["DAC_write"]))
        return

    def status(self):
        ll={}
        l=self.InOutS("READ:PID?",n=2)[1]
        if l.startswith("-221"):
            ll["PID_state"] = "Servo not running?"
        else:
            l=l.split(",")
            l[-1]=l[-1].strip()
            if l[-1] == '0' :
                ll["PID_state"] = "OK"
            elif l[-1] == '1' :
                ll["PID_state"] = "DAC limit hit!"
            elif l[-1] == '2' :
                ll["PID_state"] = "Data Invalid Or Current Below Low Limit!"
            j = 0
            for i in ["DAC_write_0", "DAC_write", "DAC_read", "F_actual", "F_target", "Sum", "DELTA", "Status"]:
                try:
                    ll[i] = l[j]
                    j += 1
                except Exception as tmp:
                    print(tmp)
                    break
        return ll

    def state(self):
        """Presently is fake mode: always STANDBY."""
        return PyTango.DevState.STANDBY

    def open(self):
        return self.SerPort.open()

    def close(self):
        return self.SerPort.close()

    def InOutS(self, message, n=None):
        self.SerPort.write(message+"\n")
        if n == None:
            return self.SerPort.readlines()
        else:
            out=[]
            for i in range(n):
                out.append(self.SerPort.readline())
            return out

    def version(self):
        return self.InOutS("*IDN?")[1:]

    def start(self):
        self.start_measurement()
        return self.start_servo()
    
    def stop(self):
        self.stop_servo()

    def pos(self, dest = None, wait = True):
        """Move the DAC to the desired position or report value"""
        if dest == None:
            return float(self.InOutS("VOLT?")[1].split(" ")[0])
        self.InOutS("voltage %8.6f" % dest)
        time.sleep(self.deadtime)
        return self.pos()
    
    def go(self, dest = None):
        return self.pos(dest, wait = False)

    def period(self, period = None):
        if period == None:
            per=self.InOutS("PER?")[1]
            return float(per.split(" ")[0])
        self.InOutS("PER %8.6f" % period)
        return self.period()
    
    def profile_internal(self, p1=0.5, p2=9.5, np=100, draw=True, verbose = 0):
        """Provide (and draw if draw=True) the target function over the interval p1 --> p2
        where p1 and p2 are the DAC limits. np is the number of points.
        Returned values are: (maximum position, center of mass and [x, y] data).
        The deadtime is useful: wrong results are provided over RS232 for deadtime< 2* integration."""
        dp=float(p2- p1) / np
        x=[]
        y=[]
        print("Profile...")
        ll = self.InOutS("PID:PROF 0",n=2)
        if verbose > 0:
            print(ll)
        ll = self.InOutS("PID:SERV 0",n=2)
        if verbose > 0:
            print(ll)
        self.pos(0.1)
        ll = self.InOutS("INIT",n=2)
        if verbose > 0:
            print(ll)
        ll = self.InOutS("CONF:PID:PROF:LIM %i %i" % (int(p1), int(p2)),n=2)
        if verbose > 0:
            print(ll)
        ll = self.InOutS("CONF:PID:PROF:POINTS %i" % (np),n=2)
        if verbose > 0:
            print(ll)
        ll = self.InOutS("PID:PROF 1",n=2)
        if verbose > 0:
            print(ll)
        for i in range(np):
            time.sleep(self.deadtime)
            ll=self.InOutS("FETCH:PROF?", n=2)
            if verbose > 1:
                print(ll)
            x.append(float(ll[1].split(",")[1]))
            cor_value = float(ll[1].split(",")[0])
            if cor_value == 1.:
                cor_value = 0
            y.append(cor_value)
        ll = self.InOutS("PID:PROF 0",n=2)
        if verbose > 0:
            print(ll)
        tmp=[numpy.arange(p1, p2 , dp), numpy.array(y)]
        if draw:
            plot(tmp[0], tmp[1])
            #plot(x,tmp[1])
        mp = tmp[0][tmp[1].argmax()]
        cmp = sum(tmp[0] * tmp[1]) / sum(tmp[1])
        print("maximum position is", mp)
        print("center of mass   is", cmp)
        return mp, cmp, tmp

    def profile(self, p1=1, p2=9, np=50, draw=True, verbose = 0):
        """Provide (and draw if draw=True) the target function over the interval p1 --> p2
        where p1 and p2 are the DAC limits. np is the number of points.
        Returned values are: (maximum position, center of mass and [x, y] data).
        The deadtime is useful: wrong results are provided over RS232 for deadtime< 2* integration."""
        mode=self.pid()["mode"]
        dt = self.period()*2.
        self.pos(p1)
        dp = float(p2 - p1) / np
        y = []
        print("Profile...")
        ll = self.InOutS("PID:SERV 0",n=2)
        if verbose > 0:
            print(ll)
        for p in numpy.arange(p1, p2+dp, dp):
            self.pos(p)
            time.sleep(dt)
            i1, i2 = self.currents()[0:2]
            if verbose >2 : 
                print("currents --> %g %g" % (i1, i2))
            if mode == 0:
                y.append(i1)
            elif mode == 1:
                y.append(i1 + i2)
            elif mode == 2:
                y.append(i1 - i2)
            elif mode == 3:
                y.append(i1 / i2)
            elif mode == 4:
                y.append((i1 - i2) / (i1 + i2 + 1e-14))
            tmp=[numpy.arange(p1, p2+dp, dp), numpy.array(y)]
        if draw:
            plot(tmp[0], tmp[1])
        mp = tmp[0][tmp[1].argmax()]
        cmp = sum(tmp[0] * tmp[1]) / sum(tmp[1])
        print("maximum position is", mp)
        print("center of mass   is", cmp)
        return mp, cmp, tmp

    def capacitor(self,capacity = None):
        if capacity == None:
            l=self.InOutS("CONF:CAP?")[1].strip().split(",")
            return int(l[0]),l[1]
        if capacity in [0,1]:
            self.InOutS("CONF:CAP %i"%(capacity))
        else:
            raise Exception("I200: wrong capacity value specified (must be 0 or 1).")   
        return self.capacitor()

    def currents(self):
        l=self.InOutS("READ:CURR?")
        ll=l[-1].split(",")
        i1 = float(ll[1].split(" ")[0])
        i2 = float(ll[2].split(" ")[0])
        overload = int(ll[3].strip())
        if overload: 
            ST="OVERLOAD"
        else:
            ST="OK"
        return i1,i2,ST

    def start_measurement(self):
        self.InOutS("INIT")
        r=self.range()[0]
        if self.currents()[2] == "OVERLOAD": r = r * 10
        while(self.currents()[2] == "OVERLOAD" and r <= float(self.capacitor()[1].split()[0]) / 1e-5):
            self.range(r)
            r = r * 10
        return self.currents()[2]

    def stop_measurement(self):
        self.stop_servo()
        return self.InOutS("ABORT",n=2)[1].strip()

    def start_servo(self):
        self.start_measurement()
        return self.InOutS("PID:SERV 1", n=2)[1].strip()

    def stop_servo(self):
        return self.InOutS("PID:SERV 0", n=2)[1].strip()
    
    def mode(self, mode = None):
        if mode == None:
            return self.pid()["mode"]
        self.pid(mode = mode)
        return self.mode()

    def pid(self,**kwargs):
        """The best way to learn to use this function is to provide no arguments and check output. 
        Try to use the output provided to set new parameters with the very same syntax:
        use the keywords of the dictionary as function keyword.
        e.g.: pid provides {"KP": 1} use pid(KP=0.1) to change the parameter to 0.1
        NOTA BENE: case of names matters!"""
        modes={0:"I1", 1:"I1 + I2", 2:"I1 - I2", 3:"I1 / I2", 4:"(I1 - I2) / (I1 + I2)"}
        if kwargs == {}:
            mode = int(self.InOutS("CONF:PID:MOD?", n=2)[1].strip())
            #print "mode = " + modes[mode]
            rate = int(self.InOutS("CONF:PID:RAT?", n=2)[1].strip())
            limits=(self.InOutS("CONF:PID:LIM?", n=2)[1].strip()).split(",")
            limits=[float(limits[0][:-1]),float(limits[1][:-1])]
            lowCurrent=float(self.InOutS("CONF:PID:I1I2LOW?", n=2)[1].strip())
            KP=float(self.InOutS("CONF:PID:KP?", n=2)[1].strip())
            KI=float(self.InOutS("CONF:PID:KI?", n=2)[1].strip())
            return {"mode": mode, "rate": rate, "limits": limits,"lowCurrent": lowCurrent,"KP": KP,"KI": KI,"modename":modes[mode]}
        for i in kwargs:
            if i == "mode":
                tmp=self.InOutS("CONF:PID:MOD %i" % kwargs[i])
            elif i == "rate":
                tmp=self.InOutS("CONF:PID:RAT %i" % kwargs[i])
            elif i == "lowCurrent":
                tmp=self.InOutS("CONF:PID:I1I2LOW %f" % kwargs[i])
            elif i == "limits":
                tmp=self.InOutS("CONF:PID:LIM %f %f" % tuple(kwargs[i]))
            elif i == "KP":
                tmp=self.InOutS("CONF:PID:KP %f" % kwargs[i])
            elif i == "KI":
                tmp=self.InOutS("CONF:PID:KI %f" % kwargs[i])
        return self.pid()

    def range(self, arg = None):
        """If no argument provided: returns range (A) and integration period (s)
        If a range is provided, it sets it."""
        if arg == None:
            t=float(self.InOutS("CONF:GAT:INT:PER?",n=2)[1].split(" ")[0])
            r=float(self.InOutS("CONF:GAT:INT:RANG?",n=2)[1].split(" ")[0])
            return r,t
        else:
            self.InOutS("CONF:GAT:INT:RANG %5.2e 1" % (float(arg)))
        try:
            if self.range()[1] > self.deadtime:
                self.deadtime = self.range()[1]*2.
        except:
            pass
        return self.range()
    
    def tune(self, p1=1, p2=9, np=100, offset = 0.025, draw=True):
        """Set the mode to I1+I2, maximize flux going to baricenter 
        then lock position to it starting servo in mode (I1-I2)/(I1+I2)"""
        self.stop()
        self.start_measurement()
        if self.currents()[2] != "OK":
            raise Exception("I200 currents reading not OK: %s" % self.currents[2])
        __mode = self.mode()
        if not self.mode() in [0, 1]:
           self.mode(1)
        if __mode in [0,1]:
           locked_pos=self.profile(p1 = p1, p2 = p2, np = np, draw=draw)[1]+offset
           #locked_pos=self.profile_internal(p1 = p1, p2 = p2, np = np, draw=draw)[1]+offset
           self.pos(locked_pos + offset)
        else:
           locked_pos=self.profile(p1 = p1, p2 = p2, np = np)[1]
           self.pos(locked_pos)
        if __mode in [0, 1]:
            self.pid(limits=[max(locked_pos - offset, 0.5), min(locked_pos + 10 * offset, 9.5)])
        else:
            self.pid(limits=[max(locked_pos - 2.5, 0.5), min(locked_pos + 2.5,9.5)])
        self.mode(__mode)
        #return 
        return self.start()
    
class I200_tango(I200_serial):
    
    def __init__(self, port=None, echo=1, EndOfLine=10, Space=32, deadtime=0.025):
        """System is asymmetric: 10 is sent to end command, while 10,13 is received"""
        myEOL={10:"\n",13:"\r"}
        self.serial=tango_serial(port, EndOfLine=[EndOfLine,], space=Space, deadtime=deadtime)
        self.deadtime=deadtime
        self.label="I200_" + port
        self.EndOfLine = myEOL[EndOfLine]
        if echo in [0, 1]:
            self.InOutS("SYST:COMM:TERM %1i"%echo)
        self.InOutS("*CLS")
        #Cleanup pending auto profile if active
        self.InOutS("PID:PROF 0")
        try:
            self.deadtime = min(0.2, max(0.025, 2*self.range()[1]))
            #if self.range()[1] >= self.deadtime:
            #    self.deadtime = self.range()[1]*2.
        except:
            pass
        print(self.version())
        return

    def open(self):
        """Unused in the tango_serial version"""
        return

    def close(self):
        """Unused in the tango_serial version"""
        return

    def InOutS(self, message, n=None):
        """In the tango_serial version the value of n is not used."""
        ll = self.serial.writeread(message).split(self.EndOfLine)
        time.sleep(self.deadtime)
        l = self.serial.read()
        while(l != ""):
            ll.append(l)
            l = self.serial.read()
        return ll
    

