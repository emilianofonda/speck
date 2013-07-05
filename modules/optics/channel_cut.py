from numpy import sin,cos
from e2theta import *

class channel_cut:
	def __init__(self,d=1.637472,h=10,l1=50,l2=50,theta=None,tz=None):
		self.label="ChannelCut"
		self.d=d
		self.h=h
		self.l1=l1
		self.l2=l2
		self.theta=theta
		self.tz=tz
		return

	def __str__(self):
                return "MOTOR"

	def __repr__(self):
	        return self.label+" at %10.6f"%(self.pos())

	def subtype(self):
	        return "SAMBA MONOCHROMATOR"

									
	def pos(self,energy=None,wait=True):
		if energy==None:
			return theta2e(self.theta.pos(),d=self.d)
		th=e2theta(energy,d=self.d)
		if wait:
			self.theta.pos(th)
			return self.pos()
		else:
			self.theta.go(th)
			return energy

	def go(self,energy):
		return self.pos(energy,wait=False)

	def calculate_tz(self,theta=None):
		if theta==None: theta=self.theta.pos()
		t=theta/180.*pi
		return self.l2*0.5*sin(t)-0.5*self.h*(1-cos(t))

	def state(self):
		return self.theta.state()
