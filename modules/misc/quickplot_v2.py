from __future__ import print_function
from GracePlotter import xplot
from PyTango import DeviceProxy, DevError
from e2theta import *
from numpy import log
from time import sleep

def quickplot2(qm=DeviceProxy("tmp/qexafs-v1/qexafs_manager_mono2"), curve = -1, dx= 0., dy=0.):
    try:
        energy_data = qm.energySpectrum
        mux_data = qm.muxSpectrum
        #for i in xrange(5):
            #dt = ni6602.read_attribute("DeltaTheta")
            #channel0_Raw, channel1_Raw =  sai1.read_attributes(["channel0_Raw","channel1_Raw"])
            #if abs(dt.time.tv_sec - channel0_Raw.time.tv_sec) < 1:
            #    break
        #energy_data = theta2e(dt.value + qm.deltaTheta0 + qm.theta, qm.cristalInterReticularDistance)
        #mux_data = log(1.0 * channel0_Raw.value / channel1_Raw.value)
    except DevError as tmp:
        if tmp["reason"] == "API_AttrValueNotSet":
            print("Try later... ni6602 sees no new data...")
        return
    except Exception as tmp:
        print(tmp)
        return
    term1 = len(energy_data)
    if term1 > 10e3:
        itv = int(term1 / 10e3)
    else: 
        itv = 1
    xplot(energy_data[::itv] + dx, mux_data[::itv] + dy, curve=curve)
    del energy_data, mux_data
    return

def autoquickplot2(t=2, curve=1, dx=0., dy=0.):
    ddx=0.
    ddy=0.
    while(True):
        quickplot2(curve=curve,dx=ddx,dy=ddy)
        ddx += dx
        ddy += dy
        sleep(t)

