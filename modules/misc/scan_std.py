# -*- coding: utf-8 -*-

from __future__ import print_function
import PyTango
import time
import numpy
from numpy import shape
#import pvt

##############################################################################################

_scan = PyTango.DeviceProxy("d09-1-c00/ex/scan.1")
_recorder = PyTango.DeviceProxy("storage/recorder/datarecorder.1")
_cpt1 = PyTango.DeviceProxy("d09-1-c00/ca/cpt.1")
_mca1 = PyTango.DeviceProxy("d09-1-cx1/dt/dtc-mca_xmap.1")
_timeBases=["d09-1-c00/ca/cpt.1"]
#_timeBases=["d09-1-c00/ca/cpt.1","d09-1-cx1/dt/dtc-mca_xmap.1"]
#_hkl = PyTango.DeviceProxy("i14-c-cx2/ex/dif_4c-sim-hkl")
#_dif = PyTango.DeviceProxy("i14-c-cx2/ex/dif_4c")


#_att1 = PyTango.DeviceProxy("i14-c-c07/ex/att.1")
#_att2 = PyTango.DeviceProxy("i14-c-c07/ex/att.2")
#_fastatt = PyTango.DeviceProxy("i14-c-c07/ex/fast_att.1")
#_4axis = PyTango.DeviceProxy("i14-c-cx2/ex/UHVgroup-test")

#_detc2 = PyTango.DeviceProxy("i14-c-cx1/ex/dect-tangoparser")


############################################################################################# 
   
#_viewerC03 = PyTango.DeviceProxy("i14-c-c03/dt/imag.1-MT_Tz.1-POS")
#_viewerC07 = PyTango.DeviceProxy("i14-c-c06/dt/imag.1-MT_Tz.1-POS")

#############################################################################################

_movables = {
            'x': 'd09-1-cx1/ex/tab-mt_tx.1/position',
            'z': 'd09-1-cx1/ex/tab-mt_tz.1/position'
	    }
