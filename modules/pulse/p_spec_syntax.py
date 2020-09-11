#Spec like commands created on 3/12/2007

#Imports section
#from IPython.core.ipapi import get as get_ipython
from IPython.core.getipython import get_ipython
from numpy import log, sin, cos, tan, exp, sum
import numpy
import exceptions
from time import time, sleep
import os, shutil
import thread
import tables


import PyTango
from PyTango import DevState
import Universal_Prefilter

import p_post_calc

#Speclike functions

from numpy import mod
from mycurses import *

def whois(x):
    """This function may return wrong results if the object supplied 
    has a non unique value. For example it will not work on a simple
    variable, but use it on object instances, they have unique addresses."""
    names = []
    g = get_ipython().user_ns
    #g = globals()
    for i in g:
        try:
            j = eval(i, g)
        except:
            j = g[0]
        try:
            Congruente = (len(j) == 1)
            j = j[0]
        except:
            Congruente = True
        if Congruente:
            try:
                if x == eval(i, g) and not(i.startswith("_")):
                    names.append(i)
            except:
                #print i
                pass
    if len(names) == 0:
        return None
    else:
        return names[0]


def wa(returns = False, verbose = True):
    """Tells the correspondence between tango and python motor names and their positions. 
    Should be rewritten to point to a dictionary of classes defined in the main initialisation.
    The list of classes is presently hard coded."""
    lm=[]
    g = get_ipython().user_ns
    #g=globals()
    for i in g:
        if not(i.startswith("_")):
            j=eval(i,g)
            if isinstance(j,eval("motor",g)) or isinstance(j,eval("piezo",g)) or isinstance(j,eval("motor_slit",g)) \
            or isinstance(j,eval("mono1",g)) or isinstance(j,eval("moveable",g)): 
                lm.append([i,j])
    lm.sort()
    outout=[]
    if verbose:
        print "pySamba motors:"
    color=RED
    for i in lm:
        if color==RED:
            color=""
        else:
            color=RED
        try:
            outoutline="%18s is %32s at %g"%(i[0],i[1].label,i[1].pos())
        except:
            outoutline="%18s is %32s at %s"%(i[0],i[1].label,"nan")
        if verbose: print color+outoutline+RESET
        if returns: outout.append(outoutline)
    if returns:
        return outout 
    else:
        return

def wm(x):
    if type(x) in [tuple, list]:
        out = map(lambda i: (whois(i), i.pos()), x)
        for i in out:
            print "%s at %g" % (i[0],i[1])
    else:
        return x.pos()

def whereall():
    return wa()

def move_motor(*motor,**kw):
    """Move one or more motors. Support motor lists or just a motor object.
    Syntax move_motor(motor1,1,motor2,123.2,motor3,12).
    Only an even number of parameters is acceptable.
    """
    verbose=True
    if "verbose" in kw.keys():
        verbose = kw["verbose"]
    if mod(len(motor),2)<>0 : raise exceptions.SyntaxError("odd number of parameters!")
    motors=[]
    if verbose:
        textout = map(lambda i: "%s was %g"%(whois(i),i.pos()), motor[::2])
        for i in textout:
            print i
    try:
        for i in range(0,len(motor),2):
            motor[i].go(motor[i+1])
            motors.append(motor[i])
        return wait_motor(motors, verbose=verbose)
    except (KeyboardInterrupt,SystemExit), tmp:
        for i in motors:
            i.stop()
        raise tmp
    except PyTango.DevFailed, tmp:
        for i in motors:
            i.stop()
        raise tmp
    except Exception, tmp:
        print "Unhandled error... raising exception"
        raise tmp

