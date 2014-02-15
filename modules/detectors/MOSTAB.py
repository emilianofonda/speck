#and now something completely different...
import time

from ascan import ascan, ScanStats

import numpy
import pylab
from pylab import plot

#import serial
import PyTango

from tango_serial import tango_serial

class MOSTAB_serial:

    def __init__(self, port=0, baudrate=9600, echo=1, deadtime=0.05):
        self.SerPort=serial.Serial(0)
        self.SerPort.baudrate=baudrate
        self.SerPort.timeout=1
        self.deadtime = deadtime
        self.label="MOSTAB_%i" % port
        if echo == 0:
            self.InOutS("NOECHO")
        elif echo == 1:
            self.InOutS("ECHO")
        self.SerPort.flush()
        #self.InOutS("*CLS")
        #Cleanup pending auto profile if active
        #self.InOutS("PID:PROF 0")
        self.states_table = {
            "IDLE":PyTango.DevState.STANDBY,
            "MOVE":PyTango.DevState.MOVING,
            "SCAN":PyTango.DevState.MOVING,
            "SEARCH":PyTango.DevState.MOVING,
            "RUN":PyTango.DevState.RUNNING,
            "WAITBEAM":PyTango.DevState.RUNNING,
            "RUN":PyTango.DevState.RUNNING,
            "OVERLOAD":PyTango.DevState.ALARM,
            "ALARM":PyTango.DevState.ALARM
            }
        return

    def __call__(self,arg = None):
        if arg <> None:
            return self.InOutS(arg)
        print "MOSTAB is at ", self.pos()
        #print "I0=%8.6e I1=%8.6e State=%s" % self.currents()
        #print "mode = %s" % self.pid()["modename"]
        #_i200_status = self.status()
        #if _i200_status["PID_state"] == "Servo not running?":
        #    print "Servo not running?"
        #else:
        #    print "DAC_write_0 = %s DAC_write = %s" % (_i200_status["DAC_write_0"], _i200_status["DAC_write"])
        return

    def status(self):
        ll=[]
        ll.append(self.InOutS("?STATE"))
        ll.append(self.InOutS("?MODE"))
        ll.append(self.InOutS("?AMPLITUDE"))
        ll.append(self.InOutS("?FREQUENCY"))
        ll.append(self.InOutS("?PHASE"))
        ll.append(self.InOutS("?TAU"))
        ll.append(self.InOutS("?INBEAM"))
        ll.append(self.InOutS("?OUTBEAM"))
        ll.append(self.InOutS("?OPRANGE"))
        ll.append(self.InOutS("?PIEZO"))
        ll.append(self.InOutS("?SPEED"))
        ll.append(self.InOutS("?SLOPE"))
        return ll

    def state(self):
        ss = self.InOutS("?STATE")[1]
        return self.states_table[ss]

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
            for i in xrange(n):
                out.append(self.SerPort.readline())
            return out

    def version(self):
        return self.InOutS("?VER")[1:]

    def start(self):
        self.InOutS("GO")
        err = self.error()
        if err <> "OK":
            raise Exception("MOSTAB: " + err)
        return self.state()
   
    def stop(self):
        self.InOutS("STOP")
        err = self.error()
        if err <> "OK":
            raise Exception("MOSTAB: " + err)
        return self.state()

    def error(self):
        return self.InOutS("?ERR")[1]

    def pos(self, dest = None, wait = True):
        """Move the PIEZO to the desired position or report value"""
        if dest == None:
            return float(self.InOutS("?PIEZO")[1].split(" ")[0])
        self.InOutS("PIEZO %8.6f" % dest)
        err = self.error()
        if err <> "OK":
            raise Exception("MOSTAB: " + err)
        time.sleep(self.deadtime)
        if wait:
            while self.state() == PyTango.DevState.MOVING:
                time.sleep(self.deadtime)
        return self.pos()
    
    def go(self, dest = None):
        return self.pos(dest, wait = False)

#    def period(self, period = None):
#        if period == None:
#            per=self.InOutS("PER?")[1]
#            return float(per.split(" ")[0])
#        self.InOutS("PER %8.6f" % period)
#        return self.period()
    