#            'L': 'I14-C-CX2/EX/DIF_4C-L/position',
#            'omega' : 'I14-C-CX2/EX/OMEGA-UHV/position',
#            'mu' : 'I14-C-CX2/EX/MU-UHV/position',
#            'delta' : 'I14-C-CX2/EX/DELTA-UHV/position',
#            'gamma' : 'I14-C-CX2/EX/GAMMA-UHV/position',
#            'omegaG' : 'I14-C-CX2/EX/UHVgroup-test/omega-uhv',
#            'muG' : 'I14-C-CX2/EX/UHVgroup-test/mu-uhv',
#            'deltaG' : 'I14-C-CX2/EX/UHVgroup-test/delta-uhv',
#            'gammaG' : 'I14-C-CX2/EX/UHVgroup-test/gamma-uhv',
#            'eta-A' : 'I14-C-CX2/EX/eta-A-UHV/position',
#            'delta-A' : 'I14-C-CX2/EX/delta-A-UHV/position',
#            'omega-A' : 'I14-C-CX2/EX/omega-A-UHV/position',
#            'bragg' : 'I14-C-C02/OP/MONO-MT_Rm.1/position',
#            'pitch' : 'I14-C-C02/OP/MONO-MT_Rx.1/position',
#            'tz' : 'I14-C-C02/OP/MONO-MT_Tz.1/position',
#            'roll' : 'I14-C-C02/OP/MONO-MT_Rs.1/position',
#            'pslvg' : 'I14-C-C01/EX/FENT_V.1/gap',
#            'pslvp' : 'I14-C-C01/EX/FENT_V.1/position',
#            'pslhg' : 'I14-C-C01/EX/FENT_H.1/gap',
#            'pslhp' : 'I14-C-C01/EX/FENT_H.1/position',
#            'energy' : 'I14-C-C00/EX/BEAMLINEENERGY/energy',
#            'gap' : 'ans-c14/ei/c-u20/gap',
#            'mono':'I14-C-C02/OP/MONO/energy',
#            'ssl1vg' : 'I14-C-C03/EX/FENT_V.2/gap',           
#            'ssl1vp' : 'I14-C-C03/EX/FENT_V.2/position',
#            'ssl1hg' : 'I14-C-C03/EX/FENT_H.2/gap',
#            'ssl1hp' : 'I14-C-C03/EX/FENT_H.2/position',
#            'ssl6vg' : 'I14-C-CX2/EX/FENT_V.6/gap',
#            'ssl6vp' : 'I14-C-CX2/EX/FENT_V.6/position',
#            'ssl6hg' : 'I14-C-CX2/EX/FENT_H.6/gap',
#            'ssl6hp' : 'I14-C-CX2/EX/FENT_H.6/position',
#            'x' : 'i14-c-cx2/ex/hexapod-uhv/x',
#            'y' : 'i14-c-cx2/ex/hexapod-uhv/y',
#            'z' : 'i14-c-cx2/ex/hexapod-uhv/z',
#            'u' : 'i14-c-cx2/ex/hexapod-uhv/u',
#            'v' : 'i14-c-cx2/ex/hexapod-uhv/v',
#            'w' : 'i14-c-cx2/ex/hexapod-uhv/w',
#            'cyb-ht' : 'i14-c-cx2/dt/cyberstar.1/voltage',            
#            'cyb-up' : 'i14-c-cx2/dt/cyberstar.1/scaUpperThreshold',        
#            'cyb-lo' : 'i14-c-cx2/dt/cyberstar.1/scaLowerThreshold',            
#            'cyb-pkt' : 'i14-c-cx2/dt/cyberstar.1/peakingTime',
#            'cyb-wg' : 'i14-c-cx2/dt/cyberstar.1/windowWidth',
#            'cyb-wp' : 'i14-c-cx2/dt/cyberstar.1/windowCenterPosition',
#            'cyb-gain' : 'i14-c-cx2/dt/cyberstar.1/amplifierGain',   
#            'apd-ht' : 'i14-c-cx2/dt/det-avalanche.1/voltage',            
#            'apd-up' : 'i14-c-cx2/dt/det-avalanche.1/scaUpperThreshold',        
#            'apd-lo' : 'i14-c-cx2/dt/det-avalanche.1/scaLowerThreshold',            
#            'apd-sht' : 'i14-c-cx2/dt/det-avalanche.1/shapingTime',
#            'apd-wg' : 'i14-c-cx2/dt/det-avalanche.1/WindowWidth',
#            'apd-wp' : 'i14-c-cx2/dt/det-avalanche.1/scaWindowCenterPosition',             
#            'z1-base-uhv' : "i14-c-cx2/ex/base_z.z1_plan-uhv/position",
#            'z2-base-uhv' : "i14-c-cx2/ex/base_z.z2_trait-uhv/position",
#            'z3-base-uhv' : "i14-c-cx2/ex/base_z.z3_point-uhv/position",
#            'y1-base-uhv' : "i14-c-cx2/ex/base_y.y_point-uhv/position",
#            'y2-base-uhv' : "i14-c-cx2/ex/base_y.y_trait-uhv/position",
#            'mon2' : "i14-c-c07/dt/mi_ddio.2-mt_tz.1/position",
#            'cam' : "i14-c-cx2/dt/cam-mt_tx.1/position",
# MED
#            'omegaG_MED' : 'I14-C-CX1/EX/MED-GROUP.1/omega-med',
#            'muG_MED' : 'I14-C-CX1/EX/MED-GROUP.1/mu-med',
#            'deltaG_MED' : 'I14-C-CX1/EX/MED-GROUP.1/delta-med',
#            'gammaG_MED' : 'I14-C-CX1/EX/MED-GROUP.1/gamma-med'
#            }
#            
_sensors = [
	'd09-1-cx1/dt/dtc-mca_xmap.1/channel00',
	'd09-1-cx1/dt/dtc-mca_xmap.1/channel01',
	'd09-1-cx1/dt/dtc-mca_xmap.1/channel02',
	'd09-1-cx1/dt/dtc-mca_xmap.1/channel03',
	'd09-1-cx1/dt/dtc-mca_xmap.1/channel04',
	'd09-1-cx1/dt/dtc-mca_xmap.1/channel05',
	'd09-1-cx1/dt/dtc-mca_xmap.1/channel06',
	'd09-1-cx1/dt/dtc-mca_xmap.1/channel07',
       	'd09-1-cx1/dt/dtc-mca_xmap.1/inputCountRate00',
       	'd09-1-cx1/dt/dtc-mca_xmap.1/inputCountRate01',
       	'd09-1-cx1/dt/dtc-mca_xmap.1/inputCountRate02',
       	'd09-1-cx1/dt/dtc-mca_xmap.1/inputCountRate03',
       	'd09-1-cx1/dt/dtc-mca_xmap.1/inputCountRate04',
       	'd09-1-cx1/dt/dtc-mca_xmap.1/inputCountRate05',
       	'd09-1-cx1/dt/dtc-mca_xmap.1/inputCountRate06',
       	'd09-1-cx1/dt/dtc-mca_xmap.1/inputCountRate07',
       	'd09-1-cx1/dt/dtc-mca_xmap.1/outputCountRate00',
       	'd09-1-cx1/dt/dtc-mca_xmap.1/outputCountRate01',
       	'd09-1-cx1/dt/dtc-mca_xmap.1/outputCountRate02',
       	'd09-1-cx1/dt/dtc-mca_xmap.1/outputCountRate03',
       	'd09-1-cx1/dt/dtc-mca_xmap.1/outputCountRate04',
       	'd09-1-cx1/dt/dtc-mca_xmap.1/outputCountRate05',
       	'd09-1-cx1/dt/dtc-mca_xmap.1/outputCountRate06',
       	'd09-1-cx1/dt/dtc-mca_xmap.1/outputCountRate07',
       	'd09-1-cx1/dt/dtc-mca_xmap.1/roi00_01',
       	'd09-1-cx1/dt/dtc-mca_xmap.1/roi01_01',
       	'd09-1-cx1/dt/dtc-mca_xmap.1/roi02_01',
       	'd09-1-cx1/dt/dtc-mca_xmap.1/roi03_01',
       	'd09-1-cx1/dt/dtc-mca_xmap.1/roi04_01',
       	'd09-1-cx1/dt/dtc-mca_xmap.1/roi05_01',
       	'd09-1-cx1/dt/dtc-mca_xmap.1/roi06_01',
       	'd09-1-cx1/dt/dtc-mca_xmap.1/roi07_01',
	'd09-1-c00/ca/cpt.1/counter1',
	'd09-1-c00/ca/cpt.1/counter2',
	'd09-1-c00/ca/cpt.1/counter3',
	'd09-1-c00/ca/cpt.1/counter4',
	'd09-1-c00/ca/cpt.1/counter5',
	'd09-1-c00/ca/cpt.1/counter6',
	'd09-1-c00/ca/cpt.1/counter7',
	'd09-1-c00/ca/cpt.1/counter8',
	'd09-1-c00/ca/cpt.1/counter9',
	'd09-1-c00/ca/cpt.1/counter10',
	'd09-1-c00/ca/cpt.1/counter11',
	'd09-1-c00/ca/cpt.1/counter12',
	'd09-1-c00/ca/cpt.1/counter13',
	'd09-1-c00/ca/cpt.1/counter14',
	'd09-1-c00/ca/cpt.1/counter15',
	'd09-1-c00/ca/cpt.1/counter16',
	'd09-1-c00/ca/cpt.1/counter17',
	'd09-1-c00/ca/cpt.1/counter18',
	'd09-1-c00/ca/cpt.1/counter19',
	'd09-1-c00/ca/cpt.1/counter20',
	'd09-1-c00/ca/cpt.1/counter21',
	'd09-1-c00/ca/cpt.1/counter22',
	'd09-1-c00/ca/cpt.1/counter23',
	'd09-1-c00/ca/cpt.1/counter24',
	'd09-1-c00/ca/cpt.1/counter25',
	'd09-1-c00/ca/cpt.1/counter26',
	]