def wait_motor(motor, deadtime=0.025, timeout=-0.05, delay=None, verbose=True):
    """Wait for a motor to move and stop. Support motor lists or just a motor object. 
    To be used inside the class as a general wait procedure and as a 
    support for multimotor movements through multi motor.go commands."""
    argument_type=type(motor)
    if (not(argument_type in [tuple,list])): 
        motor_list=(motor,)
    else:
        motor_list=motor
    label_list={}
    if verbose:
        for i in motor_list:
            label_list[i] = whois(i)
    #Now the argument IS a list, anyway.
    if delay==None:
        delay=0.
        for i in motor_list:
            try:
                if i.delay>delay: delay=i.delay
            except:
                pass
    try:
        condition=True
        t=0.
        while(condition and (t<timeout)):
            sleep(deadtime)
            condition=False
            for i in motor_list:
                if(i.state() == DevState.MOVING):
                    condition = False
                    break    
            t+=deadtime
        condition=True
        if verbose:
            for i in map(lambda x: (x.label,x.pos()), motor_list):
                print " " * 40 + "\r",
                print "%s    %+8.6e" % (i[0], i[1])
        while(condition):
            sleep(deadtime)
            condition = (DevState.MOVING in map(lambda x: x.state(), motor_list))
            if verbose:
                print "\033[%iA" % (len(motor_list)),
                for i in map(lambda x: (label_list[x], x.pos()), motor_list):
                    print " " * 40 + "\r",
                    print "%s    %+8.6e"%(i[0], i[1])

        if verbose: print ""
        sleep(delay)
        if len(motor_list) == 1:
            return motor_list[0].pos()
        else:
            return [x.pos() for x in  motor_list]
    except (KeyboardInterrupt,SystemExit), tmp:
        for i in motor_list:
            i.stop()
        raise tmp
    except PyTango.DevFailed, tmp:
        raise tmp
    except Exception, tmp:
        print "Unhandled error, raising exception..."
        raise tmp

def go_motor(*motor):
    """Move one or more motors. Support motor lists or just a motor object. 
    Syntax move_motor(motor1,1,motor2,123.2,motor3,12). 
    Only an even number of parameters is acceptable.
    """
    motors=[]
    if mod(len(motor),2)<>0 : raise exceptions.SyntaxError("odd number of parameters!")
    try:
        for i in range(0,len(motor),2):
            motor[i].go(motor[i+1])
            motors.append(motor[i])
        return
    except (KeyboardInterrupt,SystemExit), tmp:
        for i in motors:
            i.stop()
        raise tmp
    except PyTango.DevFailed, tmp:
        for i in motors:
            i.stop()
        raise tmp
    except Exception, tmp:
        print "Unhandled error... raising exception"
        raise tmp


def mv(*args):
    """Spec like absolute move.
    But, can move one or several motors"""
    if len(args)<1:
        raise Exception("origin: mv","Error: Missing arguments!")
    if len(args)==1:
        return args[0].pos()
    if mod(len(args),2)==0:
    #    if len(args)==2:
    #        return args[0].pos(args[1])
    #    else:
        return move_motor(*args)
    else:
        raise Exception("origin: mv","Error: Odd number of parameters!")

def lm(x):
    try:
        return x.lm()
    except Exception, tmp:
        print tmp
        return None

def lmunset(x):
    try:
        return x.lmset(None, None)
    except Exception, tmp:
        print tmp
        return None

def lmset(x,min_pos = None, max_pos = None):
    try:
        return x.lmset(min_pos, max_pos)
    except Exception, tmp:
        print tmp
        return x.lm()

def mvr(*args):
    "Spec like relative move"
    if len(args) < 1:
        raise Exception("origin: mvr","Error: Missing arguments!")
    elif len(args) == 1:
        return args[0].pos()
    elif mod(len(args), 2) == 0:
        newargs = list(args)
        for i in range(1, len(args), 2):
            newargs[i] = (args[i - 1].pos() + args[i])
        return mv(*newargs)
        
def Iref(x):
    "WARNING: expert command! --> execute initialize reference position."
    try:
        if "InitializeReferencePosition" in dir(x) or "InitializeReferencePosition" in x.device_command_list:
            x.InitializeReferencePosition()
        elif "InitReferencePosition" in x.device_command_list:
            x.InitReferencePosition()
        else:
             print Exception("Cannot Execute Initialize Reference Position on motor")
    except:
        print "Cannot Execute Initialize Reference Position on motor"
    sleep(0.2)
    wait_motor(x)
    sleep(0.2)
    return x.pos()

def Dpos(*args):
    "WARNING: expert command! --> define the position of the motor."
    if mod(len(args), 2): 
        raise Exception("Dpos: odd number of parameters")
    for i in range(len(args))[::2]:
        try:
            args[i].DefinePosition(args[i+1])
            wait_motor(args[i])
        except Exception, tmp:
            print tmp
            print "Cannot Execute Initialize Reference Position on motor"
    for i in args[::2]:
        try:
            print i.label, " set at ", i.pos()
        except:
            pass
    return map(lambda i: i.pos(), args[0::2])
   
def tw(x,step):
    try:
        print "[Ctrl-C to exit] [Press Return to Step] [Type value to change step]\nPosition is (%g) Step is (%g) "%(x.pos(),step)
        while(True):
            s=raw_input()
            if s=="":
                x.pos(x.pos()+step),"\r",
                print x.pos()
            else:
                try:
                    step=float(s)
                    print "Position is (%g) Step is (%g)"%(x.pos(),step)
                except:
                    print "What do you mean by? ...",s
                    print "[Ctrl-C to exit] [Press Return to Step] [Type value to change step]"
    except exceptions.KeyboardInterrupt:
        return x.pos()

