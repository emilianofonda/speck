#EF 19/5/2011
#The following functions have been derived from the calibration made on 27/1/2010 and that of 11/9/2007.
#If something change, just modify the following equations. Theta is the pitch of the first mirror.

from PyTango import DevState, DeviceProxy
from time import sleep
from spec_syntax import mv
import os
import numpy

def tpp_aknowledge(x=None):
    securityTPP=DeviceProxy("d09-1-c00/ca/mir-secutpp")
    if x==None:
        x=securityTPP.read_attribute("AcknowledgeTPP").value
    else:
        securityTPP.write_attribute("AcknowledgeTPP",x)
    return x


def __Parabola(Points):
    x1,y1,x2,y2,x3,y3=\
    numpy.array([Points[0][0],Points[0][1],Points[1][0],Points[1][1],Points[2][0],Points[2][1]],'f')
    
    b=(y3-y1+(y1-y2)/(x1**2-x2**2)*(x1**2-x3**2))/\
    (x3-x1-(x2-x1)/(x1**2-x2**2)*(x1**2-x3**2))
    
    a=(y1-y2+b*(x2-x1))/(x1**2-x2**2)
    
    c=y1-a*x1*x1-b*x1
    
    print "y=a*x**2+b*x+c"
    print "a=",a
    print "b=",b
    print"c=",c
    return a,b,c

def __Parabolix(x,Points):
    a,b,c=__Parabola(Points)
    return a*x*x+b*x+c




#Mirror1
def __m1Z(theta):
    if theta<=1e-2:
        return -8.
    else:
        return 0.3
def __m1bender(theta,hgap=25.):
    if theta<=0.1:
        return 0.
    else:
        h40=74900.*theta+63750.
        h25=78375.*theta+38437.5
        h15=79300.*theta+21250.
        cible=__Parabolix(hgap,[[15,h15],[25,h25],[40,h40]])
        return cible

def __m1Roll(theta):
    return 0.

#Mirror2
def __m2theta(theta):
    if theta<=1e-2:
        return 0.
    else:
        return -4.4263e-1+1.2002*theta-3.3557e-2*theta*theta+1.8019e-3*theta*theta*theta

def __m2bender(theta,hgap=25.):
    if theta<=0.1:
        return 0.
    else:
        h40=92275.*theta-41312.5
        h25=87575.*theta-19562.5
        h15=87110.*theta-18125.
        cible=__Parabolix(hgap,[[15,h15],[25,h25],[40,h40]])
        return cible
        
def __m2Z(theta):
    base=24.6
    Max=24.9
    rate=-78.759
    xhalf=2.
    if theta<=1e-2:
        return 33.
    else:
        return base+(Max-base)*(theta**rate/(theta**rate+xhalf**rate))
        
def __m2Roll(theta):
    return -5.
#Girder
def __girder(theta):
    if theta<=1e-2:
        return 0.
    else:
        return -0.16033+2.0212*theta

#Tables
def __exafsZ(theta):
    #return 22.298+11.463*theta
    shell=get_ipython()
    dcm = shell.user_ns["dcm"]
    del shell
    return __girder(theta)*5.6+dcm.H
    
def __obxgZ(theta):
    shell=get_ipython()
    dcm = shell.user_ns["dcm"]
    del shell
    return __girder(theta)*5.6+dcm.H

#Alias for SEXAFS users
def SetAngleSEXAFS(theta=None,hgap=25.,SEXAFS=True):
    return SetAngle(theta,SEXAFS)
    

