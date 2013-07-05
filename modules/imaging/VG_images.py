#!/bin/env python

import time
import sys
import doctest

from PyTango import *
from pylab import *
#import matplotlib

class Dummy:
    pass

def set_attribute_value(DP, attribute_name, value):
    "Shortcut to set a new value to an attribute in one line."
    #_attr = DP.read_attribute(attribute_name)
    #_attr.value = value
    DP.write_attribute(attribute_name,value)

vg_tango_address = "i10-c-c01/dt/imag1-vg"
ia_tango_address = "i10-c-c01/dt/imag1-analyzer"
ROIOrig, ROISize = (130, 285), [340, 120]

#DP_vg = DeviceProxy(vg_tango_address)
#DP_ia = DeviceProxy(ia_tango_address)


#set_attribute_value(DP_ia, "EnableAutoROI", False)
#set_attribute_value(DP_ia, "EnableUserROI", True)
#DP_vg.command_inout("SetROI",[ROIOrig[1],ROIOrig[0],ROISize[1],ROISize[0]])

#set_attribute_value(DP_ia, "UserROIOriginX", ROIOrig[0])
#set_attribute_value(DP_ia, "UserROIOriginY", ROIOrig[1])
#set_attribute_value(DP_ia, "UserROIWidth", ROISize[0])
#set_attribute_value(DP_ia, "UserROIHeight", ROISize[1])


class VideoIntensityMonitor:
    """ Convert a VideoGraber tango device in a beam intensity monitor.
        needs the origin and size of the ROI to catch the beam.
        ROIdef = (ROIOrig, ROISize) example:(130, 285), [340, 120]
        self.DP.
        
        >>> V = VideoIntensityMonitor("i10-c-c01/dt/imag1-vg", "Image", ROIdef= ((88, 285), [424, 120]))
        >>> V.read_image()
        >>> V.get_imageStats()
        >>> assert V.read() != 0
    """
    
    def __init__(self, device_name, attribute_name, ROIdef=None):
        
        self.devName = device_name
        self.DP = DeviceProxy(device_name)
        #self.DP.ping()
	self.attribute_name = attribute_name
        self.ROIOrig, self.ROISize = ROIdef
        
        # Uses a dummy integration time of 0.05 ms (theoritical for 20 frams per/sec)
	self.it = Dummy()
	self.it.value = 0.2
        self.counter = False
        
        # Set the ROI
        #set_attribute_value(self.DP, "EnableAutoROI", False)
        #set_attribute_value(self.DP, "EnableUserROI", True)
        self.DP.command_inout("SetROI",[self.ROIOrig[0],self.ROIOrig[1],
                                        self.ROISize[0],self.ROISize[1]])
        
        self.image = None
        self.image_array = None
        
        # wait a little for that the 1st image is loaded by
        time.sleep(self.it.value) 
    
    def __str__(self):
        return "SENSOR: VideoIntensityMonitor %s" % self.devName
    
    
    def read_image(self):    
        i=0 ; Done=False
        while (not Done) and i < 3:
            i+=1
            try:
                self.image = self.DP.read_attribute(self.attribute_name)
                return
            except:
                print time.ctime(),"Mince",i, self.devName
        
        print "Mince de Mince, impossible de lire le sensor", self 
        return 0
    
    def setAutoROI(self):
        """Before doing that the blades needs to be open completely.
           Just do a vertical and horizontal projection, find the edge
           using a sigma cutoff, and calculate the orgin and size of the ROI.
           One can add an horiz_border and vertical_border.            
        """
        pass
    
    def get_image(self):
        if self.image == None:
            self.read_image()
        return self.image  
    
    def get_image_array(self):
        if self.image == None:
            self.read_image()
        self.image_array = array(self.image.value)
        self.image_array.shape = self.image.dim_y, self.image.dim_x
        return self.image_array 
            
    def get_imageStats(self, verbose=0):
        self.read_image()
        len_border = 3*self.ROISize[0]
        
        ia = array(self.image.value)
        border = ia[-len_border:]
        _stats = mean(border), median(border), std(border),\
                                   sum(ia),min(ia),max(ia),\
                                   sum(ia) - len(ia)*mean(border)
        if verbose:
            print "MeanBkgrd: %.1f  Median: %.1f  StdBkgrd: %.1f" % _stats[:3]
            print "Sum: %d  Min:  %5d Max:  %5d  I: %.1f" % _stats[3:],
        return _stats
        #ia[-len_border:] = ones((len_border))*1000
        #print "elapsed time read: %.4f convert to array + sum: %.4f" % (t1-t0, t2-t1)    
    
    def _read1(self):
        
        self.read_image()
        len_border = 3*self.ROISize[0]
        
        ia = array(self.image.value)
        border = ia[-len_border:]
        
        return sum(ia) - len(ia) * mean(border)
    
    def _read2(self, strong=10):
        
        self.read_image()
        len_border = 3*self.ROISize[0]
        
        ia = array(self.image.value)
        border = ia[-len_border:]
        signal_value = mean(border) + strong * std(border)
        
        return sum(iabeam) - len(iabeam) * mean(border)
    
    def _selectBeamEdge(self, axis=0, increment=0.05):
        
        ia = self.get_image_array()        

        cutoff = 1
        _proj = sum(ia, axis=axis)

        for i in range(int(1/increment - 1)):
            cutoff += increment
            _filter = (_proj >= (max(_proj) * cutoff)) * 1
            edges = (_filter[1:] - _filter[:-1]) 
            #print edges[:10], "...", edges[-10:]
            nedge = sum((_filter[1:] - _filter[:-1]) == 1)
            print "Cutoff = %5.2f   nedge = %5d" % (cutoff, nedge)
            
    
    def _read3(self, strong=10):
        
        self.read_image()
        len_border = 3*self.ROISize[0]
        
        ia = array(self.image.value)
        border = ia[-len_border:]
        signal_value = mean(border) + strong * std(border)
        
        print "RMSd = %7.1f" % std(border),
        iabeam = compress((ia>=signal_value),ia)
        ia = ia * ( ia >= signal_value)
        ia.shape = self.image.dim_y, self.image.dim_x
        #imshow(ia)
        sum0 = sum(ia, axis=0)
        sum1 = sum(ia, axis=1)
        plot(sum0 * (sum0 >= max(sum0)/3.))
        
        plot(sum1 * (sum1 >= max(sum1)/3.))
        plot(sum(ia, axis=0))
        plot(sum(ia, axis=-1))
        show()
        return sum(iabeam) - len(iabeam) * mean(border)

    def read(self):
        #return self._read1(), self._read2()
        return self._read2()

