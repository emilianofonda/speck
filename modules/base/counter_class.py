from string import lower
from time import sleep
import time as wtime
import PyTango
from PyTango import DevState,DeviceProxy
from exceptions import NotImplementedError
import exceptions
import thread
from numpy import array

class counter:
    def __init__(self,cpt=None,deadtime=0.01,maxRetries=5,user_readconfig=[], mask=[]):
        """Counters are supposed to be named from 1 up to N... it's a reasonable assumption, I guess...
        If user_readconfig is supplied it must be an appropriate list of lists [["attribute name","label","format","unit"],...].
        The mask is used to remove some counters from the dark calculation: by default all are set to 1 but the last, 
        to remove one counter set the corresponding value to 0:
        example (deafault)  for 8 counteurs where last is used as timer: [1,]*7 + [0,] or [1, 1, 1, 1, 1, 1, 1, 0]"""
        self.init_user_readconfig=user_readconfig
        self.user_readconfig=[]
        if cpt==None:
            raise Exception("Counter class: cannot define counter, undefined adress")
        try:
            self.DP=DeviceProxy(cpt)
            self.label=cpt
        except PyTango.DevFailed, tmp:
            print cpt,' is not defined in database:'
            print tmp.args
            raise tmp
        except:
            print "Unknown error defining ",cpt," device proxy"
            (ErrorType,ErrorValue,ErrorTB)=sys.exc_info()
            print sys.exc_info()
            traceback.print_exc(ErrorTB)
            raise exceptions.Exception(sys.exc_info)
        try:
            self.time=self.DP.read_attribute("integrationTime")
            self.int_time=self.time.value
            self.time="integrationTime"
            self.master=True
        except:
            #print "Cannot read Integration time.",cpt," is defined slave."
            self.master=False
            self.time=None
        self.DP.set_timeout_millis(10000)
        self.deadtime=deadtime
        self.counter_names=[]
        self.maxRetries=maxRetries
        
        try:
            if self.init_user_readconfig<>[]: 
                for i in self.init_user_readconfig:
                    #ac=self.DP.get_attribute_config_ex([i[0],])[0]
                    ac=self.DP.get_attribute_config([i[0],])[0]
                    ac.label=i[1]
                    ac.format=i[2]
                    ac.unit=i[3]
                    #self.DP.set_attribute_config_ex([ac,])
                    self.DP.set_attribute_config([ac,])
        except:
            print self.label+": Failed setting user_readconfig!"
        
        try:
            _l_att=self.DP.get_attribute_list()
            nc=0
            for i in _l_att:
                if i.startswith("counter"):
                    nc+=1
            #reset user_readconfig and reread it from device
            self.user_readconfig=[]
            for i in range(1,nc+1,1):
                self.counter_names.append("counter%i"%(i))
                #self.user_readconfig.append(self.DP.get_attribute_config_ex(["counter%i"%(i),])[0])
                self.user_readconfig.append(self.DP.get_attribute_config(["counter%i"%(i),])[0])
        except Exception, tmp:
            print "Cannot get attribute list from device ",self.label,"\n"
            raise tmp
        #MASK
        if mask <> []:
            if len(mask)==len(self.user_readconfig):
                self.mask = mask
            else:
                raise Exception("%s Error: specified mask has a length different of the user_readconfig (# of counters)."%self.label)
        else:
            self.mask = [1,] * (len(self.user_readconfig) - 1) + [0,]
        #DARK
        self.readDark()

    def __call__(self,dt=1):
        tmp=self.count(dt)
        s=self.label+" counts :"
        l=3
        for i in range(0,len(tmp),l):
            s+="\n"
            for j in range(l):
                if i+j<len(tmp):
                    s+="% -20s"%self.user_readconfig[i+j].label+": "+self.user_readconfig[i+j].format%(tmp[i+j])+"%5s"%self.user_readconfig[i+j].unit+"    "
        print s
        return

    def __str__(self):
        return "COUNTER"

    def __repr__(self):
        s=self.label+" counts :\n"
        tmp=self.count()
        if len(tmp)<=7:    
            for i in tmp: s+="%6i "%(i)
            return s
        else:
            for i in tmp[0:7]: s+="%6i "%(i)
            s+="\n"
            for j in range(0,(len(tmp)-7)/8):    
                for i in tmp[7+j*8:7+(j+1)*8]: s+="%6i "%(i)
                s+="\n"
            return s

    def subtype(self):
        if(self.master):
            return "MASTER"
        else:
            return "SLAVE"

    def command(self,cmdstr,arg=""):
        "For adventurous users only: send a command_inout string, optionally with arguments"
        if(arg==""):
            return self.DP.command_inout(cmdstr)
        else:
            return self.DP.command_inout(cmdstr,arg)

    def init(self):
        self.DP.set_timeout_millis(10000)
        return self.command("Init")

    def state(self):
        """No arguments, return the state as a string"""
        try:
            return self.DP.state()
        except PyTango.DevFailed, tmp:
            print tmp
            sleep(1)
            return self.DP.state()

    def status(self):
        """No arguments, return the status as a string"""
        return self.DP.status()

    def stop(self):
        try:
            if self.state()==DevState.RUNNING:
                #self.DP.command_inout_asynch("Stop",0)
                self.DP.command_inout_asynch("Stop")
            return
        except PyTango.DevFailed, tmp:
            print self.label,": cannot stop."
            pass

    def abort(self):
        """Stop: this is legacy"""
        self.stop()
        return

    def start(self,time=None):
        "Integration time is read, then written only if different, then start command is sent asynchrously."
        if(time!=None): self.int_time=time
        if (not(self.master)):
            raise Exception("This unit is slave. Start the master instead.")
        try:                
            __t=self.DP.read_attribute("integrationTime").value
            if(__t<>self.int_time):
                self.DP.write_attribute(self.time,self.int_time)
            #self.DP.command_inout_asynch("Start")
            return self.command("Start")
        except PyTango.DevFailed, tmp:
            print "Error setting counting time."
            raise tmp
        except PyTango.CommunicationFailed, tmp:
            print self.label," is in error:"
            print "Communication Failed!"
            raise tmp
        except Exception, tmp:
            print "Got unmanaged exception from counter ",self.label," no retry in this case."
            raise tmp

    def read(self):
        "Returns a tuple of values."
        try:
            return map(lambda x: x.value, self.DP.read_attributes(self.counter_names))
        except PyTango.DevFailed, tmp:
            print "Cannot read counters... ",
            raise tmp
        except PyTango.CommunicationFailed, tmp:
            print self.label,": communication Failed... waiting 3 sec more..."
            if obstinate_retries==self.maxRetries: 
                print "Maximum retries exceeded!\n"
                raise tmp
            else:
                sleep(3.)
        except Exception, tmp:
            print self.label,": is in error. Read function in counter_class, counter instance."
            raise tmp
            
    def count(self,time=1.):
        """-count- send a start then it waits, it finally reads and returns the result.
        In case of communication failure it tries again after 3s. Usually this workaround works fine."""
        if (not(self.master)):
            raise Exception("This unit is slave. Start the master instead.")
        for i in range(self.maxRetries):
            try:
                self.start(time)
                #sleep(time*0.8)
                while(self.state()==DevState.RUNNING):
                    pass
                    #sleep(self.deadtime)
                return self.read()
            except PyTango.DevFailed, tmp:
                print self.label,": error in counter class: command count. Device returns DevFailed."
                raise tmp
            except PyTango.CommunicationFailed, tmp:
                print "Communication Failed... waiting 3 sec more..."
                sleep(3.)
            except (KeyboardInterrupt,SystemExit), tmp:
                try:
                    self.stop()
                except:
                    try:
                        self.stop()
                    except:
                        print self.label,": cannot stop counter..."
                raise tmp
            except Exception, tmp:    
                print self.label,": error in counter class: command count." 
        raise tmp

    def writeDark(self):
        """Use it after one dark count to store dark counter values.
        If a mask is provided, counters corresponding to zeros are set to zero."""
        dark = list(array(self.read(),"f") * array(self.mask) / self.DP.integrationTime)
        print "dark values are:", dark
        self.DP.put_property({'SPECK_DARK_VALUES': map(str, dark)})
        return self.readDark()
        
    def readDark(self):
        """Reload dark values from device to python object and then return it."""
        dark = self.DP.get_property("SPECK_DARK_VALUES")['SPECK_DARK_VALUES']
        if dark == []:
            self.DP.put_property({'SPECK_DARK_VALUES':['0',] * len(self.user_readconfig)})
            dark = ['0',] * len(self.user_readconfig)
        elif len(dark) > len(self.user_readconfig):
            print "%s WARNING: dark current stored in device has wrong length: tail is cut."%self.label
            dark = dark[:len(self.user_readconfig)]
        elif len(dark) < len(self.user_readconfig):
            print "%s WARNING: dark current stored in device has wrong length: adding zeros."%self.label
            dark = dark + ['0',] * (len(self.user_readconfig)-len(dark))
        elif len(dark) == len(self.user_readconfig):
            print "dark values read from device %s"%self.label
        self.dark = map(float, dark)
        return self.dark

    def clearDark(self):
        self.DP.put_property({'SPECK_DARK_VALUES':['0',] * len(self.user_readconfig)})
        return self.readDark()
        
    def wait(self):
        """Just wait while cpt is in RUNNING mode"""
        for i in range(self.maxRetries):
            try:
                while(self.state()==DevState.RUNNING):
                    pass #sleep(self.deadtime)
                return
            except PyTango.DevFailed, tmp:
                print self.label,": error in counter class: command wait (state). Device returns DevFailed."
                raise tmp
            except PyTango.CommunicationFailed, tmp:
                print "Communication Failed... sleeping 10*deadtime"
                sleep(self.deadtime*10)
            except (KeyboardInterrupt,SystemExit), tmp:
                try:
                    self.stop()
                except:
                    try:
                        self.stop()
                    except:
                        print self.label,": cannot stop counter..."
                raise tmp
            except Exception, tmp:
                print self.label,": error in counter class: command count." 
                raise tmp
            
    def continuous(self,flag=None):
        if flag==None:
            return self.DP.read_attribute("continuous").value
        elif flag in [True,False]:
            self.DP.write_attribute("continuous",flag)
            sleep(self.deadtime*2)
            return self.continuous()
        else:
            raise Exception("counter.continuous() accepts only False, True and None")
        return