#_sensorsC00a = [
#            'i14-c-c00/dt/imag.1-analyzer/MeanIntensity',
#            'i14-c-c00/dt/imag.1-analyzer/XProjFitCenter',
#            'i14-c-c00/dt/imag.1-analyzer/YProjFitCenter'
#            ]
#_sensorsC00b = [
#            'i14-c-c00/dt/imag.2-analyzer/MeanIntensity',
#            'i14-c-c00/dt/imag.2-analyzer/XProjFitCenter',
#            'i14-c-c00/dt/imag.2-analyzer/YProjFitCenter'
#            ]
#_sensorsC03 = [
#             'i14-c-c03/dt/imag.1-analyzer/MeanIntensity',
#             'i14-c-c03/dt/imag.1-analyzer/XProjFitCenter',
#             'i14-c-c03/dt/imag.1-analyzer/YProjFitCenter',
#             'i14-c-c03/dt/imag.1-tangoparser/flux'
#            ]
#_sensorsC07 = [
#            'i14-c-c06/dt/imag.1-analyzer/MeanIntensity',
#            'i14-c-c06/dt/imag.1-analyzer/XProjFitCenter',
#            'i14-c-c06/dt/imag.1-analyzer/YProjFitCenter',
#            ]
#_sensors4	= [
#             _movables['gap'],
#	           _movables['pitch'],
#	           _movables['roll'],
#	           _movables['tz']
#            ]
#_sensors_seuil = [
#              'i14-c-c00/ex/seuil.1-tangoparser/res'
#            ]
#_sensors += _sensors_seuil
#_sensors += _sensorsC00b
#_sensors += _sensorsC03
#_sensors += _sensorsC07
	           
# print _sensors
#_actuatorsErrorStrtegy = 1
#_actuatorsRetryCount = 5
#    sensorsList = _sensors
#    if _viewerC03.state() in [PyTango._PyTango.DevState.INSERT]:
#        sensorsList += _sensorsC03
#    if _viewerC07.state() in [PyTango._PyTango.DevState.INSERT]:
#        sensorsList += _sensorsC07       

        
#################################################################################################
#  SCANS
#################################################################################################

def dscan(motor, debut, fin, n, dt,timeBases=_timeBases,delay=0.):
    att = PyTango.AttributeProxy(_movables[motor])
    position = att.read().value
    ascan(motor, position + debut, position + fin, n, dt, afterRunActionType=2,timeBases=_timeBases,delay=0.)

def ascan(motor, debut, fin, n, dt, afterRunActionType=0,timeBases=_timeBases,delay=0.):
    actuators = [_movables[motor]]
    sensors = [s for s in _sensors if s not in actuators] # impossible de mettre dans actuator et sensors le meme attribut.
    trajectories = [numpy.linspace(debut, fin, n + 1)]
    integrationTimes = numpy.ones(shape(trajectories[0])) * dt 
    
    print("fileName :" ,_recorder.read_attribute("fileName").value)
    print("actuators : ", actuators)
    print("sensors :", sensors)
    print("timebases : ", timeBases)
    print(("trajectories :", trajectories))