def get_Image(DPVG):
    len_border = 3*ROISize[0]
    t0 = time.time()
    i = DPVG.read_attribute("Image")
    t1 = time.time()
    ia = array(i.value)
    ia_border = ia[-len_border:]
    print len(ia_border), ia_border
    print "Border: Mean = %.2f  Std = %.2f Sum: %d" % (mean(ia_border), std(ia_border), sum(ia)),
    print "Min:  %5d Max:  %5d" % (min(ia), max(ia))
    t2 = time.time()
    #ia[-len_border:] = ones((len_border))*1000
    ia.shape = i.dim_y, i.dim_x
    #print "elapsed time read: %.4f convert to array + sum: %.4f" % (t1-t0, t2-t1)
    return ia
    

def get_ROIImage(DPIA):
    t0 = time.time()
    i = DPIA.read_attribute("ROIImage")
    t1 = time.time()
    ia = array(i.value)
    t2 = time.time()
    ia.shape = i.dim_y, i.dim_x
    print "elapsed time read: %.3f convert to array: %.3f" % (t1-t0, t2-t1)
    #iax = add.reduce(ia, axis=0)
    #iay = add.reduce(ia, axis=1)
    #plot(iax)
    #plot(iay)
    #show()
    return ia


def get_Profiles():    
    t0 = time.time()
    px = DP_ia.read_attribute("XProfile")
    #py = DP_ia.read_attribute("YProfile")
    #py = DP_ia.read_attribute("YProfile")
    t1 = time.time()
    pxa = array(px.value)
    t2 = time.time()
    print "elapsed time read: %.3f convert to array: %.4f" % (t1-t0, t2-t1)
    #ia.shape = i.dim_y, i.dim_x
    #return pxa
    #iax = add.reduce(ia, axis=0)
    #iay = add.reduce(ia, axis=1)
    #plot(iax)
    #plot(iay)
    #show()

def timingTest():
    images = []

    time.sleep(0.2)
    T0 = time.time()

    for a in range(5):
        images.append(get_Image(DP_vg))
        #get_Profiles()
    print "Total time = %.3f" % (time.time() -T0)        

def showTest():
    imshow(get_Image(DP_vg))
    show()

def _test():
    import doctest         # replace M with your module's name
    return doctest.testmod()   # ditto

def _test2():
    V = VideoIntensityMonitor("i10-c-c01/dt/imag1-vg", "Image", ROIdef= ((88, 285), [424, 120]))
    for i in range(1):
        t0 = time.time()
        #I = V._read3()
        V._selectBeamEdge(axis=0, increment=0.05)
        V._selectBeamEdge(axis=1, increment=0.05)
        #print "I = %8.0f\t\t readed in %.3f sec" % (I, time.time()-t0) 

if __name__ == "__main__":

    _test()