def tweak(x,step):
    return tw(x,step)


def stop(*args):
    """Spec like forward move.
    May forward one or several motors"""
    try:
        for i in args:
            if "stop" in dir(i):
                i.stop()
            elif "DP" in dir(i) and "stop" in dir(i.DP):
                i.DP.stop()
            else:
                if label in dir(i):
                    print i.label," has no method stop defined."
        wait_motor(*args)
    except Exception, tmp:
        for i in args:
            try:
                i.stop()
            except Exception, tmp2:
                print tmp2
                pass
        raise tmp

def fw(*args):
    """Spec like forward move.
    May forward one or several motors"""
    try:
        for i in args:
            i.forward()
        wait_motor(args)
    except Exception, tmp:
        for i in args:
            try:
                i.stop()
            except Exception, tmp2:
                print tmp2
                pass
        raise tmp

def bw(*args):
    """Spec like backward move.
    May forward one or several motors"""
    try:
        for i in args:
            i.backward()
        wait_motor(args)
    except Exception, tmp:
        for i in args:
            try:
                i.stop()
            except Exception, tmp2:
                print tmp2
                pass
        raise tmp
            
def open(*x):
    return Open(*x)

def init(*x):
    "init action on an object"
    if type(x) in [tuple,list]:
        if len(x)==1: x=x[0]    
    if type(x) in [tuple,list]:
        States={}
        for i in x:
            try:
                i.init()
                States[i]=i.state()
            except Exception, tmp:
                try:
                    print "Init on ",i.label,"failed"
                except:
                    print "Failure!"
                raise tmp
        return States
    else:
        return x.init()

def start(*x):
    "start action on an object"
    if type(x) in [tuple,list]:
        if len(x)==1: x=x[0]    
    if type(x) in [tuple,list]:
        States={}
        for i in x:
            try:
                i.start()
                States[i]=i.state()
            except Exception, tmp:
                try:
                    print "Start on ",i.label,"failed"
                except:
                    print "Failure!"
                raise tmp
        return States
    else:
        return x.start()

def stop(*x):
    "stop action on an object"
    if type(x) in [tuple,list]:
        if len(x)==1: x=x[0]    
    if type(x) in [tuple,list]:
        States={}
        for i in x:
            try:
                i.stop()
                States[i]=i.state()
            except Exception, tmp:
                try:
                    print "Stop on ",i.label,"failed"
                except:
                    print "Failure!"
                raise tmp
        return States
    else:
        return x.stop()

def off(*x):
    "off action on an object"
    if type(x) in [tuple,list]:
        if len(x)==1: x=x[0]    
    if type(x) in [tuple,list]:
        States={}
        for i in x:
            try:
                i.off()
            except Exception, tmp:
                try:
                    print "OFF on ",i.label,"failed"
                except:
                    print "Failure!"
                raise tmp
        sleep(0.2)
        for i in x:
            try:
                States[i]=i.state()
            except Exception, tmp:
                try:
                    print "State on ",i.label,"failed"
                except:
                    print "Failure!"
                raise tmp
        return States
    else:
        return x.off()

def on(*x):
    "on action on an object"
    if type(x) in [tuple,list]:
        if len(x)==1: x=x[0]    
    if type(x) in [tuple,list]:
        States={}
        for i in x:
            try:
                i.on()
            except Exception, tmp:
                try:
                    print "ON on ",i.label,"failed"
                except:
                    print "Failure!"
                raise tmp
        sleep(0.2)
        for i in x:
            try:
                States[i]=i.state()
            except Exception, tmp:
                try:
                    print "State on ",i.label,"failed"
                except:
                    print "Failure!"
                raise tmp
        return States
    else:
        return x.on()



def Open(*x):
    "Open action on an object (valve? Front end? ...)"
    if type(x) in [tuple,list]:
        if len(x)==1: x=x[0]    
    if type(x) in [tuple,list]:
        States={}
        for i in x:
            try:
                i.open()
                States[i]=i.state()
            except Exception, tmp:
                try:
                    print "Open on ",i.label,"failed"
                except:
                    print "Failure!"
                raise tmp
        return States
    else:
        return x.open()

def close(*x):
    return Close(*x)

