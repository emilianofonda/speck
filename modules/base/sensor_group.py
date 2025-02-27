from __future__ import print_function
from builtins import range
from builtins import object
import PyTango
from numpy import nan
from time import sleep
class sensor_group(object):
    def __init__(self,dev_atts={},functions=[]):
        """
        The idea is to have a group of data collected at the same time from
        TANGO devices and from user defined functions.
        dev_atts is a list of lists of the form:
        [  ["device1",["attribute1","attribute2"]], ["device2",["oneattribute",], ["device3":...] ]
        """
        self.dev_atts=dev_atts
        self.functions=functions
        self.DPS={}
        for i in dev_atts:
            try:
                self.DPS[i[0]]=PyTango.DeviceProxy(i[0])
            except:
                print("Device Proxy: %s does not exist or it is not connected."%i)
        self.user_readconfig=[]
        for i in self.dev_atts:
        #for j in i[1]:
            self.user_readconfig+=self.DPS[i[0]].get_attribute_config(i[1])
        #ac.label=i[1]
        #ac.format=i[2]
        #ac.unit=i[3]
        return

    def __repr__(self):
        tmp=self.read()
        s=""
        for i in range(len(tmp)):
            s0=self.user_readconfig[i].label+"="+self.user_readconfig[i].format+self.user_readconfig[i].unit+"\n"
            s+=s0%(tmp[i])
        return s
        
    def call(self):
        return self.read()

    def read(self):
        retour=[]
        for i in self.dev_atts:
            again = True
            againN = 0
            while again:
                try:
                    retour += [x.value for x in self.DPS[i[0]].read_attributes(i[1])]
                    again = False
                except Exception as tmp:
                    if againN < 3:
                        againN += 1
                        sleep(0.1)
                    else:
                        print("Maximum retrial exceeded, original exception follows")
                        raise tmp
        for i in self.functions:
            tmp = i()
            if type(tmp) == list:
                retour += tmp
            else:
                retour.append(tmp)
        return retour

