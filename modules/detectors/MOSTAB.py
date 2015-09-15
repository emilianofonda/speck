#and now something completely different...
import time

from ascan import ascan, ScanStats

import numpy
from numpy import inf, nan
import pylab
from pylab import plot

#import serial
import PyTango

from tango_serial import tango_serial

class MOSTAB_serial:

    def __init__(self, port=0, baudrate=9600, echo=0, deadtime=0.05, init_file="",scaler="cpt", channel=0):
        self.SerPort=serial.Serial(0)
        self.SerPort.baudrate=baudrate
        self.SerPort.timeout=1
        self.deadtime = deadtime
        self.scaler="cpt"
        self.channel=3
        self.label="MOSTAB_%i" % port
        if echo == 0:
            self.InOutS("NOECHO")
        elif echo == 1:
            self.InOutS("ECHO")
        self.echo = echo
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
            "WAITBEAM":PyTango.DevState.MOVING,
            "RUN":PyTango.DevState.RUNNING,
            "OVERLOAD":PyTango.DevState.ALARM,
            "ALARM":PyTango.DevState.ALARM
            }
        self.init_file = init_file
        return

#    def init(self):
#        print "Setting hard coded SAMBA setup on MOSTAB (MoCo2) unit...",
#        self("MODE OSCILLATION")
#        self("AMPLITUDE 0.025")
#        self("PHASE 76.15")
#        self("FREQUENCY 38.4615")
#        self("TAU 1")
#        self("SLOPE -0.13")
#        self("INBEAM SOFT 1")
#        self("OUTBEAM VOLT NORM UNIP 10 NOAUTO")
#        self("OPRANGE 0.1 9.9 5")
#        self("SPEED 2 10")
#        print "OK."
#        print self.status()
#        print self()
#        return
 
    def init(self):
        if self.init_file <> "":
            try:
                ll = file(self.init_file).readlines()
            except:
                raise Exception("init_file specified not found or not readable: " + self.init_file)
        else:
            raise Exception("No init_file specified")
        print "Setting setup read from %s on MOSTAB (MoCo2) unit..."%(self.init_file)
        for i in ll:
            cmd = i.strip()
            if not cmd.startswith("#"):
                try:
                    self(cmd)
                except Exception, tmp:
                    raise Exception("Cannot send command to MOSTAB: " + cmd)
        print "...OK."
        print self.status()
        return self()

    def __call__(self,arg = None):
        if arg <> None:
            return self.InOutS(arg)
        max_Vout,gain_mode = self("?OUTBEAM")[self.echo].split()[-2:]
        minp, maxp = self.lm()
        print "MOSTAB at ", self.pos(),"[%4.2f:%4.2f]"%(minp, maxp)," is in state ",self.state(), "the outbeam signal is at %sV/%sV gain mode is %s"\
        %(self("?BEAM")[self.echo].split()[1], max_Vout, gain_mode)
        #print "I0=%8.6e I1=%8.6e State=%s" % self.currents()
        #print "mode = %s" % self.pid()["modename"]
        #_i200_status = self.status()
        #if _i200_status["PID_state"] == "Servo not running?":
        #    print "Servo not running?"
        #else:
        #    print "DAC_write_0 = %s DAC_write = %s" % (_i200_status["DAC_write_0"], _i200_status["DAC_write"])
        return self.pos()

