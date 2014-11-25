from mycurses import *
from string import lower
import PyTango
from PyTango import DeviceProxy, DevState
from time import sleep,time
import exceptions
from exceptions import KeyboardInterrupt,SystemExit,SyntaxError, NotImplementedError, Exception
from numpy import mean,std,mod, nan, inf
import thread

#def move_motor(*motor):
#    """Move one or more motors. Support motor lists or just a motor object. 
#    Syntax move_motor(motor1,1,motor2,123.2,motor3,12). 
#    Only an even number of parameters is acceptable.
#    """
#    motors=[]
#    if mod(len(motor),2)<>0 : raise exceptions.SyntaxError("odd number of parameters!")
#    #print map(lambda i: "%s at %g"%(whois(i),i.pos()), x)
#    try:
#        for i in range(0,len(motor),2):
#            motor[i].go(motor[i+1])
#            motors.append(motor[i])
#        return wait_motor(motors)
#    except (KeyboardInterrupt,SystemExit), tmp:
#        for i in motors:
#            i.stop()
#        raise tmp
#    except PyTango.DevFailed, tmp:
#        for i in motors:
#            i.stop()
#        raise tmp
#    except Exception, tmp:
#        print "Unhandled error... raising exception"
#        raise tmp

#def go_motor(*motor):
#    """Move one or more motors. Support motor lists or just a motor object. 
#    Syntax move_motor(motor1,1,motor2,123.2,motor3,12). 
#    Only an even number of parameters is acceptable.
#    Tested a little."""
#    motors=[]
#    if mod(len(motor),2)<>0 : raise exceptions.SyntaxError("odd number of parameters!")
#    try:
#        for i in range(0,len(motor),2):
#            motor[i].go(motor[i+1])
#            motors.append(motor[i])
#        return
#    except (KeyboardInterrupt,SystemExit), tmp:
#        for i in motors:
#            i.stop()
#        raise tmp
#    except PyTango.DevFailed, tmp:
#        for i in motors:
#            i.stop()
#        raise tmp
#    except Exception, tmp:
#        print "Unhandled error... raising exception"
#        raise tmp
#
#def wait_motor(motor, deadtime=0.025, timeout=-0.05, delay=None, verbose=True):
#    """Wait for a motor to move and stop. Support motor lists or just a motor object. 
#    To be used inside the class as a general wait procedure and as a 
#    support for multimotor movements through multi motor.go commands."""
#    argument_type=type(motor)
#    if (not(argument_type in [tuple,list])): 
#        motor_list=(motor,)
#    else:
#        motor_list=motor
#    #Now the argument IS a list, anyway.
#    if delay==None:
#        delay=0.
#        for i in motor_list:
#            try:
#                if i.delay>delay: delay=i.delay
#            except:
#                pass
#    try:
#        condition=True
#        t=0.
#        while(condition and (t<timeout)):
#            sleep(deadtime)
#            condition=False
#            for i in motor_list:
#                if(i.state()==DevState.MOVING):
#                    condition=False
#                    break    
#            t+=deadtime
#        condition=True
#        if verbose:
#            for i in map(lambda x: (x.label,x.pos()), motor_list):
#                print " " * 40 + "\r",
#                print "%s    %+8.6e" % (i[0], i[1])
#        while(condition):
#            sleep(deadtime)
#            condition = (DevState.MOVING in map(lambda x: x.state(), motor_list))
#            if verbose:
#                print "\033[%iA" % (len(motor_list)),
#                for i in map(lambda x: (x.label, x.pos()), motor_list):
#                    print " " * 40 + "\r",
#                    print "%s    %+8.6e"%(i[0], i[1])
#
#        if verbose: print ""
#        sleep(delay)
#        if len(motor_list) == 1:
#            return motor_list[0].pos()
#        else:
#            return map(lambda x: x.pos(), motor_list)
#    except (KeyboardInterrupt,SystemExit), tmp:
#        for i in motor_list:
#            i.stop()
#        raise tmp
#    except PyTango.DevFailed, tmp:
#        raise tmp
#    except Exception, tmp:
#        print "Unhandled error, raising exception..."
#        raise tmp
        
