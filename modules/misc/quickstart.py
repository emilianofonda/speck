from PyTango import DevState, DeviceProxy
from motor_class import motor
import time as pytime
from time import sleep, time
import os
def quickstart(prefix="",folder="",qm_proxy="",datarecorder_proxy="",cam_amplitude_motor=None,cam_rotation_motor=None,save=True,wait=True,timeout=10):
	"""quickstart does the following:
	verify the parameters coherence (speed and amplitude) and 
	set the appropriate values in the quick manager
	starts the quickexafs manager acquisition.
	prefix is the beginning of the file name
	if folder is not defined is created with the name of year/yyyymmddHHMM_prefix"""
	
	qm=DeviceProxy(qm_proxy)
	dtr=DeviceProxy(datarecorder_proxy)
	qm.SavingNexusFile=save
	qm.set_timeout_millis(int(timeout*1000))
	print "Parametrs for scan are:"
	print "Manager says: speed=%6.3f cam_amplitude=%6.3f"%(qm.oscillationVelocity,qm.oscillationAmplitude)
	print "Motors   say: speed=%6.3f cam_amplitude=%6.3f"%(cam_rotation_motor.speed(),cam_amplitude_motor.pos())
	print "Sending motors values to Manager...",
	qm.oscillationVelocity=cam_rotation_motor.speed()
	qm.oscillationAmplitude=cam_amplitude_motor.pos()
	sleep(0.1)
	print "OK\n"
	print "Manager says: speed=%6.3f cam_amplitude=%6.3f\n"%(qm.oscillationVelocity,qm.oscillationAmplitude)
	print "Setting file name and folder in datarecorder...",
	if prefix<>"":
		dtr.fileName=prefix+"_[n]"
	else:
		dtr.fileName="qexafs_data_"+pytime.strftime("20%2y%2m%2d%2H%2M",pytime.localtime())+"_[n]"
	year=pytime.strftime("20%2y",pytime.localtime())
	if folder<>"":
		dtr.subDirectory=year+os.sep+folder
	else:
		__subName=year+os.sep+pytime.strftime("20%2y%2m%2d",pytime.localtime())+\
		os.sep+pytime.strftime("20%2y%2m%2d%2H%2M",pytime.localtime())
		if prefix<>"":
			__subName+="_"+prefix
		dtr.subDirectory=__subName
	print "OK"
	print dtr.subDirectory
	#
	print "Let's rock...",
	qm.Start()
	t0=time()
	while(qm.state()<>DevState.RUNNING and time()-t0<=timeout):
		sleep(1)
	print "rocking!"
	return
	#Following code is really old
	#NI6602=DeviceProxy("tmp/TEST-QEXAFS/cpt.2")
	#SAI=DeviceProxy("tmp/TEST-QEXAFS/sai.1")
	#cb=DeviceProxy("d09-1-c00/ca/bai.1131-mos.1-cb")
	#qm.Stop()
	#q3_delta=motor("d09-1-c04/op/mono3-mt_rx.1")
	#q3_encoder=motor("d09-1-c04/op/mono3-cd_rx.1")
	#q3_delta.stop()
	#q3_delta.mo()
	#sleep(1.)
	#print "Encoder value is: %8.6f"%q3_encoder.pos(), "verify correspondence with deltaTheta0"
	#cb.ExecLowLevelCmd("SHA")
	##q3_delta.DP.command_inout_asynch("MotorON",0)
	#q3_delta.DP.command_inout_asynch("MotorON")
	#sleep(0.02)
	#try:
	#	qm.Start()
	#except:
	#	print "Error"
	#print "Encoder value captured by qmanager is %8.6f"%(qm.deltaTheta0)
	#while(NI6602.state()<>DevState.RUNNING and SAI.state()<>DevState.RUNNING):
	#	sleep(0.01)
	#q3_delta.sh()
	#cb.ExecLowLevelCmd("SHA")
	#cb.ExecLowLevelCmd("JGA=-2036;BGA")
	#return 

def quickstop(qm_proxy="",wait=True,timeout=10,sleeper_time=3):
	qm=DeviceProxy(qm_proxy)
	qm.Stop()
	if not(wait):
		return
	sleep(sleeper_time)
	t0=time()
	while(time()-t0<timeout and qm.state()<>DevState.STANDBY):
		sleep(1)
	sleep(sleeper_time)
	while(qm.state()==DevState.ALARM and "PROCESS REMAINING FILES" in qm.status()):
		sleep(1)
	return qm.state()