#   def status(self):
#       ll=[]
#       ll.append(self.InOutS("?STATE"))
#       ll.append(self.InOutS("?MODE"))
#       ll.append(self.InOutS("?AMPLITUDE"))
#       ll.append(self.InOutS("?FREQUENCY"))
#       ll.append(self.InOutS("?PHASE"))
#       ll.append(self.InOutS("?TAU"))
#       ll.append(self.InOutS("?INBEAM"))
#       ll.append(self.InOutS("?OUTBEAM"))
#       ll.append(self.InOutS("?OPRANGE"))
#       ll.append(self.InOutS("?PIEZO"))
#       ll.append(self.InOutS("?SPEED"))
#       ll.append(self.InOutS("?SLOPE"))
#       return ll

    def state(self):
        ss = self.InOutS("?STATE")[self.echo]
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

    def lm(self):
        ss = self.InOutS("?OPRANGE")[self.echo]
        ss = ss.split()
        return float(ss[0]), float(ss[1])
    
    def lmset(self, min_value = None, max_value = None):
        ll = self.lm()
        current_min, current_max =ll[0], ll[1] 
        if min_value in [-inf, inf]:
            min_value = 0.
        elif min_value == None:
            min_value = current_min
        if max_value == inf:
            max_value = 10.
        elif max_value == None:
            max_value = current_max
        self.InOutS("OPRANGE %4.2f %4.2f %4.2f" % (min_value, max_value, (min_value+max_value)*0.5))
        new_limits = self.lm()
        print "New limits: ", new_limits
        return new_limits
        
        ss = self.InOutS("?OPRANGE")[self.echo]
        ss = ss.split()
        return float(ss[0]),float(ss[1])

    def version(self):
        return self.InOutS("?VER")[1:]

    def start(self):
        if self.mode("OSCILLATION"):
            self.InOutS("OSCIL ON")
        time.sleep(0.1)
        print "?OSCIL"
        print self("?OSCIL")[1]
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
        return self.InOutS("?ERR")[self.echo]

    def pos(self, dest = None, wait = True):
        """Move the PIEZO to the desired position or report value"""
        if dest == None:
            return float(self.InOutS("?PIEZO")[self.echo].split(" ")[0])
        self.InOutS("PIEZO %8.6f" % dest)
        err = self.error()
        if err <> "OK":
            pmin, pmax = self.lm()
            if dest <= pmin or dest >= pmax:
                raise Exception("You tried to move MOSTAB out of limits.\n \
                If necessary, set limits with command lmset.")
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
#            per=self.InOutS("PER?")[self.echo]
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
#            x.append(float(ll[self.echo].split(",")[1]))
#            cor_value = float(ll[self.echo].split(",")[0])
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
            return self.InOutS("?MODE")[self.echo]
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
#            mode = int(self.InOutS("CONF:PID:MOD?", n=2)[self.echo].strip())
#            #print "mode = " + modes[mode]
#            rate = int(self.InOutS("CONF:PID:RAT?", n=2)[self.echo].strip())
#            limits=(self.InOutS("CONF:PID:LIM?", n=2)[self.echo].strip()).split(",")
#            limits=[float(limits[0][:-1]),float(limits[self.echo][:-1])]
#            lowCurrent=float(self.InOutS("CONF:PID:I1I2LOW?", n=2)[self.echo].strip())
#            KP=float(self.InOutS("CONF:PID:KP?", n=2)[self.echo].strip())
#            KI=float(self.InOutS("CONF:PID:KI?", n=2)[self.echo].strip())
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
    def tune(self, p1=2, p2=8, np=60, dt=0.1, oprange=1.2, offset = 0., draw=True, tune="center"):
        """The tuning procedure can move to max intenisty (tune="max")
        or to baricenter (tune="center")
        """
        self.InOutS("OPRANGE 0. 10. 5.")
        ascan(self, p1, p2, (p1-p2)/float(np), dt = dt, channel=self.channel, graph=0, scaler=self.scaler)
        if tune == "max":
            pt = ScanStats.max_pos
        elif tune =="center":
            pt = ScanStats.baricenter_scaled
        else:
            pt = None
            raise Exception("Unknown tune method request for MOSTAB.tune")
        self.pos(0.1)
        self.InOutS("OPRANGE %4.2f %4.2f %4.2f" % (max(0., pt - oprange*0.5), min(10., pt + oprange*0.5), pt))
        time.sleep(0.1)
        self.pos(pt)
        time.sleep(0.1)
        if self.mode() == "POSITION":
            self.__call__("TUNE #")
            time.sleep(2)
        else:
            self.start()
        return self.state()

    def oscbeam(self,p1,p2,dp=0.01, phase = 0., repeat=3):
        self.mode("OSCILLATION")
        self.InOutS("PHASE %6.1f"% phase)
        points = []
        self.InOutS("OSCIL OFF")
        
        frequency = float(self.InOutS("?FREQUENCY")[self.echo])
        amplitude = float(self.InOutS("?AMPLITUDE")[self.echo])
        tau = float(self.InOutS("?TAU")[self.echo])
        
        time.sleep(0.1)
        for p in numpy.arange(p1, p2+dp, dp):
            print self.pos(p)
            time.sleep(0.1)
            self.InOutS("OSCIL ON")
            time.sleep(2)
            main=0.
            quad=0.
            for i in xrange(repeat):
                t_main, t_quad = map(float, self.InOutS("?OSCBEAM")[self.echo].split())
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

    def status(self):
        ll = ""
        ll += "MOSTAB at %f\n"%self.pos()
        ll += "Reporting MOSTAB setup\n"
        ll += "----------------------\n"
        ll += "MODE       = %s\n"% self("?MODE")[self.echo]
        ll += "AMPLITUDE  = %s\n"% self("?AMPLITUDE")[self.echo]
        ll += "PHASE      = %s\n"% self("?PHASE")[self.echo]
        ll += "FREQUENCY  = %s\n"% self("?FREQUENCY")[self.echo]
        ll += "TAU        = %s\n"% self("?TAU")[self.echo]
        ll += "SLOPE      = %s\n"% self("?SLOPE")[self.echo]
        ll += "INBEAM     = %s\n"% self("?INBEAM")[self.echo]
        ll += "OUTBEAM    = %s\n"% self("?OUTBEAM")[self.echo]
        ll += "OPRANGE    = %s\n"% self("?OPRANGE")[self.echo]
        ll += "SPEED      = %s\n"% self("?SPEED")[self.echo]
        ll += "In case of doubt, please, verify bandwith limit of amplifier...\n"
        return ll

class MOSTAB_tango(MOSTAB_serial):
    def __init__(self, port=None, echo=1, EndOfLine=13, Space=32, deadtime=0.05, EndOfLine_out="\r\n", init_file = "",scaler="cpt",channel=0):
        """System is asymmetric: 10 is sent to end command, while 13,10 is received"""
        myEOL={10:"\n",13:"\r"}
        self.serial=tango_serial(port, EndOfLine=[EndOfLine,], space=Space, deadtime=0.1)
        self.deadtime=deadtime
        self.label="MOSTAB_" + port
        self.channel=channel
        self.scaler=scaler
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
        self.echo = echo
        #if echo in [0, 1]:
        #    self.InOutS("SYST:COMM:TERM %1i"%echo)
        #self.InOutS("*CLS")
        #Cleanup pending auto profile if active
        #self.InOutS("PID:PROF 0")
        self.init_file = init_file
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
    

