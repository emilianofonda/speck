#Simple object for input output through the serial line
#Tested only with the ACE APD

from PyTango import DeviceProxy
from time import sleep

class tango_serial:
	def __init__(self,label="",EndOfLine=[10,13],space=32,deadtime=0.1):
		self.DP=DeviceProxy(label)
		self.label=label
		self.space=32
		self.EndOfLine=EndOfLine
		self.deadtime=deadtime
		return
		
	def state(self):
		return self.DP.state()
		
	def status(self):
		return self.DP.status()
		
	def init(self):
		return self.DP.init()
		
	def writeread(self,CCS):
		self.write(CCS)
		sleep(self.deadtime)
		return self.read()
		
	def write(self,CCS):
		#Clean line before write
		self.read()
		CCS_morse=[]
		for i in CCS:
			if i<>" ":
				CCS_morse.append(ord(i))
			else:
				CCS_morse.append(32)
		charsent=self.DP.command_inout("DevSerWriteChar",CCS_morse+self.EndOfLine)
		if charsent<>len(CCS_morse+self.EndOfLine): 
			print "Serial line ",self.label," error writing data."
			print "Number of bytes sent is not corresponding to string length!"
		return

	def read(self):
		return self.DP.command_inout("DevSerReadRaw").rstrip()

