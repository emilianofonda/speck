from math import sin,cos,tan,asin,pi
from time import sleep,time
from motor_class import *
from counter_class import counter
import PyTango
from PyTango import DeviceProxy, DevState
import galil_multiaxis
from exceptions import Exception
import exceptions
from numpy import arange,sign,array,nan
import thread
import moveable

class sagittal_bender:
	def __init__(self,bender1_name="",bender2_name="",controlbox_rawdata1=None,controlbox_rawdata2=None,axis1=None,axis2=None,\
		A1_1=None,A0_1=None,A1_2=None,A0_2=None,deadtime=0.03,timeout=.05):
		"""The bender motors and the control box raw data device are passed by their tango addresses.
		The axis are the axis numbers on the rawdata device (0 to 7) axis1 for motor1 and axis2 for motor2.
		bender.c1=A1_1*1/R+A0_1
		bender.c2=A1_2*1/R+A0_2"""
		#self.DP=None
		self.label="Bender :"+bender1_name+" + "+bender2_name
		self.c1=motor(bender1_name)
		self.c2=motor(bender2_name)
		self.timeout=timeout
		self.deadtime=deadtime
		self.cb1=DeviceProxy(controlbox_rawdata1)
		self.cb2=DeviceProxy(controlbox_rawdata2)
		self.axis1=axis1
		self.axis2=axis2
		#self.max_as=max_as
		self.asy_value=self.c1.pos()-self.c2.pos()
		#self.MotOff=MotOff
		self.A1_1=A1_1
		self.A0_1=A0_1
		self.A1_2=A1_2
		self.A0_2=A0_2
		#self.bender_offset=bender_offset
		return
		
	def __str__(self):
		return "MOTOR"
		
	def __repr__(self):
		return self.label+" at %10.6f"%(self.pos())
	
	def subtype(self):
		return "SAGITTAL BENDER"
	
	def analog1(self,n=1):
		return Read_AI(self.cb1,self.axis1,n)

	def analog2(self,n=1):
		return Read_AI(self.cb2,self.axis2,n)

	def compute_state(self):
		"""State returns MOVING if one of the benders is moving, in any other case combined state with (state of 1) OR (state of 2) is returned. 
		This is a workaround since OFF has priority over MOVING and the code must follow motors movement even if one is OFF."""
		s1=self.c1.state()
		s2=self.c2.state()
		s12=[s1,s2]
		if DevState.MOVING in s12: return DevState.MOVING
		if s12==[DevState.STANDBY,DevState.STANDBY]: return DevState.STANDBY
		if s12==[DevState.UNKNOWN,DevState.UNKNOWN]: return DevState.UNKNOWN
		if DevState.OFF in s12: return DevState.OFF
		if DevState.DISABLE in s12: return DevState.DISABLE
		if DevState.ALARM in s12: return DevState.ALARM
		else:
			return s1 and s2

	def offset(self,dest=None):
		"""Set an offset over C1 and C2 motors in motor steps.
		If you have to increase the value of the bender.pos od DX, 
		you have to type bender.offset(DX) and this function will set 
		a -DX offset on the two motors."""
		oc1=self.c1.offset()
		oc2=self.c2.offset()
		if dest<>None:
			self.c1.offset(oc1-dest)
			self.c2.offset(oc2-dest)
		return {"Old offsets":[oc1,oc2],"New offsets":[self.c1.offset(),self.c2.offset()]}
	
	def stop(self):
		self.c1.stop()
		self.c2.stop()
		return self.state()

	def on(self):
		self.c1.on()
		self.c2.on()
		return self.state()

	def off(self):
		self.c1.off()
		self.c2.off()
		return self.state()

	
	def r(self,dest=None,wait=True):
		"""Radius in meters. Can send the bender to a curvature radius if specified.
		The actual calibration has been made on the curvature: 1/R which is linear with energy or sin(theta)"""
		if dest==None:
			return 1./self.curv()
		else:
			return 1./self.curv(1./dest,wait=wait)

 	def calculate_steps_for_r(self,dest):
		"""Radius in meters. Returns the bender steps for the specified r in m.
		The actual calibration has been made on the curvature: 1/R which is linear with energy or sin(theta)"""
		return self.calculate_steps_for_curv(1./dest)
		

	def curv(self,dest=None,wait=True):
		"""The calibration is in the A1_1,A0_1... constants. C1=A1_1/R+A0_1, C2=...
		curv=0.5*(C1-A0_1)/A1_1+0.5*(C2-A0_2)/A1_2
		The position is returned in 1/m or the bender is sent to that value."""
		if dest==None:
			return ((self.c1.pos()-self.A0_1)/self.A1_1+(self.c2.pos()-self.A0_2)/self.A1_2)*0.5
		else:
			self.c1.fire(dest*self.A1_1+self.A0_1)
			self.c2.fire(dest*self.A1_2+self.A0_2)
			if not wait: return dest
			wait_motor(self.c1,self.c2)
			return self.curv()

	def calculate_steps_for_curv(self,dest=None):
		"""Curvature in 1/m. Returns the C1 and C2 bender motors steps for the specified 1/r in 1/m.
		The calibration is in the A1_1,A0_1... constants. C1=A1_1/R+A0_1, C2=..."""
		return [dest*self.A1_1+self.A0_1,dest*self.A1_2+self.A0_2]
	
	def pos(self,dest=None,wait=True):
		if(dest==None):
			return 0.5*(self.c1.pos()+self.c2.pos())
		ss=self.state()
		if(ss in [DevState.DISABLE,DevState.OFF,DevState.UNKNOWN]):
			print "At least one motor is in Off,Unknown or Disable state!!!"
			self.stop()
			raise Exception("Bender in bad state")
		dest1=dest-self.pos()+self.c1.pos()
		#dest1=dest+self.asy_value*0.5
		dest2=dest-self.pos()+self.c2.pos()
		#dest2=dest-self.asy_value*0.5
		try:
			if(not(wait)):
				self.c1.fire(dest1)
				self.c2.fire(dest2)
				return dest
			self.c1.fire(dest1)
			self.c2.fire(dest2)
			t=time()
			while((self.state()<>DevState.MOVING) and (time()-t<self.timeout)):
				sleep(self.deadtime)
			while(self.state()==DevState.MOVING): 
				sleep(self.deadtime)
				pass
				#print "Bender=%8.3f\r"%(self.pos(dest=None)),
				
		except (KeyboardInterrupt,SystemExit), tmp:
		                self.stop()
				print ""
		                raise tmp								
		except Exception, tmp:
			self.stop()
			#if(self.MotOff):
			#	self.mo()
			#	print ""
			#	print "Motors OFF"
			print "Stopped over exception"
			print  self.pos()
			raise tmp
		#print ""
		return self.pos()
		
	def go(self,dest):
		return self.pos(dest,wait=False)
		
	def fire(self,dest=None):
		"""This is a way to send the go command in a thread. Use it for full speed when multiple go commands
		have to be sent in series on different motors. It returns the thread ID. Use only if you are aware of thread risks.
		This is an experimental feature at present. Prefer go since it already uses threads."""
		if dest==None:
                	return self.go()
		return thread.start_new_thread(self.go,(dest,))
															
	def asy(self,dest=None,wait=True):
		"""Asymmetry is defined as bender1-bender2, this is a signed value: positive means bender1>bender2."""
		if(dest==None):
			print "Last memorised value=%g This will be applied to next bender movement"%(self.asy_value)
			return (self.c1.pos()-self.c2.pos())
		ss=self.state()
		if(ss==DevState.MOVING):
			raise Exception("Motors are already moving !!!")
		if(ss in [DevState.DISABLE,DevState.OFF,DevState.UNKNOWN]):
			print "At least one motor is in Off,Unknown or Disable state!!!"
			self.stop()
			raise Exception("Bender: at least one motor is in Off,Unknown or Disable state!!!")
		dest1=self.c1.pos()+0.5*(dest-(self.c1.pos()-self.c2.pos()))
		dest2=self.c2.pos()-0.5*(dest-(self.c1.pos()-self.c2.pos()))
		try:
			self.c1.fire(dest1)
			self.c2.fire(dest2)
			self.asy_value=dest
			if(not(wait)):
				return dest
			t=0.
			while(((self.c1.state()<>DevState.MOVING) and (self.c2.state()<>DevState.MOVING)) and (t<self.timeout)):
				sleep(self.deadtime)
				t+=self.deadtime
			while((self.c1.state()==DevState.MOVING) or (self.c2.state()==DevState.MOVING)): 
				sleep(self.deadtime)
				#print "Asy=%8.3f\r"%(self.c1.pos()-self.c2.pos()),
		except (KeyboardInterrupt,SystemExit), tmp:
		                self.stop()
				self.asy_value=self.c1.pos()-self.c2.pos()
		                raise tmp								
		except Exception, tmp:
			print "Stopped on exception"
			self.stop()
			self.asy_value=self.c1.pos()-self.c2.pos()
			print ""
			#if(self.MotOff):
			#	self.mo()
			#	print "Motors OFF"
			raise tmp
		#print ""
		return self.asy()

	def status(self):
		return "Status does not exist for this bender."

	def state(self):
		"""The state function of the bender do not incorporate a check of the bender anymore.""" 
		try:
			s=self.compute_state()
		except (KeyboardInterrupt,SystemExit), tmp:
		                self.c1.stop()
				self.c2.stop()
		                raise tmp								
		except Exception, tmp:
			self.c1.stop()
			self.c2.stop()
			print self.label," stopped over exception"
			print  self.pos()
			raise tmp
		return s
	

