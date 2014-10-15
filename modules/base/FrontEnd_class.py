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
        self.StateTable = {
        60:["OPEN AUTO",DevState.OPEN],
        50:["OPEN",DevState.OPEN],
        47:["OPEN 1/2 AUTO",DevState.OPEN],
        45:["OPEN 1/2",DevState.OPEN],
        40:["CLOSE",DevState.CLOSE],
        30:["ALARM",DevState.ALARM],
        20:["DISABLE",DevState.DISABLE],
        10:["FAULT",DevState.FAULT],
        5:["UNKNOWN",DevState.UNKNOWN]
        }
		return

    def __str__(self):
            return "FRONT END"
		
    def __repr__(self):
            return self.label+" is %s"%(self.state())
					
    def subtype(self):
            return "FRONT END"

	def command(self,command):
		"Send the command to the device proxy. Command is a string. May return a value."
		return self.DP.command_inout(command)

	def state(self):
		"""Remark: FrontEnd state is UNKNOWN when an exception is returned to state query"""
		try:
            state = self.DP.state()
            state = self.StateValue()[1]
		except:
			print "Front End issue... "
			return DevState.UNKNOWN

    def status(self):
		try:
			ll = self.command("Status")
            ll += "\n" + "State Description is:" + self.StateValue()[0] + "\n"
		except:
			return "Unknown: device error."

	def init(self):
		return self.command("Init")
		
	def interlock(self):
		try:	
			il=self.DP.read_attribute("frontEndStateValue").value
		except:
		    print "Warning: cannot read Front End state Value."
		if(il in [5,10,20,30,70]):
			return True
		else:
			return False
	
	def StateValue(self):
		try:	
			il=self.DP.read_attribute("frontEndStateValue").value
		except:
			print "Warning: cannot read Front End state Value."
            return self.StateTable[5]
		if il in self.StateTable.keys():
            return self.StateTable[il]
        else:
            raise Exception("frontEndStateValue not recognized! Call Local Contact.")
			
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


