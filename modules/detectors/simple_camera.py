from __future__ import print_function
import PyTango
from PyTango import DevState, DeviceProxy,DevFailed
from time import sleep

class camera:
    def __init__(self,label="",deadtime=0.1):
        self.deadtime = deadtime
        self.label=label
        self.DP=DeviceProxy(label)
        __tmp=PyTango.AttributeInfoEx()
        __tmp.label="expTBasler"
        __tmp.unit="s"
        __tmp.format="%9d"
        self.user_readconfig=[__tmp,]
        #self.user_readconfig=[]
        del __tmp
        return

    def init(self):
        try:
            self.DP.command_inout("Init")
        except:
            try:
                self.DP.command_inout("Init")
            except:
                pass
            sleep(1)
        return

    def reinit(self):
        return

    def __repr__(self):
        return sel.read()
                    
    def __call__(self,x=None):
        print(self.__repr__())
        return self.state()                              

    def state(self):
        return self.DP.state()

    def status(self):
        return self.DP.status()
        
    def start(self,dt=0):
        if dt == 0:
            if self.state()!=DevState.RUNNING:
                self.DP.command_inout("Start")
            else:
                raise Exception("Camera already in RUNNING state. Stop it first.")
            return self.state()
        elif dt > 0:
            if self.state()!=DevState.RUNNING:
                if self.DP.exposureTime != dt * 1000:
                    self.DP.exposureTime = dt * 1000
                    sleep(self.deadtime)
                self.DP.command_inout("snap")
            else:
                raise Exception("Camera already in RUNNING state. Stop it first.")
            return self.state()
            
    def stop(self):
        if self.state()==DevState.RUNNING:
            self.DP.command_inout("Stop")
        return self.state()
    
    def read_image(self, channels=None):
        mca=self.DP.image
        return mca

#    def read_mca(self, channels=None):
#        mca=self.DP.image
#        return mca

    def read(self):
        essais = 5
        while(essais > 0):
            try:
                return [self.DP.exposureTime/1000.,]
                #return [sum(sum(self.DP.image)),]
            except:
                essais = essais -1
                sleep(self.deadtime*4)
        raise PyTango.DevFailed("camera has failed again!")
        
    def count(self,dt=1):
        try:
            self.start(dt)
            while(self.state()==DevState.RUNNING):
                sleep(self.deadtime)
            return self.read()
        except PyTango.DevFailed as tmp:
            print(self.label,": error in camera class: command count. Device returns DevFailed.")
            raise tmp
        except PyTango.CommunicationFailed as tmp:
            print("Communication Failed... waiting 3 sec more...")
            sleep(3.)
        except (KeyboardInterrupt,SystemExit) as tmp:
            try:
                self.stop()
            except:
                try:
                    self.stop()
                except:
                    print(self.label,": cannot stop camera...")
            raise tmp
        except Exception as tmp:    
            print(self.label,": error in counter class: command count.") 
            raise tmp
        return self.read()

    def wait(self):
        try:
            while(self.state()==DevState.RUNNING):
                sleep(self.deadtime)
            return
        except PyTango.DevFailed as tmp:
            print(self.label,": error in camera class: command wait (state). Device returns DevFailed.")
            raise tmp
        except (KeyboardInterrupt,SystemExit) as tmp:
            try:
                self.stop()
            except:
                try:
                    self.stop()
                except:
                    print(self.label,": cannot stop camera...")
            raise tmp
        except Exception as tmp:
            print(self.label,": error in camera class: command count.") 
            raise tmp
        return
        
