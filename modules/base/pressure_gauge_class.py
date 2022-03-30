from __future__ import print_function
from builtins import object
from PyTango import DeviceProxy,DevState
from time import sleep

class pressure_gauge(object):
	def __init__(self,tangoname,deadtime=0.5):
		try:
			self.DP=DeviceProxy(tangoname)
		except:
			print(tangoname," does not exist.")
		self.label=tangoname
		self.deadtime=deadtime
		return
		
	def __str__(self):
		return "temperature_gauge"
	
	def __repr__(self):
		return self.label, "is at ",self.pos()

	def command(self,commandstring):
		return self.DP.command_inout(commandstring)
	
	def state(self):
		##the following line is a workaround for a device bug: the correct state is returned after a pressure reading
		tmp=self.p()
		return self.command("State")
		
	def status(self):
		##the following line is a workaround for a device bug: the correct state is returned after a pressure reading
		tmp=self.p()
		return self.command("Status")
	
	def OFF(self):
		self.command("OFF")
		sleep(self.deadtime)
		return self.state()

	def ON(self):
		self.command("ON")
		sleep(self.deadtime)
		return self.state()
	
	def p(self):
		return self.pressure()

	def pressure(self):
		return self.DP.read_attribute("pressure").value
	
	def pos(self,dest=None):
		"""As a standard, the pressure is returned as position. For absurd you can do a move on it:
		   without any effect of course!"""
		return self.p()