#    print("integrationTimes : ", integrationTimes)

    time.sleep(1)
    _scan.Clean()
    _scan.actuatorsdelay = delay   # util pour apd
    _scan.actuators = actuators
    _scan.sensors = sensors
    _scan.timeBases = timeBases
    _scan.integrationTimes = integrationTimes
    _scan.trajectories = trajectories
    _scan.afterRunActionType = afterRunActionType
    _scan.Start()

    try:
        while _scan.state() not in [PyTango.DevState.ON, PyTango.DevState.ALARM]:
            time.sleep(.1)
    except KeyboardInterrupt:
        _scan.abort()

def d2scan(motor1, debut1, fin1, motor2, debut2, fin2, n, dt,timeBases=_timeBases,delay=0.):
    att1 = PyTango.AttributeProxy(_movables[motor1])
    att2 = PyTango.AttributeProxy(_movables[motor2])
    position1 = att1.read().value
    position2 = att2.read().value
    a2scan(motor1, position1 + debut1, position1 + fin1, motor2, position2 + debut2, position2 + fin2, n, dt, afterRunActionType=2)
    return

def a2scan(motor1, debut1, fin1, motor2, debut2, fin2, n, dt, afterRunActionType=0,timeBases=_timeBases):
    actuators = [_movables[motor1],_movables[motor2]]
    sensors = [s for s in _sensors if s not in actuators] # impossible de mettre dans actuator et sensors le meme attribut.
    trajectories = numpy.linspace(debut1, fin1, n + 1), numpy.linspace(debut2, fin2, n + 1)
    integrationTimes = numpy.linspace(dt,dt,n+1)
    
    print("fileName :" ,_recorder.read_attribute("fileName").value)
    print("actuators : ", actuators)
    print("sensors :", sensors)
    print("timebases : ", timeBases)
#    print("trajectories :", trajectories)
#    print("integrationTimes : ", integrationTimes)

    time.sleep(1)
    _scan.Clean()
#    _scan.actuatorsdelay = .1
    _scan.actuators = actuators
    _scan.sensors = sensors
    _scan.timeBases = timeBases
    _scan.integrationTimes = integrationTimes
    _scan.trajectories = trajectories
    _scan.afterRunActionType = afterRunActionType
    _scan.Start()

    try:
        while _scan.state() not in [PyTango.DevState.ON, PyTango.DevState.ALARM]:
            time.sleep(.1)
    except KeyboardInterrupt:
        _scan.abort()
    return
    
#def dfscan(motor, debut, fin, n, dt):
#    att = PyTango.AttributeProxy(_movables[motor])
#    position = att.read().value
#    afscan(motor, position + debut, position + fin, n, dt, afterRunActionType=2)
    
#def afscan(motor, debut, fin, n, dt, afterRunActionType=0):
#    """
#    scan on the fly for 1 actuator
#    """
#    actuators = [_movables[motor]]
#    sensors = [s for s in _sensors if s not in actuators] # impossible de mettre dans actuator et sensors le meme attribut.
#    timeBases = ['I14-C-C00/CA/CPT.1']
#    trajectories = [numpy.linspace(debut, fin, n + 1)]
#    integrationTimes = numpy.ones(shape(trajectories[0])) * dt
#    scanSpeed = [numpy.fabs((float(fin)-float(debut))/(n*dt))]
#    
#    print "fileName :" ,_recorder.read_attribute("fileName").value    
#    print "actuators : ", actuators
#    print "sensors :", sensors
#    print "timebases : ", timeBases
#    print("trajectories :", trajectories)
#    print("integrationTimes : ", integrationTimes)
    
