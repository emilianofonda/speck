from PyTango import DeviceProxy,DevState
from time import sleep

class NHQ_HVsupply:
    def __init__(self,label="",channel="A",speed=50.,deadtime=0.2,timeout=3.,tolerance=2.):
        """Control just one of the two HV channels: channels are A and B. Default channel is A.
        You can currently set the voltage, restore the voltage and change the speed ramp."""
        self.label=label
        self.DP=DeviceProxy(self.label)
        self.channel=channel
        self.deadtime=deadtime
        self.timeout=timeout
        self.deadtime=deadtime
        self.tolerance=tolerance
        self.att_voltage="voltage"+self.channel
        self.att_speed="rampSpeed"+self.channel
        self.DP.write_attribute(self.att_speed,speed)
        self.att_maxV="maxVoltage"+self.channel
        self.att_maxCur="maxCurrent"+self.channel
        self.voltage_target=self.voltage()
        print self.label," current voltage is %g"%(self.DP.read_attribute(self.att_voltage).value)
        return
    

    def __str__(self):
        return "HV supply"

    def __repr__(self):
        return self.label+"."+self.channel+"= %g Volts"%(self.voltage())
    
    def subtype(self):
        return "NHQ"
    
    def command(self,commandstring,arg=""):
        """Pass a command to the device."""
        if arg=="":
            return self.DP.command_inout(commandstring)
        else:
            return self.DP.command_inout(commandstring,arg)
        
    def state(self):
        """Returns the device state"""
        #if abs(self.att_voltage.value-v0)>self.tolerance:
        #    return DevState.MOVING
        sleep(self.deadtime)
        #Communication and refresh are very sloooooow!!!!!!!!!
        if abs(self.voltage()-self.voltage_target)>(self.tolerance):
            return DevState.MOVING
        return self.command("State")
        
    def status(self):
        """Returns the device status string"""
        return self.command("Status")
    
    def stop(self):
        self.voltage(0.)
        return "Setting voltage to zero."

    def pos(self,volts=None,wait=True):
        return self.voltage(volts,wait)

    def go(self,volts=None):
        return self.pos(volts,wait=False)
        
    def voltage(self,volts=None,wait=True):
        if(volts==None):
            volts=self.DP.read_attribute("voltage"+self.channel).value
            return volts
        else:
            if(volts<=self.maxVoltage()):
                self.voltage_target = volts
                self.DP.write_attribute(self.att_voltage,volts)
                if wait: 
                    print"\n"
                    while(self.state()==DevState.MOVING):
                        print "\r %g"%(self.voltage()),
                        sleep(self.deadtime)
                    print "\n"
                return self.voltage()        
            else:
                print "Requested value exceed maxVoltage!"
                return self.voltage()

    def maxVoltage(self,volts=None):
        """Returns or set the maximum voltage in V"""
        if(volts==None):
            volts=self.DP.read_attribute("maxVoltage"+self.channel).value
            return volts
        else:
            self.DP.write_attribute(self.att_maxV,volts)
            sleep(self.deadtime)
            return self.maxVoltage()

    def maxCurrent(self,cur=None):
        """Returns or set the maximum current in microA"""
        if(cur==None):
            cur=self.DP.read_attribute("maxCurrent"+self.channel).value
            return cur
        else:
            self.DP.write_attribute(self.att_maxCur,cur)
            sleep(self.deadtime)
            return self.maxCurrent()

    def speed(self,speed=None):
        """Returns or set the speed ramp in V/s"""
        if(speed==None):
            speed=self.DP.read_attribute("rampSpeed"+self.channel).value
            return speed
        else:
            self.DP.write_attribute(self.att_speed,speed)
            sleep(self.deadtime*40.)
            return self.speed()

    def current(self):
        """Read only; returns the current value in microA"""
        return self.DP.read_attribute("current"+self.channel).value
    
    def init(self):
        """Send the Init command to the device."""
        self.state()
        self.command("Init")
        return 

    def restoreVoltage(self):
        """Reset the inhibit if it has switched on, but the trigger is no more active."""
        return self.command("RestoreVoltage")


