#Last update 4/10/2007  EF

import PyTango
from PyTango import DevState, DeviceProxy
from time import sleep
from numpy import *
import exceptions
from exceptions import NotImplementedError

class mirror:
	"""Use this class to access properly to a mirror device based on a one motor bender plus a tpp. Please never access directly to motors one by one."""
	def __init__(self,mirrorname,deadtime=.1,timeout=3.):
		self.DP=DeviceProxy(mirrorname)
		self.label=mirrorname
		self.DP_bender=DeviceProxy(mirrorname+"-COURB")
		self.DP_tpp=DeviceProxy(mirrorname+"-tpp")
		self.DP_c1=DeviceProxy(mirrorname+"-mt_c.1")
		self.DP_t1z=DeviceProxy(mirrorname+"-mt_t1")
		self.DP_t2z=DeviceProxy(mirrorname+"-mt_t2")
		self.DP_t3z=DeviceProxy(mirrorname+"-mt_t3")
	
		self.deadtime=deadtime
		self.timeout=timeout
		self.name=mirrorname
		#
		tmp=[self.DP.state(),self.DP_bender.state()]
		if tmp[0]==DevState.FAULT:
			print self.label+": Mirror device is in FAULT state. Trying to fix this"
			try:
				self.DP.Init()
			except:
				print self.label+": error while trying to init mirror that was in fault!"
				print "Keep going..."
			t0=time()
			while(not (self.DP.state() in [DevState.STANDBY,DevState.OFF,DevState.ALARM]) and time()-t0<=self.timeout):
				sleep(self.deadtime)
		#
		self.att_theta=self.DP.read_attribute("theta")
		try:
			self.att_q=self.DP.read_attribute("qDistance")
		except PyTango.DevFailed, tmp:
			if(tmp.args[0].reason=='API_EmptyDeviceAttribute'):
				#print "Collimating mirror"
				self.att_p=self.DP.read_attribute("pDistance")
				self.att_q=self.att_p
				self.att_q.value=inf
				self.att_q.name="qDistance"
		except:
			print "Unknown error reading qDistance"
			raise NotImplementedError
		try:
			self.att_p=self.DP.read_attribute("pDistance")
		except PyTango.DevFailed, tmp:
			if(tmp.args[0].reason=='API_EmptyDeviceAttribute'):
				#print "Focusing mirror"
				self.att_q=self.DP.read_attribute("qDistance")
				self.att_p=self.att_q
				self.att_p.value=inf
				self.att_p.name="pDistance"
		except:
			print "Unknown error reading pDistance"
			raise NotImplementedError
		self.att_nobender=self.DP.read_attribute("isBenderLess")
		self.att_curvature=self.DP.read_attribute("curvature")
		self.att_zC=self.DP_tpp.read_attribute("zC")
		self.att_pitch=self.DP_tpp.read_attribute("pitch")
		self.att_roll=self.DP_tpp.read_attribute("roll")
		self.att_t1z=self.DP_tpp.read_attribute("t1z")
		self.att_t2z=self.DP_tpp.read_attribute("t2z")
		self.att_t3z=self.DP_tpp.read_attribute("t3z")
		return
		
	def stop(self):
		"""Stop Generic Mirror Device, TPP and MT_C."""
		try:
			self.DP.command_inout("Stop")
		except:
			print "Stop failed on GenericMirrorDevice"
			try:
				self.DP_tpp.command_inout("Stop")
			except:
				print "Stop failed on TPP. Panic!"
				return 
			try:
				self.DP_c1.command_inout("Stop")
			except:
				print "Stop failed on MT_C. Panic!"
				return 
		return 

	def mo(self):
		"""Motors OFF."""
		if(self.stop()):
			print "TPP stopped, as a general remark: next time try to shutdown motors yourself, please.\n"
			try:
				self.DP_c1.command_inout("MotorOFF")
			except:
				print self.mirrorname,": ","Cannot switch off C1. Panic!"
			try:
				self.DP_t1z.command_inout("MotorOFF")
			except:
				print self.mirrorname,": ";"Cannot switch off T1Z. Panic!"
			try:
				self.DP_t2z.command_inout("MotorOFF")
			except:
				print self.mirrorname,": ";"Cannot switch off T2Z. Panic!"
			try:
				self.DP_t3z.command_inout("MotorOFF")
			except:
				print self.mirrorname,": ";"Cannot switch off T3Z. Panic!"
		return

	def sh(self):
		"""Motors ON."""
		try:
			self.DP_c1.command_inout("MotorON")
		except:
			print self.mirrorname,": ","Cannot switch on C1. Panic!"
		try:
			self.DP_t1z.command_inout("MotorON")
		except:
			print self.mirrorname,": ";"Cannot switch on T1Z. Panic!"
		try:
			self.DP_t2z.command_inout("MotorON")
		except:
			print self.mirrorname,": ";"Cannot switch on T2Z. Panic!"
		try:
			self.DP_t3z.command_inout("MotorON")
		except:
			print self.mirrorname,": ";"Cannot switch on T3Z. Panic!"
		return

	def init(self):
		"""Init devices."""
		try:
			self.DP_c1.command_inout("Init")
		except:
			print self.mirrorname,": ","Cannot Init C1. Panic!"
		try:
			self.DP_t1z.command_inout("Init")
		except:
			print self.mirrorname,": ";"Cannot Init T1Z. Panic!"
		try:
			self.DP_t2z.command_inout("Init")
		except:
			print self.mirrorname,": ";"Cannot Init T2Z. Panic!"
		try:
			self.DP_t3z.command_inout("Init")
		except:
			print self.mirrorname,": ";"Cannot Init T3Z. Panic!"
		return


	def state(self):
                """No arguments, return the state as a string"""
		return self.DP.command_inout("State")

	def status(self):
                """No arguments, return the status as a string"""
		return self.DP.command_inout("Status")

	def tpp_state(self):
                """No arguments, return the state as a string"""
		return self.DP_tpp.command_inout("State")

	def tpp_status(self):
                """No arguments, return the status as a string"""
		return self.DP_tpp.command_inout("Status")
		
	def bender_state(self):
                """No arguments, return the state as a string"""
		return self.DP_bender.command_inout("State")

	def bender_status(self):
                """No arguments, return the status as a string"""
		return self.DP_bender.command_inout("Status")

	def theta(self,dest=inf): 
		"""With no arguments returns the position. 
                   With a value, go to the position and wait for the pseudo motor to stop, 
                   then it returns the position."""
		if(dest==inf):
			self.att_theta=self.DP.read_attribute("theta")
			return self.att_theta.value
		else:
			self.state()
			try:	
				self.DP.write_attribute("theta",dest)
				sleep(self.deadtime)
				while(self.state()==PyTango.DevState.MOVING):
					sleep(self.deadtime)
				return self.theta()
			except (KeyboardInterrupt,SystemExit), tmp:
				self.stop()
				raise tmp
			except PyTango.DevFailed, tmp:
				raise tmp
			except PyTango.DevError, tmp:
				raise tmp
			except :
				print "Unknown Error"
				self.stop()
				raise NotImplementedError

			
	def zC(self,dest=inf):
		"""With no arguments returns the position. 
                   With a value, go to the position and wait for the pseudo motor to stop, 
                   then it returns the position."""
		if(dest==inf):
			self.att_zC=self.DP_tpp.read_attribute("zC")
			return self.att_zC.value
		else:
			self.state()
			try:
				self.DP_tpp.write_attribute("zC",dest)
				sleep(self.deadtime)
				while(self.tpp_state()==PyTango.DevState.MOVING):
					sleep(self.deadtime)
				return self.zC()
			except (KeyboardInterrupt,SystemExit), tmp:
				self.stop()
				raise tmp
			except PyTango.DevFailed, tmp:
				raise tmp
			except PyTango.DevError, tmp:
				raise tmp
			except :
				print "Unknown Error"
				self.stop()
				raise NotImplementedError
						
	def roll(self,dest=inf):
		"""With no arguments returns the position. 
                   With a value, go to the position and wait for the pseudo motor to stop, 
                   then it returns the position."""
		if(dest==inf):
			self.att_roll=self.DP_tpp.read_attribute("roll")
			return self.att_roll.value
		else:
			self.state()
			try:
				self.DP_tpp.write_attribute("roll",dest)
				sleep(self.deadtime)
				while(self.tpp_state()==PyTango.DevState.MOVING):
					sleep(self.deadtime)
				return self.roll()
			except (KeyboardInterrupt,SystemExit), tmp:
				self.stop()
				raise tmp
			except PyTango.DevFailed, tmp:
				raise tmp
			except PyTango.DevError, tmp:
				raise tmp
			except :
				print "Unknown Error"
				self.stop()
				raise NotImplementedError

	def pitch(self,dest=inf):
		"""With no arguments returns the position. 
                   With a value, go to the position and wait for the pseudo motor to stop, 
                   then it returns the position."""
		if(dest==inf):
			self.att_pitch=self.DP_tpp.read_attribute("pitch")
			return self.att_pitch.value
		else:
			self.state()
			try:
				self.DP_tpp.write_attribute("pitch",dest)
				sleep(self.deadtime)
				while(self.tpp_state()==PyTango.DevState.MOVING):
					sleep(self.deadtime)
				return self.pitch()
			except (KeyboardInterrupt,SystemExit), tmp:
				self.stop()
				raise tmp
			except PyTango.DevFailed, tmp:
				raise tmp
			except PyTango.DevError, tmp:
				raise tmp
			except :
				print "Unknown Error"
				self.stop()
				raise NotImplementedError

	def t1z(self,dest=inf):
		"Set t1z through the tpp device or just read it when no argument is given."
		if(dest==inf):
			self.att_t1z=self.DP_tpp.read_attribute("t1z")
			return self.att_t1z.value
		try:
			self.DP_tpp.write_attribute("t1z",dest)
			while(self.tpp_state()==DevState.MOVING):
				sleep(self.deadtime)
			return self.t1z()
		except (KeyboardInterrupt,SystemExit), tmp:
			self.stop()
			print self.t1z()
			raise tmp
		except PyTango.DevFailed, tmp:
			raise tmp
		except PyTango.DevError, tmp:
			raise tmp
		except :
			print "Unknown Error"
			self.stop()
			raise NotImplementedError

	def t2z(self,dest=inf):
		"Set t2z through the tpp device or just read it when no argument is given."
		if(dest==inf):
			self.att_t2z=self.DP_tpp.read_attribute("t2z")
			return self.att_t2z.value
		try:
			self.DP_tpp.write_attribute("t2z",dest)
			while(self.tpp_state()==DevState.MOVING):
				sleep(self.deadtime)
			return self.t2z()
		except (KeyboardInterrupt,SystemExit), tmp:
			self.stop()
			print self.t2z()
			raise tmp
		except PyTango.DevFailed, tmp:
			raise tmp
		except PyTango.DevError, tmp:
			raise tmp
		except :
			print "Unknown Error"
			self.stop()
			raise NotImplementedError

	def t3z(self,dest=inf):
		"Set t3z through the tpp device or just read it when no argument is given."
		if(dest==inf):
			self.att_t3z=self.DP_tpp.read_attribute("t3z")
			return self.att_t3z.value
		try:
			self.DP_tpp.write_attribute("t3z",dest)
			while(self.tpp_state()==DevState.MOVING):
				sleep(self.deadtime)
			return self.t3z()
		except (KeyboardInterrupt,SystemExit), tmp:
			self.stop()
			raise tmp
		except PyTango.DevFailed, tmp:
			raise tmp
		except PyTango.DevError, tmp:
			raise tmp
		except :
			print "Unknown Error"
			self.stop()
			raise NotImplementedError

	def pos(self):
		"Use it just to get the position. It does not work yet in the write direction."
		return self.t1z(),self.t2z(),self.t3z() 		
		