#    time.sleep(1)
#    _scan.Clean()
#    _scan.actuators = actuators
#    _scan.sensors = sensors
#    _scan.timeBases = timeBases
#    _scan.integrationTimes = integrationTimes
#    _scan.trajectories = trajectories
#    _scan.onTheFly = True
#    _scan.enableScanSpeed = True
#    _scan.scanSpeed = scanSpeed
#    _scan.afterRunActionType = afterRunActionType
#    _scan.Start()
#    
#    try:
#        while _scan.state() not in [PyTango.DevState.ON, PyTango.DevState.ALARM]:
#            time.sleep(.1)
##            print "remaining time = ", _scan.read_attribute("scanRemainingTime").value
#    except KeyboardInterrupt:
#        _scan.abort()
#
#def dcscan(motor, debut, fin, n, dt):
#    att = PyTango.AttributeProxy(_movables[motor])
#    position = att.read().value
#    acscan(motor, position + debut, position + fin, n, dt, afterRunActionType=2)
#
#def acscan(motor, debut, fin, n, dt, afterRunActionType=0):
#    actuators = [_movables[motor]]
#    sensors = ['I14-C-C00/CA/CPT.2/DT1']
#    if motor != 'mu':
#        sensors += ['I14-C-C00/CA/CPT.2/UHV_MU']
#    if motor != 'omega':
#        sensors += ['I14-C-C00/CA/CPT.2/UHV_OMEGA']
#    if motor != 'delta': 
#        sensors += ['I14-C-C00/CA/CPT.2/UHV_DELTA']
#    if motor != 'gamma':
#        sensors += ['I14-C-C00/CA/CPT.2/UHV_GAMMA']
#    sensors += ['I14-C-CX2/EX/calc-continuoushkl/h']
#    sensors += ['I14-C-CX2/EX/calc-continuoushkl/k']
#    sensors += ['I14-C-CX2/EX/calc-continuoushkl/l']
#    timeBases = ['I14-C-C00/CA/CPT.2']
#    trajectories = [[debut, fin]]
#    integrationTimes = [dt,dt]
#    scanSpeed = [numpy.fabs((float(fin)-float(debut))/(n*dt))]
#
#    print "fileName :" ,_recorder.read_attribute("fileName").value
#    print "actuators : ", actuators
#    print "sensors :", sensors
#    print "timebases : ", timeBases
#    print "trajectories :", trajectories 
#    print "integrationTimes : ", integrationTimes 
#
#    time.sleep(1)
#    _scan.Clean()
#    _scan.hwContinuous = True
#    _scan.hwContinuousNbPt = n + int(3./dt)
#    _scan.actuators = actuators
#    _scan.sensors = sensors
#    _scan.timeBases = timeBases
#    _scan.integrationTimes = integrationTimes
#    _scan.trajectories = trajectories
#    _scan.enableScanSpeed = True
#    _scan.scanSpeed = scanSpeed
#    _scan.afterRunActionType = afterRunActionType
#    _scan.Start()
#
#    try:
#        while _scan.state() not in [PyTango.DevState.ON, PyTango.DevState.ALARM]:
#            time.sleep(.1)
#    except KeyboardInterrupt:
#        _scan.abort()
#
def dmesh(motor, debut, fin, n, motor2, debut2, fin2, n2, dt):
    att = PyTango.AttributeProxy(_movables[motor])
    position = att.read().value
    att2 = PyTango.AttributeProxy(_movables[motor2])
    position2 = att.read().value
    mesh(motor, position + debut , position + fin, n, motor2, position2 + debut2, position2 + fin2, n2, dt)


def mesh(motor, debut, fin, n, motor2, debut2, fin2, n2, dt=1.,timeBases=_timeBases,delay=0.):
    actuators = [_movables[motor]]
    actuators2 = [_movables[motor2]]
    sensors = [s for s in _sensors if s not in actuators + actuators2 ] # impossible de mettre dans actuator et sensors le meme attribut.
    trajectories = [numpy.linspace(debut, fin, n + 1)]
    trajectories2 = [numpy.linspace(debut2, fin2, n2 +1)]
    integrationTimes = numpy.ones(len(trajectories[0]))*dt

    print("fileName :" ,_recorder.read_attribute("fileName").value)
    print("actuators : ", actuators)
    print("actuators2 : ", actuators2)
    print("sensors :", sensors)
    print("timebases : ", timeBases) 
    print("trajectories :", trajectories) 
    print("trajectories2 : ", trajectories2) 
    print("integrationTimes : ", integrationTimes) 
#
    time.sleep(1)
    _scan.Clean()
    _scan.actuators = actuators
    _scan.actuators2 = actuators2
    _scan.sensors = sensors
    _scan.timeBases = timeBases
    _scan.integrationTimes = integrationTimes
    _scan.trajectories = trajectories
    _scan.trajectories2 = trajectories2
    _scan.Start()
    try:
        while _scan.state() not in [PyTango.DevState.ON, PyTango.DevState.ALARM]:
            time.sleep(.1)
    except KeyboardInterrupt:
        _scan.abort()

