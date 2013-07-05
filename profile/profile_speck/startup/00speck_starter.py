
#Import Python modules
import sys,os
import scipy

#Define environment
dn=os.getenv("SPECK")+os.sep+"modules"
sys.path.append(dn)
subdn=os.listdir(dn)
#print subdn
for i in subdn: sys.path.append(dn+os.sep+i)

#Import generic speck modules
import pymucal
from GracePlotter import *

#Import Control Related (PyTango related) modules
from PyTango import *
