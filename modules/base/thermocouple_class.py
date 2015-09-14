from PyTango import DeviceProxy,DevState
from time import sleep

class temperature_gauge:
	def __init__(self,tangoname,deadtime=0.5):
		try:
			self.DP=DeviceProxy(tangoname)
		except:
			print tangoname," does not exist."
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
	
	def t(self):
		return self.temperature()

	def temperature(self):
		return self.DP.read_attribute("temperature").value
	
	def pos(self,dest=None):
		"""Returns the temperature. Can be used in a move command... without effect, of course"""
		return self.t()

