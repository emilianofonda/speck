#24/04/2007 EF:written from scratch
#A wait loop should be inserted in the extract/insert functions to wait for a change in the set values.
#Timeout should be introduced in the init function to this purpose.


import PyTango
from PyTango import DeviceProxy, DevState
from time import sleep
from numpy import nan

class absorbing_system:
        def __init__(self,tangoname,deadtime=0.1):
                try:
                        self.DP=DeviceProxy(tangoname)
                except:
                        print "Wrong  attenuator --> ",tangoname," not defined"
                        return
                self.deadtime=deadtime
                self.label=tangoname
		self.el0="noElementInserted"
		self.el1="firstElementInserted"
		self.el2="secondElementInserted"
                return

	def command(self,command):
                "Send the command to the device proxy. Command is a string. May return a value."
                return self.DP.command_inout(command)

	def state(self):
	        return self.command("State")

	def status(self):
	        return self.command("Status")
							
	def set(self,elements=[]):
		if (elements==[]):
			elements=[self.DP.read_attribute("noElementInserted").value,self.DP.read_attribute("firstElementInserted").value,self.DP.read_attribute("secondElementInserted").value]
			return elements
		else:
			try:
				self.DP.write_attributes([self.el0,elements[0],self.el1,elements[1],self.el2,elements[2]])
			except PyTango.DevFailed, tmp:
				print type(tmp)
				print "Arguments must be of the type [True/False,True/False,True/False]\n"
				print elements,"\n"
				raise tmp
		return
	
	def extract(self):
		self.set([True,False,False])
		return

	def insert0(self):
		self.extract()
		return

	def insert1(self):
		self.set([False,True,False])
		return	

	def insert2(self):
		self.set([False,False,True])
		return

