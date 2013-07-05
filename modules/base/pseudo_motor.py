import PyTango
from PyTango import DevState
from time import time,sleep
import motor_class
from exceptions import KeyboardInterrupt, SystemExit, Exception

class pseudo_motor:
	"""This class allows the definition of a pseudo motor: a motor that is a read write 
	function of a combination of other motors, even other pseudo motors. 
	You have to provide a list of motors. Keep the same order of the list for the writefunction results!
	You have to define a function that returns the position of the pseudo motor as a function of the other motors, this is the read_function.
	You have to define a function that returns where each motor should go if x is the pseudo_motor position desired.
	Example:
		the pseudo motor is the gap of a pseudo slit built with motor1 and motor2:
			the readfunction could be myreadf:
				def myreadf(motor1,motor2):
					return motor1.pos()-motor2.pos()
			the writefunction could be built as follow:
				def mywritef(motor1,motor2):
					return (motor1.pos()+motor1.pos())*0.5+x*0.5, (motor1.pos()+motor1.pos())*0.5-x*0.5
	Finally:     mygapmotor=pseudo_motor([motor1,motor2],myreadf,mywritef)
	It exists also a post-move function. Actually, while this function is executed the state should be MOVING even if the state of the motors is not moving."""

	def __init__(self,motorslist=None,readposition=None,writeposition=None,label="PseudoMotor",postmove_function=None,deadtime=0.05,timeout=0.):
		self.motorslist=motorslist
		self.readposition=readposition
		self.writeposition=writeposition
		self.postmove_function=postmove_function
		self.DP=None
		self.label=label
		self.pseudostate=None
		self.deadtime=deadtime
		self.timeout=timeout
		return
	
        def __str__(self):
                return "MOTOR"

        def __repr__(self):
                return self.label+" at %g"%(self.pos())

        def subtype(self):
                return "PSEUDOMOTOR"

	def state(self):
		"""WARNING: this state should be never used by the pseudo motor itself! 
		It can be safely used by other pseudomotors or the waitmotors function and so on, 
		but it is not intended to be used by the pos function itself since the pseudostate 
		is changed to MOVING during the pseudomovement to lock the state during the function call. 
		Other important point for programmers, the pseudo state must be switched back to None 
		on exception before any other action in order to prevent a deadlock."""
		if self.pseudostate==DevState.MOVING:
			return DevState.MOVING
		__s=[]
		for i in self.motorslist:
			__s.append(i.state())
		if DevState.MOVING in __s:
			return DevState.MOVING
		if DevState.DISABLE in __s:
			return DevState.DISABLE
		if DevState.OFF in __s:
			return DevState.OFF
		if __s==[DevState.STANDBY,]*len(__s):
			return DevState.STANDBY
		else:
			__rs=__s[0]
			for i in __s[1:]: __rs=__rs and i
			return __rs	
	
	def status(self):
		return "Status is not yet supported on pseudo motors"

	def pos(self,dest=None,wait=True):
		if dest==None:
			return self.readposition()
		if self.pseudostate==DevState.MOVING:
			raise Exception("Writing on moving motor")
		tupledest=self.writeposition(dest)
		try:
			self.pseudostate=DevState.MOVING
			for i in zip(self.motorslist,tupledest):
					i[0].go(i[1])
			motor_class.wait_motor(self.motorslist,deadtime=self.deadtime,timeout=self.timeout,delay=0.)
			if self.postmove_function<>None:
				self.postmove_function()
		except (PyTango.DevFailed,PyTango.DevError), tmp:
			self.stop()
			raise tmp
		except (SystemExit,KeyboardInterrupt), tmp:
			self.stop()
			raise tmp
		self.pseudostate=None
		return self.pos()
		
	def go(self,dest=None):
		return self.pos(dest,wait=False)
	
	def stop(self):
		stoppedWell=True
		for i in self.motorslist: 
			try:
				i.stop()
			except:
				print "Error stopping :",i
				stoppedWell=False
		self.pseudostate=None
		return stoppedWell

	