class motor:
    """Define a motor in terms of a DeviceProxy. You provide a correct nomenclature and you got
    a motor object that have the following functions: pos, go, state, status, speed,accel and decel.
    timeout is used before moving, deadtime for polling and delay after moving.
    Test on GalilAxis 2 in progress. Mostly working."""

    def __init__(self,motorname,deadtime=.025,delay=0.,timeout=0.2,verbose=True):
        try:
            self.DP=DeviceProxy(motorname)
            #try:
            #    self.DP.command_inout("Init")
            #    sleep(0.1)
            #except:
            #    try:
            #        sleep(0.1)
            #        self.DP.command_inout("Init")
                    #               sleep(0.1)
            #    except:
            #        print "Cannot initialize motor"
            #        raise PyTango.DevFailed
        except PyTango.DevFailed, tmp:
            print "Error when defining :",motorname," as a motor.\n"
            print tmp.args
            raise tmp
        self.deadtime = deadtime
        self.delay = delay
        self.timeout = timeout
        self.label = motorname
        self.att_pos = "position"
        self.att_name= self.att_pos
        self.att_speed = "velocity"
        self.att_accel = "acceleration"
        self.att_decel = "deceleration"
        self.att_offset = "offset"
        self.verbose=verbose
        return

    def __str__(self):
        return "MOTOR"

    def __repr__(self):
        lm0, lm1 = self.lm()
        if lm0 == None: lm0 = -inf
        if lm1 == None: lm1 = inf
        return self.label+" at %10.6f [%g:%g] is in state: %s"%(self.pos(), lm0, lm1, self.state())

    def subtype(self):
        return "MOTOR"

    def state(self):
        """Return the state"""
        return self.DP.state()

    def status(self):
        """No arguments, return the status as a string"""
        #State bug workaround!
        self.state()
        return self.DP.status()

    def stop(self):
        """Just stop it: asynchronous command is used... watch out!"""
        #self.DP.command_inout_asynch("Stop",0)
        self.DP.command_inout_asynch("Stop")
        return
        
    def command(self,cmdstr,arg=""):
        "For adventurous users only: send a command_inout string, optionally with arguments"
        if(arg==""):
            return self.DP.command_inout(cmdstr)
        else:
            return self.DP.command_inout(cmdstr,arg)
        return

    def init(self):
        self.state()
        self.command("Init")
        return
        
    def off(self):
        self.state()
        self.command("MotorOFF")
        return 
    
    def on(self):
        self.state()
        self.command("MotorON")
        return

    def sh(self):
        return self.on()

    def mo(self):
        return self.off()

    def DefinePosition(self,value=None):
        """Set the motor position to the new proposed value. There is no default value, but with no argument it returns the current position."""
        if (value==None): return self.pos()
        try:
            value=float(value)        
        except:
            print "Position value is not valid."
            raise SyntaxError
        if (self.state()==DevState.OFF):
            raise Exception("Cannot initialize on a motor that is OFF!")
        try:
            self.command("DefinePosition",value)
        except PyTango.DevFailed, tmp:
                raise tmp
        except:
            print "Cannot define position for an unknown reason"
            raise NotImplementedError
        return self.pos()
        

    def InitializeReferencePosition(self):
        """Execute the GalilAxis V2 intializeReferencePosition command: uses the default property. 
        It includes a workaround to set the speed to the value set before the initializeReferencePosition command."""
        if (self.state()==DevState.OFF):
            raise Exception("Cannot initialize on a motor that is OFF!")
        #Speed bug workaround...
        #old_speed=self.speed()
        try:
            #state bug workaround
            #self.state()
            self.command("InitializeReferencePosition")
            t=0.
            if self.state()<>DevState.MOVING:
                while((self.state()<>DevState.MOVING) and (t<self.timeout)):
                    sleep(self.deadtime)
                    t+=self.deadtime
            while(self.state()==DevState.MOVING):
                if self.verbose: print "%8.6f\r"%(self.pos()),
                sleep(self.deadtime)
        except PyTango.DevFailed, tmp:
            self.stop()
            print "Error. Verify the following :\n"
            print "properties for initializereference have not been correctly set."
            raise tmp
        except (KeyboardInterrupt,SystemExit), tmp:
            self.stop()
            print "Stop on user request."
            raise tmp
        except:
            self.stop()
            print "Cannot initialize position for an unknown reason"
            raise NotImplementedError
        sleep(self.delay)
        #...speed bug workaround
        #self.speed(old_speed)
        return self.pos()
        
    
    def move(self,dest=None,wait=True):
        return self.pos(dest,wait)

    def pos(self,dest=None,wait=True):
        """With no arguments returns the position. 
                   With a value, go to the position and wait for the motor to stop, 
                   then it returns the position. Useful for careful single motor positioning.
                   Can be easily modified to iterate until good positioning is achieved.
           The wait parameter is set to True by default, if it's False or 0 it means that the motor will not wait."""
        if(dest==None):
            return self.DP.read_attribute(self.att_pos).value
        try:
            #state bug workaround
            st=self.state()
            if(st==DevState.OFF): 
                raise Exception("Motor is OFF! Use motor.on() to power up.")
            #sleep(self.deadtime)
            self.DP.write_attribute(self.att_pos,dest)
            if(not(wait)):
                return dest
            t=0.
            if self.state()<>DevState.MOVING:
                while((self.state()<>DevState.MOVING) and (t<self.timeout)):
                    sleep(self.deadtime)
                    t+=self.deadtime
            while(self.state()==DevState.MOVING):
                if self.verbose: print "%8.6f\r"%(self.pos()),
                sleep(self.deadtime)
            sleep(self.delay)
            return self.pos()
        except (KeyboardInterrupt,SystemExit), tmp:
            self.stop()
            raise tmp
        except PyTango.DevFailed, tmp:
            self.stop()
            raise tmp
        #except :
        #    print "Unknown Error"
        #    self.stop()
        #    raise NotImplementedError
    
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
                return thread.start_new_thread(self.go,(dest,))
            except thread.error,tmp:
                print "Error firing ",self.label,"to ",dest
                print "Error is :",tmp
                print "Using a go command instead."
                self.go(dest)
                return None

    def speed(self,dest=None):
        """With no arguments returns the speed. 
           With a value, set the speed.
           It returns an error code, if the motor is moving."""                   
        if(dest==None):
            #state bug workaround
            self.state()
            return self.DP.read_attribute("velocity").value
        else:
            if(self.state()==DevState.MOVING):
                print "Cannot write on moving motor\n"
                return self.speed()
            else:
                self.DP.write_attribute(self.att_speed,dest)
                sleep(self.delay)
                return self.speed()

    def accel(self,dest=None):
        """With no arguments returns the accel. 
           With a value, set the accel.
           It returns an error code, if the motor is moving."""                   
        if(dest==None):
            #state bug workaround
            self.state()
            return self.DP.read_attribute(self.att_accel).value
        else:
            if(self.state()==DevState.MOVING):
                print "Cannot write on moving motor\n"
                return self.accel()
            else:
                self.DP.write_attribute(self.att_accel,dest)
                sleep(self.delay)
                return self.accel()

    def decel(self,dest=None):
        """With no arguments returns the decel. 
           With a value, set the decel.
           It returns an error code, if the motor is moving."""                   
        if(dest==None):
            #state bug workaround
            self.state()
            return self.DP.read_attribute(self.att_decel).value
        else:
            if(self.state()==DevState.MOVING):
                print "Cannot write on moving motor\n"
                return self.decel()
            else:
                self.DP.write_attribute(self.att_decel,dest)
                sleep(self.delay)
                return self.decel()


    def offset(self,dest=None):
        """With no arguments returns the offset. 
           With a value, set the offset.
           It returns an error code, if the motor is moving."""                   
        if(dest==None):
            #state bug workaround
            self.state()
            return self.DP.read_attribute(self.att_offset).value
        else:
            if(self.state()==DevState.MOVING):
                print "Cannot write on moving motor\n"
                return self.offset()
            else:
                self.DP.write_attribute(self.att_offset,dest)
                sleep(self.delay)
                return self.offset()
    
    
    def forward(self,wait=True):
       try:
           #state bug workaround
           self.state()
           self.command("Forward")
           if(not(wait)):
               return self.pos()
           t=0.
           while((self.state() <> DevState.MOVING) and (t<self.timeout)):
               sleep(self.deadtime)
               t+=self.deadtime
           while(self.state() == DevState.MOVING):
               print "%8.6f\r"%(self.pos()),
               sleep(self.deadtime)
           sleep(self.delay)
           return self.pos()
       except (KeyboardInterrupt,SystemExit):
           self.stop()
           return self.pos()
       except PyTango.DevFailed, tmp:
           print tmp.args
           return self.stop()
           raise tmp
       #except :
       #    print "Unknown Error"
       #    self.stop()
       #    raise NotImplementedError

    def backward(self,wait=True):
       try:
           #state bug workaround
           self.state()
           self.command("Backward")
           if(not(wait)): 
               return self.pos()
           t=0.
           while((self.state() <> DevState.MOVING) and (t<self.timeout)):
               sleep(self.deadtime)
               t+=self.deadtime
           while(self.state() == DevState.MOVING):
               print "%8.6f\r"%(self.pos()),
               sleep(self.deadtime)
           sleep(self.delay)
           return self.pos()
           
       except (KeyboardInterrupt,SystemExit):
           self.stop()
           return self.pos()
           
       except PyTango.DevFailed, tmp:
           print tmp.args
           return self.stop()
           raise tmp

       except Exception, tmp:
           print "Unhandled error, raising exception..."
           self.stop()
           raise tmp

    def forwardLimitSwitch(self):
        try:
            return self.DP.read_attribute("forwardLimitSwitch").value
        except:
            print "Error reading forward limit switch..."
            return None
    
    def backwardLimitSwitch(self):
        try:
            return self.DP.read_attribute("backwardLimitSwitch").value
        except:
            print "Error reading backward limit switch..."
            return None
            
    def lm(self):
        """It returns the soft limits on the moveable attribute"""
        att_cfg = self.DP.get_attribute_config(self.att_name)
        try:
            min_value = float(att_cfg.min_value)
        except:
            min_value = -inf
        try:
            max_value = float(att_cfg.max_value)
        except:
            max_value = inf
        return min_value, max_value

    def lmset(self, min_value = None , max_value = None):
        """It sets and then returns the soft limits on the moveable attribute"""
        att_cfg = self.DP.get_attribute_config(self.att_name)
        current_min, current_max = att_cfg.min_value, att_cfg.max_value
        if min_value in [-inf, inf]:
            min_value = "Not specified"
        elif min_value == None:
            min_value = current_min
        else:
            min_value = "%g" % min_value
        if max_value == inf:
            max_value = "Not specified"
        elif max_value == None:
            max_value = current_max
        else:
            max_value = "%g" % max_value
        att_cfg.min_value, att_cfg.max_value = min_value, max_value
        self.DP.set_attribute_config(att_cfg)
        new_limits = self.lm()
        print "New limits: ", new_limits
        return new_limits


