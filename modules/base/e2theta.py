from __future__ import division
from past.utils import old_div
from numpy import pi,sin,arcsin

def e2theta(energy,d=1):
	"""Calculate the angle for a given energy"""
	return old_div(arcsin(12398.41857/(2.*d*energy)),pi)*180.

def theta2e(theta,d=1):
	"""Calculate the energy for a given angle"""
	return 12398.41857/(2.*d*sin(theta/180.*pi))
										
