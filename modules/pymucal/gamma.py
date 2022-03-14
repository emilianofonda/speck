from __future__ import division
from __future__ import print_function
from builtins import range
from past.utils import old_div
from numpy import array,resize,size,log,exp,log10,interp
from pymucal import *

def locat(x0,x):
    locat=0
    u=size(x)	
    while ((u-locat)>1):
        m=(old_div((u+locat),2))
        if(x0<x[m-1]):
            u=m
        else:
            locat=m
    return locat

def line_interp(x,y,x0):
    #pos=locat(x0,x)
    #pos = min( max(pos,0) , 7 )
    #print "pos=",pos
    #m=0.0
    #q=0.0 
    #p0=m,q
    #print "x,y=",x[pos-1:pos+1],y[pos-1:pos+1]
    #p=optimize.leastsq(linear_residual,p0,args=(x[pos-1:pos+1],y[pos-1:pos+1]))[0]
    #y_interp=p[0]*x0+p[1]
    #y_interp=y[pos-1]+((y[pos]-y[pos-1])/(x[pos]-x[pos-1]))*(x0-x[pos-1])
    #return y_interp
    return interp(x0,x,y)

def setgam(iz, ihole):
    "This function is an adaptation not authorized and not guaranteed in any way of the gamach subroutine of Feff810d.\n Use it under your own responsability and not for commercial use."

#c     Sets gamach, core hole lifetime.  Data comes from graphs in
#c     K. Rahkonen and K. Krause,
#c     Atomic Data and Nuclear Data Tables, Vol 14, Number 2, 1974.

        # implicit double precision (a-h, o-z)

    zh=array([0.99,  10.0, 20.0, 40.0, 50.0, 60.0, 80.0, 95.1,
      0.99, 18.0, 22.0, 35.0, 50.0, 52.0, 75.0,  95.1,
      0.99,  17.0, 28.0, 31.0, 45.0, 60.0,  80.0, 95.1,
      0.99,  17.0, 28.0, 31.0, 45.0, 60.0,  80.0, 95.1,
      0.99,  20.0, 28.0, 30.0, 36.0, 53.0,  80.0, 95.1,
      0.99,  20.0, 22.0, 30.0, 40.0, 68.0,  80.0, 95.1,
      0.99,  20.0, 22.0, 30.0, 40.0, 68.0,  80.0, 95.1,
      0.99,  36.0, 40.0, 48.0, 58.0, 76.0,  79.0, 95.1,
      0.99,  36.0, 40.0, 48.0, 58.0, 76.0,  79.0, 95.1,
      0.99,  30.0, 40.0, 47.0, 50.0, 63.0,  80.0, 95.1,
      0.99,  40.0, 42.0, 49.0, 54.0, 70.0,  87.0, 95.1,
      0.99,  40.0, 42.0, 49.0, 54.0, 70.0,  87.0, 95.1,
      0.99,  40.0, 50.0, 55.0, 60.0, 70.0,  81.0, 95.1,
      0.99,  40.0, 50.0, 55.0, 60.0, 70.0,  81.0, 95.1,
      0.99,  71.0, 73.0, 79.0, 86.0, 90.0,  95.0,100.0,
      0.99,  71.0, 73.0, 79.0, 86.0, 90.0,  95.0,100.0],'f')

    zh=resize(zh,(16,8))

    gamh=array([0.02,  0.28, 0.75,  4.8, 10.5, 21.0, 60.0, 105.0,
      0.07,  3.9,  3.8,  7.0,  6.0,  3.7,  8.0,  19.0,
      0.001, 0.12,  1.4,  0.8,  2.6,  4.1,   6.3, 10.5,
      0.001, 0.12, 0.55,  0.7,  2.1,  3.5,   5.4,  9.0,
      0.001,  1.0,  2.9,  2.2,  5.5, 10.0,  22.0, 22.0,
      0.001,0.001,  0.5,  2.0,  2.6, 11.0,  15.0, 16.0,
      0.001,0.001,  0.5,  2.0,  2.6, 11.0,  10.0, 10.0,
      0.0006,0.09, 0.07, 0.48,  1.0,  4.0,   2.7,  4.7,
      0.0006,0.09, 0.07, 0.48, 0.87,  2.2,   2.5,  4.3,
      0.001,0.001,  6.2,  7.0,  3.2, 12.0,  16.0, 13.0,
      0.001,0.001,  1.9, 16.0,  2.7, 13.0,  13.0,  8.0,
      0.001,0.001,  1.9, 16.0,  2.7, 13.0,  13.0,  8.0,
      0.001,0.001, 0.15,  0.1,  0.8,  8.0,   8.0,  5.0,
      0.001,0.001, 0.15,  0.1,  0.8,  8.0,   8.0,  5.0,
      0.001,0.001, 0.05, 0.22,  0.1, 0.16,   0.5,  0.9,
      0.001,0.001, 0.05, 0.22,  0.1, 0.16,   0.5,  0.9],'f')

    gamh=resize(gamh,(16,8))
    
    zk=array(zeros(8)*0.1)
    gamkp=array(zeros(8)*0.1)
    ryd  = 13.6056980
    hart = 2*ryd

    #c     Note that 0.99 replaces 1.0, 95.1 replaces 95.0 to avoid roundoff
    #c     trouble.
    #c     Gam arrays contain the gamma values.
    #c     We will take log10 of the gamma values so we can do linear
    #c     interpolation from a log plot.
    
    if(ihole<=0):
        print("Zero or Negative hole number. Abort.")
        return nan
    if (ihole>16):
        print('No data. Gamma set to 0.1 eV for O1 and higher holes')
        return 0.1
    if (ihole<=16):
        for i in range(8):
            gamkp[i]=log10(gamh[ihole-1,i])
            zk[i] = zh[ihole-1,i]
        
        gamach=line_interp(zk,gamkp,float(iz))
    else:
        print("gamach is set to 0.1eV for any O-hole for any element.")
        gamach = -1.0
    #c     Change from log10(gamma) to gamma
    gamach = 10.0 ** gamach
    return gamach