class piezo:
    """Define a motor (piezo) in terms of a DeviceProxy. You provide a correct nomenclature and you got a motor object that have the following functions: pos, go, state, status,... It is not a normal motor. Some functions are missing. The returned position is the feeback position. Is it an option to envisage to return a tuple instead (command, feedback) ?"""

    def __init__(self,motorname,deadtime=0.01,delay=0.0,timeout=0.01):
        self.DP=DeviceProxy(motorname)
        self.timeout=timeout
        self.deadtime=deadtime
        self.delay=delay
        self.label=motorname
        self.att_pos="position"

    def __str__(self):
        return "MOTOR"

    def __repr__(self):
        return self.label+" at %10.6f"%(self.pos())
       
    def subtype(self):
        return "PIEZO"


    def state(self):
        """No arguments, return the state as a string"""
        return self.DP.state()
        
    def status(self):
        """No arguments, return the status as a string"""
        return self.DP.status()

    def stop(self):
        """No stop for piezos..."""
        #self.DP.command_inout("Stop")
        return
        
    def command(self,cmdstr,arg=""):
        "For adventurous users only: send a command_inout string"
        if(arg==""):
            return self.DP.command_inout(cmdstr)
        else:
            return self.DP.command_inout(cmdstr,arg)
        return

    def init(self):
        self.state()
        self.command("Init")

    def off(self):
        self.state()
        self.command("OFF")
        return 
    
    def on(self):
        self.state()
        self.command("ON")
        return

    def sh(self):
        return self.on()

    def mo(self):
        return self.off()

    def move(self,dest=None,wait=True):
        return self.pos(dest,wait)

    def DefinePosition(self,dest):
        print "DefinePosition is useless on a generic piezo actuator.\n"
        return self.pos()

    def InitializeReferencePosition(self,dest):
        print "InitializeReferencePosition is useless on a generic piezo actuator.\n"
        return self.pos()


    def pos(self,dest=None,wait=True):
        """With no arguments returns the position. 
        With a value, go to the position and wait for the motor to stop, 
        then it returns the position.  Useful for careful single motor positioning.
        If wait is False, the function will not wait. 
        Can be easily modified to iterate until good positioning is achieved."""
        if(dest==None):
            return self.DP.read_attribute(self.att_pos).value
        else:
            #state bug workaround
            self.state()
            self.DP.write_attribute(self.att_pos,dest)
            if(not(wait)):
                return self.pos()
            t=0.
            while((self.state()<>DevState.MOVING) and (t<self.timeout)):
                sleep(self.deadtime)
                t+=self.deadtime
            while(self.state()==DevState.MOVING):
                sleep(self.deadtime)
            sleep(self.delay)
            return self.pos()
                
    def go(self,dest=None):
        """This is an alias for motor.pos(dest,wait=False). See motor.pos for more help."""                   
        if(dest==None):
            return self.pos()
        else:
            return self.pos(dest,wait=False)

    def fire(self,dest=None):
        """This is a way to send the go command in a thread. Use it for full speed when multiple go commands
        have to be sent in series on different motors. It returns the thread ID. Use only if you are aware of thread risks.
        This is an experimental feature at present"""
        if dest==None:
            return self.pos()
        else:
            try:
                dest=float(dest)
            except:    
                raise Exception("Argument must be a number!")
            try:
                return thread.start_new_thread(self.go,(dest,))
            except thread.error,tmp:
                print "Error firing ",self.label,"to ",dest
                print "Error is :",tmp
                print "Using a go command instead."
                self.go(dest)
                return None

