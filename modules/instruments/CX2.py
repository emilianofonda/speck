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

from p_dxmap import dxmap

try:
    config = {"fileGeneration":False,"streamTargetPath":'D:\\FTP',\
    "mode":"MAP1", "streamNbAcqPerFile":250,"nbPixelsPerBuffer":50}
    cx2xia1=dxmap("d09-1-cx2/dt/dtc-mca_xmap.1",FTPclient="",identifier = "cx2xia1",\
    FTPserver="",spoolMountPoint="/dev/shm/cx2xia1", config=config)
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
"nexusTargetPath":'/dev/shm/cx2sai1',"nexusNbAcqPerFile":1000,"dataBufferNumber":1,\
"statHistoryBufferDepth":1000}

try:

    sai_1 = p_sai("d09-1-cx2/ca/sai.1", timeout=10., deadtime=0.1, spoolMountPoint="/dev/shm/cx2sai1",\
    config=config, identifier="cx2sai1",GateDownTime=2.)

except Exception, tmp:
    print tmp

#bufferedCounter (Theta)

from p_bufferedCounter import bufferedCounter as p_bufferedCounter

config = {"frequency":100,"integrationTime":0.01,"nexusFileGeneration":False,\
"nexusTargetPath":'/dev/shm/cpt3',"nexusNbAcqPerFile":1000,"totalNbPoint":1000,\
"bufferDepth":100}

cpt3 = p_bufferedCounter("d09-1-c00/ca/cpt.3",deadtime=0.1,timeout=10,config = config,
spoolMountPoint="/dev/shm/cpt3",identifier="encoder_rx1",GateDownTime=2.)


#PulseGenerator

from p_pulsegen import pulseGen
config = {"generationType":"FINITE","pulseNumber":1,"counter0Enable":True,\
"initialDelay0":0,"delayCounter0":2,"pulseWidthCounter0":998}
#delayCounter0 is the GateDownTime of the other cards

pulseGen0 = pulseGen("d09-1-cx2/dt/pulsgen.2",config=config,deadtime=0.1,timeout=10.)

try:
#    ctPosts=[\
#    {"name":"MUX","formula":"log(float(ch[0])/ch[1])","units":"","format":"%9.7f"},\
#    {"name":"MUS","formula":"log(float(ch[1])/ch[2])","units":"","format":"%9.7f"},\
#    {"name":"I1Norm","formula":"float(ch[1])/ch[0]","units":"","format":"%9.7e"},\
#    {"name":"MUF","formula":"float(sum(ch[4:8]))/ch[0]","units":"","format":"%9.7e"},]

#These Posts should be modified each time when changing detectors.
    from p_spec_syntax import pseudo_counter

    cpt=pseudo_counter(masters=[pulseGen0,])
    #ct=pseudo_counter(masters=[pulseGen0,],slaves=[mca1,], posts= ctPosts)
    #ct=pseudo_counter(masters=[pulseGen0],slaves=[sai_1,x3mca], posts= ctPosts)
    #Remember to set the cpt3 card from master to slave mode and modify BNC cable position from OUT to GATE
    #ct=pseudo_counter(masters=[pulseGen0,],slaves=[sai_1,mca1,cpt3], posts= ctPosts)
    ct=pseudo_counter(masters=[pulseGen0,],slaves=[sai_1,cx2xia1,cpt3])

except Exception, tmp:
    print tmp
    print "Failure defining ct command"

mostab.scaler = "ct"

execfile(__pySamba_root+"/modules/pulse/p_ascan.py")

#from p_ecscan import ecscan

#legacy definitions

def setSTEP():
    return
def setMAP():
    return
