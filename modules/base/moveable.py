from mycurses import *
from time import time,sleep
from PyTango import DeviceProxy,DevState
from numpy import nan
from exceptions import KeyboardInterrupt,SystemExit,SyntaxError, NotImplementedError, Exception
class moveable:
    def __init__(self,label="",attribute="",moving_state=DevState.MOVING,stop_command="",deadtime=0.01,timeout=0.1,delay=0.):
        #print "moveable class: experimental version."
        self.DP=DeviceProxy(label)
        cmds=map(lambda x:x.cmd_name, self.DP.command_list_query())
        self.device_command_list=cmds
        if("MotorON" in cmds):
            self.powerup_command="MotorON"
        elif("On" in cmds):
            self.powerup_command="On"
        else:
            self.powerup_command=""

        if("MotorOFF" in cmds):
            self.powerdown_command="MotorOFF"
        elif("Off" in cmds):
            self.powerdown_command="Off"
        else:
            self.powerdown_command=""
        if stop_command=="":
            if "Stop" in cmds:
                self.stop_command="Stop"
            elif "Abort" in cmds:
                self.stop_command="Abort"
            else:
                self.stop_command=""
        else:
            if stop_command in cmds:
                self.stop_command=stop_command
            else:
                raise Exception(label+" has not the "+stop_command+" command")
            
        self.delay=delay
        self.label=label
        self.att_name=attribute
        self.movingstate=moving_state
        self.deadtime=deadtime
        self.timeout=timeout
        self.state=self.DP.state
        self.status=self.DP.status
        self.ac=self.DP.get_attribute_config([self.att_name,])[0]
        if self.ac.format=="":
            self.ac.format="%g"
        #ac--> label,format,unit
        #Load attributes
        #for i in self.DP.get_attribute_list():
        #Load commands
        self.init_is_over=True
        return

    def __repr__(self):
        if self.state() in [DevState.FAULT,DevState.ALARM]: 
            color=BOLD+RED
        elif self.state() in [DevState.ON,DevState.STANDBY,DevState.OPEN]: 
            color=BOLD+GREEN
        elif self.state() in [DevState.RUNNING,DevState.MOVING]: 
            color=BOLD+BLUE
        else: 
            color=""
        return self.label+"/"+self.att_name+" (attribute label=%s) at "%self.ac.label+self.ac.format%self.pos()+" %s"%self.ac.unit\
        +" is in state: "+color+"%s"%(self.state())+RESET
    
    def __call__(self,x=None):
        print self.__repr__()
        return self.pos()

    def pos(self,x=None,wait=True):
        if x==None:
            return self.DP.read_attribute(self.att_name).value
        if x==self.pos(): return self.pos()
        try:
            self.DP.write_attribute(self.att_name,x)
            if wait:
                if self.movingstate<>None:
                    t0=time()
                    while(self.state()<>self.movingstate and time()-t0<self.timeout):
                        sleep(self.deadtime)
                    while(self.state()==self.movingstate):
                        sleep(self.deadtime)
                    sleep(self.delay)
                else:
                    sleep(self.deadtime)
        except (KeyboardInterrupt,SystemExit), tmp:
            self.stop()
            print self.__repr__()
            raise tmp
        except Exception, tmp:
            self.stop()
            raise tmp
            
        return self.pos()

    def lm(self):
        """It returns the soft limits on the moveable attribute"""
        att_cfg = self.DP.get_attribute_config(self.att_name)
        try:
            min_value = float(att_cfg.min_value)
        except:
            min_value = nan
        try:
            max_value = float(att_cfg.max_value)
        except:
            max_value = nan
        return min_value, max_value

    def set_lm(self, min_value, max_value):
        """It sets and then returns the soft limits on the moveable attribute"""
        # the expressioin x <> x checks for x being nan ! :-)
        if min_value <> min_value:
            print "lower limit unset"
            min_value = "Not Specified"
        else:
            min_value = "%g" % min_value
        if max_value <> max_value:
            print "higher limit unset"
            max_value = "Not Specified"
        else:
            max_value = "%g" % max_value
        att_cfg = self.DP.get_attribute_config(self.att_name)
        att_cfg.min_value, att_cfg.max_value = min_value, max_value 
        self.DP.set_attribute_config(att_cfg)
        return self.lm()

    def go(self,x=None,wait=False):
        return self.pos(x,wait)

    def stop(self):
        if self.stop_command<>"": self.DP.command_inout(self.stop_command)
        return self.state()

    def on(self):
        if self.powerup_command<>"": 
            self.DP.command_inout(self.powerup_command)
        else:
            print "on is "+RED+"not"+RESET+" a supported command on %s"%(self.label)
        return self.state()
        
    def off(self):
        if self.powerdown_command<>"": 
            self.DP.command_inout(self.powerdown_command)
        else:
            print "off is "+RED+"not"+RESET+" a supported command on %s"%(self.label)
        return self.state()

    def __getattr__(self,att):
        return eval("self.DP."+att)
    
    def __setattr__(self,att,value):
        if not self.__dict__.has_key("init_is_over"):
            self.__dict__[att]=value
            return
        else:
            self.DP.__setattr__(att,value)
            return

    def DefinePosition(self,att=None):
        if att==None:
            return self.pos()
        else:
            if "DefinePosition" in self.device_command_list:
                self.DP.DefinePosition(att)
                sleep(self.deadtime)
                return self.pos()
            else:
                print "DefinePosition "+RED+"not"+RESET+" defined on %s"%self.label
                return self.pos()
    

class sensor(moveable):    
    def pos(self,x=None,wait=True):
        return self.DP.read_attribute(self.att_name).value

    def go(self,x=None,wait=False):
        return self.pos()

