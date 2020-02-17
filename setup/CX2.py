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

from p_spec_syntax import *

from p_dxmap import dxmap

try:
    config = {"fileGeneration":False,"streamTargetPath":'D:\\FTP',\
    "mode":"MAP", "streamNbAcqPerFile":250,"nbPixelsPerBuffer":50,"streamtargetfile":"cx2xia1"}
    cx2xia1=dxmap("d09-1-cx2/dt/dtc-mca_xmap.1",FTPclient="d09-1-c00/ca/ftpclientcx2xia1",identifier = "cx2xia1",\
    FTPserver="d09-1-c00/ca/ftpservercx2xia1",spoolMountPoint="/nfs/tempdata/samba/com-samba/cx2xia1", config=config)
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

#SAI

from p_sai import sai as p_sai

config = {"configurationId":3,"frequency":10000,"integrationTime":1,"nexusFileGeneration":False,\
"nexusTargetPath":'/nfs/tempdata/samba/com-samba/cx2sai1',"nexusNbAcqPerFile":1000,"dataBufferNumber":1,\
"statHistoryBufferDepth":1000}

try:

    sai = p_sai("d09-1-cx2/ca/sai.1", timeout=10., deadtime=0.1, spoolMountPoint="/nfs/tempdata/samba/com-samba/cx2sai1",\
    config=config, identifier="cx2sai1",GateDownTime=2.)

except Exception, tmp:
    print tmp

#bufferedCounter (Theta)

from p_bufferedCounter import bufferedCounter as p_bufferedCounter

config = {"frequency":100,"integrationTime":0.01,"nexusFileGeneration":False,\
"nexusTargetPath":'/nfs/tempdata/samba/com-samba/cpt3',"nexusNbAcqPerFile":1000,"totalNbPoint":1000,\
"bufferDepth":1}

cpt3 = p_bufferedCounter("d09-1-c00/ca/cpt.3",deadtime=0.1,timeout=10,config = config,
spoolMountPoint="/nfs/tempdata/samba/com-samba/cpt3",identifier="encoder_rx1",GateDownTime=2.)


#PulseGenerator

from p_pulsegen import pulseGen
config = {"generationType":"FINITE","pulseNumber":1,"counter0Enable":True,\
"initialDelay0":0,"delayCounter0":2,"pulseWidthCounter0":998}
#delayCounter0 is the GateDownTime of the other cards

pulseGen0 = pulseGen("d09-1-cx2/dt/pulsgen.2",config=config,deadtime=0.1,timeout=10.)

try:
    ctPosts=[\
    {"name":"MUX","formula":"log(float(ch[0])/ch[1])","units":"","format":"%9.7f"},\
#    {"name":"MUS","formula":"log(float(ch[1])/ch[2])","units":"","format":"%9.7f"},\
#    {"name":"I1Norm","formula":"float(ch[1])/ch[0]","units":"","format":"%9.7e"},\
    {"name":"MUF","formula":"float(ch[16])/ch[0]","units":"","format":"%9.7e"},
    ]  
    XAS_dictionary = {
        "addresses":{
            "I0":"cx2sai1.I0",
            "I1":"cx2sai1.I1",
            "I2":"cx2sai1.I2",
            "I3":"cx2sai1.I3",
            "ROI0":"cx2xia1.roi00",
            "ICR0":"cx2xia1.icr00",
            "OCR0":"cx2xia1.ocr00",
            },
        "constants":{},
        "formulas":{
            "XMU":"numpy.log(I0[:]/I1[:])",
            "FLUO":"ROI0[:]*ICR0[:]/(I0[:]*OCR0[:])",
            "FLUO_RAW":"ROI0[:]/I0[:]",
            "REF":"numpy.log(I1[:]/I2[:])",
            "FLUO_DIODE":"I3[:]/I0[:]",
            },
    }


#These Posts should be modified each time when changing detectors.
    from p_spec_syntax import pseudo_counter

    cpt=pseudo_counter(masters=[pulseGen0,])
    #ct=pseudo_counter(masters=[pulseGen0,],slaves=[mca1,], posts= ctPosts)
    #ct=pseudo_counter(masters=[pulseGen0],slaves=[sai_1,x3mca], posts= ctPosts)
    #Remember to set the cpt3 card from master to slave mode and modify BNC cable position from OUT to GATE
    #ct=pseudo_counter(masters=[pulseGen0,],slaves=[sai_1,mca1,cpt3], posts= ctPosts)
    ct=pseudo_counter(masters=[pulseGen0,],slaves=[sai,cx2xia1,cpt3],posts=ctPosts, postDictionary=XAS_dictionary)
    #ct=pseudo_counter(masters=[pulseGen0,], slaves=[sai,cpt3], posts=ctPosts, postDictionary=XAS_dictionary)

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
__Johann_Geometry = {"atom":"Si","hkl":[3,1,1],"order":3,"R":0.985,"A":0.05,"alpha":0.,"detectorsize":0.3,"beamsize":3e-4,"angleMax":85,"angleMin":55.}
__Johann_Motors ={"crystal_theta":thetaCrystal,"crystal_x":xCrystal,"detector_theta":thetaDetector,"detector_x":xDetector,"detector_z":zDetector}
jo = Johann.JohannSpectro(__Johann_Motors, __Johann_Geometry)
del __Johann_Geometry, __Johann_Motors
jo.offset_crystal_theta=0.441

print "Sample distance from monochromator should be at 19.881"
print "Remember to set correctly the master property of CPT3 to false when switching to CX2 and to true when back to CX1"
