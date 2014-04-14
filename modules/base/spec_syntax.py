#Spec like commands created on 3/12/2007

#Imports section
from IPython.core.ipapi import get as get_ipython

import exceptions
from time import time, sleep
import os
import thread

from motor_class import motor,piezo,motor_slit,move_motor, wait_motor
from moveable import moveable
from mm4005 import mm4005_motor
from mono1b import mono1

from PyTango import DevState
import Universal_Prefilter

#Speclike functions

from numpy import mod
from mycurses import *

#def whois(x, glob=globals()):
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


#def wa(g = globals(),returns = False, verbose = True):
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
            if isinstance(j,motor) or isinstance(j,piezo) or isinstance(j,motor_slit) \
            or isinstance(j,mono1) or isinstance(j,mm4005_motor) or isinstance(j,moveable): 
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

#def whereall(g=globals()):
#    return wa(g)

def wm(x):
    return x.pos()

def whereall():
    return wa()

#move, mover,whereall, tweak must be removed in the long form
#mv and mvr should be able to move several motors toghether and maybe take advantage of galilmultiaxis.
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

def unset_lm(x):
    try:
        return x.set_lm(None, None)
    except Exception, tmp:
        print tmp
        return None

def set_lm(x,min_pos = "Undef", max_pos = "Undef"):
    try:
        return x.set_lm(min_pos, max_pos)
    except Exception, tmp:
        print tmp
        return None

def move(*args):
    "Spec like absolute move"
    return mv(*args)

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
    "Execute initialize reference position"
    try:
        x.InitializeReferencePosition()
    except:
        print "Cannot Execute Initialize Reference Position on motor"
    wait_motor(x)
    sleep(0.2)
    return x.pos()
   
def mover(*args):
    "Spec like relative move"
    return mvr(*args)

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
            if "forward" in dir(i):
                i.forward()
            elif "DP" in dir(i) and "forward" in dir(i.DP):
                i.DP.forward()
            else:
                if label in dir(i):
                    print i.label," has no method forward defined."
        wait_motor(*args)
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
            if "backward" in dir(i):
                i.backward()
            elif "DP" in dir(i) and "backward" in dir(i.DP):
                i.DP.backward()
            else:
                if label in dir(i):
                    print i.label," has no method backward defined."
        wait_motor(*args)
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

def OFF(*x):
    "OFF action on an object"
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

def ON(*x):
    "ON action on an object"
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

#def ct(x=None):
#    """Counts on all beamline counters... just a spec-like shortcut to cpt.
#    This will be changed to scan_tools.py when possible."""
#    if x==None: 
#        return cpt.count()
#    if x<0:
#        print "Cannot work in pulse mode! Refer to hardware driver configuration."
#        return 
#    return cpt.count(x)

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
    return shell.user_ns["Universal_Prefilter"].process_macro_file(macrofilename,shell.user_ns,n)
#    return SyntaxPrefilter.process_macro_file(macrofilename,__IP.user_ns)

