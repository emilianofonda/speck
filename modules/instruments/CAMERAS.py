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