def Close(*x):
    "Close action on an object (valve? Front end? ...)"
    if type(x) in [tuple,list]:
        if len(x)==1: x=x[0]
    if type(x) in [tuple,list]:
        States={}
        for i in x:
            try:
                i.close()
                States[i]=i.state()
            except Exception, tmp:
                try:
                    print "Close on ",i.label,"failed"
                except:
                    print "Failure!"
                raise tmp
        return States
    else:
        return x.close()

def state(x):
    return x.state()

def ps(x):
    """ print the status of x to screen"""
    return status(x)

def status(x):
    print x.status()

def editmacro(macrofilename):
    try:
        filepath = os.getcwd()
        if not macrofilename[-3:] in [".py","txt"]:
            macrofilename += ".py"
        os.system("nedit " + macrofilename)
    except Exception, tmp:
        print tmp
    return filepath + os.sep + macrofilename

def domacro(macrofilename, n=1):
    """macro file is a python code in the current folder or
    in the scripts folder in the __pysamba_root folder.
    n may be used to repeat n times the same macro."""
    shell = get_ipython()
    if not(macrofilename in os.listdir(".")):
        if macrofilename in os.listdir(shell.user_ns["__pySamba_root"] + "/scripts"):
            macrofilename = shell.user_ns["__pySamba_root"] + "/scripts/" + macrofilename
        elif macrofilename + ".py" in os.listdir(shell.user_ns["__pySamba_root"] + "/scripts"):
            macrofilename = shell.user_ns["__pySamba_root"] + "/scripts/" + macrofilename + ".py"
    return shell.user_ns["Universal_Prefilter"].process_macro_file(macrofilename,shell.user_ns,n)
#    return SyntaxPrefilter.process_macro_file(macrofilename,__IP.user_ns)

def dark(dt=10):
    """dark use shclose to measure dark current over dt seconds on ct.
    dt=0 means a clear on all dark values (set them to 0).
    The shutters are not re opened after command."""
    shell = get_ipython()
    shclose = shell.user_ns["shclose"]
    shopen = shell.user_ns["shopen"]
    shstate = shell.user_ns["shstate"]
    ct = shell.user_ns["ct"]
    if dt == 0:
        ct.clearDark()
    else:
        previous = shstate()
        shclose(1)
        sleep(1)
        ct.count(dt)
        ct.writeDark()
        shopen(previous)
    print ct.readDark()
    return