#    def profile_internal(self, p1=0.5, p2=9.5, np=100, draw=True, verbose = 0):
#        """Provide (and draw if draw=True) the target function over the interval p1 --> p2
#        where p1 and p2 are the DAC limits. np is the number of points.
#        Returned values are: (maximum position, center of mass and [x, y] data).
#        The deadtime is useful: wrong results are provided over RS232 for deadtime< 2* integration."""
#        dp=float(p2- p1) / np
#        x=[]
#        y=[]
#        print "Profile..."
#        ll = self.InOutS("PID:PROF 0",n=2)
#        if verbose > 0:
#            print ll
#        ll = self.InOutS("PID:SERV 0",n=2)
#        if verbose > 0:
#            print ll
#        self.pos(0.1)
#        ll = self.InOutS("INIT",n=2)
#        if verbose > 0:
#            print ll
#        ll = self.InOutS("CONF:PID:PROF:LIM %i %i" % (int(p1), int(p2)),n=2)
#        if verbose > 0:
#            print ll
#        ll = self.InOutS("CONF:PID:PROF:POINTS %i" % (np),n=2)
#        if verbose > 0:
#            print ll
#        ll = self.InOutS("PID:PROF 1",n=2)
#        if verbose > 0:
#            print ll
#        for i in xrange(np):
#            time.sleep(self.deadtime)
#            ll=self.InOutS("FETCH:PROF?", n=2)
#            if verbose > 1:
#                print ll
#            x.append(float(ll[1].split(",")[1]))
#            cor_value = float(ll[1].split(",")[0])
#            if cor_value == 1.:
#                cor_value = 0
#            y.append(cor_value)
#        ll = self.InOutS("PID:PROF 0",n=2)
#        if verbose > 0:
#            print ll
#        tmp=[numpy.arange(p1, p2 , dp), numpy.array(y)]
#        if draw:
#            plot(tmp[0], tmp[1])
#            #plot(x,tmp[1])
#        mp = tmp[0][tmp[1].argmax()]
#        cmp = sum(tmp[0] * tmp[1]) / sum(tmp[1])
#        print "maximum position is", mp
#        print "center of mass   is", cmp
#        return mp, cmp, tmp
#
#    def profile(self, p1=1, p2=9, np=50, draw=True, verbose = 0):
#        """Provide (and draw if draw=True) the target function over the interval p1 --> p2
#        where p1 and p2 are the DAC limits. np is the number of points.
#        Returned values are: (maximum position, center of mass and [x, y] data).
#        The deadtime is useful: wrong results are provided over RS232 for deadtime< 2* integration."""
#        mode=self.pid()["mode"]
#        dt = self.period()*2.
#        self.pos(p1)
#        dp = float(p2 - p1) / np
#        y = []
#        print "Profile..."
#        ll = self.InOutS("PID:SERV 0",n=2)
#        if verbose > 0:
#            print ll
#        for p in numpy.arange(p1, p2+dp, dp):
#            self.pos(p)
#            time.sleep(dt)
#            i1, i2 = self.currents()[0:2]
#            if verbose >2 : 
#                print "currents --> %g %g" % (i1, i2)
#            if mode == 0:
#                y.append(i1)
#            elif mode == 1:
#                y.append(i1 + i2)
#            elif mode == 2:
#                y.append(i1 - i2)
#            elif mode == 3:
#                y.append(i1 / i2)
#            elif mode == 4:
#                y.append((i1 - i2) / (i1 + i2 + 1e-14))
#            tmp=[numpy.arange(p1, p2+dp, dp), numpy.array(y)]
#        if draw:
#            plot(tmp[0], tmp[1])
#        mp = tmp[0][tmp[1].argmax()]
#        cmp = sum(tmp[0] * tmp[1]) / sum(tmp[1])
#        print "maximum position is", mp
#        print "center of mass   is", cmp
#        return mp, cmp, tmp
#
#    def capacitor(self,capacity = None):
#        if capacity == None:
#            l=self.InOutS("CONF:CAP?")[1].strip().split(",")
#            return int(l[0]),l[1]
#        if capacity in [0,1]:
#            self.InOutS("CONF:CAP %i"%(capacity))
#        else:
#            raise Exception("I200: wrong capacity value specified (must be 0 or 1).")   
#        return self.capacitor()
#
#    def currents(self):
#        l=self.InOutS("READ:CURR?")
#        ll=l[-1].split(",")
#        i1 = float(ll[1].split(" ")[0])
#        i2 = float(ll[2].split(" ")[0])
#        overload = int(ll[3].strip())
#        if overload: 
#            ST="OVERLOAD"
#        else:
#            ST="OK"
#        return i1,i2,ST
#
#    def start_measurement(self):
#        self.InOutS("INIT")
#        r=self.range()[0]
#        if self.currents()[2] == "OVERLOAD": r = r * 10
#        while(self.currents()[2] == "OVERLOAD" and r <= float(self.capacitor()[1].split()[0]) / 1e-5):
#            self.range(r)
#            r = r * 10
#        return self.currents()[2]
#
#    def stop_measurement(self):
#        self.stop_servo()
#        return self.InOutS("ABORT",n=2)[1].strip()
#
#    def start_servo(self):
#        self.start_measurement()
#        return self.InOutS("PID:SERV 1", n=2)[1].strip()
#
#    def stop_servo(self):
#        return self.InOutS("PID:SERV 0", n=2)[1].strip()
#    
    def mode(self, mode = None):
        if mode == None:
            return self.InOutS("?MODE")[1]
        self.InOutS(mode)
        return self.mode()

