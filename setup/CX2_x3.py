print "CX2: preparing."
#import sys,os
#sys.path.append(os.getenv("SPECK")+os.sep+"modules"+os.sep+"pulse")

#This instrument set up the beamline for 
#PulseGen master on CX2

#The master is the first counter card, but started as a pulsegenerator device (Astor...)

#GateDownTime is 2 (ms for all, it can be reduced  down to 2microseconds= 0.002ms)


#Generic identifiers
#sai cards: sai1, sai2, ...
#xia cards: xia1, xia2, ...
#xspress3:  xspress1, xspress2, ...

#dxmap: configured forVortexME4 (MAP10)

from p_escan import *
from p_spec_syntax import *

from p_dxmap import dxmap

try:
    #Recognized detector names:
    #CdTe, Canberra_Ge36, Canberra_Ge7, Vortex_SDD4, Vortex_SDD1, Canberra_SDD13
    #detector_details={"detector_name":"CdTe","real_pixels_list":"1","comment":"AMPTEK CdTe installed in CX2"}
    detector_details={"detector_name":"SDD1","real_pixels_list":"1","comment":"Vortex 100mm2 SDD installed in CX2"}

    config = {"fileGeneration":False,"streamTargetPath":'D:\\FTP',\
    "mode":"VORTEX", "streamNbAcqPerFile":630,"nbPixelsPerBuffer":63,"streamtargetfile":"cx2xia1"}
    cx2xia1=dxmap("d09-1-cx2/dt/dtc-mca_xmap.1",FTPclient="d09-1-c00/ca/ftpclientcx2xia1",identifier = "fluo01",\
    FTPserver="d09-1-c00/ca/ftpservercx2xia1",spoolMountPoint="/nfs/.autofs/srv5/spool1/cx2xia1", config=config, detector_details=detector_details)
    mca1=cx2xia1
    mca2=None
    print GREEN+"cx2xia1 --> DxMap card"+RESET
except Exception, tmp:
    print tmp
    print RED+"Failure defining dxmap: d09-1-cx2/dt/dtc-mca_xmap.1"+RESET

#EXSPRESS3
#trigger modes can be internal_trigger or external_gate

#from xspress3 import xspress3mini

#try:
#    config={"acq_trigger_mode":"external_gate",\
#    "saving_suffix":"hdf","saving_prefix":"xsp3_","saving_format":"hdf5",\
#    "saving_directory":"/mnt/spoolSAMBA/xsp3","saving_mode":"auto_frame",\
#    "saving_overwrite_policy":"abort"}
    
#    x3mca = xspress3mini(label = "xspress3/xspress3/xspress3.1", timeout=30,deadtime=0.1,
#    spoolMountPoint="/nfs/srv5/spool1/xsp3",specificDevice="xspress3/xspress3/xspress3.1-specific",\
#    config=config,identifier="xspress_1")
#except Exception, tmp:
#    print tmp
#EXSPRESS3
#trigger modes can be internal_trigger or external_gate  

from p_xspress3_QD import xspress3

try:
    #config={"acq_trigger_mode":"internal_trigger",\
    config={"acq_trigger_mode":"external_gate",\
    "saving_suffix":"hdf","saving_prefix":"x3x_","saving_format":"hdf5",\
    "saving_directory":"/mnt/spool/x3x","saving_mode":"auto_frame",\
    "saving_overwrite_policy":"abort"}

    detector_details={"detector_name":"Canberra_SDD13","real_pixels_list":"1,2,3,4,5,6,7,8,9,10,11,12,13","comment":"Canberra 13 elements SDD + xspress3x"}
    
#   x3mca = xspress3(label = "d09-1-cx1/dt/xspress3x.1", timeout=30,deadtime=0.1,
#   spoolMountPoint="/nfs/srv5/spool1/x3x",specificDevice="d09-1-cx1/dt/xspress3x.1-specific",\
#   config=config,identifier="fluo03")

    x3mca = xspress3(label = "lima/limaccd/1", timeout=30,deadtime=0.1,
    spoolMountPoint="/nfs/srv5/spool1/x3x",specificDevice="lima/xspress3/1",\
    config=config,identifier="fluo03")
