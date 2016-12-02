from sensor_group import sensor_group
__tmp=sensor_group(\
[
#["d09-1-c02/dt/vg1.0-analyzer",["XProjFitCenter","YProjFitCenter","XProjFitFWHM","YProjFitFWHM","MeanIntensity"]],\
#["d09-1-c04/dt/vg1.1-analyzer",["XProjFitCenter","YProjFitCenter","XProjFitFWHM","YProjFitFWHM","MeanIntensity"]],\
#["d09-1-c06/dt/vg1.2-analyzer",["XProjFitCenter","YProjFitCenter","XProjFitFWHM","YProjFitFWHM","MeanIntensity"]],\
["d09-1-cx1/dt/vg2-basler-analyzer",["XProjFitCenter","YProjFitCenter","XProjFitFWHM","YProjFitFWHM","MeanIntensity"]]\
])
ct.all.append(__tmp)
ct.slaves.append(__tmp)
ct.reinit()
cam4_vga = DeviceProxy("d09-1-cx1/dt/vg2-basler-analyzer")
#Set Up Analysis Parameters
print "Modifing video grabber parameters"
cam4_vga.AutoROIMagFactorX = 3
cam4_vga.AutoROIMagFactorY = 3
cam4_vga.EnableUserROI = False
cam4_vga.EnableAutoROI = True
cam4_vga.EnableProfiles = True
cam4_vga.AutoROIThreshold  = 20
print """
cam4_vga.AutoROIMagFactorX = 3\
cam4_vga.AutoROIMagFactorY = 3
cam4_vga.EnableUserROI     = False
cam4_vga.EnableAutoROI     = True
cam4_vga.EnableProfiles    = True
cam4_vga.AutoROIThreshold  = 20
"""

