from __future__ import print_function
from p_sensor_group import sensor_group
__tmp=sensor_group(\
[
["d09-1-cx2/dt/vg2-basler-analyzer",["XProjFitCenter","YProjFitCenter","XProjFitFWHM","YProjFitFWHM","MeanIntensity"]]\
])
ct.all.append(__tmp)
ct.slaves.append(__tmp)
ct.reinit()
cam5_vga = DeviceProxy("d09-1-cx2/dt/vg2-basler-analyzer")
#Set Up Analysis Parameters
print("Modifing video grabber parameters")
cam5_vga.AutoROIMagFactorX = 3
cam5_vga.AutoROIMagFactorY = 3
cam5_vga.EnableUserROI = False
cam5_vga.EnableAutoROI = True
cam5_vga.EnableProfiles = True
cam5_vga.AutoROIThreshold  = 20
print("""
cam5_vga.AutoROIMagFactorX = 3\
cam5_vga.AutoROIMagFactorY = 3
cam5_vga.EnableUserROI     = False
cam5_vga.EnableAutoROI     = True
cam5_vga.EnableProfiles    = True
cam5_vga.AutoROIThreshold  = 20
""")

