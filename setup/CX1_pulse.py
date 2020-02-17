print "CX1_pulse: preparing."

from p_spec_syntax import *

from p_dxmap import dxmap

try:
    config = {"fileGeneration":False,"streamTargetPath":'D:\\FTP',\
    "mode":"MAP2", "streamNbAcqPerFile":250,"nbPixelsPerBuffer":50,"streamtargetfile":"xia1"}
    
    cx1xia1=dxmap("d09-1-cx1/dt/dtc-mca_xmap.1",FTPclient="d09-1-c00/ca/ftpclientxia.1",identifier = "cx1xia1",\
    FTPserver="d09-1-c00/ca/ftpserverxia.1",spoolMountPoint="/nfs/tempdata/samba/com-samba/xia1", config=config)
    
    print GREEN+"cx1xia2 --> DxMap card"+RESET
    
    config = {"fileGeneration":False,"streamTargetPath":'D:\\FTP',\
    "mode":"MAP2", "streamNbAcqPerFile":250,"nbPixelsPerBuffer":50,"streamtargetfile":"xia2"}
    
    cx1xia2=dxmap("d09-1-cx1/dt/dtc-mca_xmap.2",FTPclient="d09-1-c00/ca/ftpclientxia.2",identifier = "cx1xia2",\
    FTPserver="d09-1-c00/ca/ftpserverxia.2",spoolMountPoint="/nfs/tempdata/samba/com-samba/xia2", config=config)
    
    print GREEN+"cx1xia1 --> DxMap card"+RESET
    
    mca1=cx1xia1
    mca2=cx1xia2
except Exception, tmp:
    print tmp

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
"nexusTargetPath":'/nfs/tempdata/samba/com-samba/cx1sai1',"nexusNbAcqPerFile":1000,"dataBufferNumber":1,\
"statHistoryBufferDepth":1000}

try:

    sai = p_sai("d09-1-c00/ca/sai.1", timeout=10., deadtime=0.1, spoolMountPoint="/nfs/tempdata/samba/com-samba/cx1sai1",\
    config=config, identifier="cx1sai1",GateDownTime=2.)

except Exception, tmp:
    print tmp

#bufferedCounter (Theta)

from p_bufferedCounter import bufferedCounter as p_bufferedCounter

config = {"frequency":100,"integrationTime":0.01,"nexusFileGeneration":False,\
"nexusTargetPath":'/nfs/tempdata/samba/com-samba/cpt3',"nexusNbAcqPerFile":1000,"totalNbPoint":1000,\
"bufferDepth":1}

cpt3 = p_bufferedCounter("d09-1-c00/ca/cpt.3",deadtime=0.1,timeout=10,config = config,
spoolMountPoint="/nfs/tempdata/samba/com-samba/cpt3",identifier="encoder_rx1",GateDownTime=2.)

#Associate counters to moveables for continuous scans

x.DP.associated_counter = "encoder_rx1.X"
dcm.DP.associated_counter = "encoder_rx1.Theta"


#PulseGenerator

from p_pulsegen import pulseGen
config = {"generationType":"FINITE","pulseNumber":1,"counter0Enable":True,\
"initialDelay0":0,"delayCounter0":2,"pulseWidthCounter0":998}
#delayCounter0 is the GateDownTime of the other cards

pulseGen0 = pulseGen("d09-1-cx1/dt/pulsgen.1",config=config,deadtime=0.1,timeout=10.)

#The following post format is very heavy with large array detectors.
#A simplification could be provided if detectors provided already computed averages or corrected counts, but it is tricky 
#for detctors cut in several devices as our Germanium one

try:
    ctPosts=[\
    {"name":"MUX","formula":"log(float(ch[0])/ch[1])","units":"","format":"%9.7f"},\
#    {"name":"MUS","formula":"log(float(ch[1])/ch[2])","units":"","format":"%9.7f"},\
#    {"name":"I1Norm","formula":"float(ch[1])/ch[0]","units":"","format":"%9.7e"},\
    {"name":"MUF","formula":"float(sum(ch[7:24])+sum(ch[87:103]))/ch[0]","units":"","format":"%9.7e"},
    ]  
    XAS_dictionary = {
        "addresses":{
            "I0":"cx1sai1.I0",
            "I1":"cx1sai1.I1",
            "I2":"cx1sai1.I2",
            "I3":"cx1sai1.I3",
            "ROI0":"cx1xia1.roi15",
            "ICR0":"cx1xia1.icr15",
            "OCR0":"cx1xia1.ocr15",
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
    #ct=pseudo_counter(masters=[pulseGen0,],slaves=[sai,cx1xia1,cx1xia2,cpt3],posts=ctPosts, postDictionary=XAS_dictionary)
    #ct=pseudo_counter(masters=[pulseGen0,], slaves=[sai,cpt3], posts=ctPosts, postDictionary=XAS_dictionary)
    ct=pseudo_counter(masters=[pulseGen0,], slaves=[sai,cpt3], posts=ctPosts)

except Exception, tmp:
    print tmp
    print "Failure defining ct command"

mostab.scaler = "ct"


# Scan macros

execfile(__pySamba_root+"/modules/pulse/p_ascan.py")
execfile(__pySamba_root+"/modules/pulse/p_cscan.py")
execfile(__pySamba_root+"/modules/pulse/p_ecscan.py")

#legacy definitions

def setSTEP():
    return
def setMAP():
    return

__shclose = shclose
__shopen = shopen