class pseudo_counter:
    def __init__(self,masters=[],slaves=[],slaves2arm=[],slaves2arm2stop=[],deadtime=0.,timeout=1):
        """masters are started and waited (all). slaves are only read. 
        slaves2arm are armed before masters with a start command.
        slaves2arm2stop are armed with a stop before masters,
        stopped after masters and then waited to final stop.
        Examples:
        masters are individual counter cards
        slaves can be slave counter cards
        slaves2arm2stop are the XIA cards in slave mode.
        slaves are not supposed to accept a time argument, masters yes.
        Objects passed to pseudo_counter should have at least:
        self.start(dt), self.stop(), self.read(): functions
        self.user_readconfig that is a list containing attribute information for all read values in TANGO format:
            (class PyTango.AttributeInfoEx)
        Only self.read functions returning 1D lists are accepted.
        """
        self.masters=masters
        self.slaves=slaves
        self.slaves2arm=slaves2arm
        self.slaves2arm2stop=slaves2arm2stop
        self.all=masters+slaves+slaves2arm+slaves2arm2stop
        self.deadtime=deadtime
        self.timeout=timeout
        self.user_readconfig=[]
        self.mca_units=[]
        for i in self.all:
            self.user_readconfig+=i.user_readconfig
            if "read_mca" in dir(i):
                self.mca_units.append(i)
        return

    def reinit(self):
        for i in self.all:
            if "reinit" in dir(i):
                i.reinit()
        self.user_readconfig = []
        for i in self.all:
            self.user_readconfig += i.user_readconfig
        return

    def __call__(self,dt=1):
        tmp = self.count(dt)
        ltmp = len(tmp)
        s = ""
        l = 3
        for i in range(0,ltmp,l):
            s+="\n"
            for j in range(l):
                if i+j<ltmp:
                    s += BOLD + "%03i " % (i + j) + RED + "% -10s" % self.user_readconfig[i+j].label + ":" + RESET\
                    + "%9s" % (self.user_readconfig[i+j].format % (tmp[i+j]))+" % -6s " % self.user_readconfig[i+j].unit + " "
        print s
        return

    def state(self):
        for i in self.masters+self.slaves2arm2stop:
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
        for i in self.masters:
            _s = i.state()
            if _s == DevState.RUNNING:
                return DevState.RUNNING
            if _s == DevState.FAULT:
                return DevState.FAULT
            if _s == DevState.UNKNOWN:
                return DevState.UNKNOWN
            #if i.state() == DevState.ON:
            #    return DevState.ON
            #if i.state() == DevState.OFF:
            #    return DevState.OFF
            if _s == DevState.INIT:
                return DevState.INIT
            if _s == DevState.ALARM:
                return DevState.ALARM
        return DevState.STANDBY

    def wait_armed(self):
        t0 = time()
        try:
            s = DevState.STANDBY
            while(s <> DevState.RUNNING):
                if time() - t0 > self.timeout:
                    raise Exception("pseudo_counter: timeout in self.wait_armed. timeout is %f"%self.timeout)
                s = DevState.RUNNING
                for i in self.slaves2arm + self.slaves2arm2stop:
                    i_s = i.state()
                    if i_s <> DevState.RUNNING:
                        s = i_s
                        break
        except KeyboardInterrupt, tmp:
            print "ct: Halt on user request"
            self.stop()
            raise tmp
        except Exception, tmp:
            self.stop()
            raise tmp
        return
        
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
    
    def start(self,dt=1):
        for i in self.slaves2arm2stop + self.slaves2arm:
            i.start()
        self.wait_armed()
        for i in self.masters:
            i.start(dt)
        return

    def stop(self):
        try:
            for i in self.masters:
                i.stop()
            while(self.masters_state() == DevState.RUNNING): pass
            for i in self.slaves2arm2stop:
                __tmp=thread.start_new_thread(i.stop,())
            while(self.state() == DevState.RUNNING): pass
            return
        except Exception, tmp:
            for i in self.all:
                i.stop()
                #Stop anyway!
            raise tmp

    def read(self):
        "All timebases must provide a read command, this command will supply a list of values"
        counts=[]
        for i in self.all:
            counts += i.read()
        if len(counts) <> len(self.user_readconfig):
            self.reinit()
        return counts

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
            while(self.masters_state() <> DevState.RUNNING and time() - t0 < self.timeout): pass
            while(self.masters_state() == DevState.RUNNING): pass
            for i in self.slaves2arm2stop:
                __tmp=thread.start_new_thread(i.stop,())
            while(self.state() == DevState.RUNNING): pass
            return self.state()
        except (KeyboardInterrupt, SystemExit), tmp:
            self.stop()
            raise tmp

    def count(self,dt=1):
        try:
            self.start(dt)
            self.wait()
            return self.read()
        except (KeyboardInterrupt, SystemExit), tmp:
            self.stop()
            raise tmp
    
