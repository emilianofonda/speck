#Import Python modules
import sys,os
import scipy
import exceptions
from time import asctime,time,sleep,clock
import numpy
from numpy import *

#Define environment
dn=os.getenv("SPECK")+os.sep+"modules"
sys.path.append(dn)
subdn=os.listdir(dn)
#print subdn
for i in subdn: sys.path.append(dn+os.sep+i)


##
## Data folders
##
import os
__Default_Data_Folder=os.getenv("SPECK_DATA_FOLDER")
#"/home/experiences/samba/com-samba/ExperimentalData/"
__Default_Backup_Folder=os.getenv("SPECK_BACKUP_FOLDER")
#"/nfs/ruche-samba/samba-soleil/com-samba/"




#Import generic speck modules
from Universal_Prefilter import *
import pymucal
from GracePlotter import *
try:
    import Gnuplot
except Exception, tmp:
    print "Cannot import Gnuplot"
from mycurses import *

#Import Periodic Table
print '\x1b[01;06m'
print "Loading Periodic Table: usage type Fe or other chemical symbol for information"
print '\x1b[32;01m',
print "help(pymucal) or help(atomic_data) for more details"
print '\x1b[0m'
for i in pymucal.atomic_data.atoms.keys():
        exec("%s=pymucal.atomic_data(i)"%(i))

#Import Control Related (PyTango related) modules
import PyTango
from PyTango import DeviceProxy, DevState

########
# BEEP #
########
try:
    import Tkinter
    def wakemeup():
        """Uses Tkinter to alert user that the run is finished... just in case he was sleeping..."""
        try:
            a=Tkinter.Tk()
            for j in range(5):
                for i in range(3):
                    a.bell()
                    sleep(0.025)
                sleep(0.35)
            a.destroy()
        except:
            print "WARNING: Error alerting for end of scan... no Tkinter?\n"
            print "BUT: Ignore this message if escan is working well,\n just report this to your local contact\n"
        return
except Exception, tmp:
    print "Cannot initialize wakemeup function, reason follows:"
    print tmp


########
#MAGICS#
########

#Not yet!

#
#General configuration parameters
#

__pySamba_root=os.getenv("SPECK")
__pySamba_scans=__pySamba_root+"/modules/scans/"


try:
    get_ipython().magic("logstart -ort "+__pySamba_root+"/files/log/log.txt rotate")
except Exception, tmp:
    print tmp
    print "Cannot log commands!"

    
#Import more specific speck modules

imp_mdls = ["galil_multiaxis", "xbpm_class", "PSS"]

from_mdls = {"ascan":"*","GetPositions":"*","e2theta":"*", "motor_class":"*", "mono1b":"*", "counter_class":"*", "valve_class":"valve", "pressure_gauge_class":"pressure_gauge", "thermocouple_class":"temperature_gauge", "mirror_class":"mirror", "absorbing_system_class":"*", "FrontEnd_class":"FrontEnd", "ic_gas":"xbpm_abs,  ic_abs", "NHQ_HVsupply_class":"NHQ_HVsupply", "rontec_MCA":"rontec_MCA", "mm4005":"mm4005_motor", "channel_cut":"channel_cut", "simple_DxMAP":"dxmap", "moveable":"moveable, sensor","beamline_alignement":"*","escan_class_b":"escan, escan_class", "spec_syntax":"*","setuser":"*"}

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

def instrument(name=None):
    if name == None:
        tmp = os.listdir(__pySamba_root+"/modules/instruments/")
        instrs=[]
        for i in tmp:
            if i.endswith(".py"):
                instrs.append(i[:i.rfind(".")])
        return instrs
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

setuser()
