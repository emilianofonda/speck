from __future__ import print_function
from past.builtins import execfile
from builtins import range
print("CX1_pulse: preparing.")

from p_escan import *
from p_spec_syntax import *
from p_dxmap import dxmap
from matplotlib import pyplot as plt

try:
    #Fastosh recognized detector names:
    #CdTe, Canberra_Ge36, Canberra_Ge7, Vortex_SDD4, Vortex_SDD1, Canberra_SDD13
    detector_details={"detector_name":"Canberra_Ge36","real_pixels_list":"nan,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19","comment":"Canberra 36 pixels HPGe installed in CX1"}

    config = {"fileGeneration":False,"streamTargetPath":'D:\\FTP',\
    "mode":"MAP2", "streamNbAcqPerFile":630,"nbPixelsPerBuffer":63,"streamtargetfile":"xia1"}
    
    cx1xia1=dxmap("d09-1-cx1/dt/dtc-mca_xmap.1",FTPclient="d09-1-c00/ca/ftpclientxia.1",identifier = "fluo01",timeout=90.,\
    FTPserver="d09-1-c00/ca/ftpserverxia.1",spoolMountPoint="/nfs/srv5/spool1/xia1", config=config,detector_details = detector_details)
    
    print(GREEN+"cx1xia1 --> DxMap card"+RESET)
    
    detector_details={"detector_name":"Canberra_Ge36","real_pixels_list":"20,21,22,23,24,25,26,27,28,29,30,31,32,33,35,36","comment":"Canberra 36 pixels HPGe installed in CX1"}
    
    config = {"fileGeneration":False,"streamTargetPath":'D:\\FTP',\
    "mode":"MAP2", "streamNbAcqPerFile":630,"nbPixelsPerBuffer":63,"streamtargetfile":"xia2"}
    
    cx1xia2=dxmap("d09-1-cx1/dt/dtc-mca_xmap.2",FTPclient="d09-1-c00/ca/ftpclientxia.2",identifier = "fluo02",timeout=90.,\
    FTPserver="d09-1-c00/ca/ftpserverxia.2",spoolMountPoint="/nfs/srv5/spool1/xia2", config=config,detector_details = detector_details)
    
    print(GREEN+"cx1xia2 --> DxMap card"+RESET)
    
    mca1=cx1xia1
    mca2=cx1xia2

except Exception as tmp:
    print(tmp)

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
    config=config,identifier="fluo03",detector_details = detector_details)
except Exception as tmp:
    print(tmp)

#SAI

from p_sai import sai as p_sai

config = {"configurationId":3,"frequency":10000,"integrationTime":1,"nexusFileGeneration":False,\
"nexusTargetPath":'/nfs/srv5/spool1/cx1sai1',"nexusNbAcqPerFile":1000,"dataBufferNumber":1,\
"statHistoryBufferDepth":1000}

try:

    cx1sai = p_sai("d09-1-c00/ca/sai.1", timeout=10., deadtime=0.1, spoolMountPoint="/nfs/srv5/spool1/cx1sai1",\
    FTPclient="",FTPserver="",
    config=config, identifier="cx1sai1",GateDownTime=1.)

except Exception as tmp:
    print(tmp)

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
"initialDelay0":0.0,"delayCounter0":5.,"pulseWidthCounter0":995.}
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
    __cx1xia1_channels=list(range(0,20))
    __cx1xia2_channels=list(range(0,16))
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
    del __FLUO
    del __FLUO_RAW
#These Posts should be modified each time when changing detectors.
    from p_spec_syntax import pseudo_counter

    cpt=pseudo_counter(masters=[pulseGen0,])
    #ct=pseudo_counter(masters=[pulseGen0,],slaves=[mca1,], posts= ctPosts)
    #ct=pseudo_counter(masters=[pulseGen0],slaves=[cx1sai_1,x3mca], posts= ctPosts)
    #Remember to set the cpt3 card from master to slave mode and modify BNC cable position from OUT to GATE
    #ct=pseudo_counter(masters=[pulseGen0,],slaves=[cx1sai_1,mca1,cpt3], posts= ctPosts)
    #ct=pseudo_counter(masters=[pulseGen0,], slaves=[cx1sai,cpt3], posts=ctPosts, postDictionary=XAS_dictionary)
    #ct=pseudo_counter(masters=[pulseGen0,], slaves=[cx1sai,cpt3], posts=ctPosts)

    #ct=pseudo_counter(masters=[pulseGen0,],slaves=[cx1sai,cx1xia1,cx1xia2,cpt3])
    ct0=pseudo_counter(masters=[pulseGen0,],slaves=[cx1sai,cx1xia1,cx1xia2,cpt3],posts=ctPosts, postDictionary=XAS_dictionary)

except Exception as tmp:
    print(tmp)
    print("Failure defining ct0 config")


###########################################
# Post definitions for xspress3x ct_x3mca #
###########################################