except Exception, tmp:
    print tmp


#SAI

from p_sai import sai as p_sai

config = {"configurationId":3,"frequency":10000,"integrationTime":1,"nexusFileGeneration":False,\
"nexusTargetPath":'/nfs/tempdata/samba/com-samba/cx2sai1',"nexusNbAcqPerFile":1000,"dataBufferNumber":1,\
"statHistoryBufferDepth":1000}

try:

    sai01 = p_sai("d09-1-cx2/ca/sai.1", timeout=10., deadtime=0.1, spoolMountPoint="/nfs/tempdata/samba/com-samba/cx2sai1",\
    config=config, identifier="sai01",GateDownTime=2.)

except Exception, tmp:
    print tmp

#bufferedCounter (Theta)

from p_bufferedCounter import bufferedCounter as p_bufferedCounter

config = {"frequency":100,"integrationTime":0.01,"nexusFileGeneration":False,\
"nexusTargetPath":'/nfs/tempdata/samba/com-samba/cpt3',"nexusNbAcqPerFile":1000,"totalNbPoint":1000,\
"bufferDepth":1}

cpt3 = p_bufferedCounter("d09-1-c00/ca/cpt.3",deadtime=0.1,timeout=10,config = config,
spoolMountPoint="/nfs/tempdata/samba/com-samba/cpt3",identifier="encoder01",GateDownTime=1.)


#PulseGenerator

from p_pulsegen import pulseGen
config = {"generationType":"FINITE","pulseNumber":1,"counter0Enable":True,\
"initialDelay0":0,"delayCounter0":1.,"pulseWidthCounter0":999.}
#delayCounter0 is the GateDownTime of the other cards
#Verify the point above with oscilloscope please.

pulseGen0 = pulseGen("d09-1-cx2/dt/pulsgen.2",config=config,deadtime=0.1,timeout=10.)

try:
    ctPosts=[\
    {"name":"MUX","formula":"log(float(ch[0])/ch[1])","units":"","format":"%9.7f"},\
    {"name":"MUS","formula":"log(float(ch[1])/ch[2])","units":"","format":"%9.7f"},\
    {"name":"I1Norm","formula":"float(ch[1])/ch[0]","units":"","format":"%9.7e"},\
    {"name":"MUF","formula":"float(ch[4])/ch[0]","units":"","format":"%9.7e"},
    ]  
    XAS_dictionary = {
        "addresses":{
            "Theta":"encoder01.Theta",
            "I0":"sai01.I0",
            "I1":"sai01.I1",
            "I2":"sai01.I2",
            "I3":"sai01.I3",
            "ROI0":"fluo03.roi00",
            "ICR0":"fluo03.icr00",
            "OCR0":"fluo03.ocr00",
            },
        "constants":{},
        "formulas":{
            "Theta":"Theta[:]",
            "energy":"dcm.theta2e(Theta[:])",
            "I0":"I0[:]",
            "I1":"I1[:]",
            "I2":"I2[:]",
            "I3":"I3[:]",
            "MUX":"numpy.log(I0[:]/I1[:])",
            "FLUO":"ROI0[:]*ICR0[:]*OCR0[:]",
            "FLUO_RAW":"ROI0[:]",
            #"FLUO":"ROI0[:]*ICR0[:]/(I0[:]*OCR0[:])",
            #"FLUO_RAW":"ROI0[:]/I0[:]",
            "REF":"numpy.log(I1[:]/I2[:])",
            "FLUO_DIODE":"I3[:]/I0[:]",
            },
    }


