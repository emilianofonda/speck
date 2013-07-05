import PyTango
from PyTango import DevState, DeviceProxy,DevFailed
from time import sleep

class camera:
	def __init__(self,label=""):
		self.label=label
		self.DP=DeviceProxy(label)
		__tmp=PyTango.AttributeInfoEx()
		__tmp.label="Basler"
		__tmp.unit="cts"
		__tmp.format="%9d"
		self.user_readconfig=[__tmp,]
		del __tmp
		return

	def init(self):
		try:
			self.DP.command_inout("Init")
		except:
			try:
				self.DP.command_inout("Init")
			except:
				pass
			sleep(1)
		return

	def reinit(self):
		return

	def __repr__(self):
      	 	repr=self.label+" intensity=%i\n"%self.read()
		return repr
					
      	def __call__(self,x=None):
      		print self.__repr__()
      		return self.state()						      

	def state(self):
		return self.DP.state()

	def status(self):
		return self.DP.status()
		
	def start(self,dt=1):
		if self.state()<>DevState.RUNNING:
			self.DP.command_inout("Start")
		return self.state()
		
	def stop(self):
		if self.state()==DevState.RUNNING:
			self.DP.command_inout("Stop")
		return self.state()
	
	def read_image(self, channels=None):
		mca=self.DP.image
		return mca

#	def read_mca(self, channels=None):
#		mca=self.DP.image
#		return mca

	def read(self):
		return [sum(sum(self.DP.image)),]
		
	def count(self,dt=1):
		"""Not working, this is a slave device"""
		return

		
		