class pseudo_counter:
    def __init__(self,masters=[],slaves=[],posts=[],postDictionary={},deadtime=0.05,timeout=3):
        """
        In this version the only distinction should be between masters and slaves.
        the slaves themselves are configured through prepare, pre count and post count functions if defined.
       
        The slaves know how to save their data in HDF files or data will not be saved.

        masters are started and waited (all). slaves are only read. 

        Examples:
        masters are individual counter cards
        slaves can be slave counter cards, xia cards, analog to digital converters....

        Objects passed to pseudo_counter should have at least:
        self.start(dt), self.stop(), self.read(): functions
        self.user_readconfig that is a list containing attribute information for all read values in TANGO format:
            (class PyTango.AttributeInfoEx)
        Only self.read functions returning 1D lists are accepted.
        
        posts are used in place of tango parsers:
        formulas are based on ch[number of channel] values and diplayed at the end as additional channels;
        posts cannot calculate over other posts.
        posts=[{"name":"Delta","formula":"ch[1]-ch[2]","format":"%6.3f","units"}]

        BEWARE posts have a limited usage and are not used in continuous scans.
        Have a look to p_post_calc.dataBlock instructions for defining a postDictionary to perform such computations 
        and store results in the HDF file. (Highly experimental!)

        New version !
        A multi points time scan with data saving can be performed with the following sequence
        A single point without data saving follow the same sequence or may be performed with a simple count method.
        
        The wait method must be used and all steps are necessary. For instance the wait method performs the postCount operation
        as the preCount is performed by the start method

        (*) = data saving is active 

        self.prepare
        self.openHDFfile (*)
        self.start
        self.wait
        self.saveData2HDF (*)
        self.closeHDFfile (*)
        """

        #HDF filters should be defined as a global parameter with a reasonable default. This modification is pending.

        self.masters = masters
        self.slaves = slaves
        self.all = masters + slaves 
        self.preCountList = []
        self.postCountList = []
        self.stepWaitList = []
        self.handler = None

        for i in slaves: 
            if "preCount" in dir(i):
                self.preCountList.append(i)
            if "postCount" in dir(i):
                self.postCountList.append(i)
            if "stepWait" in dir(i):
                self.stepWaitList.append(i)

        self.deadtime = deadtime
        self.timeout = timeout
        self.user_readconfig = []
        self.mca_units = []
        n = 0
        self.clock_channel = -1
        #Data for prepare
        self.nexusFileGeneration = False
        self.NbFrames=1
        #
        for i in self.all:
            self.user_readconfig+=i.user_readconfig
            if "read_mca" in dir(i):
                self.mca_units.append(i)
            if "clock_channel" in dir(i):
                self.clock_channel = i.clock_channel + n
            n += len(i.user_readconfig)
        
        #Strange xia behaviour due to init system and config file depencency
        #This code should be removed, too specific
        self.xia_units = [i for i in self.mca_units if "currentMode" in dir (i)]
        #
        
        self.dark = self.readDark()
        self.posts = []
        for i in posts:
            if not "name" in i.keys() or not "formula" in i.keys():
                raise Exception("Missing parameters in posts definition, check config.")
            if not "units" in i.keys():
                i["units"]=""
            if not "format" in i.keys():
                i["format"]="%9g"
            self.posts.append(i)
        
        self.postDictionary = postDictionary
        return

    def reinit(self):
        for i in self.all:
            if "reinit" in dir(i):
                i.reinit()
        self.user_readconfig = []
        n=0
        for i in self.all:
            self.user_readconfig += i.user_readconfig
            if "clock_channel" in dir(i):
                self.clock_channel = i.clock_channel + n
            n += len(i.user_readconfig)
        return

    def __call__(self,dt=1,NbFrames=1, nexusFileGeneration=False, fileName ="", HDFfilters = tables.Filters(complevel = 1, complib='zlib')):
        tmp = self.count(dt, NbFrames, nexusFileGeneration, fileName, HDFfilters)
        if NbFrames == 1:
            ltmp = len(tmp) - len(self.posts)
            s = ""
            plainS = ""
            l = 3
            for i in range(0,ltmp,l):
                s+="\n"
                for j in range(l):
                    if i+j<ltmp:
                        plainS += "%03i " % (i + j) + "% -20s" % self.user_readconfig[i+j].label + ":"\
                        + "%9s" % (self.user_readconfig[i+j].format % (tmp[i+j]))+" % -8s " % self.user_readconfig[i+j].unit + " "
                        s += BOLD + "%03i " % (i + j) + RED + "% -20s" % self.user_readconfig[i+j].label + ":" + RESET\
                        + "%9s" % (self.user_readconfig[i+j].format % (tmp[i+j]))+" % -8s " % self.user_readconfig[i+j].unit + " "
            print s
            print "User Defined Post Calculations:"
            nchan = ltmp
            for i in self.posts:
                try:
                    print BOLD + "%03i " % (nchan) + RED + "% -10s" % i["name"] + ":" + RESET + i["format"] % tmp[nchan] + i["units"]
                except Exception, CatchedExc:
                    print CatchedExc
                nchan = nchan + 1
            shell = get_ipython()
            shell.logger.log_write(plainS+"\n", kind='output')
        else:
            print "Time scan finished."
            if not nexusFileGeneration:
                print "Data not saved since nexusFileGeneration is not active."
        return

    def state(self):
        for i in self.masters:
            _s=i.state()
            if _s==DevState.RUNNING:
                return DevState.RUNNING
            if _s==DevState.FAULT:
                return DevState.FAULT
            if _s==DevState.UNKNOWN:
                return DevState.UNKNOWN
            #if i.state() == DevState.ON:
            #    return DevState.ON
            #if i.state() == DevState.OFF:
            #    return DevState.OFF
            if _s==DevState.INIT:
                return DevState.INIT
            if _s==DevState.ALARM:
                return DevState.ALARM
        return DevState.STANDBY
    
    def masters_state(self):
        return self.state()

    def status(self):
        return "Nothing"

    def __repr__(self):
        return "pseudo_counter"

    def __str__(self):
        return "pseudo_counter"
    
    def init(self):
        for i in self.all:
            i.init()
        return

    def prepare(self,dt=1, NbFrames=1, nexusFileGeneration=False, stepMode=False, upperDimensions=()):
        """New version of pseudo_counter, commonly defined ct:
        the prepare must be used before counting, the sequence should be as follows.

        (*) = data saving is active 

        self.prepare
        self.openHDFfile (*)
        self.start
        self.wait
        self.saveData2HDF (*)
        self.closeHDFfile (*)
        """
        if stepMode:
            for i in self.masters:
                if "prepare" in dir(i):
                    i.prepare(dt = dt, NbFrames = 1,nexusFileGeneration = nexusFileGeneration, stepMode=stepMode,upperDimensions=upperDimensions)
        else:
            for i in self.masters:
                if "prepare" in dir(i):
                    i.prepare(dt = dt, NbFrames = NbFrames,nexusFileGeneration = nexusFileGeneration,stepMode=stepMode,upperDimensions=upperDimensions)
        for i in self.slaves:
            if "prepare" in dir(i):
                i.prepare(dt = dt, NbFrames = NbFrames,nexusFileGeneration = nexusFileGeneration,stepMode=stepMode,upperDimensions=upperDimensions)
        return

    def start(self,dt=1):
        """slaves and arming is moved to prepare"""
        for i in self.preCountList:
            i.preCount(dt=dt)
        for i in self.masters:
            i.start(dt=dt)
        return


    def stop(self):
        try:
            for i in self.all:
                i.stop()
            while(self.state() == DevState.RUNNING):
                sleep(self.deadtime)
            return
        except Exception, tmp:
            #Try again
            for i in self.all:
                i.stop()
            raise tmp
        finally:
            try:
                self.closeHDFfile()
            except:
                pass
    def read(self):
        "All objects must provide a read command, this command will supply a list of values"
        counts=[]
        for i in self.all:
            counts += i.read()
        if len(counts) <> len(self.user_readconfig):
            self.reinit()
        #Use counts for calculating posts (duplicate values for security of original counts)
        ch = [] + counts
        cposts = []
        for i in self.posts:
            try:
                cposts.append(eval(i["formula"]))
            except Exception, catchExc:
                cposts.append(numpy.nan)
                print catchExc,":",i["name"], "=", i["formula"]
        return counts + cposts

    def read_mca(self):
        """read all mca units in self.mca_units.
        One mca unit is an object possessing a read_mca function and a channels_labels list;
        this function must return a list of 1D vectors, every vector is a separate channel.
        This read_mca join all channels together as they are listed in self.all 
        and return a dictionary with self.unit.label_01 as typical key and the 1D vector as 
        corresponding value."""
        mcas={}
        for i in self.mca_units:
            k=0
            if "channels_labels" in dir(i):
                for j in i.read_mca():
                    mcas[i.channels_labels[k]]=j
                    k+=1
            else:
                for j in i.read_mca():
                    k+=1
                    mcas[i.label+"_%02i"%k]=j
        return mcas
        
    def wait(self):
        try: 
            t0=time()
            while(self.masters_state() <> DevState.RUNNING and time() - t0 < self.timeout):
                sleep(self.deadtime)
            while(self.masters_state() == DevState.RUNNING):
                sleep(self.deadtime) 
            for i in self.postCountList:
                i.postCount()
            return
        except (KeyboardInterrupt, SystemExit), tmp:
            self.stop()
            raise tmp

    def waitMasters(self):
        try: 
            t0=time()
            while(self.masters_state() <> DevState.RUNNING and time() - t0 < self.timeout):
                sleep(self.deadtime)
            while(self.masters_state() == DevState.RUNNING):
                sleep(self.deadtime) 
