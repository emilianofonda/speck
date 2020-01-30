#Johann geometry, "Scheinhost type": crystal is located in the XY plane as the incoming beam and the sample. 

#Crystal analyzer has radius R

import numpy as npy
from time import  sleep
import pymucal 
from pylab import plot,figure,xlim,ylim,title,arange,text,xlabel,ylabel,draw
from p_spec_syntax import move_motor, go_motor, wait_motor
from PyTango import DevState


class JohannAnalyzer:
    def __init__(self,atom="Si",h=1,k=1,l=1,order=1,R=1,A=0.05,alpha=0.,detectorsize=0.3,beamsize=3e-4,angleMax=85,angleMin=55.):
        """
        the crystal can be (atom) "Si" or "Ge"
        h,k,l are the miller indices of a diamond type crystal
        the order multiplies all indices
        R is the curvature radius in meters
        A is the radius of the crystal mask in meters
        alpha is the cut asymmetry (miscut) in degrees
        detectorsize is the length of the used detector (for drawing) in meters
        beamsize is the FWHM of the beam in Z direction (or other dominant component, actually)
        beamsize is in meters: typical value 3e-4m (300microns)
        """
        self.angleMin = angleMin
        self.angleMax = angleMax
        #extinction rules
        #Allowed:
        #H,K,L all odd
        #H,K,L all even and H+K+L = 4n
        Oddity = (npy.mod(h*order,2) and npy.mod(k*order,2) and npy.mod(l*order,2))
        Evenly = (not npy.mod(h*order,2) and not npy.mod(k*order,2) and not npy.mod(l*order,2))
        if Oddity or (Evenly and not npy.mod(order*(h+k+l),4)):
                #K. O. Kvashnina and A. C. Scheinost, Journal of Synchrotron Radiation 23 (3), 836-841 (2016).
                self.lattice_a={"Ge":5.6574,"Si":5.4309}
                #
                #self.d = a[atom]/(npy.sqrt(h*h+k*k+l*l)*order)
                self.atom=atom
                self.R=R
                self.A=A
                self.poisson={"Si":0.22,"Ge":0.27}
                self.detectorsize=detectorsize
                self.beamsize = beamsize
                self.alpha=alpha
                self.h, self.k, self.l, self.order = h,k,l,order
                print "Angle Min:  %4.2f    Energy Max: %5.1f   Resolution: %3.1f"%(self.angleMin,self.theta2e(self.angleMin),self.resolution(self.theta2e(self.angleMin)))
                print "Angle Max:  %4.2f    Energy Min: %5.1f   Resolution: %3.1f"%(self.angleMax,self.theta2e(self.angleMax),self.resolution(self.theta2e(self.angleMax)))
        else:
            print("#extinction rules:\n Allowed:\n H,K,L all odd\n H,K,L all even and H+K+L = 4n")
            print("Forbidden reflection: extinction rules apply!")
        return
        

    def e2theta(self,energy):
        return npy.arcsin(12398.41857/\
        (2.*energy*self.lattice_a[self.atom]/(npy.sqrt(self.h**2+self.k**2+self.l**2)*self.order))\
        )*180./npy.pi   

    def theta2e(self,theta):
        return 12398.41857/(2.*self.lattice_a[self.atom]/(npy.sqrt(self.h**2+self.k**2+self.l**2)*self.order)\
        *npy.sin(theta/180.*npy.pi))

    def crystalXY(self,theta):
        """theta is in degrees, it's the incidence angle on the crystal
        R is the radius of the crystal, the Rowland circle has radius r=0.5*R"""
        x = self.R * npy.sin(theta*npy.pi/180.)
        y = 0.*theta
        return x,y

    def detectorXY(self,theta):
        """theta is in degrees, it's the incidence angle on the crystal
        R is the radius of the crystal, the Rowland circle has radius r=0.5*R"""
        x = 2 * self.R * npy.sin(theta*npy.pi/180.)*npy.cos(theta*npy.pi/180.)**2
        y = 2 * self.R * npy.cos(theta*npy.pi/180.)*npy.sin(theta*npy.pi/180.)**2
        return x,y

    def detectorTheta(self,theta):
        """Just to remeber, the detector looks down to crystal with angle 180-2*theta"""
        return 2 * theta 


    def crystalLine(self,theta):
        """return two points delimiting the crystal to draw it schematically
        """
        dx = self.A * npy.cos(theta/180.*npy.pi)
        dy = self.A * npy.sin(theta/180.*npy.pi)
        return npy.array(zip(
        self.crystalXY(theta=theta) + npy.array([dx,dy]),
        self.crystalXY(theta=theta) + npy.array([-dx,-dy])))
    
    def detectorLine(self,theta):
        """return two points delimiting the detector to draw it schematically
        size is the length of the detector"""
        dx = -self.detectorsize * npy.cos((2*theta-180.)/180.*npy.pi)
        dy = -self.detectorsize * npy.sin((2*theta-180.)/180.*npy.pi)
        return npy.array(zip(
        self.detectorXY(theta=theta) + npy.array([0,0]),
        self.detectorXY(theta=theta) + npy.array([dx,dy])))
    
    def test(self,t0=20,t1=80,dt=5):
        f1=figure(1,figsize=(10,10))
        f1.clear()
        title(r"Johann Geometry %4.2f<$\theta$<%4.2fdeg $R_{crystal}=%4.2fm$"%(t0,t1,self.R))
        for t in arange(t0,t1+dt,dt):
            plot(*self.detectorXY(t),marker="o")
            plot(*self.crystalXY(t),marker="o")
            plot(*zip([0,0],self.crystalXY(t),self.detectorXY(t)))
            plot(*self.crystalLine(theta=t),linewidth=4)
            plot(*self.detectorLine(theta=t),linewidth=10)
            t0x,t0y=self.detectorLine(theta=t)[:,1]
            text(t0x,t0y,"%i"%t,rotation=2*t)
        xlim(-self.detectorsize,self.R+self.detectorsize)
        ylim(-self.detectorsize,self.R+self.detectorsize)
        xlabel("X(m)")
        ylabel("Z(m)")
        draw()
        return


    def resolutionBeamSize(self,theta):
        """theta is the Bragg angle in degrees
        """
        return (self.beamsize/(self.R*npy.sin((theta-self.alpha)/180.*npy.pi)))**2
    
    def resolutionJohannAberration(self,theta):
        """theta is the Bragg angle in degrees
        (the crystal is supposed to be a round wafer of radius A)
        """
        return 0.125*(self.A/(self.R*npy.sin((theta-self.alpha)/180.*npy.pi)))**2\
        /(npy.tan((theta-self.alpha)/180.*npy.pi) * npy.tan(theta/180.*npy.pi))
        #return deltaThetaJohann / npy.tan(theta)

    def resolutionBentCrystal(self,theta,energy):
        """theta is the Bragg angle
        energy is the energy of the analyzed radiation in eV
        """
        t=npy.log(2.)/(pymucal.muro(self.atom,energy)*pymucal.atomic_data(self.atom).density)/100.
        return t/self.R*(1/npy.tan(theta/180.*npy.pi)-2*self.poisson[self.atom])

    def resolution(self,energy):
        """Gives the approximate resolution of the crystal analyzer at a given energy in eV)"""
        if type(energy) in [list,tuple,npy.ndarray]:
            return npy.array([(en*npy.sqrt(self.resolutionBentCrystal(self.e2theta(en),en)**2+\
            self.resolutionJohannAberration(self.e2theta(en))**2+\
            self.resolutionBeamSize(self.e2theta(en))**2)) for en in energy])
        else:
            theta=self.e2theta(energy)
            return energy*npy.sqrt(self.resolutionBentCrystal(theta,energy)**2+\
            self.resolutionJohannAberration(theta)**2+\
            self.resolutionBeamSize(theta)**2)

    def position(self,energy):
        """Gives the position of the crystal and the detectors in meters and degrees in a dictionary
        CT = crystal theta
        CX = position in X of the crystal
        CZ = position in Z of the crystal (always 0, here)
        DX = detector position in X
        DZ = detector position in Z
        DT = rotation of the detector
        """
        __tmp={}
        theta = self.e2theta(energy)
        __tmp["CT"] = theta
        __tmp["DT"]= self.detectorTheta(theta)
        __tmp["CX"], __tmp["CZ"] = self.crystalXY(theta)
        __tmp["DX"], __tmp["DZ"] = self.detectorXY(theta)
        
        return __tmp 

    def airTransmission(self,energy):
        """Gives the approximate resolution of the crystal analyzer at a given energy in eV)"""
        if type(energy) in [list,tuple,npy.ndarray]:
            out=[]
            for ee in energy:
                p = self.position(ee)
                ltot = p["CX"]+npy.sqrt(p["DX"]**2+p["DZ"]**2)
                out.append(npy.exp(-2.*pymucal.atomic_data("N").weight*101325./(8.314462*293.)*\
                1e-6*pymucal.muro("N",ee)*ltot*100))
            return npy.array(out)
        else:
            p = self.position(energy)
            ltot = p["CX"]+npy.sqrt(p["DX"]**2+p["DZ"]**2)
            return npy.exp(-2.*pymucal.atomic_data("N").weight*101325./(8.314462*293.)*\
            1e-6*pymucal.muro("N",energy)*ltot*100)