class motor_slit:
    """Alternative to the slit class: define one of the four pseudo-motors per each slit: pos,gap,Up/In,Down/Out. Each has standard motor attributes and special behaviour with regard to speed and acceleration and so on. You must provide the device address of the slits, of the two motors and the keyword corresponding to the attribute you want to control: pos, gap, up (or) in,down (or) out. To be decommissione in favor of moveables."""
    def __init__(self,slitname,insideUp_name,outsideDown_name,argument="pos",deadtime=.01,timeout=.1,delay=0.1):
        self.DP_slit=DeviceProxy(slitname)
        self.DP_IU=DeviceProxy(insideUp_name);self.mt_IU=motor(insideUp_name)
        self.DP_OD=DeviceProxy(outsideDown_name);self.mt_OD=motor(outsideDown_name)
        if(not(argument in ["pos","gap","in","out","up","down"])):
            print "Invalid argument keyword!"
            raise SyntaxError
        if(argument=="pos"):
            self.DP=self.DP_slit
            self.att_pos="position"
            self.argument="position"
        if(argument=="gap"): 
            self.DP=self.DP_slit
            self.att_pos="gap"
            self.argument="gap"
        if(argument in ["in","up"]):
            self.DP=self.DP_IU    
            self.att_pos="insideUpPosition"
            self.argument="insideUpPosition"
        if(argument in ["out","down"]): 
            self.DP=self.DP_OD
            self.att_pos="outsideDownPosition"
            self.argument="outsideDownPosition"
        self.deadtime=deadtime
        self.timeout=timeout
        self.delay=delay
        self.label=slitname+"_"+argument
        if self.DP_slit.get_property(["InvertPositionDirection",])["InvertPositionDirection"][0]=="true":
            self.invertedDir=-1
        else:
            self.invertedDir=1
        return

    def __str__(self):
        return "MOTOR"

    def __repr__(self):
        return self.label+" at %10.6f"%(self.pos())

    def subtype(self):
        return "SLIT"
    
    def state(self):
        """No arguments, return the state as a string"""
        return self.DP.state()

    def status(self):
        """No arguments, return the status as a string"""
        return self.DP_slit.status()

    def slit_state(self):
        """No arguments, return the state of the slits device as a string"""
        return self.DP_slit.state()

    def status(self):
        """No arguments, return the status of the slits device as a string"""
        return self.DP_slit.status()
        
    def stop(self):
        """Just stop it"""
        try:
            self.command_slit("Stop")
        except:
            print "Cannot stop slits"
            print self.status()
        return self.state()

    def command(self,cmdstr,arg=""):
        "For adventurous users only: send a command_inout string, optionally with arguments. Command is sent to slit_motor if this is a motor object (up, down,...), not to the slit device. For this, use command_slit instead."
        if(arg==""):
            return self.DP.command_inout(cmdstr)
        else:
            return self.DP.command_inout(cmdstr,arg)
        return

    def command_slit(self,cmdstr,arg=""):
        "For adventurous users only: send a command_inout string, optionally with arguments. Command is sent to slit device not to the slit motor. For this, use command of a slit motor object."
        if(arg==""):
            return self.DP_slit.command_inout(cmdstr)
        else:
            return self.DP_slit.command_inout(cmdstr,arg)
        return

    def setIndependantMode(self):
        return self.command_slit("SetIndependantMode")
    
    def pos(self,dest=None,wait=True):
        """With no arguments returns the position.
        With a value, go to the position and wait for the slits to stop and returns position."""
        if self.argument=="position":
            if(dest==None):
                return self.DP_slit.read_attribute(self.att_pos).value
            else:
                if (self.slit_state() == DevState.MOVING):
                    raise Exception("Slits are already moving.")
                if (self.mt_IU.backwardLimitSwitch() or self.mt_OD.backwardLimitSwitch()\
                or self.mt_IU.forwardLimitSwitch() or self.mt_OD.forwardLimitSwitch()):
                    self.setIndependantMode()
                    sleep(0.1)
                    self.mt_IU.go(self.mt_IU.pos()-(dest-self.pos())*self.invertedDir)
                    self.mt_OD.go(self.mt_OD.pos()+(dest-self.pos())*self.invertedDir)
                    sleep(0.1)
                else:    
                    self.DP_slit.write_attribute(self.att_pos,dest)
        if self.argument=="gap":
            if(dest==None):
                return self.DP_slit.read_attribute(self.att_pos).value
            else:
                if (self.slit_state()==DevState.MOVING):
                    raise Exception("Slits are already moving.")
                if (self.mt_IU.backwardLimitSwitch() or self.mt_OD.backwardLimitSwitch()\
                or self.mt_IU.forwardLimitSwitch() or self.mt_OD.forwardLimitSwitch()):
                    self.setIndependantMode()
                    sleep(0.1)
                    self.mt_IU.go(self.mt_IU.pos()+(dest-self.pos())*0.5)
                    self.mt_OD.go(self.mt_OD.pos()+(dest-self.pos())*0.5)
                    sleep(0.1)
                else:    
                    self.DP_slit.write_attribute(self.att_pos,dest)
        if self.argument == "insideUpPosition":
            if(dest==None):
                return self.mt_IU.pos()
            else:
                self.DP_slit.state()
                if self.state()==DevState.DISABLE:
                    self.setIndependantMode()
                return self.mt_IU.pos(dest,wait)        
        if self.argument=="outsideDownPosition":
            if(dest==None):
                return self.mt_OD.pos()
            else:
                self.DP_slit.state()
                if self.state()==DevState.DISABLE:
                    self.setIndependantMode()
                return self.mt_OD.pos(dest,wait)        
        try:
            if(not(wait)):
                return self.pos()
            t=time()
            sleep(self.deadtime)
            while((self.slit_state()<>DevState.MOVING) and (time()-t<self.timeout)):
                sleep(self.deadtime)
            while(self.slit_state()==DevState.MOVING):
                print "%10.8f\r"%(self.pos()),
                sleep(self.deadtime)
            sleep(self.delay)
            if self.argument in ["gap", "position"]:
                if (self.mt_IU.backwardLimitSwitch() or self.mt_OD.backwardLimitSwitch()):
                    print "Backward limit switch attained!"
                if (self.mt_IU.forwardLimitSwitch() or self.mt_OD.forwardLimitSwitch()):
                    print "Forward  limit switch attained!"
                    return self.pos()
        except (KeyboardInterrupt,SystemExit), tmp:
            self.stop()
            raise tmp
        except PyTango.DevFailed, tmp:
            self.stop()
            raise tmp
        except PyTango.DevError, tmp:
            self.stop()
            raise tmp
        #except :
        #       print "Unknown Error"
        #       return self.pos()
    
    def move(self,des=None,wait=True):
        "Synonim of pos"
        return self.pos(dest,wait)

    def go(self,dest=None):
        """With no arguments returns the position.
        With a value, go to the position without waiting.
        Alias for motor.pos(dest,wait=False)."""
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
                return thread.start_new_thread(self.go,(dest,))
            except thread.error,tmp:
                print "Error firing ",self.label,"to ",dest
                print "Error is :",tmp
                print "Using a go command instead."
                self.go(dest)
                return None
                          
    def mo(self):
        return self.off()

    def sh(self):
        return self.on()

    def off(self):
        if(self.argument in ["gap","position"]):
            self.setIndependantMode()
            self.DP_IU.command_inout("MotorOFF")
            self.DP_OD.command_inout("MotorOFF")
        else:
            self.command("MotorOFF")
        return 
    
    def on(self):
        if(self.argument in ["gap","position"]):
            self.setIndependantMode()
            self.DP_IU.command_inout("MotorON")
            self.DP_OD.command_inout("MotorON")
        else:
            self.command("MotorON")
        return

    def DefinePosition(self,value=None):
        """Set the motor position to the new proposed value. There is no default value, but with no argument it returns the current position. Actually, you can define everything just with gap and position."""
        if (value==None): return self.pos()
        try:
            value=float(value)        
        except:
            print "Position value is not valid."
            raise SyntaxError
        if (self.state()==DevState.OFF):
            raise Exception("Cannot initialize on a motor that is OFF!")
        if((self.state()==DevState.MOVING) or (self.slit_state==DevState.MOVING)):
            raise Exception("Cannot write on moving motor")
        else:
            try:
                if(self.argument in ["gap","position"]):
                    __gap=self.DP_slit.read_attribute("gap")
                    __pos=self.DP_slit.read_attribute("position")
                    if self.argument=="gap":
                        __iu=0.5*value-__pos.value
                        __od=0.5*value+__pos.value
                    if self.argument=="position":
                        __iu=0.5*__gap.value-value*self.invertedDir
                        __od=0.5*__gap.value+value*self.invertedDir
                    self.setIndependantMode()
                    sleep(self.delay)
                    self.mt_IU.DefinePosition(__iu)
                    sleep(self.delay)
                    self.mt_OD.DefinePosition(__od)
                    sleep(self.delay)
                    return self.pos()
                else:
                    self.setIndependantMode()
                    sleep(self.delay)
                    self.command("DefinePosition",float(value))
                    sleep(self.delay)
                    return self.pos()
            except PyTango.DevFailed, tmp:
                raise tmp
            #except:
            #    print "Cannot define position for an unknown reason"
            #    raise NotImplementedError

        

    def InitializeReferencePosition(self):
        """Execute the GalilAxis V2 intializeReferencePosition command: uses the default property. 
        This is a slit, you can do it on gap only or pos only since the two blades will be initialised."""
        if (self.state()==DevState.OFF):
            raise Exception("Cannot initialize on a motor that is OFF!")
        try:
            #state bug workaround
            self.state()
            if(self.argument in ["gap","position"]):
                self.setIndependantMode()
                sleep(0.2)
                self.mt_IU.InitializeReferencePosition()
                sleep(0.2)
                self.mt_OD.InitializeReferencePosition()
                return self.pos()
            else:
                self.setIndependantMode()
                sleep(0.2)
                if self.argument=="insideUpPosition":
                    self.mt_IU.InitializeReferencePosition()
                elif self.argument=="outsideDownPosition":    
                    self.mt_OD.InitializeReferencePosition()
                sleep(0.2)
                return self.pos()
        except PyTango.DevFailed, tmp:
            self.stop()
            print "Error. Verify the following :\n"
            print "properties for initializereference have not been correctly set."
            raise tmp
        except (KeyboardInterrupt,SystemExit), tmp:
            self.stop()
            print "Stop on user request."
            raise tmp
        #except:
        #    self.stop()
        #    print "Cannot initialize position for an unknown reason"
        #    raise NotImplementedError
        return self.pos()

    def init(self):
        if(self.argument in ["gap","position"]):
            self.DP_IU.command_inout("Init")
            self.DP_OD.command_inout("Init")
        else:
            self.command("Init")
        return

    def speed(self,dest=None):
        """With no arguments returns the speed. 
           With a value, set the speed.
           It returns an error code, if the motor is moving."""  
        if(dest==None):
            self.slit_state()
            self.state()
            if(self.argument in ["gap","postion"]):
                up_speed=self.DP_IU.read_attribute("velocity")
                down_speed=self.DP_OD.read_attribute("velocity")
                #Not standard behaviour in the ouput.
                #Tells the minimum of the two speed to be used in wait procedures
                return min(up_speed.value,down_speed.value)
            else:
                return self.DP.read_attribute("velocity").value
        else:
            if((self.state()==DevState.MOVING) or (self.slit_state==DevState.MOVING)):
                print "Cannot write on moving motor\n"
                return self.speed() 
                #...or raise PyTango.DevFailed ???
            else:
                if(self.argument in ["gap","postion"]):
                    self.DP_IU.write_attribute("velocity",dest)
                    self.DP_OD.write_attribute("velocity",dest)
                    sleep(self.delay)
                    return self.speed()
                else:
                    self.DP.write_attribute("velocity",dest)
                    sleep(self.delay)
                    return self.speed()

    def accel(self,dest=None):
        """With no arguments returns the acceleration. 
                   With a value, set the acceleration.
                   It returns an error code, if the motor is moving."""  
        if(dest==None):
            self.slit_state()
            self.state()
            if(self.argument in ["gap","postion"]):
                up_accel=self.DP_IU.read_attribute("acceleration")
                down_accel=self.DP_OD.read_attribute("acceleration")
                #Not standard behaviour in the ouput.
                #Tells the minimum of the two accel to be used in wait procedures
                return min(up_accel.value,down_accel.value)
            else:
                return self.DP.read_attribute("acceleration").value
        else:
            if((self.state()==DevState.MOVING) or (self.slit_state==DevState.MOVING)):
                print "Cannot write on moving motor\n"
                return self.accel() 
                #...or raise PyTango.DevFailed ???
            else:
                if(self.argument in ["gap","postion"]):
                    self.DP_IU.write_attribute("acceleration",dest)
                    self.DP_OD.write_attribute("acceleration",dest)
                    sleep(self.delay)
                    return self.accel()
                else:
                    self.DP.write_attribute("acceleration",dest)
                    sleep(self.delay)
                    return self.accel()

    def decel(self,dest=None):
        """With no arguments returns the deceleration. 
        With a value, set the decelaration.
        It returns an error code, if the motor is moving."""  
        if(dest==None):
            self.slit_state()
            self.state()
            if(self.argument in ["gap","postion"]):
                up_decel=self.DP_IU.read_attribute("deceleration")
                down_decel=self.DP_OD.read_attribute("deceleration")
                #Not standard behaviour in the ouput.
                #Tells the minimum of the two decel to be used in wait procedures
                return min(up_decel.value,down_decel.value)
            else:
                return self.DP.read_attribute("deceleration").value
        else:
            if((self.state()==DevState.MOVING) or (self.slit_state==DevState.MOVING)):
                print "Cannot write on moving motor\n"
                return self.decel() 
                #...or raise PyTango.DevFailed ???
            else:
                if(self.argument in ["gap","postion"]):
                    self.DP_IU.write_attribute("deceleration",dest)
                    self.DP_OD.write_attribute("deceleration",dest)
                    sleep(self.delay)
                    return self.decel()
                else:
                    self.DP.write_attribute("deceleration",dest)
                    sleep(self.delay)
                    return self.decel()

    def forward(self,wait=True):
        if(self.argument in ["gap","postion"]):
            print "Cannot execute forward on the ",self.argument," slit motor type."
            return self.pos()
        try:
            #state bug workaround
            self.state()
            self.slit_state()
            self.command_slit("SetIndependantMode")
            sleep(self.deadtime)
            try:
                self.command("Forward")
            except:
                self.command("Forward")
            if(not(wait)):
                return self.pos()
            t=0.
            while((self.state()<>DevState.MOVING) and (t<self.timeout)):
                sleep(self.deadtime)
                t+=self.deadtime
            while(self.state()==DevState.MOVING):
                print "%8.6f\r"%(self.pos()),
                sleep(self.deadtime)
            sleep(self.delay)
            return self.pos()
            
        except (KeyboardInterrupt,SystemExit):
            self.stop()
            return self.pos()

        except PyTango.DevFailed, tmp:
            print tmp.args
            return self.stop()
            raise tmp

        #except :
        #    print "Unknown Error"
        #    self.stop()
        #    raise NotImplementedError

    def backward(self,wait=True):
        if(self.argument in ["gap","postion"]):
            print "Cannot execute backward on the ",self.argument," slit motor type."
            return self.pos()
        try:
            #state bug workaround
            self.state()
            self.slit_state()
            self.command_slit("SetIndependantMode")
            sleep(self.deadtime)
            try:
                self.command("Backward")
            except:
                self.command("Backward")
            if(not(wait)):
                return self.pos()
            t=0.
            while((self.state()<>DevState.MOVING) and (t<self.timeout)):
                sleep(self.deadtime)
                t+=self.deadtime
            while(self.state()==DevState.MOVING):
                print "%8.6f\r"%(self.pos()),
                sleep(self.deadtime)
            sleep(self.delay)
            return self.pos()
            
        except (KeyboardInterrupt,SystemExit):
            self.stop()
            return self.pos()

        except PyTango.DevFailed, tmp:
            print tmp.args
            return self.stop()
            raise tmp

        #except :
        #    print "Unknown Error"
        #    self.stop()
        #    raise NotImplementedError




def Read_AI(cb_data,axis=0,n=1,statistics=False):
        """cb_data is the deviceproxy of the raw_data device, axis is the axis and n is the number of times you want to average the reading.
        If you want std deviation and mean ask for statistics=True.
    The raw_data should be developped as a specific python controller with all the usual tricks inside the controller... next version?"""
        att_axis=cb_data.read_attribute("axisNumber")
        if att_axis.value<>axis:
            cb_data.write_attribute("axisNumber",axis)
        y=[]
        if (not(statistics)):
                for i in range(n):
                        y.append(cb_data.read_attribute("analogInput").value)
                return mean(y)
        else:
                for i in range(n):
                        y.append(cb_data.read_attribute("analogInput").value)
                return mean(y),std(y)