#def hklscan(debut, fin, n, dt):
#    pseudo = pvt.PseudoAxesHKL("i14-c-cx2/ex/dif_4c-sim-hkl",
#                               "i14-c-cx2/ex/dif_4c")
#    
#    # compute the trajectory a la salsa.
#    debut = numpy.array(debut,dtype='f')
#    fin = numpy.array(fin, dtype='f')
#    trajectory = pvt.compute_trajectory(debut, fin, n)
#    integrationTimes = numpy.ones(n + 1) * float(dt)
#
#    # set the trajectory of the given pseudo axis.
#    pseudo.trajectory = trajectory
#
#    # recuperation de la trajectoire des axes calculé précédemment.
#    # faut il mettre cette chose dans le manager ou directement dans
#    # le device PseudoAxisHKL ?
#    # Si l'on se base sur interface à la salsa, l'utilisateur va juste dire via salsa.
#    # je veux une trajectoire entre début fin avec tant de points sur l'actuateur
#    # bidule du device machin. Donc il n'a pas à savoir qui va vraiment bouger.
#    # cela implique que le device PseudoAxis doit avoir un proxy sur ce qui va vraiment bougé.
#    # a savoir ici le XPSGroupedAxis.
#    # il faut également penser à ce qui se passe si l'utilisateur mélange plusieurs type
#    # d'actuateurs. Il faut donc une interface pour les trajectoires qui indique s'il est
#    # hardware scan compatible.
#
#    
#    actuators = [_movables['muG'], _movables['omegaG'], _movables['deltaG'], _movables['gammaG']]
#    sensors = [s for s in _sensors if s not in actuators] # impossible de mettre dans actuator et sensors le meme attribut.
#    timeBases = ['I14-C-C00/CA/CPT.1']
#    trajectories = pseudo.trajectory_axes.transpose()
#    time.sleep(1)
#    
#    print "fileName :" ,_recorder.read_attribute("fileName").value
#    print "actuators : ", actuators
#    print "sensors :", sensors
#    print "timebases : ", timeBases 
#    print "trajectories :", trajectories 
#    print "integrationTimes : ", integrationTimes 
#
#    _scan.Clean()
#    _scan.actuatorsdelay = .2
#    _scan.actuators = actuators
#    _scan.sensors = sensors
#    _scan.timeBases = timeBases
#    _scan.integrationTimes = integrationTimes
#    _scan.trajectories = trajectories
#    _scan.Start()
#    try:
#        while _scan.state() not in [PyTango.DevState.ON, PyTango.DevState.ALARM]:
#            time.sleep(.1)
#    except KeyboardInterrupt:
#        _scan.abort()
#
#def hklmesh(debut, fin1, fin2, n1, n2 ,dt):
#    pseudo = pvt.PseudoAxesHKL("i14-c-cx2/ex/dif_4c-sim-hkl",
#                               "i14-c-cx2/ex/dif_4c")
#    
#    # compute the trajectory a la salsa.
#    debut = numpy.array(debut,dtype='f')
#    fin1 = numpy.array(fin1, dtype='f')
#    fin2 = numpy.array(fin2, dtype='f')
##    fin3 = [fin1[0]+fin2[0]-debut[0],fin1[1]+fin2[1]-debut[1],fin1[2]+fin2[2]-debut[2]]
#    fin3 = fin1+fin2-debut
##    print " debut fin 1 2 3 " ,debut,fin1,fin2,fin3
#    trajectory1 = pvt.compute_trajectory(debut, fin2, n2)
#    trajectory2 = pvt.compute_trajectory(fin1, fin3, n2)
##    print "trajectoires",trajectory1 , trajectory2
#    trajectory = pvt.compute_trajectory(trajectory1[0],trajectory2[0], n1)
#    for i in range(n2) :
#        aux = pvt.compute_trajectory(trajectory1[i+1],trajectory2[i+1], n1)
#        print i,aux
#        trajectory = numpy.vstack((trajectory,aux))
#    integrationTimes = numpy.ones((n1 + 1)*(n2 + 1)) * float(dt)
##    print "trajectory",trajectory
#        # set the trajectory of the given pseudo axis.
#    pseudo.trajectory = trajectory
#
#    # recuperation de la trajectoire des axes calculé précédemment.
#    # faut il mettre cette chose dans le manager ou directement dans
#    # le device PseudoAxisHKL ?
#    # Si l'on se base sur interface à la salsa, l'utilisateur va juste dire via salsa.
#    # je veux une trajectoire entre début fin avec tant de points sur l'actuateur
#    # bidule du device machin. Donc il n'a pas à savoir qui va vraiment bouger.
#    # cela implique que le device PseudoAxis doit avoir un proxy sur ce qui va vraiment bougé.
#    # a savoir ici le XPSGroupedAxis.
#    # il faut également penser à ce qui se passe si l'utilisateur mélange plusieurs type
#    # d'actuateurs. Il faut donc une interface pour les trajectoires qui indique s'il est
#    # hardware scan compatible.
#
#    
#    actuators = [_movables['muG'], _movables['omegaG'], _movables['deltaG'], _movables['gammaG']]
#    sensors = [s for s in _sensors if s not in actuators] # impossible de mettre dans actuator et sensors le meme attribut.
#    timeBases = ['I14-C-C00/CA/CPT.1']
#    trajectories = pseudo.trajectory_axes.transpose()
#    time.sleep(1)
#    
#    print "fileName :" ,_recorder.read_attribute("fileName").value
#    print "actuators : ", actuators
#    print "sensors :", sensors
#    print "timebases : ", timeBases 
#    print "trajectory :", trajectory 
#    print "trajectories :", trajectories 
#    print "integrationTimes : ", integrationTimes 
#
#    _scan.Clean()
#    _scan.actuatorsdelay = .2
#    _scan.actuators = actuators
#    _scan.sensors = sensors
#    _scan.timeBases = timeBases
#    _scan.integrationTimes = integrationTimes
#    _scan.trajectories = trajectories
#    _scan.Start()
#    try:
#        while _scan.state() not in [PyTango.DevState.ON, PyTango.DevState.ALARM]:
#            time.sleep(.1)
#    except KeyboardInterrupt:
#        _scan.abort()
#
#
def timescan(n,dt,timeBases=_timeBases):
    sensors = _sensors
    integrationTimes = numpy.ones((n+1)) * dt
    print(("sensors :", sensors))
    print(("timebases : ", timeBases))
    print(("integrationTimes : ", integrationTimes))
    time.sleep(1)
    
    _scan.Clean()
    _scan.sensors = sensors
    _scan.timeBases = timeBases
    _scan.integrationTimes = integrationTimes
    _scan.Start()

    try:
        while _scan.state() not in [PyTango.DevState.ON, PyTango.DevState.ALARM]:
            time.sleep(.1)
    except KeyboardInterrupt:
        _scan.abort()

