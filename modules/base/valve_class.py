#Last bug fix on 8/10/2007

from PyTango import DeviceProxy, DevState
from time import sleep

class valve:
	"""Functions defined are state, status, command, close, open, timeout. Attributes: DP (the device proxy) and deadtime. """
	"""Deadtime is used for slowing down the polling and does not belong to the device as timeout."""
	def __init__(self,tangoname,deadtime=0.1):
		try:
			self.DP=DeviceProxy(tangoname)
		except:
			print "Wrong valve name--> ",tangoname," not defined"
			return
		self.deadtime=deadtime
		self.label=tangoname
		try:
			self.timeout=self.timeout_device()
		except:
			self.timeout=10
		return

	def __str__(self):
                return "VALVE"
			
        def __repr__(self):
                return self.label+" is %s"%(self.state())
						
        def subtype(self):
                return "VACUUM"

	def command(self,command):
		"Send the command to the device proxy. Command is a string. May return a value."
		return self.DP.command_inout(command)

	def state(self):
		return self.command("State")

	def status(self):
		return self.command("Status")
			
	def close(self):
		self.command("Close")
		t=0
		while(self.state()<>DevState.CLOSE and t<=self.timeout):
			sleep(self.deadtime)
			t+=self.deadtime
		#while(self.state()==DevState.MOVING):
		#	sleep(self.deadtime)
		return self.state()

	def open(self):
		self.command("Open")
		t=0.
		while(self.state()<>DevState.OPEN and t<=self.timeout):
			sleep(self.deadtime)
			t+=self.deadtime
		#while(self.state()==DevState.MOVING):
		#	sleep(self.deadtime)
		return self.state()

	def timeout_device(self,tout=None):
		"With no argument returns the timeout, with argument set it to the value. Timeout cannot be set to 0 for a valve."
		if(tout==None): 
			return self.DP.read_attribute("maxTime")
		self.DP.write_attribute("maxTime",tout)
		sleep(self.deadtime)
		return self.timeout_device()
		
