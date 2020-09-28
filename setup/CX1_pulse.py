print "CX1_pulse: preparing."

from p_spec_syntax import *
from p_dxmap import dxmap

try:
    #Recognized detector names:
    #CdTe, Canberra_Ge36, Canberra_Ge7, Vortex_SDD4, Vortex_SDD1, Canberra_SDD13
    detector_details={"detector_name":"Canberra_Ge36","real_pixels_list":"nan,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19","comment":"Canberra 36 pixels HPGe installed in CX1"}

    config = {"fileGeneration":False,"streamTargetPath":'D:\\FTP',\
    "mode":"MAP2", "streamNbAcqPerFile":630,"nbPixelsPerBuffer":63,"streamtargetfile":"xia1"}
    
    cx1xia1=dxmap("d09-1-cx1/dt/dtc-mca_xmap.1",FTPclient="d09-1-c00/ca/ftpclientxia.1",identifier = "fluo01",\
    FTPserver="d09-1-c00/ca/ftpserverxia.1",spoolMountPoint="/nfs/srv5/spool1/xia1", config=config,detector_details = detector_details)
    
    print GREEN+"cx1xia1 --> DxMap card"+RESET
    
    detector_details={"detector_name":"Canberra_Ge36","real_pixels_list":"20,21,22,23,24,25,26,27,28,29,30,31,32,33,35,36","comment":"Canberra 36 pixels HPGe installed in CX1"}
    
    config = {"fileGeneration":False,"streamTargetPath":'D:\\FTP',\
    "mode":"MAP2", "streamNbAcqPerFile":630,"nbPixelsPerBuffer":63,"streamtargetfile":"xia2"}
    
    cx1xia2=dxmap("d09-1-cx1/dt/dtc-mca_xmap.2",FTPclient="d09-1-c00/ca/ftpclientxia.2",identifier = "fluo02",\
    FTPserver="d09-1-c00/ca/ftpserverxia.2",spoolMountPoint="/nfs/srv5/spool1/xia2", config=config,detector_details = detector_details)
    
    print GREEN+"cx1xia2 --> DxMap card"+RESET
    
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

    sai = p_sai("d09-1-c00/ca/sai.1", timeout=10., deadtime=0.1, spoolMountPoint="/nfs/srv5/spool1/cx1sai1",\
    config=config, identifier="cx1sai1",GateDownTime=1.)

except Exception, tmp:
    print tmp

#bufferedCounter (Theta)

from p_bufferedCounter import bufferedCounter as p_bufferedCounter

config = {"frequency":100,"integrationTime":0.01,"nexusFileGeneration":False,\
"nexusTargetPath":'/nfs/tempdata/samba/com-samba/cpt3',"nexusNbAcqPerFile":1000,"totalNbPoint":1000,\
"bufferDepth":1}

cpt3 = p_bufferedCounter("d09-1-c00/ca/cpt.3",deadtime=0.1,timeout=10,config = config,
spoolMountPoint="/nfs/tempdata/samba/com-samba/cpt3",identifier="encoder01",GateDownTime=1.)

#Associate counters to moveables for continuous scans

x.DP.associated_counter = "encoder01.X"
dcm.DP.associated_counter = "encoder01.Theta"

#PulseGenerator

from p_pulsegen import pulseGen
config = {"generationType":"FINITE","pulseNumber":1,"counter0Enable":True,\
"initialDelay0":0.0,"delayCounter0":1.,"pulseWidthCounter0":999.}
#delayCounter0 is the GateDownTime of the other cards

pulseGen0 = pulseGen("d09-1-cx1/dt/pulsgen.1",config=config,deadtime=0.1,timeout=10.)

#The following post format is very heavy with large array detectors.
#A simplification could be provided if detectors provided already computed averages or corrected counts, but it is tricky 
#for detectors cut in several devices as our Germanium one. Even normalisation schemes may differ depending on experiment layout.

#Attention has to be paid here, since any detector change has an impact on these posts that rely on order of channels and naming conventions
#It is evident that it cannot be different, since these are user defined functions.