#
#    def pid(self,**kwargs):
#        """The best way to learn to use this function is to provide no arguments and check output. 
#        Try to use the output provided to set new parameters with the very same syntax:
#        use the keywords of the dictionary as function keyword.
#        e.g.: pid provides {"KP": 1} use pid(KP=0.1) to change the parameter to 0.1
#        NOTA BENE: case of names matters!"""
#        modes={0:"I1", 1:"I1 + I2", 2:"I1 - I2", 3:"I1 / I2", 4:"(I1 - I2) / (I1 + I2)"}
#        if kwargs == {}:
#            mode = int(self.InOutS("CONF:PID:MOD?", n=2)[1].strip())
#            #print "mode = " + modes[mode]
#            rate = int(self.InOutS("CONF:PID:RAT?", n=2)[1].strip())
#            limits=(self.InOutS("CONF:PID:LIM?", n=2)[1].strip()).split(",")
#            limits=[float(limits[0][:-1]),float(limits[1][:-1])]
#            lowCurrent=float(self.InOutS("CONF:PID:I1I2LOW?", n=2)[1].strip())
#            KP=float(self.InOutS("CONF:PID:KP?", n=2)[1].strip())
#            KI=float(self.InOutS("CONF:PID:KI?", n=2)[1].strip())
#            return {"mode": mode, "rate": rate, "limits": limits,"lowCurrent": lowCurrent,"KP": KP,"KI": KI,"modename":modes[mode]}
#        for i in kwargs:
#            if i == "mode":
#                tmp=self.InOutS("CONF:PID:MOD %i" % kwargs[i])
#            elif i == "rate":
#                tmp=self.InOutS("CONF:PID:RAT %i" % kwargs[i])
#            elif i == "lowCurrent":
#                tmp=self.InOutS("CONF:PID:I1I2LOW %f" % kwargs[i])
#            elif i == "limits":
#                tmp=self.InOutS("CONF:PID:LIM %f %f" % tuple(kwargs[i]))
#            elif i == "KP":
#                tmp=self.InOutS("CONF:PID:KP %f" % kwargs[i])
#            elif i == "KI":
#                tmp=self.InOutS("CONF:PID:KI %f" % kwargs[i])
#        return self.pid()
#
#    def range(self, arg = None):
#        """If no argument provided: returns range (A) and integration period (s)
#        If a range is provided, it sets it."""
#        if arg == None:
#            t=float(self.InOutS("CONF:GAT:INT:PER?",n=2)[1].split(" ")[0])
#            r=float(self.InOutS("CONF:GAT:INT:RANG?",n=2)[1].split(" ")[0])
#            return r,t
#        else:
#            self.InOutS("CONF:GAT:INT:RANG %5.2e 1" % (float(arg)))
#        try:
#            if self.range()[1] > self.deadtime:
#                self.deadtime = self.range()[1]*2.
#        except:
#            pass
#        return self.range()
#    
    def tune(self, p1=1, p2=9, np=50, dt=0.1, offset = 0., draw=True):
        ascan(self, p1, p2, (p1-p2)/float(np), dt = dt, channel=0, graph=0, scaler="cpt")
        self.pos(ScanStats.baricenter_scaled)
        time.sleep(1)
        return self.start()

    def oscbeam(self,p1,p2,dp=0.01, phase = 0., repeat=1):
        self.mode("OSCILLATION")
        self.InOutS("PHASE %6.1f"% phase)
        points = []
        self.InOutS("OSCIL OFF")
        
        frequency = float(self.InOutS("?FREQUENCY")[1])
        amplitude = float(self.InOutS("?AMPLITUDE")[1])
        tau = float(self.InOutS("?TAU")[1])
        
        time.sleep(0.1)
        for p in numpy.linspace(p1, p2, int((p2-p1)/dp)):
            print self.pos(p)
            time.sleep(0.1)
            self.InOutS("OSCIL ON")
            time.sleep(2)
            main=0.
            quad=0.
            for i in xrange(repeat):
                t_main, t_quad = map(float, self.InOutS("?OSCBEAM")[1].split())
                main += t_main
                quad += t_quad
            main = main / repeat
            quad = quad /repeat
            points.append([p, main, quad])
        points = numpy.array(points).transpose()
        pylab.figure()
        pylab.title("Ph= %6.4f Freq= %3.1f A=%5.3f T=%3.1f" % (phase, frequency, amplitude, tau) )
        pylab.plot(points[0], points[1],"b-",label ="main") 
        pylab.plot(points[0], points[2], "r-", label="quad")
        pylab.plot(points[0], points[2], "r+")
        pylab.legend()
        pylab.grid()
        return points

    def report(self):
        print "MOSTAB at ", self.pos()
        print "Reporting MOSTAB setup"
        print "----------------------"
        print "AMPLITUDE  = ", self("?AMPLITUDE")[1]
        print "PHASE      = ", self("?PHASE")[1]
        print "FREQUENCY  = ", self("?FREQUENCY")[1]
        print "TAU        = ", self("?TAU")[1]
        print "SLOPE      = ", self("?SLOPE")[1]
        print "OUTBEAM    = ", self("?OUTBEAM")[1]
        print "OPRANGE    = ", self("?OPRANGE")[1]
        print ""
        print "In case of doubt, please, verify bandwith limit of amplifier..."
        return