#These Posts should be modified each time when changing detectors.
    from p_spec_syntax import pseudo_counter

    cpt=pseudo_counter(masters=[pulseGen0,])
    ct=pseudo_counter(masters=[pulseGen0],slaves=[sai01,x3mca,cpt3], posts= ctPosts, postDictionary=XAS_dictionary)
    #Remember to set the cpt3 card from master to slave mode and modify BNC cable position from OUT to GATE

except Exception, tmp:
    print tmp
    print "Failure defining ct command"

mostab.scaler = "ct"

thetaCrystal  = moveable("d09-1-cx2/dt/cristal-mt_rs.1","position")
xCrystal      = moveable("d09-1-cx2/dt/cristal-mt_tx.1","position")
thetaDetector = moveable("d09-1-cx2/dt/det-mt_rs.1","position")
xDetector     = moveable("d09-1-cx2/dt/det-mt_tx.1","position")
zDetector     = moveable("d09-1-cx2/dt/det-mt_tz.1","position")
z2  = moveable("d09-1-cx2/ex/sex-mt_tz.1","position")
z   = moveable("d09-1-cx2/ex/sex-mt_tz.2","position")
x   = moveable("d09-1-cx2/ex/sex-mt_tx.1","position")
phi = moveable("d09-1-cx2/ex/sex-mt_rz.1","position")
cam5 = moveable("d09-1-cx2/dt/vg2-basler","ExposureTime")
hx = moveable("d09-1-cx1/ex/hexa.1","x")
hy = moveable("d09-1-cx1/ex/hexa.1","y")
hz = moveable("d09-1-cx1/ex/hexa.1","z")
hu = moveable("d09-1-cx1/ex/hexa.1","u")
hv = moveable("d09-1-cx1/ex/hexa.1","v")
hw = moveable("d09-1-cx1/ex/hexa.1","w")

I0_gain = moveable("d09-1-cx2/ex/amp_i0","gain")
I1_gain = moveable("d09-1-cx2/ex/amp_i1","gain")
I2_gain = moveable("d09-1-cx2/ex/amp_i2","gain")
I3_gain = None
#I3_gain = moveable("d09-1-cx2/ex/amp_i3","gain")

# Scan macros

execfile(__pySamba_root+"/modules/pulse/p_ascan.py")
execfile(__pySamba_root+"/modules/pulse/p_ecscan.py")

#from p_ecscan import ecscan
#legacy definitions

def setSTEP():
    return
def setMAP():
    return

__shclose = shclose
__shopen = shopen

def shclose(level=2):
    return __shclose(level)
def shopen(level=2):
    return __shopen(level)


#       Johann Analyzer
import Johann
#__Johann_Geometry = {"atom":"Si","hkl":[3,1,1],"order":3,"R":0.985,"A":0.05,"alpha":0.,"detectorsize":0.3,"beamsize":3e-4,"angleMax":85,"angleMin":55.}
#__Johann_Geometry = {"atom":"Si","hkl":[2,2,0],"order":4,"R":1.000,"A":0.05,"alpha":0.,"detectorsize":0.3,"beamsize":3e-4,"angleMax":85,"angleMin":55.}
__Johann_Geometry = {"atom":"Si","hkl":[1,1,1],"order":5,"R":1.000,"A":0.05,"alpha":0.,"detectorsize":0.3,"beamsize":3e-4,"angleMax":85,"angleMin":55.}
__Johann_Motors ={"crystal_theta":thetaCrystal,"crystal_x":xCrystal,"detector_theta":thetaDetector,"detector_x":xDetector,"detector_z":zDetector}
jo = Johann.JohannSpectro(__Johann_Motors, __Johann_Geometry)
jo.offset_crystal_theta=0.17

#Previous offsets
#Si 311 jo.offset_crystal_theta=0.441
#Si 220 jo.offset_crystal_theta=0.22844905850348596
del __Johann_Geometry, __Johann_Motors

print "Sample distance from monochromator should be at 19.881"
