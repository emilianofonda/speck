from __future__ import print_function
# V 0. 23/1/2009 EF
#
#This module should be inserted in the motor class... the big moloch?
#Maybe a device form could be a better solution. Anyway...
#

from future import standard_library
standard_library.install_aliases()
from builtins import str
from builtins import object
import PyTango
from PyTango import DeviceProxy, DevState
from time import sleep,time
from numpy import bitwise_and
import _thread
#from char2bin import char2bin

class mm4005_motor(object):
    """Define a motor on a MM4005 controller via a GPIB connection. 
    The serial connection does not work well in my knowledge.
    The motorname must be of the form  gpibadress:axisnumber
    exemple: d09-1-c00/ca/gpib.0-02:3 
    for the axis 3 on the controller with gpib address 2"""
    def __init__(self,motorname,deadtime=.03,delay=0.25,timeout=0.25,verbose=True):
        try:
            sep_pos=motorname.find(":")
            if sep_pos==-1:
                print("Error defining ",motorname)
                raise Exception("MM4005_motor error","Axis number not specified! syntax is gpibdevice:axis")
            self.devicename=motorname[:sep_pos]
            self.axisnumber=motorname[sep_pos+1:]
            self.DP=DeviceProxy(self.devicename)
            #Verify if there is a real answer from the motor
            self.state()
        except:
            raise Exception("MM4005_motor error","Cannot initialize axis")
        self.deadtime=deadtime
        self.delay=delay
        self.timeout=timeout
        self.label=motorname
        self.verbose=verbose
        return

        def __str__(self):
                return "MOTOR"

        def __repr__(self):
                return self.label+" at %10.6f"%(self.pos())

        def subtype(self):
                return "MM4005 axis"

    def state(self):
                """Return the state"""
        sts=self.command("writeRead",self.axisnumber+"MS\n")
        std=ord(sts[sts.find("MS")+2:].strip())
        if bitwise_and(std,1):
            return DevState.MOVING
        if bitwise_and(std,2):
            return DevState.OFF
        return DevState.STANDBY

    def status(self):
                """No arguments, return the status as a string"""
        sts=self.command("writeRead",self.axisnumber+"MS\n")
        std=ord(sts[sts.find("MS")+2:].strip())
        status=""
        if bitwise_and(std,1):
            status+="Axis Moving: Yes\n"
        else:
            status+="Axis Moving: No\n"
        if bitwise_and(std,2):
            status+="Motor On: No\n"
        else:
            status+="Motor On: Yes\n"
        if bitwise_and(std,4):
            status+="Direction: Positive\n"
        else:
            status+="Direction: Negative\n"
        if bitwise_and(std,8):
            status+="Limit Switch +: Inactive\n"
        else:
            status+="Limit Switch +: Active\n"
        if bitwise_and(std,16):
            status+="Limit Switch +: Inactive\n"
        else:
            status+="Limit Switch +: Active\n"
        if bitwise_and(std,32):
            status+="Mechanical Zero: High\n"
        else:
            status+="Mechanical Zero: Low\n"
        return status

    def stop(self):
        """Just stop it: asynchronous command is used..."""
        self.DP.command_inout_asynch("write",self.axisnumber+"ST\n")
        return
        
    def command(self,cmdstr,arg=""):
        "For adventurous users only: send a command_inout string, optionally with arguments"
        if(arg==""):
            return self.DP.command_inout(cmdstr)
        else:
            return self.DP.command_inout(cmdstr,arg)
        return

    def init(self):
        """Init on the gpib device"""
        self.command("init")
        return
        
    def mo(self):
        """Stop all MM4005 axis"""
        self.command("write","MF\n")
        return 
    
    def sh(self):
        """Turn on all MM4005 axis"""
        self.command("write","MO\n")
        return

    def DefinePosition(self,value=None):
        """This function does not exists in the MM4005"""
        print("Warning from ",self.motorname,": this function is not implemented in the controller.")
        return self.pos()

    def InitializeReferencePosition(self,type=None):
        """Execute the default origin search for the axis.  
        the type is not set by default, but can be specified as an argument (integer):
        0: search for zero position
        1: search for mechanical zero followed by top encoder
        2: search for mechanical zero."""
        if (self.state()==DevState.OFF):
            raise Exception("Cannot initialize on a motor that is OFF!")
        try:
            if type==None:
                self.command("write",self.axisnumber+"OR\n")
            else:
                self.command("write",self.axisnumber+"OR"+str(type)+"\n")
            t=0.
            if self.state()!=DevState.MOVING:
                while((self.state()!=DevState.MOVING) and (t<self.timeout)):
                    sleep(self.deadtime)
                    t+=self.deadtime
            while(self.state()==DevState.MOVING):
                if self.verbose: print("%8.6f\r"%(self.pos()), end=' ')
                sleep(self.deadtime)
        except PyTango.DevFailed as tmp:
            self.stop()
            print("Error. Verify the following :\n")
            print("properties for initializereference have not been correctly set.")
            raise tmp
        except (KeyboardInterrupt,SystemExit) as tmp:
            self.stop()
            print("Stop on user request.")
            raise tmp
        except:
            self.stop()
            print("Cannot initialize position for an unknown reason")
            raise NotImplementedError
        sleep(self.delay)
        #...speed bug workaround
        #self.speed(old_speed)
        return self.pos()
        

    def move(self,dest=None,wait=True):
        return self.pos(dest,wait)

    def go(self,dest=None):
        """This is an alias for motor.pos(dest,wait=False). See help for motor.pos."""                   
        if(dest==None):
            return self.pos()
        else:
            return self.pos(dest,wait=False)    

    def fire(self,dest=None):
        """This is a way to send the go command in a thread. Use it for full speed when multiple go commands
        have to be sent in series on different motors. It returns the thread ID. Use only if you are aware of thread risks.
        This is an experimental feature at present"""
        if dest==None:
            return self.go()
        else:
            try:
                dest=float(dest)
            except:    
                raise Exception("Argument must be a number!")
            try:
                return _thread.start_new_thread(self.go,(dest,))
            except _thread.error as tmp:
                print("Error firing ",self.label,"to ",dest)
                print("Error is :",tmp)
                print("Using a go command instead.")
                self.go(dest)
                return None

    def pos(self,dest=None,wait=True):
        """With no arguments returns the position. 
                   With a value, go to the position and wait for the motor to stop, 
                   then it returns the position. Useful for careful single motor positioning.
                   Can be easily modified to iterate until good positioning is achieved.
           The wait parameter is set to True by default, if it's False or 0 it means that the motor will not wait."""
        if(dest==None):
            sp=self.command("writeRead",self.axisnumber+"TP\n")
            position=float(sp[sp.find("TP")+2:].strip())
            return position
        try:
            st=self.state()
            if(st==DevState.OFF): 
                #print "Motor is OFF! Use motor.sh() to power up."
                #raise PyTango.DevFailed
                self.sh()
                sleep(2.)
            self.command("write",self.axisnumber+"PA"+str(dest)+"\n")
            if(not(wait)):
                return dest
            t=0.
               if self.state()!=DevState.MOVING:
                while((self.state()!=DevState.MOVING) and (t<self.timeout)):
                    sleep(self.deadtime)
                    t+=self.deadtime
            while(self.state()==DevState.MOVING):
                if self.verbose: print("%8.6f\r"%(self.pos()), end=' ')
                sleep(self.deadtime)
            sleep(self.delay)
            #
            if self.verbose: print("\n")
            #if(self.verbose):
            #    st=self.state()
            #    if(st<>DevState.STANDBY):
            #        print "Movement finished with state:",st,"\n"
            return self.pos()
        except (KeyboardInterrupt,SystemExit) as tmp:
            self.stop()
            raise tmp
        except PyTango.DevFailed as tmp:
            self.stop()
            raise tmp


