from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
from builtins import range
print("Starting speck...")
import time
import os
from IPython.terminal.prompts import Prompts,Token

class MyPrompt(Prompts):
    def in_prompt_tokens(self,cli=None):
        return[(Token, os.getcwd()+"\nSPECK3"),(Token.Prompt,' >')]

ip=get_ipython()
ip.prompts=MyPrompt(ip)

#Import Python modules
import sys,os
import scipy
from time import asctime,time,sleep,clock
#Why these import here? old things forgotten here?
import numpy
from numpy import *

#Define environment
__SPECK_CONFIG = {}
__SPECK_CONFIG["SPECK_FOLDER"] = os.getenv("SPECK")
dn = __SPECK_CONFIG["SPECK_FOLDER"] + os.sep+"modules"
sys.path.append(dn)
subdn=os.listdir(dn)
for i in subdn: sys.path.append(dn+os.sep+i)

##
## Data folders
##
import os


exec(open(__SPECK_CONFIG["SPECK_FOLDER"]+os.sep+"config"+os.sep+"speck_folders.py","r").read())
__Default_Data_Folder=SPECK_TEMPORARY_HOME
__Default_Backup_Folder=SPECK_DATA_FOLDER
__SPECK_CONFIG["DATA_FOLDER"] = SPECK_DATA_FOLDER
__SPECK_CONFIG["BACKUP_FOLDER"] = SPECK_BACKUP_FOLDER
__SPECK_CONFIG["TEMPORARY_HOME"] = SPECK_TEMPORARY_HOME
__SPECK_CONFIG["TEMPORARY_FOLDER"] = SPECK_TEMPORARY_FOLDER

#Import generic speck modules
from Universal_Prefilter import *
import pymucal
from GracePlotter import *
try:
    import Gnuplot
except Exception as tmp:
    print("Cannot import Gnuplot")
from mycurses import *

#Import Periodic Table
print('\x1b[01;06m')
print("Loading Periodic Table: usage type Fe or other chemical symbol for information")
print('\x1b[32;01m', end=' ')
print("help(pymucal) or help(atomic_data) for more details")
print('\x1b[0m')
for i in list(pymucal.atomic_data.atoms.keys()):
        exec("%s=pymucal.atomic_data(i)"%(i))

#Import Control Related (PyTango related) modules
import PyTango
from PyTango import DeviceProxy, DevState

########
# BEEP #
########
try:
    import tkinter
    def wakemeup():
        """Uses Tkinter to alert user that the run is finished... just in case he was sleeping..."""
        try:
            a=tkinter.Tk()
            for j in range(5):
                for i in range(3):
                    a.bell()
                    sleep(0.025)
                sleep(0.35)
            a.destroy()
        except:
            print("WARNING: Error alerting for end of scan... no Tkinter?\n")
            print("BUT: Ignore this message if escan is working well,\n just report this to your local contact\n")
        return
except Exception as tmp:
    print("Cannot initialize wakemeup function, reason follows:")
    print(tmp)


########
#MAGICS#
########

#Not yet!

#
#General configuration parameters
#

__pySamba_root=os.getenv("SPECK")
__pySamba_scans=__pySamba_root+"/modules/scans/"


    
#Import more specific speck modules

imp_mdls = ["galil_multiaxis", "xbpm_class", "PSS"]

from_mdls = {"ascan":"*","GetPositions":"*","e2theta":"*", "motor_class":"*", "mono1d":"*", "counter_class":"*", "valve_class":"valve", "pressure_gauge_class":"pressure_gauge", "thermocouple_class":"temperature_gauge", "mirror_class":"mirror", "absorbing_system_class":"*", "FrontEnd_class":"FrontEnd", "ic_gas":"xbpm_abs,  ic_abs", "NHQ_HVsupply_class":"NHQ_HVsupply", "rontec_MCA":"rontec_MCA", "mm4005":"mm4005_motor", "channel_cut":"channel_cut", "simple_DxMAP":"dxmap", "moveable":"moveable, sensor","beamline_alignement":"*","escan_class":"escan, escan_class", "spec_syntax":"*","setuser":"*"}


for i in imp_mdls:
    try:
        exec("import "+i)
    except Exception as tmp:
        print("Error while importing ",i)
        print("Exception description follows: \n",tmp)

for i in from_mdls:
    try:
        exec("from %s import %s"%(i,from_mdls[i]))
    except Exception as tmp:
        print("Error while importing ",from_mdls[i]," from ",i)
        print("Exception description follows: \n",tmp)

                        
print("OK")


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
    print("Loading instrument macro from "+instrument_file)
    return domacro(instrument_file)

##### External Commands: #####


def atkpanel(object):
    try:
        atkpanel_command=os.popen("which atkpanel").readlines()[0].strip()
        try:
            __oname__=object.DP.dev_name()
        except:
            try:
                __oname__=object.dev_name()
            except:
                print("Cannot ...")
         
        print("atkpanel ",__oname__)
        #os.spawnvp(os.P_NOWAIT,"/usr/Local/DistribTango/soleil-root/tango/bin/atkpanel",[" ",__oname__])
        os.system(atkpanel_command+" "+__oname__+" >& /dev/null &")
        return
    except os.EX_OSERR as tmp:
        print(tmp.args)
        return 
    except: 
        print("Error!")
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

setuser()