class MOSTAB_tango(MOSTAB_serial):
    def __init__(self, port=None, echo=1, EndOfLine=13, Space=32, deadtime=0.05, EndOfLine_out="\r\n"):
        """System is asymmetric: 10 is sent to end command, while 13,10 is received"""
        myEOL={10:"\n",13:"\r"}
        self.serial=tango_serial(port, EndOfLine=[EndOfLine,], space=Space, deadtime=0.1)
        self.deadtime=deadtime
        self.label="MOSTAB_" + port
        self.EndOfLine = myEOL[EndOfLine]
        self.EndOfLine_out = EndOfLine_out
        self.states_table = {
            "IDLE":PyTango.DevState.STANDBY,
            "MOVE":PyTango.DevState.MOVING,
            "SCAN":PyTango.DevState.MOVING,
            "SEARCH":PyTango.DevState.MOVING,
            "RUN":PyTango.DevState.RUNNING,
            "WAITBEAM":PyTango.DevState.RUNNING,
            "RUN":PyTango.DevState.RUNNING,
            "OVERLOAD":PyTango.DevState.ALARM,
            "ALARM":PyTango.DevState.ALARM
            }
        if echo == 0:
            self.InOutS("NOECHO")
        elif echo == 1:
            self.InOutS("ECHO")
        #if echo in [0, 1]:
        #    self.InOutS("SYST:COMM:TERM %1i"%echo)
        #self.InOutS("*CLS")
        #Cleanup pending auto profile if active
        #self.InOutS("PID:PROF 0")
        return

    def open(self):
        """Unused in the tango_serial version"""
        return

    def close(self):
        """Unused in the tango_serial version"""
        return

    def InOutS(self, message, n=None):
        """In the tango_serial version the value of n is not used."""
        if self.EndOfLine_out <> "":
            ll = self.serial.writeread(message).split(self.EndOfLine_out)
        else:
            ll = self.serial.writeread(message).split(self.EndOfLine)
        time.sleep(self.deadtime)
        l = self.serial.read()
        while(l <> ""):
            ll[1] += l
            l = self.serial.read()
        return ll
    

