from __future__ import print_function
from builtins import object
from mycurses import *
from time import time,sleep
from PyTango import DeviceProxy,DevState
from numpy import nan, inf

#The following function should be moved to spec_syntax
def speckit(name,classname,*args,**kwargs):
    ip = get_ipython()
    ip.user_ns[name] = classname(*args,**kwargs)
    try:
        ip.user_ns[name].speck_label = name
    except:
        pass
    return

class moveable(object):
    def __init__(self,label="",attribute="",moving_state=DevState.MOVING,stop_command="",deadtime=0.01,timeout=0.1,delay=0.):
        self.DP=DeviceProxy(label)
        cmds=[x.cmd_name for x in self.DP.command_list_query()]
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
        self.moving_state=moving_state
        self.deadtime=deadtime
        self.timeout=timeout
        #self.state=self.DP.state
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
        #return self.label+"/"+self.att_name+" (attribute label=%s) at "%self.ac.label+self.ac.format%self.pos()+\
        #"[" + self.ac.format + ":" + self.ac.format + "]" % (*self.lm()) +" %s"%self.ac.unit\
        #+" is in state: "+color+"%s"%(self.state())+RESET
        lmts= list(self.lm())
        lmf0 = self.ac.format
        lmf1 = self.ac.format
        if lmts[0] == None:
            lmts[0] = -inf
            lmf0 = "%g"
        if lmts[1] == None:
            lmts[1] = inf
            lmf1 = "%g"
        fmt = self.label + "/" + self.att_name + " (attribute label=%s) at " + self.ac.format + "[" + lmf0 + ":" + lmf1 + "]"\
        +" %s"+" is in state: " + color + " %s " + RESET
        fmt_g = self.label + "/" + self.att_name + " (attribute label=%s) at " + "%g " + "[" + "%g" + ":" + "%g" + "]"\
        +" %s"+" is in state: " + color + " %s " + RESET
        try:
            return fmt % (self.ac.label, self.pos(), lmts[0], lmts[1], self.ac.unit, self.state())
        except:
            return fmt_g % (self.ac.label, self.pos(), lmts[0], lmts[1], self.ac.unit, self.state())
    
    def __call__(self,x=None):
        print(self.__repr__())
        return self.pos()

    def pos(self,x=None,wait=True):
        if x==None:
            return self.DP.read_attribute(self.att_name).value
        if x==self.pos(): return self.pos()
        if self.state() == DevState.DISABLE:
            self.init()
            sleep(self.deadtime * 5)
        try:
            self.DP.write_attribute(self.att_name,x)
            if self.moving_state == None:
                sleep(self.deadtime)
            elif wait:
                if self.moving_state!=None:
                    t0=time()
                    while(self.state()!=self.moving_state and time()-t0<self.timeout):
                        sleep(self.deadtime)
                    while(self.state() == self.moving_state):
                        sleep(self.deadtime)
                    sleep(self.delay)
                else:
                    sleep(self.deadtime)
        except (KeyboardInterrupt,SystemExit) as tmp:
            self.stop()
            print(self.__repr__())
            raise tmp
        except Exception as tmp:
            self.stop()
            raise tmp            
        return self.pos()

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
        """It sets and then returns the soft limits on the moveable attribute.
        If no value is supplied it returns actual limits.
        If None is supplied to one limit, limit is suppressed."""
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
        print("New limits: ", new_limits) 
        return new_limits

    def go(self,x=None,wait=False):
        return self.pos(x,wait)

    def stop(self):
        if self.stop_command!="": self.DP.command_inout(self.stop_command)
        return self.state()

    def on(self):
        if self.powerup_command!="": 
            if self.state() == DevState.DISABLE:
                self.init()
            self.DP.command_inout(self.powerup_command)
        else:
            print("on is "+RED+"not"+RESET+" a supported command on %s"%(self.label))
        sleep(0.1)
        return self.state()
        
    def off(self):
        if self.powerdown_command!="": 
            if self.state() == DevState.DISABLE:
                self.init()
            self.DP.command_inout(self.powerdown_command)
        else:
            print("off is " + RED + "not" + RESET + " a supported command on %s" % (self.label))
        sleep(0.1)
        return self.state()

    def __getattr__(self,att):
        return eval("self.DP."+att)
    
    def __setattr__(self,att,value):
        if "init_is_over" not in self.__dict__:
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
                print("DefinePosition "+RED+"not"+RESET+" defined on %s"%self.label)
                return self.pos()

    def state(self):
        s = self.DP.state()
        if s == self.moving_state:
            return DevState.MOVING
        else:
            return s
    def status(self):
        return self.DP.status()

class sensor(moveable):    
    def pos(self,x=None,wait=True):
        return self.DP.read_attribute(self.att_name).value

    def go(self,x=None,wait=False):
        return self.pos()

