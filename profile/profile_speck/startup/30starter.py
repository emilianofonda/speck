#
#General configuration parameters
#

import os,sys
from time import asctime,time,sleep,clock
import PyTango
from PyTango import DeviceProxy,DevState
import thread
import exceptions, traceback
import numpy
from numpy import *

try:
    import grace_np
except:
    print "grace_np module not found! No plotting in xmgrace available."
    __GRACE_FAULTY=True
try:
    import Gnuplot
except Exception, tmp:
    print "Cannot import Gnuplot"
    #raise tmp

from mycurses import *

__pySamba_root=os.getenv("SPECK")
__pySamba_scans=__pySamba_root+"/modules/scans/"

#try:
#    _ip.magic("logstart -ot "+__pySamba_root+"/files/log/log.txt rotate")
#except:
#    print "Cannot log commands!"

    
imp_mdls = ["galil_multiaxis", "xbpm_class", "PSS"]

from_mdls = {"e2theta":"*", "motor_class":"*", "mono1b":"*", "counter_class":"*", "valve_class":"valve", "pressure_gauge_class":"pressure_gauge", "thermocouple_class":"temperature_gauge", "mirror_class":"mirror", "absorbing_system_class":"*", "FrontEnd_class":"FrontEnd", "ic_gas":"xbpm_abs,  ic_abs", "NHQ_HVsupply_class":"NHQ_HVsupply", "rontec_MCA":"rontec_MCA", "mm4005":"mm4005_motor", "channel_cut":"channel_cut", "simple_DxMAP":"dxmap", "moveable":"moveable, sensor"}

__exec_files = []

for i in imp_mdls:
    try:
        exec("import "+i)
    except Exception, tmp:
        print "Error while importing ",i
        print "Exception description follows: \n",tmp

for i in from_mdls:
    try:
        exec("from %s import %s"%(i,from_mdls[i]))
    except Exception, tmp:
        print "Error while importing ",from_mdls[i]," from ",i
        print "Exception description follows: \n",tmp

#for i in __exec_files:
#    try:
#        execfile(__pySamba_root+i)
#    except Exception, tmp:
#                print "Error while executing ",__pySamba_root+i
#                print "Exception description follows: \n",tmp
                        
print "OK"


#A simple way to load Instrumental setups:

def instrument(name):
    instrument_file=__pySamba_root+"/modules/instruments/"+name+".py"
    print "Loading instrument macro from "+instrument_file
    return domacro(instrument_file)

##### External Commands: #####


def atkpanel(object):
    try:
        atkpanel_command=os.popen("which atkpanel").readlines()[0].strip()
        __oname__=object.DP.dev_name()
        print "atkpanel ",__oname__
        #os.spawnvp(os.P_NOWAIT,"/usr/Local/DistribTango/soleil-root/tango/bin/atkpanel",[" ",__oname__])
        os.system(atkpanel_command+" "+__oname__+" >& /dev/null &")
        return
    except os.EX_OSERR,tmp:
        print tmp.args
        return 
    except: 
        print "Error!"
        return

def atk(object):
    return atkpanel(object)

def _print_file(filename):
    """Send a file to the predefined unix printer: required by GetPositions """
    try:
        print "Sending file to printer... "
        #os.spawnvp(os.P_NOWAIT,"/usr/bin/lpr",[" ",filename])
        os.system("/usr/bin/lpr "+filename+" &")
        return
    except os.EX_OSERR,tmp:
        print tmp
        return 
    except Exception, tmp: 
        print "Printing Error! Ignoring..."
        print tmp
        return

def Beep(n,t):
    for i in range(n):
        os.system('echo -ne "\a"')
        sleep(t)
    return

######### Internal Variables ###########################
__allmotors=[]
__allpiezos=[]
__allmirrors=[]
__allanalog_encoders=[]
__allslits=[]
__pennings=[]
__valves=[]

#Following values are used in definitions
#they should be defined before they are defined as
#actual objects

#Main counter card
cpt=None
#A generic motor
mot=None
#The front end
FE=None
#At least the gamma beamstopper
obxg=None
#####################################################################

##Usefull constants
#Values of d here below are actually 2d !!!
__d220=2*1.92015585
__d111=2.*3.1356

__samplePos=13.95


##--------------------------------------------------------------------------------------
##General actions defined as functions: e.g. stop all motors, all motor off, etcetera
##--------------------------------------------------------------------------------------



##
##  Functions to wait for a certain time, date, for the beam to come back...
##

#try:
#    from wait_functions import wait_until
#except Exception, tmp:
#    print "wait_functions.py module in error"
#    print tmp

    

##--------------------------------------------------------------------------------------
##MOTORS
##--------------------------------------------------------------------------------------

def Stop():
    """Stop all motors that support the Stop command that are in the allmotors tuple + mirrors in mirrors tuple."""
    for mot in __allmotors+__allmirrors:
        try:
            thread.start_new_thread(mot.stop,())
            print mot.label," stop command sent.\n"
        except:
            print "Error on motor!"
    return

def MotorsOFF():
    """Put all motors that support the MotorOff command in the allmotors tuple."""
    for mot in __allmotors+__allmirrors+__allpiezos:
        try:
            mot.mo()
            print mot.label," off\n"
        except:
            print "Error on motor: "+mot.label+"\n"
    return

def MotorsON():
    """Put all motors that support the sh (servo here) command in the allmotors tuple. Turns on the piezos too."""
    for mot in __allmotors+__allmirrors+__allpiezos:
        try:
            mot.sh()
            print mot.label," on\n"
        except:
            print "Error on motor: "+mot.label+"\n"
    return

def InitMotors():
    """Init galilaxis of all motors and piezos: the init command must be supported."""
    for mot in __allmotors+__allmirrors+__allpiezos:
        try:
            mot.init()
            print mot.label," init ok"
        except:
            print "Error on motor: "+mot.label+"\n"
    return

##--------------------------------------------------------------------------------------
##Include the definition of the GetPositions and SetPositions Commands.
##--------------------------------------------------------------------------------------

##GetPositions require the _print_file function to be defined
#try:
#    execfile(__pySamba_root+"/modules/base/"+"GetPositions.py")
#except:
#    print "Error executing GetPositions.py  !!!!!!!"
#    def GetPositions():
#        return
#    def PrintPositions():
#        return


def GetPressures():
    __pressures=[__pennings,range(len(__pennings))]
    for i in range(len(__pressures[0])):
        if(__pressures[0][i].state()==DevState.OFF):
            __pressures[1][i]=nan
        else:
            __pressures[1][i]=__pressures[0][i].pressure()
    for i in range(len(__pressures[0])):
        print __pennings[i].label+"= %4.2e"%(__pressures[1][i])
    return 



#Start user defined environment:

#execfile(__pySamba_root+"/modules/user_config.py")