class JohannSpectro:
    def __init__(self,motors={},Geometry={}):
        """
        motors is dictionary assigning the right motor to the right axis
        e.g. "crystalTheta":"speckNameForCrystalTheta"
        if no axis axis exist for a movement just not define it.
        Some motors have to be defined in any case:
        "crystal_theta"
        "crystal_x"
        "detector_theta"
        "detector_x"
        "detector_z"

        The geometry dictionary correspond to the necessary data to define a JohannAnalyzer (see class JohannAnalyzer)
        Defaults are
        {"atom":"Si","hkl":[1,1,1],"order":1,"R":1,"A":0.05,"alpha":0.,"detectorsize":0.3,"beamsize":3e-4,"angleMax":85,"angleMin":55.}

        If any parameter in Geometry dictionary is changed after creating the object, the reinit function must be called to apply the change.

        """
        self.offset_crystal_theta=0.
        self.delay=0.1
        self.deadtime=0.1
        self.mode=1
        self.motors = motors
        self.label = self.motors["crystal_theta"].label
        #for i in motors.keys():
        #    if i in ["crystal_theta","crystal_x","detector_theta","detector_x","detector_z"]:
        #        setattr(self,i,motors[i])
        self.Geometry={"atom":"Si","hkl":[1,1,1],"order":1,"R":1,"A":0.05,"alpha":0.,"detectorsize":0.3,"beamsize":3e-4,"angleMax":85,"angleMin":55.}
        for i in Geometry.keys():
            if i in ["atom","hkl","order","R","A","alpha","detectorsize","beamsize","angleMax","angleMin"]:
                self.Geometry[i]=Geometry[i]
        for i in self.Geometry.keys():
                setattr(self,i,self.Geometry[i])
        self.Analyzer=JohannAnalyzer(atom=self.atom,h=self.hkl[0],k=self.hkl[1],l=self.hkl[2],
        order=self.order,R=self.R,A=self.A,alpha=self.alpha,detectorsize=self.detectorsize,beamsize=self.beamsize,
        angleMax=self.angleMax,angleMin=self.angleMin)
        return

    def reinit(self):
        for i in self.Geometry.keys():
            if i in ["atom","hkl","order","R","A","alpha","detectorsize","beamsize","angleMax","angleMin"]:
                setattr(self,i,self.Geometry[i])
        self.Analyzer=JohannAnalyzer(atom=self.atom,h=self.hkl[0],k=self.hkl[1],l=self.hkl[2],
        order=self.order,R=self.R,A=self.A,alpha=self.alpha,detectorsize=self.detectorsize,beamsize=self.beamsize,
        angleMax=self.angleMax,angleMin=self.angleMin)
        return
    
    def status(self):
        for i in self.motors.keys():
            print "%s at %6.4f"%(i,self.motors[i].pos())
        if self.mode == 0:
            return "Mode = 0 ==> Analyzer Move in Angular Mode"
        elif self.mode == 1:
            return "Mode = 1 ==> Analyzer Move in Energy  Mode"
        else:
            print "Bad mode selected. mode can be 0 (angle) or 1 (energy) only."
        print "Analyzer Crystal Theta Offset = %6.4f"%(self.offset_crystal_theta)
    def __call__(self):
        Geometry=self.Geometry
        if self.mode == 0:
            return "Crystal %s%s order= %i is at %6.2fdeg"%(Geometry["atom"],tuple(Geometry["hkl"]),Geometry["order"],self.pos())
        if self.mode == 1:
            return "Crystal %s%s order= %i is at %6.2feV"%(Geometry["atom"],tuple(Geometry["hkl"]),Geometry["order"],self.pos())
    
    def state(self):
        for i in self.motors.keys():
            _s=self.motors[i].state()
            if _s==DevState.MOVING:
                return DevState.MOVING
            if _s==DevState.FAULT:
                return DevState.FAULT
            if _s==DevState.UNKNOWN:
                return DevState.UNKNOWN
            if _s== DevState.OFF:
                return DevState.OFF
            if _s==DevState.INIT:
                return DevState.INIT
            if _s==DevState.ALARM:
                return DevState.ALARM
        return DevState.STANDBY

    def stop(self):
        for i in self.motors.keys():
            self.motors[i].stop()
        return self.state()

    def off(self):
        for i in self.motors.keys():
            self.motors[i].off()
        return self.state()

    def on(self):
        for i in self.motors.keys():
            self.motors[i].on()
        return self.state()
    def go(self,position=None):
        return self.pos(position,wait=False)

    def pos(self,position=None,wait=True):
        """The position can be angle or energy depending on the attribute mode:
        self.mode=0   angle
        self.mode=1   energy (default)
        """
        if position == None:
            if self.mode == 0:
                return self.motors["crystal_theta"].pos() + self.offset_crystal_theta
            elif self.mode == 1:
                return self.Analyzer.theta2e(self.motors["crystal_theta"].pos() + self.offset_crystal_theta)
        if self.mode == 0:
            thC = position - self.offset_crystal_theta
        elif self.mode == 1:
            thC = self.Analyzer.e2theta(position) - self.offset_crystal_theta
        else:
            print "Bad mode defined, I will not move. Modes are 0 for angle and 1 for energy"
            return
        if self.state() not in [DevState.ALARM, DevState.STANDBY]:
            raise Exception("Cannot move if state is %s"%self.state())
        xD,zD = self.Analyzer.detectorXY(thC)
        xC,zC = self.Analyzer.crystalXY(thC)
        thD = self.Analyzer.detectorTheta(thC)
        go_motor(
        self.motors["crystal_theta"],thC,
        self.motors["crystal_x"],xC*1000.,
        self.motors["detector_theta"],thD,
        self.motors["detector_x"],xD*1000.,
        self.motors["detector_z"],zD*1000.,
        )
        if wait:
            wait_motor([self.motors["crystal_theta"],self.motors["crystal_x"],\
            self.motors["detector_theta"],self.motors["detector_x"],self.motors["detector_z"]],verbose=False)
        return self.pos()

