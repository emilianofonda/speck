import PyTango
from PyTango import DeviceProxy, DevState
import counter_class
from time import sleep,time
import exceptions

class xbpm:
	"""This class is designed for the Samba implementation of the Oxford Split Ion Chamber. 
	It uses two counters, so you just use read or pos if you want to start and then read 
	or just read the counters."""
	def __init__(self,countername=None,ch1=None,ch2=None,slope=1.,offset=0.,verbose=False):
		"""xbpm class: first draft. xbpm.pos(t) returns the position after counting for t seconds"""
		self.counter=counter_class.counter(countername)
		self.ch1=ch1
		self.ch2=ch2
		self.offset=offset
		self.slope=slope
		self.verbose=verbose
		return

	def read(self):
		"""Returns the position [c1-c2]/[c1+c2]*slope+offset without starting the counters"""
		c=self.counter.read()
		c1=float(c[self.ch1])
		c2=float(c[self.ch2])
		try:
			p=((c1-c2)/(c1+c2))*self.slope+self.offset
		except exceptions.ZeroDivisionError, tmp:
			if self.verbose: print "Zero Intensity in the xbpm channels!!!!!"
			return 0.
		return p

	def pos(self,t=1.):
		"""Returns the position [c1-c2]/[c1+c2]*slope+offset"""
		c=self.counter.count(t)
		c1=float(c[self.ch1])
		c2=float(c[self.ch2])
		try:
			p=((c1-c2)/(c1+c2))*self.slope+self.offset
		except exceptions.ZeroDivisionError, tmp:
			if self.verbose: print "Zero Intensity in the xbpm channels!!!!!"
			return 0.
		return p

class qbpm:
	"""This class interface with the front end XBPMs, known as QBPMs. The interface is still evolving on the device side... be carefull"""
	def __init__(self,device_name="",deadtime=0.025,delay=0.,timeout=0.):
		self.label=device_name
		self.DP=DeviceProxy(self.label)
		self.deadtime=deadtime
		self.timeout=timeout
		self.att_pos1=self.DP.read_attribute("verticalPosition1")
		self.att_pos2=self.DP.read_attribute("verticalPosition2")
		#self.att_version=self.DP.read_attribute("version")
		try:
			self.att_errorAttributeReport=self.DP.read_attribute("errorAttributeReport")
		except:
			self.att_errorAttributeReport=None
		try:
			self.att_errorCommandReport=self.DP.read_attribute("errorCommandReport")
		except:
			self.att_errorCommandReport=None
		return
		
        def __str__(self):
                return "QBPM"

        def __repr__(self):
                return self.label+" at %10.6f"%(self.pos())

        def subtype(self):
                return "QBPM"

        def state(self):
                """No arguments, return the state as a string"""
                return self.DP.state()

        def status(self):
                """No arguments, return the status as a string"""
                #State bug workaround!
                self.state()
                return self.DP.status()

        def stop(self):
                """Just do nothing..."""
                return

        def command(self,cmdstr,arg=""):
                "For adventurous users only: send a command_inout string, optionally with arguments"
                if(arg==""):
                        return self.DP.command_inout(cmdstr)
                else:
                        return self.DP.command_inout(cmdstr,arg)
                return
	
	def init(self):
                self.state()
                self.command("Init")
		return

	#def initDevice(self):
	#	self.state()
	#	self.command("InitDevice")
	#	return

	def read(self,dest=None):
		"""Returns the average position: mean(vertPos1,vertPos2)"""
		return self.pos(dest)
	
	def pos(self,dest=None):
		"""Returns the average position: mean(vertPos1,vertPos2)"""
		__p1,__p2=self.DP.read_attributes(["verticalPosition1","verticalPosition2"])
		return 0.5*(__p1.value+__p2.value)

	def delta(self):
		"""Returns the delta=Pos2-Pos1, which gives an error estimate"""
		__p1,__p2=self.DP.read_attributes(["verticalPosition1","verticalPosition2"])
		return (__p2.value-__p1.value)

	def pos1():
		"""Returns vertical pos1"""
		return self.DP.read_attribute("verticalPosition1").value

	def pos2():
		"""Returns vertical pos2"""
		return self.DP.read_attribute("verticalPosition2").value