#            for i in self.postCountList:
#                i.postCount()
            return
        except (KeyboardInterrupt, SystemExit), tmp:
            self.stop()
            raise tmp

    def count(self, dt=1, NbFrames=1, nexusFileGeneration=False, fileName ="", stepMode=False, HDFfilters = tables.Filters(complevel = 1, complib='zlib')):
        """It counts and return results for a single point.
        New function: multi points (frames) that makes sense when saving data.
        The data file must be named without prepending a folder specification.
        This restriction is due to the naming convention sending hdf files directly to the ruche subfolder.
        For step scans use prepare and then use stepCount for one single count of the series."""
        try:
            self.prepare(dt=dt, NbFrames = NbFrames, nexusFileGeneration = nexusFileGeneration,stepMode=stepMode)
            if nexusFileGeneration:
                if fileName == "":
                    handler = self.openHDFfile("ascan_out", HDFfilters = HDFfilters)
                else:
                    handler = self.openHDFfile(fileName, HDFfilters = HDFfilters)
                print "Saving data into %s" % handler.filename
            self.start(dt=dt)
            self.wait()
            if nexusFileGeneration:
                self.saveData2HDF(wait=True)
                self.closeHDFfile()
        finally:     
            self.stop()
            if nexusFileGeneration:
                self.closeHDFfile()
        return self.read()

    def stepCount(self, dt=1):
        try:
            self.start(dt=dt)
            self.waitMasters()
            for i in self.stepWaitList:
                i.stepWait()
        except:
            self.stop()
            raise
        return self.read()
   
    def readDark(self):
        dark=[]
        for i in self.all:
            if "readDark" in dir(i):
                dark += list(i.readDark())
            else:
                dark += [0,] * len(i.user_readconfig) 
        self.dark = dark
        return self.dark
        
    def writeDark(self):
        for i in self.all:
            if "writeDark" in dir(i):
                i.writeDark()
        return self.readDark()
        
    def clearDark(self):
        for i in self.all:
            if "clearDark" in dir(i):
                i.clearDark()
        return self.readDark()
   
    def openHDFfile(self, fileName, HDFfilters = tables.Filters(complevel = 1, complib='zlib')):
        """
        Use it to open an HDF file for writing scan results.
        self.handler will store the pointer to the file object

        The fileName is only a first part of the actual file name
        openHDFfile invoke the __prepareHDF method: use this method only AFTER the prepare method.

        The method returns the fileName to let the calling process to use it.
        To write data to this file in the calling process, use the self.handler pointer

        The file has to be explicitly closed at the end of the scan: self.closeHDFfile.
        The saving scheme use the old global variable __DefaultBackup_Folder to determine where to save.
        This has probably to be changed soon.
        """
        sh = get_ipython()
