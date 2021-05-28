#and now something completely different...
import time

#from ascan import ascan, ScanStats
from IPython.core.getipython import get_ipython

import numpy
from numpy import inf, nan
import pylab
from pylab import plot

#import serial
import PyTango

from tango_serial import tango_serial

class MOSTAB_serial:

    def __init__(self, port=0, baudrate=9600, echo=0, deadtime=0.05, init_file="",scaler="cpt", channel=0,
        forceOutBeam=""):
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
        self.forceOutBeam = forceOutBeam
        self.ipy = get_ipython()
        return


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
        return self.pos()

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

    
    def on(self):
        if self.mode("OSCILLATION"):
            self.InOutS("OSCIL ON")
        time.sleep(0.1)
        print self("?OSCIL")[1]
        time.sleep(0.2)
        return

    def off(self):
        if self.mode("OSCILLATION"):
            self.InOutS("OSCIL OFF")
        time.sleep(0.1)
        print self("?OSCIL")[1]
        time.sleep(0.2)
        return
    
    def start(self):
        if self.mode("OSCILLATION"):
            self.InOutS("OSCIL ON")
        time.sleep(0.1)
        print "?OSCIL"
        print self("?OSCIL")[1]
        time.sleep(0.2)
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

    
    def mode(self, mode = None):
        if mode == None:
            return self.InOutS("?MODE")[self.echo]
        self.InOutS(mode)
        return self.mode()
    
    def tune(self, p1=2, p2=8, np=100, dt=0.1, oprange=1.2, offset = 0., draw=True, tune="max"):
        """The tuning procedure can move to max intenisty (tune="max")
        or to baricenter (tune="center")
        """
        if self.forceOutBeam:
            self.__call__(self.forceOutBeam)
        self.InOutS("OPRANGE 0. 10. 5.")
        ascan = self.ipy.user_ns["ascan"]
        ScanStats = self.ipy.user_ns["ScanStats"]
        rocca = ascan(self, p1, p2, (p1-p2)/float(np), dt = dt, channel=self.channel, graph=-1, scaler=self.scaler, returndata=True)
        if tune == "max":
            pt = ScanStats.max_pos
        elif tune =="center":
            pt = ScanStats.baricenter_scaled
        else:
            pt = None
            raise Exception("Unknown tune method request for MOSTAB.tune")
        #self.pos(0.1)
        self.InOutS("OPRANGE %4.2f %4.2f %4.2f" % (max(0., pt - oprange*0.5), min(10., pt + oprange*0.5), pt))
        time.sleep(0.1)
        self.pos(pt)
        time.sleep(0.1)
        if self.mode() == "POSITION":
            self.__call__("TUNE #")
            time.sleep(2)
        elif self.mode() == "OSCILLATION":
            phi = float(self("?PHASE")[self.echo])
            #dp = float(self("?AMPLITUDE")[self.echo])
            #ob_xy = self.oscbeam(pt - 2. * dp, pt + 1. * dp, 0.25 * dp, phase = phi, repeat = 10)
            dp = oprange/400.
            #dp = oprange/200.
            ob_xy = self.oscbeam(pt - 6. * dp, pt + 5. * dp, dp, phase = phi, repeat = 50)
            ob_fit = numpy.polyfit(ob_xy[0], ob_xy[1], 1)
            pylab.subplot(1,2,2)
            pylab.plot(ob_xy[0], ob_fit[0] * ob_xy[0] + ob_fit[1], "g--", linewidth=3)
            pylab.text(pt, max(ob_xy[1])*0.5, "SLOPE = %4.2f" % ob_fit[0])
            pylab.xlabel("Volts")
            pylab.ylabel("Channel = %i"%self.channel)
            pylab.subplot(1,2,1)
            pylab.plot(rocca[0],rocca[1],"b-")
            pylab.plot(rocca[0],rocca[1],"r*")
            pylab.xlabel("Volts")
            pylab.draw()
            self("SLOPE %4.2f" % ob_fit[0])
            self.start()
        else:
            self.start()
        return self.state()

    def oscbeam(self,p1,p2,dp=0.01, phase = 0., repeat=50):
        self.mode("OSCILLATION")
        self.InOutS("PHASE %6.1f"% phase)
        points = []
        #self.InOutS("OSCIL OFF")
        
        frequency = float(self.InOutS("?FREQUENCY")[self.echo])
        amplitude = float(self.InOutS("?AMPLITUDE")[self.echo])
        tau = float(self.InOutS("?TAU")[self.echo])

        self.InOutS("OSCIL ON")
        
        self.pos(self.lm()[0]+0.05)
        time.sleep(0.1)
        for p in numpy.arange(p1, p2+dp, dp):
            print self.pos(p)
            time.sleep(0.1)
            #self.InOutS("OSCIL ON")
            #time.sleep(2)
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
        pylab.subplot(1,2,2)
        pylab.title("Ph= %6.4f Freq= %3.1f A=%5.3f T=%4.2f" % (phase, frequency, amplitude, tau) )
        pylab.plot(points[0], points[1],"b-",label ="main") 
        pylab.plot(points[0], points[2], "r-", label="quad")
        pylab.plot(points[0], points[2], "r+")
        pylab.legend(loc="lower left")
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
    def __init__(self, port=None, echo=1, EndOfLine=13, Space=32, deadtime=0.05, EndOfLine_out="\r\n", init_file = "",scaler="cpt",channel=0, 
    forceOutBeam=""):
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
        self.forceOutBeam = forceOutBeam
        self.ipy = get_ipython()
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
    