class mono1:
	def __init__(self,d,H,mono_name,\
		rx1=None,\
		tz2=None,\
		ts2=None,\
		rx2=None,\
		rs2=None,\
		rx2fine=None,\
		rz2=None,\
		tz1=None,\
		bender=None,\
		timeout=.05,deadtime=0.03,delay=0.0,sourceDistance=None,counter_label="d09-1-c00/ca/cpt.1",counter_channel=0,\
		Rz2_par=[],Rs2_par=[],Rx2_par=[],
		WhiteBeam={"rx1":None,"tz1":None,"tz2":None},emin=None,emax=None):
		"""Experimental version: should use the galil_axisgroup. 
		Initialisation is different and everything is modified with respect to mono1.py. Under active test since first half 2009.
		Change in defaults 2/11/2009: ts2 never moves if you do not ask it explicitly. Use the seten command."""
		self.DP=DeviceProxy(mono_name)
		self.label=mono_name
		self.bender=bender
		try:
			self.counter=counter(counter_label)
		except:
			self.counter=None
			print "No usable counter: no tuning possible"
		self.counter_channel=counter_channel
		try:
			self.att_qDistance=self.DP.read_attribute("qDistance")
		except:
			print "Cannot read attribute qDistance from ",self.label
			self.att_qDistance=None
		self.sourceDistance=sourceDistance
		self.H=H
		self.d=d
		self.emin=emin
		self.emax=emax
		self.motors=[]
		self.m_rx1=rx1
		self.__userx1=True
		self.__usetz2=True
		self.__usets2=True
		self.__userx2=True
		self.__users2=True
		self.__userz2=True
		self.__userx2fine=True
		self.WhiteBeamPositions=WhiteBeam
		if(rx1==None): self.__userx1=False
		self.m_tz2=tz2
		if(tz2==None): self.__usetz2=False
		self.m_ts2=ts2
		if(ts2==None): self.__usets2=False
		self.m_rx2=rx2
		if(rx2==None): self.__userx2=False
		self.m_rz2=rz2
		if(rz2==None): self.__userz2=False
		self.m_rs2=rs2
		if(rs2==None): self.__users2=False
		self.m_rx2fine=rx2fine
		if(rx2fine==None): self.__userx2fine=False
		self.m_tz1=tz1
		if(tz1==None): self.__usetz1=False
		if(bender==None):
			self.bender=bender
			self.__usebender=False
			c1=None
			c2=None
		else:
			self.bender=bender
			self.__usebender=True
			self.motors=[self.bender,]+self.motors
			c1=bender.c1
			c2=bender.c2
		self.timeout=timeout
		self.deadtime=deadtime
		self.delay=delay
		self.counter_channel=counter_channel
		self.motors=[self.m_rx1,self.m_tz2,self.m_ts2,self.m_rx2fine,self.m_rz2,self.m_rs2,self.m_rx2,self.m_tz1]
		__motor_group=[]
		for i in [rx1, tz2, ts2, rz2, rs2, rx2, c1, c2 ]:
			if i <>None: __motor_group.append(i)
		self.motor_group=galil_multiaxis.galil_axisgroup(__motor_group)
		self.default_enables={"ts2":False,"tz2":True,"rs2":False,"rz2":False,"rx2":False,"rx2fine":False}
		tpm=[]
		for i in self.motors:
			if(i<>None): tpm.append(i)
		self.motors=tpm
		#for i in self.motors:
		#	i.verbose=False
		self.Rz2_par=Rz2_par
		self.Rs2_par=Rs2_par
		self.Rx2_par=Rx2_par
		return
		
	def __str__(self):
		return "MOTOR"
		
	def __repr__(self):
		return self.label+" at %10.6f"%(self.pos())
	
	def subtype(self):
		return "SAMBA MONOCHROMATOR"

	def on(self):
		for i in self.motors: i.on()
		return self.state()
		
	def off(self):
		for i in self.motors: i.off()
		return self.state()
	
	def whitebeam(self):
		print "Moving to white beam operation. Hope you are sure of what you are doing..."
		print "Motors should move to:"
		print "Rx1:",self.WhiteBeamPositions["rx1"]
		print "Tz1:",self.WhiteBeamPositions["tz1"]
		print "Tz2:",self.WhiteBeamPositions["tz2"]
		print "Ready to move in 30s..."
		sleep(30.)
		print " OK, let's go..."
		motors_moved={}
		if self.WhiteBeamPositions["rx1"]<>None:
			self.m_rx1.go(self.WhiteBeamPositions["rx1"])
		if self.WhiteBeamPositions["tz1"]<>None:
			self.m_tz1.go(self.WhiteBeamPositions["tz1"])
		if self.WhiteBeamPositions["tz2"]<>None:
			self.m_tz2.go(self.WhiteBeamPositions["tz2"])
		wait_motor([self.m_tz1,self.m_rx1,self.m_tz2])
		if self.WhiteBeamPositions["tz1"]<>None:
			motors_moved["tz1"]=self.m_tz1.pos()
		if self.WhiteBeamPositions["rx1"]<>None:
			motors_moved["rx1"]=self.m_rx1.pos()
		if self.WhiteBeamPositions["tz2"]<>None:
			motors_moved["tz2"]=self.m_tz2.pos()
		print self.label," is in white beam position."
		return motors_moved
		
	def disable_ts2(self):
		self.__usets2=False
		return
		
	def enable_ts2(self):
		self.__usets2=True
		return

	def usets2(self,value=None):
		if(value in [True,False]): 
			self.__usets2=value
		else :
			return self.__usets2

	def disable_tz2(self):
		self.__usetz2=False
		return
		
	def enable_tz2(self):
		self.__usetz2=True
		return

	def usetz2(self,value=None):
		if(value in [True,False]): 
			self.__usetz2=value
		else :
			return self.__usetz2
	
	def disable_bender(self):
		return self.usebender(False)

	def enable_bender(self):
		return self.usebender(True)

	def usebender(self,value=None):
		if(value in [True,False]): 
			self.__usebender=value
		else :
			return self.__usebender

	def sample_at(self,distance=None):
		for i in range(5):
			try:
				self.att_qDistance=self.DP.read_attribute("qDistance")
				break
			except:
				if i==4: raise Exception("Cannot read focusing distance")
		if distance==None:
			return self.att_qDistance.value
		else:
			self.att_qDistance.value=distance
			if self.state()==DevState.MOVING:
				print "Trying to write qDistance on dcm while dcm is moving! wait..."
				while(self.state()==DevState.MOVING):
					sleep(self.deadtime)
			self.DP.write_attribute("qDistance",distance)
			return self.sample_at()

	def status(self):
		return "Nothing yet"

	def state(self):
		"""State returns MOVING if one of the motors is moving, in any other case combined state is returned. 
		This is a workaround since OFF has priority over MOVING, but the code must follow motors movement even if one is OFF."""
		j=[]
		for i in self.motors:
			tmp=i.state()
			if tmp==DevState.MOVING: return DevState.MOVING
			j.append(tmp)
		if j==[DevState.STANDBY,]*len(j): 	return DevState.STANDBY
		if j==[DevState.UNKNOWN,]*len(j): 	return DevState.UNKNOWN
		if j==[DevState.OFF,]*len(j): 		return DevState.OFF
		if DevState.DISABLE in j: 		return DevState.DISABLE
		if DevState.ALARM in j:			return DevState.ALARM
		j=self.motors[0].state()
		for i in self.motors[1:]:
			j=(i.state() and j)
			return j


	def stop(self):
		for i in self.motors:
			try:
				i.stop()
			except:
				print i.label," is not responding!\n"
		return
		
	def e2theta(self,energy):
		"""Calculate the energy for a given angle"""
		return asin(12398.41857/(2.*self.d*energy))/pi*180.

	def theta2e(self,theta):
		"""Calculate the angle for a given energy"""
		return 12398.41857/(2.*self.d*sin(theta/180.*pi))

	def ts2(self,theta):
		"""Calculate ts2 position for a given angle"""
		return self.H*0.5/sin(theta/180.*pi)

	def tz2(self,theta):
		"""Calculate tz2 position for a given angle"""
		return self.H*0.5/cos(theta/180.*pi)
	
	def calculate_curvature(self,theta):
		"""The sample distance and source distance are referred to the center of rotation of the first crystal.
		This is not exact, but turns out to be a good approximation. The more accurate code is commented and ready for use."""
		th=theta/180.*pi
		#rec_p1=1./(self.sourceDistance+self.H/sin(2.*th))
		if self.sourceDistance<>0.:
			rec_p1=1./self.sourceDistance
		else:
			raise Exception("Monochromator "+self.label+"sourceDistance=0 !")
		#rec_q1=1./self.sample_at()-H*cos(2*th)/sin(2*th)
		if self.sample_at()<>0.: 
			rec_q1=1./self.sample_at()
		else:	
			raise Exception("Monochromator "+self.label+"Cannot compute actual sample distance!")
		if th<>0.:
			curv=0.5*(rec_p1+rec_q1)/sin(th)
		else:
			raise Exception("Monochromator "+self.label+"Cannot compute curvature!\n\
			theta=%g 1/p=%g 1/q=%g"%(theta,rec_p1,rec_q1))
		return curv
	
	def calculate_curvatureradius(self,theta):
		return 1./self.calculate_curvature(theta)

	def pos(self,energy=None,wait=True,Ts2_Moves=False,NOFailures=0):
		"""Move the mono at the desired energy"""
		if NOFailures>5:
			raise Exception("mono1b: too many retries trying the move. (NO>5)")
		try:
			move_list=[]
			if(energy==None):
				ps=self.m_rx1.pos()
				if ps==0.: return 9.99e12
				return self.theta2e(ps)
			if self.emin<>None and energy<self.emin:
				raise Exception("Requested energy below monochromator limit: %7.2f"%self.emin)
			if self.emax<>None and energy>self.emax:
				raise Exception("Requested energy above monochromator limit: %7.2f"%self.emax)
			theta=self.e2theta(energy)
			move_list+=[self.m_rx1,theta]
			if(self.__usebender): 
				__c1c2=self.bender.calculate_steps_for_curv(self.calculate_curvature(theta))
				#if __c1c2[0]>310000 or __c1c2[1]>395000:
				#	print "mono1b.py: Hard coded limits of the Si220 bender exceeded"
				#	raise Exception("Hard bender limits are c1<=310000steps and c2<=395000Steps")
				move_list+=[self.bender.c1,__c1c2[0],self.bender.c2,__c1c2[1]]
			if((Ts2_Moves)and(self.usets2())): 
				move_list+=[self.m_ts2,self.ts2(theta)]
			if(self.usetz2()): move_list+=[self.m_tz2,self.tz2(theta)]
			#Let's move it, move it!
			#print move_list
			#print __c1c2[0], __c1c2[1]
			self.motor_group.pos(*move_list)
			#
			sleep(self.delay)
		except (KeyboardInterrupt,SystemExit), tmp:
			self.stop()
			raise tmp
		except PyTango.DevFailed, tmp:
			NOFailures+=1
			self.stop()
			print "Error while moving... retrying #",NOFailures
			print "Waiting 1 s"
			sleep(1.)
			print self.label,":(mono1b) state is now", self.state()
			self.pos(energy,wait=wait,Ts2_Moves=Ts2_Moves,NOFailures=NOFailures)
			#raise tmp
		except PyTango.DevError, tmp:
			self.stop()
			raise tmp
		except Exception, tmp:
			self.stop()
			print "\nUnknown Error"
			print "Positions energy, theta=", self.pos(), self.m_rx1.pos()
			raise tmp
		return self.pos()

	def move(self,energy=None,wait=True,Ts2_Moves=False):
		"""Please use pos instead. Move is obsolete and subject ro removal in next future. """
		return self.pos(energy,wait,Ts2_Moves)

	def go(self,energy=None,wait=False,Ts2_Moves=False):
		"""Go to energy and do not wait."""
		return self.pos(energy,wait,Ts2_Moves)	
		
	def theta(self,theta=None,wait=True):
		if(theta==None):
			return self.m_rx1.pos()
		return self.pos(self.theta2e(theta),wait)

	def calibrate(self,experiment_energy,true_energy):
		"""This function applies a new offset to the main rotation rx1. 
		It requires the experimental energy position of the spectral feature as first argument
		and the true energy of the feature as second argument
		calibrate(Energy_I_See,Energy_From_Tables)"""
		print "Main goniometer offset was: %8.6f"%(self.m_rx1.offset())
		offset=self.m_rx1.offset()+self.e2theta(true_energy)-self.e2theta(experiment_energy)
		print "New goniometer offset is:   %8.6f"%(offset)
		oe=self.pos()
		self.m_rx1.offset(offset)
		return {"Old energy":oe,"New energy":self.pos()}

	def oldtune(self,piezomin=1.,piezomax=9.,np=20,tolerance=0.005,countingtime=0.1,nested=False):
		"""Scan the mono.m_rx2fine motor to achieve maximum intensity in the desired counter/channel.
		Set the piezo to the position, returns the position in terms of voltage to apply.
		Feedback and control values differ on a piezo, the control value is always returned."""
		if self.counter==None:
			return
		cpt=self.counter
		channel=self.counter_channel
		if(self.__userx2fine==False): 
			print "dcm setup excludes a piezo. Tuning is nonsense without the piezo."
			return 0.
		if(np<4):
			print "I use minimum 4 intervals (5 points). I set np=4."
			np=4
		piezomax=max(piezomin,piezomax)
		if (float(piezomax-piezomin)/np>1.): np=int((piezomax-piezomin)/1.)+1
		dp=float(piezomax-piezomin)/np
		if(dp==0): return "Invalid Range"
		p=piezomin
		scan=[[0.]*np,[0.]*np]
		t=time()
		self.m_rx2fine.pos(1.)
		sleep(0.1)
		self.m_rx2fine.pos(1.2)
		sleep(0.1)
		for i in range(np):
			self.m_rx2fine.pos(p)
			scan[0][i]=p
			scan[1][i]=cpt.count(countingtime)[channel]
			p+=dp
		optimum= scan [0] [ scan[1].index(max(scan[1])) ]
		if(dp*np>tolerance):
			dp=dp/float(np-1)
			if(optimum-dp*np<=0.):
				print "Point on lower end..."
				optimum=np*dp+tolerance
			if(optimum+dp*np>=10.):
				print "Point on higher end..."
				optimum=10.-np*dp-tolerance
			p1=optimum-(np*dp)
			p2=optimum+(np*dp)
			print "p1=%6.4f p2=%6.4f"%(p1,p2)
			optimum=self.oldtune(p1,p2,np,tolerance,countingtime,nested=True)
		if(not(nested)):
			self.m_rx2fine.pos(optimum)
	        	print "Tuning this point took: %5.2f seconds"%(time()-t)
		return optimum

	def tune(self,piezomin=1.,piezomax=9.,np=20,tolerance=0.005,countingtime=0.2,nested=False):
		"""Scan the mono.m_rx2fine motor to achieve maximum intensity in the desired counter/channel.
		Set the piezo to the position, returns the position in terms of voltage to apply.
		Feedback and control values differ on a piezo, the control value is always returned."""
		if self.counter==None:
			return
		cpt=self.counter
		channel=self.counter_channel
		if(self.__userx2fine==False): 
			print "dcm setup excludes a piezo. Tuning is nonsense without the piezo."
			return 0.
		if(np<4):
			print "I use minimum 4 intervals (5 points). I set np=4."
			np=4
		piezomax=max(piezomin,piezomax)
		if (float(piezomax-piezomin)/np>1.): np=int((piezomax-piezomin)/1.)+1
		dp=float(piezomax-piezomin)/np
		if(dp==0): return "Invalid Range"
		p=float(piezomin)
		scan=[[0.]*np,[0.]*np]
		t=time()
		self.m_rx2fine.pos(max(piezomin-0.2,0.1))
		sleep(0.1)
		self.m_rx2fine.pos(max(piezomin-0.1,0.1))
		sleep(0.1)
		for i in range(np):
			self.m_rx2fine.pos(p)
			scan[0][i]=p
			if type(channel)==int:
				scan[1][i]=cpt.count(countingtime)[channel]
			elif type(channel) in [tuple,list]:
				scan[1][i]=0
				ccs=cpt.count(countingtime)
				for j in channel:
					scan[1][i]+=ccs[j]
			p+=dp
		try:
			optimum= sum(array(scan[0],"f")*(array(scan[1],"f")-min(scan[1])))/sum(array(scan[1],"f")-min(scan[1]))
			if optimum==nan: 
				print "Tuning failed!"
				optimum=5.
		except Exception, tmp:
			print sum(array(scan[1],"f"))
			print "No tuning found!"
			print "Returning 5 Volts as result... check it again!"
			optimum=5.
			print tmp
		if not(nested):
			dp=0.75
			optimum=self.tune(max(optimum-dp,0.1),min(optimum+dp,9.9),np=np,tolerance=tolerance,countingtime=countingtime,nested=True)
			self.m_rx2fine.pos(optimum)
	       		print "Tuning this point took: %5.2f seconds"%(time()-t)
		return optimum
	
	def ftune(self,piezomin=1.,piezomax=9.,np=20,tolerance=0.005,countingtime=0.2,nested=False):
		"""Scan the mono.m_rx2fine motor to achieve maximum intensity in the desired counter/channel.
		Set the piezo to the position, returns the position in terms of voltage to apply.
		Feedback and control values differ on a piezo, the control value is always returned."""
		I0_average=moveable.sensor("d09-1-c00/ca/sai.1","averagechannel0")
		if self.counter==None:
			return
		cpt=self.counter
		channel=self.counter_channel
		if(self.__userx2fine==False): 
			print "dcm setup excludes a piezo. Tuning is nonsense without the piezo."
			return 0.
		if(np<4):
			print "I use minimum 4 intervals (5 points). I set np=4."
			np=4
		piezomax=max(piezomin,piezomax)
		if (float(piezomax-piezomin)/np>1.): np=int((piezomax-piezomin)/1.)+1
		dp=float(piezomax-piezomin)/np
		if(dp==0): return "Invalid Range"
		p=float(piezomin)
		scan=[[0.]*np,[0.]*np]
		t=time()
		self.m_rx2fine.pos(max(piezomin-0.2,0.1))
		sleep(0.1)
		self.m_rx2fine.pos(max(piezomin-0.1,0.1))
		sleep(0.1)
		for i in range(np):
			self.m_rx2fine.pos(p)
			scan[0][i]=p
			if type(channel)==int:
				#scan[1][i]=cpt.count(countingtime)[channel]
				scan[1][i]=I0_average.pos()
			elif type(channel) in [tuple,list]:
				scan[1][i]=0
				ccs=cpt.count(countingtime)
				for j in channel:
					scan[1][i]+=ccs[j]
			p+=dp
		try:
			optimum= sum(array(scan[0],"f")*(array(scan[1],"f")-min(scan[1])))/sum(array(scan[1],"f")-min(scan[1]))
			if optimum==nan: 
				print "Tuning failed!"
				optimum=5.
		except Exception, tmp:
			print sum(array(scan[1],"f"))
			print "No tuning found!"
			print "Returning 5 Volts as result... check it again!"
			optimum=5.
			print tmp
		if not(nested):
			dp=0.75
			optimum=self.tune(max(optimum-dp,0.1),min(optimum+dp,9.9),np=np,tolerance=tolerance,countingtime=countingtime,nested=True)
			self.m_rx2fine.pos(optimum)
	       		print "Tuning this point took: %5.2f seconds"%(time()-t)
		return optimum
	
	def detune(self,fraction):
		"""Use the mono1.tune method and then detune the two crystals to get a fraction of the intensity. 
		Tha value of fraction must be in the [-1:0[ or ]0:1] bounds."""
		if self.counter==None:
			return
		cpt=self.counter
		channel=self.counter_channel
		if fraction <=-1. or fraction>=1. or fraction==0.: 
			raise exceptions.Exception("Illegal range","fraction value is out of bounds",fraction)
		print "Finding maximum..."
		p=self.tune()
		imax=cpt.count(.2)[channel]
		print "Maximum=",imax/0.2," Position=",p
		inow=imax
		dp=0.1*sign(fraction)
		tolerance=0.01
		while (abs(float(inow)/imax-abs(fraction)) >=tolerance):
			print "detuning... step=%5.3f"%(dp)
			while(inow>abs(imax*fraction)):
				p+=dp
				self.m_rx2fine.pos(p)
				inow=cpt.count(0.2)[channel]
			p=p-dp
			self.m_rx2fine.pos(p)
			inow=cpt.count(0.2)[channel]
			dp=dp*0.2
		print "Detuned=",inow/0.2," Position=",p
		return p
	
	def calculate_rz2(self,energy):
		"""Calculate rz2 for given energy value: parameters are in self.Rz2
		The polynome is calculated over curvature: rz2=Sum(self.Rz2[i]*1/R**i)"""
		curv=self.calculate_curvature(self.e2theta(energy))
		if len(self.Rz2_par)==0:
			return None
		__rz2=0.
		for i in range(len(self.Rz2_par)):
			__rz2+=self.Rz2_par[i]*curv**i
		return __rz2
		
	def calculate_rs2(self,energy):
		"""Calculate rs2 for given energy value: parameters are in self.Rs2
		The polynome is calculated over theta: rs2=Sum(self.Rs2[i]*theta**i)"""
		#th=self.e2theta(energy)
		if len(self.Rs2_par)==0:
			return None
		__rs2=0.
		for i in range(len(self.Rs2_par)):
			__rs2+=self.Rs2_par[i]*energy**i
		return __rs2

	def calculate_rx2(self,energy):
		"""Calculate rx2 for given energy value: parameters are in self.Rx2
		The polynome is calculated over theta: rx2=Sum(self.Rs2[i]*(theta**i))"""
		th=self.e2theta(energy)
		if len(self.Rx2_par)==0:
			return None
		__rx2=0.
		for i in range(len(self.Rx2_par)):
			__rx2+=self.Rx2_par[i]*th**i
		return __rx2

	def seten(self,energy=None):
		if energy==None:
			return self.pos()
		self.enable_tz2()
		if self.m_rx2fine<>None: self.m_rx2fine.pos(5)
		if self.m_rz2<>None:     self.m_rz2.pos(self.calculate_rz2(energy))
		if self.m_rs2<>None:     self.m_rs2.pos(self.calculate_rs2(energy))
		if self.m_rx2<>None:     self.m_rx2.pos(self.calculate_rx2(energy))
		self.pos(energy,Ts2_Moves=True)
		if energy<=6000.:
			self.m_ts2.pos(35.)
		return self.pos()
	
	def setall(self,energy=None):
		if energy==None:
			return self.pos()
		self.pos(energy,Ts2_Moves=True)
		tmp=self.calculate_rz2(energy)
		if tmp<>None: self.m_rz2.pos(tmp)
		tmp=self.calculate_rs2(energy)
		if tmp<>None: self.m_rs2.pos(tmp)
		self.m_rx2fine.pos(5.)
		tmp=self.calculate_rx2(energy)
		if tmp<>None: self.m_rx2.pos(tmp)
		self.tune()
		return self.pos()