#The following line cannot work
        #self.handler = tables.openFile(findNextFileName(sh.user_ns["__Default_Data_Folder"] + os.sep + fileName, "hdf"), "w")
#The following line works but directly writes in ruche
        #self.handler = tables.openFile(findNextFileName(filename2ruche(fileName),"hdf"), "w")
#The following lines could work, but closeHDFfile should move the file from temp folder.
#Find the final file name
        self.final_filename = findNextFileName(filename2ruche(fileName),"hdf")
#Prepare the temporary file name
        __itmp = self.final_filename.rfind(os.sep)
        if __itmp > 0:
            __tmp = sh.user_ns["__SPECK_CONFIG"]["TEMPORARY_FOLDER"] + self.final_filename[__itmp:]
        else:
            __tmp = sh.user_ns["__SPECK_CONFIG"]["TEMPORARY_FOLDER"] + os.sep + self.final_filename[:]
        self.handler = tables.openFile(__tmp, "w")
#file is open and can be prepared
        self.handler.createGroup("/", "data")
        self.handler.createGroup("/", "post")
        self.handler.createGroup("/", "context")
        self.handler.createGroup("/", "coordinates")
        self.__prepareHDF(HDFfilters = HDFfilters)
        return self.handler

    def closeHDFfile(self):
        self.handler.close()
#Now move file from temporary folder to ruche
        shutil.move(self.handler.filename, self.final_filename)
        return

    def __prepareHDF(self, HDFfilters = tables.Filters(complevel = 1, complib='zlib')):
        """the handler is an already opened file object that will be passed to all masters and slaves
        owing a prepareHDFfunction
        The function will not open nor close the file to be written
        This function should be used to write more standard scan macros"""
        for i in self.all:
            if "prepareHDF" in dir(i):
                i.prepareHDF(self.handler, HDFfilters = HDFfilters)
        return

    def saveData2HDF(self, wait=True,upperIndex=(),reverse=1):
        """the handler is an already opened file object that will be passed to all masters and slaves
        owing a saveHDFfunction
        
        The function will not open nor close the file to be written so it has to be used after an openHDFfile method.

        This function should be used to write more standard scan macros"""
        for i in self.all:
            if "saveData2HDF" in dir(i):
                i.saveData2HDF(self.handler, wait = wait,upperIndex=upperIndex,reverse=reverse)
        if self.postDictionary not in [{}, None]:
            self.savePostDictionary2HDF(HDFfilters = tables.Filters(complevel = 1, complib='zlib'), domain="post")
        return

    def savePost2HDF(self, name, value, group = "", wait = True, HDFfilters = tables.Filters(complevel = 1, complib='zlib'),domain="post"):
        """
        the name is a string that will be the name of the value stored in the HDF file.
        The value can be saved in a subgroup to order the post calculated value in order  to find them grouped as
        xas.mux   or    map.elastic
        
        this function has been designed to store values derived from measured quantities right after scan is finished
        and just before closing the HDF file.

        The value MUST be a numpy.array. Anyway.
        
        the handler is an already opened file object that will be passed to all masters and slaves
        owing a saveHDFfunction
       
        The domain can be changed from post to other to save the data under /domain/group/name 

        The domain should be data, post and context for scan data, post calculated and contextual data respectively

        The function will not open nor close the file to be written so it has to be used after an openHDFfile method.

        This function should be used to write more standard scan macros"""
