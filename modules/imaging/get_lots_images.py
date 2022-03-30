#!/bin/env python

from __future__ import print_function
import time
import sys

from pylab import *
from PyTango import DeviceProxy
from VG_images import VideoIntensityMonitor


VG = VideoIntensityMonitor("i10-c-c01/dt/imag1-vg", "Image", ROIdef= ((88, 285), [424, 120]))
U20 = DeviceProxy("ans-c10/ei/c-u20")

def get_U20gap():
      return U20.read_attribute("gap").value

for i in range(1,1000):
    #time.sleep(0.1)
    VG.read_image()
    gap = get_U20gap()
    title("U20 Gap =%6.2f mm  %s" % (get_U20gap(),time.ctime()))

    imshow(VG.get_image_array())
    print("At %27s saved image %04d for gap %6.2f" % (time.ctime(), i, gap))
    savefig("beam_images_30to6/beam_%04d.png" % i)
    