def _goto(type, actuator, sensor):
        _scan.afterRunActionType = type
        _scan.afterRunActionSensor = sensor
        _scan.afterRunActionActuator = actuator
        _scan.ExecuteAction()
        try:
                while _scan.State() not in [PyTango.DevState.ON, PyTango.DevState.ALARM]:
                        time.sleep(1)
        except KeyboardInterrupt:
                _scan.abort()

def cen(sensor=0):
        print("goto center of mass")
        _goto(7, 0, sensor)


def pic(sensor=0):
        print("goto peak")
        _goto(3, 0,sensor)

#############################################################################################
#   UTIL
#############################################################################################

#def ct(t=1):
#  _start = 0
#  if _cpt1.state() in [PyTango.DevState.RUNNING]:
#     _cpt1.Stop()
#     _start = 1
#  _mode = _cpt1.read_attribute("continuous").value   
#  _cpt1.write_attribute("continuous",False)
#  _cpt1.write_attribute("integrationTime",t)
#  _cpt1.Start()
#  
#  while _cpt1.state() not in [PyTango.DevState.STANDBY, PyTango.DevState.ALARM]:
#    time.sleep(.1)
#    
#  print "cpt1 =", _cpt1.read_attribute("counter1").value
#  print "cpt2 =", _cpt1.read_attribute("counter2").value
#  print "monitor C03 =", _mon1.read_attribute("intensity").value
#  print "monitor C07 =", _mon2.read_attribute("intensity").value
#  
#  _nbfilter = _fastatt.vStatus0
#  if _nbfilter < 16 :
#    print "Attenuator (Al) = ", _nbfilter   
#  if _nbfilter > 35 :
#    print "Attenuator (Ag) = ", _nbfilter/64   
#
##  print "Attenuator (Al) = ", _att1.filtersCombination, " Coeff. = ", _att1.appliedAttenuation   
##  print "Attenuator (Ag) = ", _att2.filtersCombination, " Coeff. = ", _att2.appliedAttenuation
#  print "detc2 (Ag) =",  _detc2.detc
#  wh()   
#  
#  _cpt1.write_attribute("continuous",_mode)
#  if _start == 1:
#    _cpt1.Start()
#
#def shopen(shnb=0):
#  if shnb >= 0:
#    while _tdl.state() not in [PyTango._PyTango.DevState.OPEN] :
#      _tdl.open()
#      time.sleep(1)
#    print "TdL is open" 
#  if shnb >= 1:
#    while _obgx.state() not in [PyTango._PyTango.DevState.OPEN] :
#      _obgx.open()
#      time.sleep(1)
#    print "OBX 1 is open" 
#  if shnb >= 2:
#    while _obx.state() not in [PyTango._PyTango.DevState.OPEN] :
#      _obx.open()
#      time.sleep(1)
#    print "OBX 2 is open" 
#
#def shclose(shnb=0):
#  if shnb <= 0:
#    while _tdl.state() not in [PyTango._PyTango.DevState.CLOSE] :
#      _tdl.close()
#      time.sleep(1)
#    print "TdL is close" 
#  if shnb <= 1:
#    while _obgx.state() not in [PyTango._PyTango.DevState.CLOSE] :
#     _obgx.close()
#     time.sleep(.5)
#    print "OBX 1 is close" 
#  if shnb <= 2:
#    while _obx.state() not in [PyTango._PyTango.DevState.CLOSE] :
#      _obx.close()
#      time.sleep(.5)
#    print "OBX 2 is close"
# 
#def mv(motor, position):
#    att = PyTango.AttributeProxy(_movables[motor])
#    att.write(position)
#    try:
#      while att.state() not in [PyTango.DevState.STANDBY, PyTango.DevState.ON, PyTango.DevState.ALARM]:
#		 		 time.sleep(.3)
#				 print("%s = %f\r" % (motor, att.read().value))
#    except KeyboardInterrupt:
#      name = _movables[motor]
#      device = PyTango.DeviceProxy(name[:name.rindex('/')])
#      device.stop()
#      print ("%s = %f\r" % (motor, att.read().value))
#
#def mvr(motor, step):
#    att = PyTango.AttributeProxy(_movables[motor])
#    position = att.read().value
#    mv(motor, position + step)
#
#def mvYuhv(position):
#	mv('y1-base-uhv',position)
#	mv('y2-base-uhv',position)
#
#def mvZuhv(position):
#	mv('z1-base-uhv',position)
#	mv('z2-base-uhv',position)
#	mv('z3-base-uhv',position)
#
#def mvrYuhv(step):
#	mvr('y1-base-uhv',step)
#	mvr('y2-base-uhv',step)
#
#def mvrZuhv(step):
#	mvr('z1-base-uhv',step)
#	mvr('z2-base-uhv',step)
#	mvr('z3-base-uhv',step)
#      
#def wm(motor):
#    att = PyTango.AttributeProxy(_movables[motor])
#    print ("%s = %f\r" % (motor, att.read().value))
#
#def wh():
#	print ("%s = %f  %s = %f %s = %f \r" % ("H", PyTango.AttributeProxy(_movables["H"]).read().value , "K", PyTango.AttributeProxy(_movables["K"]).read().value ,"L ", PyTango.AttributeProxy(_movables["L"]).read().value))  
#	print ("%s = %f  %s = %f %s = %f %s = %f \r" % ("mu",PyTango.AttributeProxy(_movables["mu"]).read().value,"omega", PyTango.AttributeProxy(_movables["omega"]).read().value, "delta",PyTango.AttributeProxy(_movables["delta"]).read().value," gamma", PyTango.AttributeProxy(_movables["gamma"]).read().value))
#        
#def _compute_angles(h, k, l):
#    _hkl.h = h
#    _hkl.k = k
#    _hkl.l = l
#    _dif.simulated = False
#    time.sleep(0.5)
#    _dif.simulated = True
#    _hkl.Apply()
#    return _dif.angles
#
#def ca(h, k, l):
#    """
#    compute angles for a given h, k, l
#    """
#    solutions = _compute_angles(h, k, l)
#    for axis in _dif.AxesNames:
#        print "\t%s" % axis.replace("Axis", ""),
#    print
#    for solution in solutions:
#        print " %f %f %f %f" % (solution[1], solution[2], solution[3], solution[4])
#
#def br(h, k, l):
#    """
#    send the diffractometer to h, k, l
#    """
#    solutions = _compute_angles(h, k, l)
#    for axis in _dif.AxesNames:
#        print "\t%s" % axis.replace("Axis", ""),
#    print
#    for solution in solutions:
#        print " %f %f %f %f" % (solution[1], solution[2], solution[3], solution[4])
#        
#    _4axis.write_attributes([['mu-uhv',solution[1]],['omega-uhv',solution[2]],['delta-uhv',solution[3]],['gamma-uhv',solution[4]]])

