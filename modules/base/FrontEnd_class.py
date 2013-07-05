#Made on 17/10/2007

from PyTango import DeviceProxy, DevState
from time import sleep
import time as wtime

class FrontEnd:
	"""Functions defined are state, status, command, close, open, timeout. Attributes: DP (the device proxy) and deadtime. 
	Deadtime is used for slowing down the polling and does not belong to the device as timeout."""
	def __init__(self,tangoname,deadtime=0.1):
		try:
			self.DP=DeviceProxy(tangoname)
		except:
			print "Wrong valve name--> ",tangoname," not defined"
			return
		self.deadtime=deadtime
		self.label=tangoname
		self.timeout=10
		return

        def __str__(self):
                return "FRONT END"
			
        def __repr__(self):
                return self.label+" is %s"%(self.state())
						
        def subtype(self):
                return "FRONT END"
									
########def reconnect(self):
########	__error=False
########	for i in range(5):
########		try:	
########			self.initDevice()
########			sleep(5.)
########			__error=False
########			break
########		except Exception, tmp:
########			__error=True
########			print self.label+" initDevice gives error... trying again %1i/5"%(i)
########			sleep(5.)
########	if __error:
########		raise tmp
########	__error=False
########	for i in range(5):
########		try:	
########			self.init()
########			sleep(5.)
########			__error=False
########			break
########		except Exception, tmp:
########			__error=True
########			print self.label+" init gives error... trying again %1i/5"%(i)
########			sleep(5.)
########	if __error:
########		raise tmp
########	return


	def command(self,command):
		"Send the command to the device proxy. Command is a string. May return a value."
		return self.DP.command_inout(command)

	def state(self):
		"""Remark: FrontEnd state is UNKNOWN when an exception is returned to state query"""
		try:
			return self.DP.state()
		except:
			print "Front End issue... "
			return DevState.UNKNOWN
		
	def init(self):
		return self.command("Init")

	#def initDevice(self):
	#	return self.command("InitDevice")
		
	def interlock(self):
		#frontEndStateValue: state value of the front end : 
		#1 : Front End Fault
		#2 : Front End Closed, Front End interlocked 
		#3 : Front End Closed on BeamLine interlock ou interlock PSS 
		#4 : Front End Closed, open is possible 
		#5 : Front End Opened ( normal, by user ) 
		#6 : Front End Opened ( automatic mode, after commissionning ) 
		#7 : Unknwon state
		for i in range(3):
			try:	
				il=self.DP.read_attribute("frontEndStateValue").value
				break
			except:
				print "Warning: cannot read Front End state Value."
				#self.reconnect()
				sleep(1.)
		if(il in [1,2,3,7]):
			return True
		else:
			return False
	
	def StateValue(self):
		legenda=[\
		"Front End Fault",\
		"Front End Closed, Front End interlocked",\
		"Front End Closed on BeamLine interlock ou interlock PSS",\
		"Front End Closed, open is possible",\
		"Front End Opened ( normal, by user )",\
		"Front End Opened ( automatic mode, after commissionning )",\
		"Unknwon state"]
		il=6
		try:	
			il=self.DP.read_attribute("frontEndStateValue").value
		except:
			print "Warning: cannot read Front End state Value."
		if(il in range(7)):
			il=[il,legenda[il-1]]
		else:
			il=[il,"None"]
		return il

	def status(self):
		try:
			return self.command("Status")
		except:
			return "Unknown"
			
	def close(self):
		try:
			self.command("Close")
		except:
			print "Cannot close"
		t=0
		while(self.state()<>DevState.CLOSE and t<=self.timeout):
			sleep(self.deadtime)
			t+=self.deadtime
		return self.state()

	def open(self):
		try:
			self.command("Open")
		except:
			print "Cannot open"
		t=0.
		while(self.state()<>DevState.OPEN and t<=self.timeout):
			sleep(self.deadtime)
			t+=self.deadtime
		return self.state()