#### after addresses, constants and formulas, links could be a good idea to give  astandard name in posts to some quantities

try:
    ctPosts=[\
    {"name":"MUX","formula":"log(float(ch[0])/ch[1])","units":"","format":"%9.7f"},\
    {"name":"MUS","formula":"log(float(ch[1])/ch[2])","units":"","format":"%9.7f"},\
    {"name":"I1Norm","formula":"float(ch[1])/ch[0]","units":"","format":"%9.7e"},\
    {"name":"FLUO_RAW","formula":"float(sum(ch[66:84])+sum(ch[132:148]))/ch[0]","units":"","format":"%9.7e"},
    ]  
    #>>>>>>>>>>>>>>>> Remember only formulas are saved to file <<<<<<<<<<<<<<<<<<<<<<<<
    XAS_dictionary = {
        "addresses":{
            "I0":"cx1sai1.I0",
            "I1":"cx1sai1.I1",
            "I2":"cx1sai1.I2",
            "I3":"cx1sai1.I3",
            "Theta":"encoder01.Theta",
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
            "REF":"numpy.log(I1[:]/I2[:])",
            "FLUO_DIODE":"I3[:]/I0[:]",
            },
    }
    __cx1xia1_channels=range(0,20)
    __cx1xia2_channels=range(0,16)
    __FLUO="("
    __FLUO_RAW="("
    for i in __cx1xia1_channels:
        XAS_dictionary["addresses"]["ROI%02i"%i] = "fluo01.roi%02i"%i
        XAS_dictionary["addresses"]["ICR%02i"%i] = "fluo01.icr%02i"%i
        XAS_dictionary["addresses"]["OCR%02i"%i] = "fluo01.ocr%02i"%i
        __FLUO+="+numpy.nan_to_num(ROI%02i[:]/OCR%02i[:]*ICR%02i[:])"%(i,i,i)
        __FLUO_RAW+="+ROI%02i[:]"%(i)
    for i in __cx1xia2_channels:
        XAS_dictionary["addresses"]["ROI%02i"%(i+20)] = "fluo02.roi%02i"%i
        XAS_dictionary["addresses"]["ICR%02i"%(i+20)] = "fluo02.icr%02i"%i
        XAS_dictionary["addresses"]["OCR%02i"%(i+20)] = "fluo02.ocr%02i"%i
        __FLUO+="+numpy.nan_to_num(ROI%02i[:]/OCR%02i[:]*ICR%02i[:])"%(i+20,i+20,i+20)
        __FLUO_RAW+="+ROI%02i[:]"%(i+20)
    __FLUO+=")/numpy.array(I0[:],'f')"
    __FLUO_RAW+=")/numpy.array(I0[:],'f')"
    XAS_dictionary["formulas"]["FLUO"] = __FLUO
    XAS_dictionary["formulas"]["FLUO_RAW"] = __FLUO_RAW

#These Posts should be modified each time when changing detectors.
    from p_spec_syntax import pseudo_counter

    cpt=pseudo_counter(masters=[pulseGen0,])
    #ct=pseudo_counter(masters=[pulseGen0,],slaves=[mca1,], posts= ctPosts)
    #ct=pseudo_counter(masters=[pulseGen0],slaves=[sai_1,x3mca], posts= ctPosts)
    #Remember to set the cpt3 card from master to slave mode and modify BNC cable position from OUT to GATE
    #ct=pseudo_counter(masters=[pulseGen0,],slaves=[sai_1,mca1,cpt3], posts= ctPosts)
    #ct=pseudo_counter(masters=[pulseGen0,], slaves=[sai,cpt3], posts=ctPosts, postDictionary=XAS_dictionary)
    #ct=pseudo_counter(masters=[pulseGen0,], slaves=[sai,cpt3], posts=ctPosts)

    #ct=pseudo_counter(masters=[pulseGen0,],slaves=[sai,cx1xia1,cx1xia2,cpt3])
    ct=pseudo_counter(masters=[pulseGen0,],slaves=[sai,cx1xia1,cx1xia2,cpt3],posts=ctPosts, postDictionary=XAS_dictionary)
 
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