#    try:
#      while _4axis.state() not in [PyTango.DevState.STANDBY, PyTango.DevState.ON, PyTango.DevState.ALARM]:
#          time.sleep(.2)
#          print " %f %f %f %f" % (_4axis.read_attribute('mu-uhv').value,_4axis.read_attribute('omega-uhv').value,_4axis.read_attribute('delta-uhv').value,_4axis.read_attribute('gamma-uhv').value)		 		 
#          time.sleep(.2)
#    except KeyboardInterrupt:
#        wh()
#
#def ci(mu, omega, delta, gamma):
#    """
#    compute h, k, l for a given diffractometer position.
#    """
#    old_auto_update = _dif.AutoUpdateFromProxies
#    _dif.AutoUpdateFromProxies = False
#    _dif.AxisMu = mu
#    _dif.AxisOmega = omega
#    _dif.AxisDelta = delta
#    _dif.AxisGamma = gamma
#    _dif.AutoUpdateFromProxies = old_auto_update
#    print "h: %f k:%f l:%f" % (_hkl.h, _hkl.k, _hkl.l)
#
#def fal(n):
#	if n > 31 : 
#		n = 31
#	if n < 0 : 
#		n = 0
#	_fastatt.vmanual = n
#	time.sleep(.5)
#	print " Attenuator (Al) = ", _fastatt.vstatus0 
#	
#def falp(s=1):
#	_fastatt.vmanual += s
#	time.sleep(.5)
#	print " Attenuator (Al) = ", _fastatt.vstatus0
#	
#def falm(s=1):
#	_fastatt.vmanual -= s
#	time.sleep(.5)
#	print " Attenuator (Al) = ", _fastatt.vstatus0
#	
#def fagp(s=1):
#	_fastatt.vmanual += s*64
#	time.sleep(.5)
#	print " Attenuator (Ag) = ", _fastatt.vstatus0/64 
#
#def fagm(s=1):
#	_fastatt.vmanual -= s*64
#	time.sleep(.5)
#	print " Attenuator (Ag) = ", _fastatt.vstatus0/64   
#		
#def fag(n):
#	if n > 15 :
#		n = 15
#	if n < 0 : 
#		n = 0
#	_fastatt.vmanual = n*64	
#	time.sleep(.5)
#	print " Attenuator (Ag) = ", _fastatt.vstatus0/64   
#	
#def fon(n=1):
#  if n==1 :
#     _fastatt.numjeu = 1
#     _fastatt.nbused = 15
#     print " SILVER automatic filters "
#  if n==2 :
#     _fastatt.numjeu = 0
#     _fastatt.nbused = 31
#     print " ALUMINIUM automatic filters "
##  else :
##     print "ERREUR"    
#  _fastatt.runningmode = 2
#
#def foff():
#  _fastatt.runningmode = 0
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
