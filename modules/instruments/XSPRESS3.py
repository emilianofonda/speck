from __future__ import print_function
#trigger modes can be internal_trigger or external_gate
from xspress3 import xspress3mini

try:
    config={"acq_trigger_mode":"internal_trigger",\
    "saving_suffix":"hdf","saving_prefix":"xsp3_","saving_format":"hdf5",\
    "saving_directory":"/mnt/spoolSAMBA","saving_mode":"auto_frame",\
    "saving_overwrite_policy":"abort"}
    
    x3mca = xspress3mini(label = "xspress3/xspress3/xspress3.1", timeout=30,deadtime=0.1,
    spoolMountPoint="/nfs/srv5/spool1/xsp3",specificDevice="xspress3/xspress3/xspress3.1-specific",\
    config=config,identifier="x3_")
except Exception as tmp:
    print(tmp)

try:
    ctPosts=[\
    {"name":"MUX","formula":"log(float(ch[0])/ch[1])","units":"","format":"%9.7f"},\
    {"name":"MUS","formula":"log(float(ch[1])/ch[2])","units":"","format":"%9.7f"},\
    {"name":"I1Norm","formula":"float(ch[1])/ch[0]","units":"","format":"%9.7e"},\
    {"name":"MUF","formula":"float(sum(ch[7:10]))/ch[0]","units":"","format":"%9.7e"},]

    cpt=pseudo_counter(masters=[cpt0,])
    ct=pseudo_counter(masters=[cpt0,x3mca],slaves2arm2stop=[mca1,],slaves2arm=[], posts= ctPosts)

except Exception as tmp:
    print(tmp)

