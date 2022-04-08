from PyTango import DeviceProxy,DevState
from time import sleep 

class pseudo_valve:
    """Version alpha use the dio device write just on the first port of the chosen channel.self.reverse reverse normal open/close behaviour."""
    def __init__(self,label="d09-1-c00/ca/dio_0.1",channel="G",delay=0.1,deadtime=0.,timeout=0,reverse=False):
        self.channel="Port"+channel
        self.DP=DeviceProxy(label)
        self.label=label
        self.delay=0.1
        self.timeout=timeout
        self.deadtime=deadtime
        self.reverse=reverse
        if self.reverse:
            self.open_value=0
            self.close_value=1
        else:
            self.open_value=1
            self.close_value=0
    
    def state(self):
        pos=self.DP.read_attribute(self.channel)
        if pos.value==self.open_value:
            return DevState.OPEN
        elif pos.value==self.close_value:
            return DevState.CLOSE
        else:
            return DevState.UNKNOWN
        
    def status(self):
        stat="Valve is "
        if self.state()==DevState.CLOSE:
            stat+="closed"
        elif self.state()==DevState.OPEN:
            stat+="open"
        else:
            stat+="in error!"
        return stat

        def __str__(self):
                return "VALVE"

        def __repr__(self):
            return self.label+" is %s"%(self.state())   

    def subtype(self):
            return "DIO"                            

    def open(self):
        pos=self.DP.read_attribute(self.channel).value
        if pos != self.open_value:
            self.DP.write_attribute(self.channel,self.open_value)
            sleep(self.delay)
        return DevState.OPEN
        
    def close(self):
        pos=self.DP.read_attribute(self.channel).value
        if pos != self.close_value:
            self.DP.write_attribute(self.channel,self.close_value)
            sleep(self.delay)
        return DevState.CLOSE
        
