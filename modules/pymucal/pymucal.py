from __future__ import print_function
#Acknowledgments

# 	Interface to the python version of the mucal fortran subroutine Revision 1.9.1 4/25/98.
#	Mucal is based on the McMaster tables of 1969.
# 	The python version has been written by Emiliano Fonda.
# 	For credits, authors et cetera... look inside the mucal source code.
# 	There is no warranty, not for the mucal not for the interface.
# 	Thanks to all the people who wrote mucal, scipy, Numeric, ...

# 	pymucal contains information coming from the setgam module.
# 	These info are the gamma corehole widths as from the Krause paper of 1979
# 	and this procedure has been translated from fortran to python using the Feff810d implementation.
# 	There is no warranty and no authorisation for commercial use.
# 	Actually, the procedure is so simple that could be simply rewritten on the basis of a table of values,
# 	if these constraints are a problem.
#-------------------------------------------------------------------------------------
# 	For any problem about copyright and so on... simply do not bother me.

# Beware
# The mucal modules keeps the keV scale, while pymucal makes the interface and expects eV

# The gamma, mucal and pymucal modules require numpy

from builtins import range
from builtins import object
import sys
from numpy import zeros,log,log10,exp,size,resize

import mucal
import gamma

def muro(atom="N",energy=9000):
    "muro is a simple way of obtaining total absorption in cm**2/g (energy is in keV)\n Defaults are atom=\"N\" and energy=9000 eV."
    xsec=zeros(10)*0.1
    edges=zeros(9)*0.1
    fly=zeros(4)*0.1
    if (len(atom)==1):
        atom=atom+" "
    erf=int(1)
    er=int(0)
    unit='C'

    for i in range(len(xsec)):
        xsec[i]=0.0
    for i in range(len(edges)):
        edges[i]=0.0
    for i in range(len(fly)):
        fly[i]=0.0
    z=int(0)
    eout=0.
    eout,atom,z,unit,xsec,edges,fly,erf,er=mucal.mucal(energy/1000.,atom,z,unit,xsec,edges,fly,erf,er)
    if (er):
        print(eout,atom,z,unit,xsec,edges,fly,erf,er)
        print("Error er=",er)
        return  nan
    return xsec[3]

