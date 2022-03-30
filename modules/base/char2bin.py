from __future__ import division
from past.utils import old_div
def char2bin(c):
	"""Converts ONE char to a string representing its binary form"""
	cv=ord(c)
	if cv==0:
		return "0000000"
	if cv==1:
		return "0000001"
	i=7
	s=""
	while(cv>=1):
		if old_div(cv,2**i):
			s+="1"
			cv=cv-2**i
		else:
			s+="0"
		i-=1
	s=s+"0"*(8-len(s))
	return s

