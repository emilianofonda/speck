from PyTango import DeviceProxy, DevState
from PyTango import AttrQuality, AttrWriteType, DispLevel
from PyTango.server import Device, attribute, command
from PyTango.server import class_property, device_property

import time
import numpy as npy


###Let's define here a class that will be used later on by the device server itself
###In this way we can check the code step by step by importing it as an object
class LTC11:

    def __init__(self,com_port,deadtime=0.1,tolerance=0.5):
        self.DP = DeviceProxy(com_port)
        self.deadtime = deadtime
        self.tolerance =tolerance
        return
   
    def write(self, message):
        for i in range(5):
            try:
                self.DP.write(message)
                break
            except:
                time.sleep(1.)
        return

    def writeread(self, message):
        for i in range(5):
            try:
                out = self.DP.writeread(message)
                break
            except:
                time.sleep(1.)
        return out

    def __call__(self):
        return

    def __repr__(self):
        ll = ""
        ll += self.writeread("*IDN?;")
        return ll

    def state(self):
        st = int(self.writeread("QISTATE?;")[0])
        if st == 0:
            return DevState.STANDBY
        elif st == 1:
            if abs(self.read_delta()) > self.tolerance:
                return DevState.MOVING
            else:
                return DevState.RUNNING
        elif st == 2:
            return DevState.MOVING
        elif st == 3:
            return DevState.OFF
        return

    def status(self):
        return

    def wait(self):
        while(self.state() == DevState.MOVING):
            time.sleep(self.deadtime)
        return

    def pos(self, target=None, wait=True):
        ch = self.select_channel()
        if ch == 1:
            if target != None:
                self.write("SETP 1,%4.2f;"%target)
                if wait: self.wait()
            else:
                return float(self.DP.writeread("QSAMP?1;")[:-3])
        elif ch == 2:
            if target != None:
                self.write("SETP 2,%4.2f;"%target)
                if wait: self.wait()
            else:
                return float(self.writeread("QSAMP?2;")[:-3])
        else:
            raise Exception("No channel selected! please choose one first.")
        return

    def mode(self,channel,mode=None):
        return

    def autoPID(self):
        return

    def get_channels(self):
        sens1on = int(self.writeread("QOUT?1;").split(";")[0]) in [1,2]
        sens2on = int(self.writeread("QOUT?2;").split(";")[0]) in [1,2] 
        return [sens1on, sens2on]
    
    def set_channels(self,channels):
        """Set the channels on or off in different ways [Heater,Analog]
        
        Exemple set_channels([True,False])   turn on internal heater and off analog output
        
        May cause system go to monitor mode."""
        if channels[0]:
            self.write("SOSEN 1,1;")
        else:
            self.write("SOSEN 1,3;")
        if channels[1]:
            self.write("SOSEN 2,2;")
        else:
            self.DP.write("SOSEN 2,3;")
        return

    def set_max_power(self,maxpower=None):
        """Set internal heater power
        index max_power
          0       Off
          1       0.05W
          2       0.5W
          3       5W
          4       50W"""
        if maxpower == None:
            return self.get_max_power()
        self.write("SHMXPWR %i;"%maxpower)
        return

    def get_max_power(self):
        """Get internal heater power
        index max_power
          0       Off
          1       0.05W
          2       0.5W
          3       5W
          4       50W"""
        return int(self.writeread("QOUT?1;").split(";")[2])

    def select_channel(self, channel=None):
        """Switch the readout of the temperature from one channel to the other."""
        if channel == 1:
            self.set_channels([1,0])
        elif channel == 2:
            self.set_channels([0,1])
        elif channel not in [1,2]:
            chs = self.get_channels()
            if chs[0]:
                return 1
            elif chs[1]:
                return 2
            else:
                print "No channel selected."
                return -1
        else:
            raise Exception("Channel must be 1 or 2!")
        return

    def read(self):
        """Read out all temperatures and returns a list."""
        return [float(self.writeread("QSAMP?1;")[:-3]),float(self.writeread("QSAMP?2;")[:-3])]

    def read_delta(self):
        """Provide delta = T(read) - T(setpoint)"""
        ch = self.select_channel()
        if ch != None:
            delta = float(self.writeread("QSAMP?%i;"%ch)[:-3]) - float(self.writeread("QSETP?%i;"%ch)[:-3])
        else:
            raise Exception("select_channel first!")
        return delta

    def start(self):
        """Set CONTROL mode"""
        self.write("SCONT;")
        return

    def stop(self):
        """Set MONITOR mode"""
        self.write("SMON;")
        return

    def ramp(self,target,speed,grain=0.1):
        """Target is destination, speed in K/minute"""
        
        speed_seconds =  speed / 60.
        dt = grain / speed_seconds
        T_0 = self.pos()
        direction = npy.sign(target - T_0)
        self.pos(T_0, wait = False)
        self.start()
        t_start = time.time()
        t_end = t_start + abs(target - T_0) / speed_seconds
        
        while(time.time() <= t_end):
            time.sleep(dt)
            self.pos(direction * (time.time() - t_start) * speed_seconds + T_0, wait=False)
        return


class LTC11(Device):
    current = attribute(label="Current", dtype=float,
                        display_level=DispLevel.EXPERT,
                        access=AttrWriteType.READ_WRITE,
                        unit="A", format="8.4f",
                        min_value=0.0, max_value=8.5,
                        min_alarm=0.1, max_alarm=8.4,
                        min_warning=0.5, max_warning=8.0,
                        fget="get_current", fset="set_current",
                        doc="the power supply current")

    noise = attribute(label="Noise", dtype=((float,),),
                      max_dim_x=1024, max_dim_y=1024,
                      fget="get_noise")

    host = device_property(dtype=str)
    port = class_property(dtype=int, default_value=9788)

    @attribute
    def voltage(self):
        self.info_stream("get voltage(%s, %d)" % (self.host, self.port))
        return 10.0

    def get_current(self):
        return 2.3456, time(), AttrQuality.ATTR_WARNING

    def set_current(self, current):
        print("Current set to %f" % current)

    def get_noise(self):
        return random_sample((1024, 1024))

    @command(dtype_in=float)
    def ramp(self, value):
        print("Ramping up...")


if __name__ == "__main__":
    LTC11.run_server()
