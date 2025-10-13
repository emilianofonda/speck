from __future__ import print_function
from numpy import arange
from time import sleep
class voltage_controller:
	def __init__(self,voltage,inverter,vmin=-5,vmax=5,speed=10,delta=0.02):
		self.inverter=inverter
		self.voltage=voltage
		self.speed=speed
		self.delta=delta
		self.deadtime=self.delta/self.speed
		self.vmax=vmax
		self.vmin=vmin
		return
	
	def __repr__(self):
		return "Voltage=%g\n"%self.pos()
		
	def pos(self,x=None):
		if self.inverter.pos()>0.5:
			position=self.voltage.pos()
		else:
			position=-self.voltage.pos()
		#print "Inverter=%g, Voltage=%g"%(self.inverter.pos(),self.voltage.pos())
		if x==None:
			return position
		if x>self.vmax or x<self.vmin:
			raise Exception("Trying to set voltage out of bounds!")
		try:
			if x<position:
				dd=-self.delta
			else:
				dd=self.delta
			for i in arange(position,x+dd,dd):
				if i>=0:
					self.voltage.pos(abs(i))
					self.inverter.pos(1)
				else:
					self.voltage.pos(abs(i))
					self.inverter.pos(0)
				#print "Voltage=%+06.3f\r"%self.pos(),
				sleep(self.deadtime)
		except (KeyboardInterrupt,SystemExit) as tmp:
			raise tmp
		except Exception as tmp:
			raise tmp
		print("\n")
		return self.pos()

		
		