#Do the full job:
#Nouvelle procedure ... rustine!
def SetAngle(theta=None,hgap=25.,SEXAFS=True):
    """Close the vertical primary slits, align everything, open the primary slits back to the previous value.
    If the previous gap value in mm exceeds the mir1_pitch (mrad) the mir1_pitch (mrad) is taken as slit gap in mm.
    WARNING: uses global variables of the shell as the following:
    mir1_pitch, po1, po2...
    """
    shell=get_ipython()
    mir1_pitch = shell.user_ns["mir1_pitch"]
    mir2_pitch = shell.user_ns["mir2_pitch"]
    mir1_roll = shell.user_ns["mir1_roll"]
    mir2_roll = shell.user_ns["mir2_roll"]
    mir1_z = shell.user_ns["mir1_z"]
    mir2_z = shell.user_ns["mir2_z"]
    mir1_c = shell.user_ns["mir1_c"]
    mir2_c = shell.user_ns["mir2_c"]
    vgap1 = shell.user_ns["vgap1"] 
    po1 = shell.user_ns["po1"]
    po2 = shell.user_ns["po2"]
    po3 = shell.user_ns["po3"]
    po4 = shell.user_ns["po4"]
    po5 = shell.user_ns["po5"]
    FE = shell.user_ns["FE"]
    del shell

    theta2=mir1_pitch.pos()
    if theta==None:
        return mir1_pitch.pos()
    try:
        previous_vgap1=vgap1.pos()
        festate=FE.state()
        if festate==DevState.OPEN:
            print "Closing front End"
            if FE.close()==DevState.CLOSE:
                print "Front End closed"
            else:
                raise "Close on front end failed. Please close front end."
        #Turn on the girders motors
        po1.on()
        po2.on()
        po3.on()
        po4.on()
        po5.on()
        #
        #Wait two Galil cycles just in case...
        sleep(0.2)
        #Work around for tpp slow communication (old Galil, again)?
        __s=mir1_pitch.state()
        __s=mir2_pitch.state()
        #Start moving
        mv(mir1_pitch, theta, mir2_pitch, __m2theta(theta), \
        po1, __girder(theta), po2, __obxgZ(theta), po3, __exafsZ(theta),\
        po4, __exafsZ(theta), po5, __exafsZ(theta), \
        mir1_c, __m1bender(theta,hgap), mir2_c, __m2bender(theta,hgap) )
        mv(mir1_roll, __m1Roll(theta), mir2_roll, __m2Roll(theta))
        mv(mir1_z, __m1Z(theta), mir2_z, __m2Z(theta))
        #mir1_c.go(__m1bender(theta,hgap))
        #mir2_c.go(__m2bender(theta,hgap))
        #po1.go(__girder(theta))
        #po2.go(__obxgZ(theta))
        #po3.go(__exafsZ(theta))
        #po4.go(__exafsZ(theta))
        #po5.go(__exafsZ(theta))
        #mir1_pitch.pos(theta)
        #mir2_pitch.pos(__m2theta(theta))
        #mir1_roll.pos(__m1Roll(theta))
        #mir2_roll.pos(__m2Roll(theta))
        #mir1_z.pos(__m1Z(theta))
        #mir2_z.pos(__m2Z(theta))
        #
        #wait_motor([mir1_c,mir2_c,po1,po2,po3,po4,po5])
    except Exception, tmp:
        if tpp_aknowledge()<>0:
            print "TPP_security active... tring to continue..."
            print "Trying...",
            tpp_aknowledge(0)
            sleep(2.)
            mir1_c.go(__m1bender(theta,hgap))
            mir2_c.go(__m2bender(theta,hgap))
            mir1_pitch.pos(theta)
            mir1_roll.pos(__m1Roll(theta))
            mir1_z.pos(__m1Z(theta))
            mir2_pitch.pos(__m2theta(theta))
            mir2_roll.pos(__m2Roll(theta))
            mir2_z.pos(__m2Z(theta))
            wait_motor([po1,po2,po3,po4,po5])
            print " OK!"
        else:
            mir1_pitch.stop()
            mir2_pitch.stop()
            po1.stop()
            po2.stop()
            po3.stop()
            po4.stop()
            po5.stop()
            mir1_c.stop()
            mir2_c.stop()
            print "Stopping over error. Hint: Verify Security of tpp."
            print "After restoring alignement, verify primary slits! they can be closed."
            raise tmp
    if (previous_vgap1>theta): 
        if theta<1e-2:
            vgap1.pos(0.5)
        else:    
            vgap1.pos(theta-0.2)
    print "Primary vertical slits aperture: %6.4f mm"%(vgap1.pos())
    #Turn off the servo motors and less used steppers 
    po1.off()
    po2.off()
    #po3.off()
    po4.off()
    po5.off()
    if festate==DevState.OPEN:
        print "Opening back front end...",
        sleep(5)
        FE.open()
        if FE.state()==DevState.OPEN: 
            print "OK!"
        else:
            print "Front End did not open? Check Front End and interlocks please..."
    print "Now: \n1)find beam by scanning po3\n2)tune dcm (if using dcm)\n3)scan po3 again\n4)if necessary tune dcm again.\n"
    return mir1_pitch.pos()

