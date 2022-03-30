from __future__ import print_function
#This instrument set up the beamline for 
#PulseGen master on CX1
#Xspress card as a slave as well as sai0
#It's not just the pulsegen

#GateDownTime is 2 (ms for all, it can be reduced  down to 2microseconds= 0.002ms)

#EXSPRESS3
#trigger modes can be internal_trigger or external_gate
from xspress3 import xspress3mini

try:
    config={"acq_trigger_mode":"external_gate",\
    "saving_suffix":"hdf","saving_prefix":"xsp3_","saving_format":"hdf5",\
    "saving_directory":"/mnt/spoolSAMBA","saving_mode":"auto_frame",\
    "saving_overwrite_policy":"abort"}
    
    x3mca = xspress3mini(label = "xspress3/xspress3/xspress3.1", timeout=30,deadtime=0.1,
    spoolMountPoint="/nfs/srv5/spool1/xsp3",specificDevice="xspress3/xspress3/xspress3.1-specific",\
    config=config,identifier="x3_")
except Exception as tmp:
    print(tmp)

from sai import sai

config = {"configurationId":3,"frequency":10000,"integrationTime":1,"nexusFileGeneration":False,\
"nexusTargetPath":'\\\\srv5\\spool1\\sai',"nexusNbAcqPerFile":1000,"dataBufferNumber":1,\
"statHistoryBufferDepth":1000}

try:
    sai0 = sai("d09-1-c00/ca/sai.1", timeout=10., deadtime=0.1, spoolMountPoint="/nfs/srv5/spool1/sai",\
    config=config, identifier="sai0_",GateDownTime=2.)
except Exception as tmp:
    print(tmp)

from bufferedCounter import bufferedCounter

config = {"frequency":100,"integrationTime":0.01,"nexusFileGeneration":False,\
"nexusTargetPath":'\\\\srv5\\spool1\\cpt',"nexusNbAcqPerFile":1000,"totalNbPoint":1000,\
"bufferDepth":100}

cpt3 = bufferedCounter("d09-1-c00/ca/cpt.3",deadtime=0.1,timeout=10,config = config,
spoolMountPoint="/nfs/srv5/spool1/cpt",identifier="cpt3",GateDownTime=2.)


from pulsegen import pulseGen
config = {"generationType":"FINITE","pulseNumber":1,"counter0Enable":True,\
"initialDelay0":0,"delayCounter0":2,"pulseWidthCounter0":998}
#delayCounter0 is the GateDownTime of the other cards
pulseGen0 = pulseGen("d09-1-c00/ca/pulsgen.1",config=config,deadtime=0.1,timeout=10.)

try:
    ctPosts=[\
    {"name":"MUX","formula":"log(float(ch[0])/ch[1])","units":"","format":"%9.7f"},\
    {"name":"MUS","formula":"log(float(ch[1])/ch[2])","units":"","format":"%9.7f"},\
    {"name":"I1Norm","formula":"float(ch[1])/ch[0]","units":"","format":"%9.7e"},\
    {"name":"MUF","formula":"float(sum(ch[4:8]))/ch[0]","units":"","format":"%9.7e"},]

    cpt=pseudo_counter(masters=[pulseGen0,])
    #ct=pseudo_counter(masters=[pulseGen0,],slaves2arm=[],slaves2arm2stop=[mca1,],slaves=[], posts= ctPosts)
    ct=pseudo_counter(masters=[pulseGen0],slaves2arm=[sai0,x3mca],slaves2arm2stop=[],slaves=[], posts= ctPosts)
    #Remember to set the cpt3 card from master to slave mode and modify BNC cable position from OUT to GATE
    #ct=pseudo_counter(masters=[pulseGen0,],slaves2arm=[sai0,x3mca,cpt3],slaves2arm2stop=[],slaves=[], posts= ctPosts)

except Exception as tmp:
    print(tmp)
    print("Failure defining ct command")

