from __future__ import print_function
from time import sleep
from PyTango import DeviceProxy,DevState
from tango_serial import tango_serial

class ACE_APD:
	def __init__(self,label='',EndOfLine=[10, 13], space=32,deadtime=0.04,timeout=0.):
		"""
		HV: high voltage in volts
		sh: servo here means HV ON
		mo: motor off: means HV OFF
		mode: INT integral or WIN window
		ll: low level of the window (INT or WIN modes)
		ws: window size (WIN mode only)
		curr: read head current
		temp: read head temperature
		deadtime is extremely important for correct RS232 commmunication. 
		"""
		self.label=label
		#The deviceproxy associated will be the serial line used
		self.DP=DeviceProxy(label)
		#The serial line must be declared to use the simple tango_serial class
		self.com=tango_serial(label,EndOfLine=EndOfLine,space=space,deadtime=deadtime)
		#deadtime and time out will be used for the movement
		self.deadtime=deadtime
		self.timeout=timeout
		self.space=space
		self.EndOfLine=EndOfLine
		#self.user_readconfig=["ACE-APD","counts"]
		print(self.writeread("NOECHO"))
		print(self.writeread(""))
		return

	def state(self):
		"""The so-called movements of this device are so fast that a minimum sleep is enough. 
		It is RUNNING, when counting ON when HV ON, OFF when HV OFF or UNKNOWN."""
		s=self.writeread("?CT")[0]
		if s=="R":
			return DevState.RUNNING
		s=self.writeread("?HVOLT").split()[1]
		if s=="ON":
			return DevState.ON
		elif s=="OFF":
			return DevState.OFF
		else:
			return DevState.UNKNOWN

	def reinit(self):
		self.__init__(self.label,self.EndOfLine,self.space,self.deadtime,self.timeout)
		return
		
	def status(self):
		"""Should output a summary of settings..."""
		ss=self.label+"\n"
		ss+="Voltage =%g\n"%self.HV()
		ss+="Voltage is %s\n"%self.state()
		ss+="SCA mode is %s\n"%self.mode()
		ss+="SCA Low Level=%g\n"%self.ll()
		if self.mode()=="WIN": ss+="SCA Window Width=%g\n"%self.ws()
		ss+="Head Temperature=%g\n"%self.temp()
		ss+="Head Current=%g\n"%self.curr()
		out0=self.out()
		ss+="Output Shaping time=%g\n"%self.out()
		if out0<30:
			ss+="Warning if out<30ns the NI6602 counter will not work properly if used."
		ss+="Firmware :"+self.version()+"\n"
		return ss

	def __call__(self):
		"Nice for interactive use: shows the setup. But it returns nothing..."
		print(self.status())
		return

	def __repr__(self):
		"Useless?"
		return self.label+"\n"+self.status()
	
	def version(self):
		return self.writeread("?VER")
	
	def mode(self,mode=None):
		if mode==None:
			res=self.writeread("?SCA").split()[0]
			if res in["WIN","INT"]: 
				return res
			else:
				self.__throw_exception("Error getting SCA mode")
		else:
			mode=mode.upper()
			if mode in ["WIN","INT"]:
				self.writeread("SCA "+mode)
				sleep(self.deadtime)
				return self.mode()
			else:
				self.__throw_exception("Syntax error: wrong SCA mode")


	def on(self):
		self.writeread("HVOLT ON")
		sleep(self.deadtime)
		return self.state()

	def off(self):
		self.writeread("HVOLT OFF")
		sleep(self.deadtime)
		return self.state()

	def start(self,dt=1):
		"""start internal counter"""
		tmp=self.com.write("TCT %i"%(int(dt*1e6)))
		return
		
	def read(self):
		"""read internal counter"""
		tmp=self.writeread("?CT DATA")
		tmp=tmp.split()
		if len(tmp)==5:
			return int(tmp[4])
		else:
			self.__throw_exception("cannot read internal counter")

	def stop(self):
		"""stops internal counter"""
		tmp=self.writeread("?CT")
		if tmp[0]=="R":
			self.writeread("STCT")
		else:
			pass
		sleep(self.deadtime)
		return self.state()
	
	def wait(self):
		"""used for counting only"""
		#sleep(self.deadtime)
		while(self.state()==DevState.RUNNING):
			sleep(self.deadtime*2)
		return
	
	def count(self,dt=1):
		self.start(dt)
		self.wait()
		return self.read()
	
	def curr(self):
		return float(self.writeread("?HCURR"))

 	def temp(self):
		return float(self.writeread("?HTEMP"))

	def HV(self,voltage=None):
		if voltage==None:
			v=self.writeread("?HVOLT").split()[0]
			v=float(v)
			return v
		else:
			v="%g"%voltage
			self.writeread("HVOLT "+v)
			sleep(self.deadtime)
			return self.HV()
	
	def ll(self,lowlevel=None):
		if lowlevel==None:
			ll=self.writeread("?SCA").split()[1]
			ll=float(ll)
			return ll
		else:
			ll="%g"%lowlevel
			ll0=self.writeread("?SCA").split()
			if len(ll0)>2:
				self.writeread("SCA "+ll0[0]+" "+ll+" "+ll0[2])
			else:
				self.writeread("SCA "+ll0[0]+" "+ll)
			sleep(self.deadtime)
			return self.ll()

	def ws(self,winSize=None):
		if winSize==None:
			ws=self.writeread("?SCA").split()
			if len(ws)<3:
				self.__throw_exception("window size is accepted only in WIN mode")
			ws=float(ws[2])
			return ws
		else:
			ws="%g"%winSize
			ll=self.writeread("?SCA").split()
			if ll[0]!="WIN": self.__throw_exception("window size is accepted only in WIN mode")
			self.writeread("SCA "+ll[0]+" "+ll[1]+" "+ws)
			sleep(self.deadtime)
			return self.ws()

	def pos(self,x=None):
		"""The low limit of the SCA is the most natural case for a scan. So it is the pos by default.
		It is easy to change it by defining a new one
		ace2=ACE_PAD(...) 
		and then 
		ace2.pos=ace2.HV
		for instance."""
		return self.ll(x)

	def out(self,x=None):
		if x==None:
			x=self.writeread("?OUT")
			return float(x)
		else:
			x0="%g"%x
			self.writeread("OUT "+x0)
			sleep(self.deadtime)
			return self.out()
		
	def go(self,x=None):
		return self.pos(x)
	
	def writeread(self,x):
		y=self.com.writeread(x)
		if y=="ERROR": __throw_exception("ERROR string received")
		return y
		
	def __throw_exception(self,comment=""):
		raise Exception("Error from ACE_APD on com:"+self.label+"\nComment="+comment)
		return
	
