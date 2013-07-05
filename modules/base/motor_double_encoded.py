from string import lower
import PyTango
from PyTango import DeviceProxy, DevState
from time import sleep,time
import exceptions
from exceptions import KeyboardInterrupt,SystemExit,SyntaxError, NotImplementedError, Exception
from numpy import mean,std,mod
import thread
from motor_class import motor

		
class motor_double_encoded(motor):

	def __init__(self,motorname,double_encoder,deadtime=.025,delay=0.,timeout=0.2,verbose=True):
		try:
			self.DP=DeviceProxy(motorname)
			self.encoder2=motor(double_encoder)
		except PyTango.DevFailed, tmp:
			print "Error when defining :",motorname," as a motor.\n"
			print tmp.args
			raise tmp
		self.deadtime=deadtime
		self.delay=delay
		self.timeout=timeout
		self.label=motorname
		self.att_pos="position"
		self.att_speed="velocity"
		self.att_accel="acceleration"
		self.att_decel="deceleration"
		self.att_offset="offset"
		self.verbose=verbose
		return


	def DefinePosition(self,value=None):
		"""Set the motor position to the new proposed value. There is no default value, but with no argument it returns the current position."""
		if (value==None): return self.pos()
		try:
			value=float(value)		
		except:
			print "Position value is not valid."
			raise SyntaxError
		if (self.state()==DevState.OFF):
			raise Exception("Cannot initialize on a motor that is OFF!")
		try:
			value=value-self.encoder2.pos()
			#self.command("DefinePosition","%f"%(value))
			self.command("DefinePosition",value)
		except PyTango.DevFailed, tmp:
				raise tmp
		except Exception, tmp:
			print "Cannot define position for an unknown reason"
			raise tmp
		return self.pos()
		

	def pos(self,dest=None,wait=True):
		"""No help """
		if(dest==None):
			dest1=self.DP.read_attribute("position").value
			dest2=self.encoder2.pos()
			return dest1+dest2
		else:
			dest0=dest
			dest=float(dest)-float(self.encoder2.pos())
		try:
			#state bug workaround
			st=self.state()
			if(st==DevState.OFF): 
				raise Exception("Motor is OFF! Use motor.sh() to power up.")
			self.DP.write_attribute(self.att_pos,dest)
			if(not(wait)):
				return dest0
			t=0.
	   		if self.state()<>DevState.MOVING:
				while((self.state()<>DevState.MOVING) and (t<self.timeout)):
					sleep(self.deadtime)
					t+=self.deadtime
			while(self.state()==DevState.MOVING):
				if self.verbose: print "%8.6f\r"%(self.pos()),
				sleep(self.deadtime)
			sleep(self.delay)
			if self.verbose: print "\n"
			return self.pos()
		
		except (KeyboardInterrupt,SystemExit), tmp:
			self.stop()
			raise tmp
		except PyTango.DevFailed, tmp:
			self.stop()
			raise tmp
	
class motor_separate_encoder(motor):

	def __init__(self,motorname,encodername,deadtime=.025,delay=0.,timeout=0.2,verbose=True):
		try:
			self.DP=DeviceProxy(motorname)
			self.encoder=motor(encodername)
		except PyTango.DevFailed, tmp:
			print "Error when defining :",motorname," as a motor.\n"
			print tmp.args
			raise tmp
		self.deadtime=deadtime
		self.delay=delay
		self.timeout=timeout
		self.label=motorname
		self.att_pos="position"
		self.att_speed="velocity"
		self.att_accel="acceleration"
		self.att_decel="deceleration"
		self.att_offset="offset"
		self.verbose=verbose
		return


	def DefinePosition(self,value=None):
		"""Set the motor position to the new proposed value. There is no default value, but with no argument it returns the current position."""
		if (value==None): return self.pos()
		try:
			value=float(value)		
		except:
			print "Position value is not valid."
			raise SyntaxError
		if (self.state()==DevState.OFF):
			raise Exception("Cannot initialize on a motor that is OFF!")
		try:
			self.encoder.command("DefinePosition",value)
			sleep(0.3)
		except PyTango.DevFailed, tmp:
				raise tmp
		except:
			print "Cannot define position for an unknown reason"
			raise NotImplementedError
		return self.encoder.pos()
		

	def pos(self,dest=None,wait=True):
		"""No help """
		if(dest==None):
			dest=self.encoder.pos()
			return dest
		else:
			dest0=dest
			dest=self.DP.read_attribute("position").value
			dest+=dest0-self.encoder.pos()
		try:
			#state bug workaround
			st=self.state()
			if(st==DevState.OFF): 
				raise Exception("Motor is OFF! Use motor.sh() to power up.")
			self.DP.write_attribute(self.att_pos,dest)
			if(not(wait)):
				return dest
			t=0.
	   		if self.state()<>DevState.MOVING:
				while((self.state()<>DevState.MOVING) and (t<self.timeout)):
					sleep(self.deadtime)
					t+=self.deadtime
			while(self.state()==DevState.MOVING):
				if self.verbose: print "%8.6f\r"%(self.pos()),
				sleep(self.deadtime)
			sleep(self.delay)
			if self.verbose: print "\n"
			return self.pos()
		
		except (KeyboardInterrupt,SystemExit), tmp:
			self.stop()
			raise tmp
		except PyTango.DevFailed, tmp:
			self.stop()
			raise tmp
	