#Define shape
        try:
            value_shape = numpy.shape(value)
        except:
            value_shape=()
#Find type from one value
        value_type = value.dtype
#Define atom type
        value_atom = tables.Atom.from_dtype(value_type)
#Get the right node and/or create it
        try:
            if group == "":
                outGroup = self.handler.getNode("/" + domain )
            else:
                outGroup = self.handler.getNode("/" + domain + "/" + group)
        except:
            if group <> "":
                try:
                    self.handler.createGroup("/" + domain, group)
                except:
                    pass
                outGroup = self.handler.getNode("/" + domain + "/" + group)
#Create nodes with the correct shape and atom type
        self.handler.createCArray(outGroup, name, title = name,\
        shape = value_shape, atom = value_atom, filters = HDFfilters)
#Point to node
        if group <> "":
            outNode = self.handler.getNode("/" + domain + "/" + group + "/" + name)
        else:
            outNode = self.handler.getNode("/" + domain + "/" + name)
#Store value
        outNode[:] = value
        return

    def savePostDictionary2HDF(self, HDFfilters = tables.Filters(complevel = 1, complib='zlib'), domain="post"):
        """
       
        this function has been designed to store values derived from measured quantities right after scan is finished
        and just before closing the HDF file.

        Values are defined using the p_post_calc scheme in a dictionary to be supplied when initializing the pseudo counter. 

        The domain can be changed from post to other to save the data under /domain/name 

        The function will not open nor close the file to be written so it has to be used after an openHDFfile method.

        This function is highly experimentally and risky, it is active if a postDictonary is defined."""
        db = p_post_calc.dataBlock(self.postDictionary, HDFfile=self.handler, domain=domain, HDFfilters=HDFfilters)
        db.evaluate()
        del db
        return

def findNextFileName(prefix,ext,file_index=1):
    #
    #Prepare correct filename to avoid overwriting
    #
    psep=prefix.rfind(os.sep)
    if(psep<>-1): 
        fdir=prefix[:psep]
    else:
        fdir="."
    if(psep<>-1): prefix=prefix[psep+1:]
    if ext<>"":
        fname=prefix+"_"+"%04i"%(file_index)+"."+ext
    else:
        fname=prefix+"_"+"%04i"%(file_index)
    _dir=os.listdir(fdir)
    while(fname in _dir):
        file_index+=1
        if ext<>"":
            fname=prefix+"_"+"%04i"%(file_index)+"."+ext
        else:
            fname=prefix+"_"+"%04i"%(file_index)
    fname=fdir+os.sep+fname
    return fname


def findNextFileIndex(prefix,ext,file_index=1):
    #
    #Prepare correct filename to avoid overwriting
    #
    psep=prefix.rfind(os.sep)
    if(psep<>-1): 
        fdir=prefix[:psep]
    else:
        fdir="."
    if(psep<>-1): prefix=prefix[psep+1:]
    if ext<>"":
        fname=prefix+"_"+"%04i"%(file_index)+"."+ext
    else:
        fname=prefix+"_"+"%04i"%(file_index)
    _dir=os.listdir(fdir)
    while(fname in _dir):
        file_index+=1
        if ext<>"":
            fname=prefix+"_"+"%04i"%(file_index)+"."+ext
        else:
            fname=prefix+"_"+"%04i"%(file_index)
    return file_index

def filename2ruche(filename):
    ##############################################################
    #
    #Returns complete filename to save data directly in ruche
    #it works only if
    #current folder is in data path
    #
    __IPy = get_ipython()
    __Default_Data_Folder = __IPy.user_ns["__SPECK_CONFIG"]["TEMPORARY_HOME"]
    __Default_Backup_Folder = __IPy.user_ns["__SPECK_CONFIG"]["DATA_FOLDER"]
    if __Default_Backup_Folder == "":
        print "No backup/ruche folder defined."
        return
#The following line is risky. Now setuser is the only way to change temporary home and saving points
    #currentDataFolder=os.path.realpath(os.getcwd())
#the folder is set via the config:
    currentDataFolder=__IPy.user_ns["__SPECK_CONFIG"]["USER_FOLDER"]
#
    currentBackupFolder=__Default_Backup_Folder+os.sep+\
    currentDataFolder.lstrip(__Default_Data_Folder.rstrip(os.sep))
    cbf=currentBackupFolder
    ruche_filename = currentBackupFolder + os.sep + filename
    return ruche_filename
   

    
    

    
    

    
    