class atomic_data(object):
    "Atomic_data class is a python way to interface the mucal fortran subroutine and some more subroutines to obtain a sort of small x-ray periodic table.\n Usage: atomic_data is a class: e.g. myatom=atomic_data(\"atom_name\"). \n Attributes energy(default=9000 eV), weight, density, fluoyield, edge, error.\n A useful function is xsection(self.energy) returns a dictionary of the xsections.\n \n The gamma attribute is a dictionary containing the core hole widths as per Krause, Oliver J. Phys. Chem. Ref. Data 8 329 (1979): the table has been converted from the original fortran code contained in feff810d."

    def __init__(self,name):
        if (not(name in self.atoms)):
            print("Atom non recognised (case sensitive).")
            return None
        self.z=self.atoms[name]
        if (len(name)==1):
            name=name+" "
        self.name=name
        self.energy=9000.
        xsec=zeros(10)*0.1
        edges=zeros(9)*0.1
        fly=zeros(4)*0.1
        zz=int(0)
        erf=int(1)
        self.error=int(0)
        unit='C'

        for i in range(len(xsec)):
            xsec[i]=0.0
        for i in range(len(edges)):
            edges[i]=0.0
        for i in range(len(fly)):
            fly[i]=0.0

        atom=self.name
        mucal.mucal(self.energy/1000.,atom,zz,unit,xsec,edges,fly,erf,self.error)
        self.weight=xsec[6]
        self.density=xsec[7]
        self.edge={"k":edges[0]*1e3,
                "l1":edges[1]*1e3,
                "l2":edges[2]*1e3,
                "l3":edges[3]*1e3,
                "m4":edges[4]*1e3,
                "ka1":edges[5]*1e3,
                "kb1":edges[6]*1e3,
                "la1":edges[7]*1e3,
                "lb1":edges[8]*1e3}
        self.fluoyield={"k":fly[0],
                "l1":fly[1],
                "l2":fly[2],
                "l3":fly[3]}
        self.gamma={"k":gamma.setgam(self.z,1),
                "l1":gamma.setgam(self.z,2),
                "l2":gamma.setgam(self.z,3),
                "l3":gamma.setgam(self.z,4),
                "m1":gamma.setgam(self.z,5),
                "m2":gamma.setgam(self.z,6),
                "m3":gamma.setgam(self.z,7),
                "m4":gamma.setgam(self.z,8),
                "m5":gamma.setgam(self.z,9),
                "n1":gamma.setgam(self.z,10),
                "n2":gamma.setgam(self.z,11),
                "n3":gamma.setgam(self.z,12),
                "n4":gamma.setgam(self.z,13),
                "n5":gamma.setgam(self.z,14),
                "n6":gamma.setgam(self.z,15),
                "n7":gamma.setgam(self.z,16),
                }

    def __repr__(self):
        l="Element: %2s Weight: %8.5f Density: %8.5f \n"%(self.name,self.weight,self.density)
        l+="Absorption Energies:\n"
        for i in ["k","l1","l2","l3","m4"]:
            l+="%s at %8.5f\n"%(i,self.edge[i])
        l+="Fluorescence Energies:\n"
        for i in ["ka1","kb1","la1","lb1"]:
            l+="%s at %8.5f\n"%(i,self.edge[i])
        return l

    def xsection(self,energy):
        self.energy=energy
        xsec=zeros(10)*0.1
        edges=zeros(9)*0.1
        fly=zeros(4)*0.1
        zz=int(0)
        erf=int(1)
        self.error=int(0)
        unit='C'

        atom=self.name
        mucal.mucal(self.energy*1.e-3,atom,zz,unit,xsec,edges,fly,erf,self.error)
        xsection={"photoel":xsec[0],
            "coherent":xsec[1],
            "incoherent":xsec[2],
            "total":xsec[3],
            "conversion":xsec[4],
            "mu":xsec[5],
            "l2jump":xsec[8],
            "l3jump":xsec[9]}
        return xsection
    

    #Number of Avogadro
    NA=6.02213670e23

    atoms={'H':1,'He':2,
    'Li':3, 'Be':4,'B':5, 'C':6, 'N':7, 'O':8, 'F':9,'Ne':10,
    'Na':11, 'Mg':12, 'Al':13, 'Si':14,'P':15, 'S':16,'Cl':17, 'Ar':18,
    'K':19,'Ca':20, 'Sc':21, 'Ti':22, 'V':23, 'Cr':24, 'Mn':25, 'Fe':26, 'Co':27, 'Ni':28, 'Cu':29, 'Zn':30, 'Ga':31, 'Ge':32, 'As':33, 'Se':34, 'Br':35, 'Kr':36,
    'Rb':37, 'Sr':38, 'Y':39,'Zr':40, 'Nb':41, 'Mo':42, 'Tc':43, 'Ru':44, 'Rh':45, 'Pd':46, 'Ag':47, 'Cd':48, 'In':49, 'Sn':50, 'Sb':51, 'Te':52, 'I':53, 'Xe':54,
    'Cs':55, 'Ba':56, 'La':57, 'Ce':58, 'Pr':59, 'Nd':60, 'Pm':61, 'Sm':62, 'Eu':63, 'Gd':64, 'Tb':65, 'Dy':66, 'Ho':67, 'Er':68, 'Tm':69, 'Yb':70, 'Lu':71, 'Hf':72, 'Ta':73, 'W':74,'Re':75, 'Os':76, 'Ir':77, 'Pt':78, 'Au':79, 'Hg':80, 'Tl':81, 'Pb':82, 'Bi':83, 'Po':84,'At':85,'Rn':86,'Fr':87,'Ra':88,'Ac':89,'Th':90,'Pa':91,'U':92,'Pu':94}

    atoms_one_char=['H', 'B', 'C', 'N', 'O', 'F', 'P', 'S', 'K', 'V', 'Y', 'I', 'W', 'U']


