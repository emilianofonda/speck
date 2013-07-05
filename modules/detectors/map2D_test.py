from motor_class import *
from rontec_MCA import *
from time import *
from numpy import *

x=motor("")
y=motor("")
rontec=rontec_MCA("")
rontec_file="Rontec_Output.txt"
roi=[0,4095]
dt=1.

for xp in arange(x1,x2,dx):
	for yp in arange(y1,y2,dy):
		move_motor(x,xp,y,yp)
		rontec.count(dt)
		mca=rontec.saveMCA(rontec_file,roi[0],roi[1],comment="x=%g y=%g"%(xp,yp))