try:
    ctPosts_x3mca = [\
    {"name":"MUX","formula":"log(float(ch[0])/ch[1])","units":"","format":"%9.7f"},\
    {"name":"MUS","formula":"log(float(ch[1])/ch[2])","units":"","format":"%9.7f"},\
    {"name":"I1Norm","formula":"float(ch[1])/ch[0]","units":"","format":"%9.7e"},\
    {"name":"FLUO_RAW","formula":"float(sum(ch[4:17]))/ch[0]","units":"","format":"%9.7e"},
    ]  
    #>>>>>>>>>>>>>>>> Remember only formulas are saved to file <<<<<<<<<<<<<<<<<<<<<<<<
    XAS_dictionary_x3mca = {
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
    __x3mca_id = x3mca.identifier
    __x3mca_channels=list(range(0,13))
    __FLUO="("
    __FLUO_RAW="("
    for i in __x3mca_channels:
        XAS_dictionary_x3mca["addresses"]["ROI%02i"%i] = __x3mca_id + ".roi%02i"%i
        XAS_dictionary_x3mca["addresses"]["ICR%02i"%i] = __x3mca_id + ".icr%02i"%i
        XAS_dictionary_x3mca["addresses"]["OCR%02i"%i] = __x3mca_id + ".ocr%02i"%i
        __FLUO+="+numpy.nan_to_num(ROI%02i[:]/OCR%02i[:]*ICR%02i[:])"%(i,i,i)
        __FLUO_RAW+="+ROI%02i[:]"%(i)
    __FLUO+=")/numpy.array(I0[:],'f')"
    __FLUO_RAW+=")/numpy.array(I0[:],'f')"
    XAS_dictionary_x3mca["formulas"]["FLUO"] = __FLUO
    XAS_dictionary_x3mca["formulas"]["FLUO_RAW"] = __FLUO_RAW
    del __FLUO
    del __FLUO_RAW
#These Posts should be modified each time when changing detectors.
    from p_spec_syntax import pseudo_counter

    ct_x3mca=pseudo_counter(masters=[pulseGen0],slaves=[cx1sai,x3mca,cpt3], posts= ctPosts_x3mca, postDictionary=XAS_dictionary_x3mca)

except Exception as tmp:
    print(tmp)
    print("Failure defining ct0 config")

#     Definition of ct_xp for ecscan_xp

try:
    ctPosts_xp=[\
    {"name":"MUX","formula":"log(float(ch[0])/ch[1])","units":"","format":"%9.7f"},\
    {"name":"MUS","formula":"log(float(ch[1])/ch[2])","units":"","format":"%9.7f"},\
    {"name":"I1Norm","formula":"float(ch[1])/ch[0]","units":"","format":"%9.7e"},\
    ]  
    #>>>>>>>>>>>>>>>> Remember only formulas are saved to file <<<<<<<<<<<<<<<<<<<<<<<<
    XAS_dictionary_xp={
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
 
    ct_xp=pseudo_counter(masters=[pulseGen0,],slaves=[cx1sai,cpt3],posts = ctPosts_xp, postDictionary = XAS_dictionary_xp)

except Exception as tmp:
    print(tmp)
    print("Failure defining ct_xp config")

mostab.scaler="ct_xp"

# Scan macros
execfile(__pySamba_root+"/modules/pulse/p_ascan.py")
execfile(__pySamba_root+"/modules/pulse/p_cscan.py")
execfile(__pySamba_root+"/modules/pulse/p_ecscan.py")

#ct=ct_xp
ct=ct0
#ct=ct_x3mca

#define ecscan_xp on the base of ecscan
def ecscanXP(fileName,e1,e2,n=1,dt=0.04,velocity=10,e0=-1,mode="t",shutter=False,beamCheck=True):
    shell=get_ipython()
    try:
        shell.user_ns["ct"]=shell.user_ns["ct_xp"]
        ecscan(fileName=fileName,e1=e1,e2=e2,n=n,dt=dt,velocity=velocity,e0=e0,mode=mode,shutter=shutter,beamCheck=beamCheck)
    except:
        raise
    finally:
        shell.user_ns["ct"]=shell.user_ns["ct0"]
    return

#legacy definitions
def setroi(ch1, ch2):
    """Set roi an ALL channels between ch1 and ch2. This is a silly way to do it... must be redesigned"""
    try:
        mca1.setROIs(ch1, ch2)
    except:
        pass
    try:
        mca2.setROIs(ch1, ch2)
    except:
        pass
    try:
        x3mca.setROIs(ch1, ch2)
    except:
        pass
    return 

def setSTEP():
    return
def setMAP():
    return

def ctx(dt=1.):
    ct(dt)
    n_mca=len(ct.mca_units)
    try:
        figure(101).clear()
    except:
        pass
    fig,ax=plt.subplots(n_mca,1,num=101)
    if n_mca == 1: 
        ax.plot(sum(ct.mca_units[0].read_mca(),axis=0))
    elif n_mca >1:
        for i in range(len(ct.mca_units)):
            ax[i].plot(sum(ct.mca_units[i].read_mca(),axis=0))
    return

__shclose = shclose
__shopen = shopen
