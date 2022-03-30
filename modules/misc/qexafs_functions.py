from __future__ import print_function
qexafs_tz=motor("d09-1-c04/op/mono2-mt_tz.1")

def qexafs_z(theta,l=10.,h=10.):
	t=theta/180.*pi
	return l*sin(t)-0.5*h*(1-cos(t))

def qexafs_set(theta,l=10.,h=10.):
	return qexafs_tz.pos(qexafs_z(theta,l,h))

def qexafs_slits(theta,l=10.,h=10.):
	t=theta/180.*pi
	print("With collimating mirror:",sin(t)*2.*l*12764.33/14118.83)
	print("Without collimating mirror:",sin(t)*2.*l*12764.33/18103.83)
	return 

