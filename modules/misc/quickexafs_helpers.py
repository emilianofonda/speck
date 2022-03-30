from __future__ import print_function
import IPython
import numpy
from GracePlotter import xplot
try:
    from quickstart import *
except Exception as tmp:
    print(tmp)

#Quick and dirty plot of quickexafs
try:
    qm2 = DeviceProxy("tmp/qexafs-v1/qexafs_manager_mono2")
    qm3 = DeviceProxy("tmp/qexafs-v1/qexafs_manager_mono3")
    #qm=DeviceProxy("d09-1-cx1/dt/qexafs_manager")
    #from quickplot_v2 import *
except Exception as tmp:
    print(tmp)
    print("No quickexafs manager")

def quickplot2():
    x,y=qm2.read_attributes(["energySpectrum","muxSpectrum"])
    evr=10**int(max(numpy.log10(len(x.value))-3,1))
    xplot(x.value[0:-1:evr],y.value[0:-1:evr])
def quickplot3():
    x,y=qm3.read_attributes(["energySpectrum","muxSpectrum"])
    evr=10**int(max(numpy.log10(len(x.value))-3,1))
    xplot(x.value[0:-1:evr],y.value[0:-1:evr])

try:
    def quickstart2(prefix="",folder="",save=True,wait=True,timeout=6.):
        #shell = IPython.core.ipapi.get()
        shell = IPython.core.getipython.get_ipython()
        q2_cam = shell.user_ns["q2_cam"]
        q2_delta = shell.user_ns["q2_delta"]
        return quickstart(prefix,folder,"tmp/qexafs-v1/QEXAFS_MANAGER_MONO2","storage/recorder/datarecorder.1",q2_cam,q2_delta,save,wait,timeout)
#        return quickstart(prefix,folder,"d09-1-cx1/dt/qexafs_manager_mono2","storage/recorder/datarecorder.1",q2_cam,q2_delta,save,wait,timeout)
        
    def quickstart3(prefix="",folder="",save=True,wait=True,timeout=6.):
        #shell = IPython.core.ipapi.get()
        shell = IPython.core.getipython.get_ipython()
        q3_cam = shell.user_ns["q3_cam"]
        q3_delta = shell.user_ns["q3_delta"]
        return quickstart(prefix,folder,"tmp/qexafs-v1/QEXAFS_MANAGER_MONO3","storage/recorder/datarecorder.1",q3_cam,q3_delta,save,wait,timeout)
#        return quickstart(prefix,folder,"d09-1-cx1/dt/qexafs_manager_mono3","storage/recorder/datarecorder.1",q3_cam,q3_delta,save,wait,timeout)
    
    def quickstop2(wait=True,timeout=6):
#        return quickstop("d09-1-cx1/dt/qexafs_manager_mono2",wait,timeout)
        return quickstop("tmp/qexafs-v1/QEXAFS_MANAGER_MONO2",wait,timeout)

    def quickstop3(wait=True,timeout=6):
#        return quickstop("d09-1-cx1/dt/qexafs_manager_mono3",wait,timeout)
        return quickstop("tmp/qexafs-v1/QEXAFS_MANAGER_MONO3",wait,timeout)
except Exception as tmp:
    print(tmp)
def q2_scan(e1,e2,de,dt,name="q2_scan",delay=0.25):
    return ascan(q2_energy,e1,e2,de,dt,name=name,delay=delay)
def q3_scan(e1,e2,de,dt,name="q3_scan",delay=0.25):
    return ascan(q3_energy,e1,e2,de,dt,name=name,delay=delay)


