#!/usr/bin/python
# -*- coding: latin-1 -*-
import sys,os
import numpy as npy
from numpy import array, pi, sin, cos, sqrt, sort
from numpy import random
import copy

try:
    import pylab
    from pylab import plot, figure, show
except:
    pass
import thread

#Import Emiliano's modules

import pymucal
import xas

axis = [5.95, 5.95, 5.95, 90., 90., 90.]

groups = {"x1": [[0., 0., 0.],[0.5, 0.5, 0.],[0.5, 0., 0.5],[0., 0.5, 0.5]],
"x2": [[0., 0., 0.5],[0., 0.5, 0.],[0.5, 0., 0.],[0.5, 0.5, 0.5]],
"y": [[0.25, 0.25, 0.25],[0.75, 0.75, 0.25],[0.75, 0.25, 0.75],[0.25, 0.75, 0.75]],
"z": [[0.75, 0.75, 0.75],[0.25, 0.75, 0.25],[0.75, 0.25, 0.25],[0.25, 0.25, 0.75]]}

occupancy = {"x1":["Mn",1.], "x2":["Ru",1.0], "y":["Mn",1.], "z":["Ga",1.]}

def makePrimitive(groups, occupancy, axis = [1, 1, 1, 90., 90., 90.], base = [0., 0., 0.], site_label=True):
    p_cell=[]
    for i in groups.keys():
        for j in groups[i]:
            if occupancy[i][1] == 1:
                if site_label:
                    label = i
                else:
                    label = occupancy[i][0]
                p_cell.append([occupancy[i][0],]+list(array(base) + Fractional2Normal(j, axis) )+[i,])
            else:
                r=random.random()
                for k in range(0,len(occupancy[i]),2):
                    if r <= sum(occupancy[i][1:k+2:2]):
                        if site_label:
                            label = i
                        else:
                            label = occupancy[i][k]
                        p_cell.append([occupancy[i][k],]\
                        +list(array(base) + Fractional2Normal(j, axis) )+ [i,])
                        break
                
    return p_cell


def makeModel(groups, occupancy, axis = [1, 1, 1, 90., 90., 90.], na = 1, nb = 1, nc = 1, site_label=True):
    model = []
    for i in range(-(na - 1) / 2,(na - 1) / 2 + 1, 1):
        for j in range(-(nb - 1) / 2,(nb - 1) / 2 + 1, 1):
            for k in range(-(nc - 1) / 2,(nc - 1) / 2 + 1, 1):
                model += makePrimitive(groups, occupancy, axis,\
                base = Fractional2Normal([i,j,k], axis),\
                site_label = site_label)
    return model

def save2xyz(model,filename):
    """Writes model to xyz type file"""
    f = open(filename, "w")
    f.write("%i\ni\n" % len(model))
    fmt = "%s    %-8.6f    %-8.6f    %-8.6f    %s\n"
    for i in model:
        f.write(fmt % tuple(i))
    f.close()
    return

def drawModel(model, radius_type = "covalent", r_factor = 0.6, temporary_file_name = "./temp.in.bs"):
    if not(radius_type in ["covalent", "vanderwaals"]):
        raise Exception("draw model error: radius_type can be covalent or vanderwaals only.")
    
    temporary_file = file(temporary_file_name, "w")
    atom_types = []
    for i in model:
        if not(i[0] in atom_types):
            atom_types.append(i[0])
        temporary_file.write("atom %s %8.6f %8.6f %8.6f %s\n" % (i[0],i[1],i[2],i[3],i[4]))

    for i in atom_types:
        atom_type_i = pymucal.atomic_data(i)
        temporary_file.write("spec %s  %4.3f %2.1f %2.1f %2.1f\n"%(i, atom_type_i.radius()[radius_type],\
        atom_type_i.rgb[0],atom_type_i.rgb[1],atom_type_i.rgb[2]))

    for i in  atom_types:
        for j in atom_types:
            lbond = \
            pymucal.atomic_data(i).radius()[radius_type] + pymucal.atomic_data(j).radius()[radius_type]
            temporary_file.write("bonds %s %s %f %f 0.1 0.2 0.2 0.2\n" % (i, j, lbond * 0.5, lbond * 1.09))
       
    temporary_file.write("inc 1\n")
    temporary_file.write("rfac %f\n"%r_factor)
    temporary_file.close()
    os.system("xbs "+temporary_file_name+" &")
    return

def loadXYZ(filename):
    """Load a text xyz file and returns a model structure.
    A model is a list of list as descibed in xas.computeXAS"""
    f=open(filename,"r")
    ll=f.readlines()
    f.close()
    del f
    model=[]
    for linea in ll:
        parts=linea.split()
        try:
            if parts[0] in pymucal.atomic_data.atoms.keys():
                model.append([parts[0],] + \
                map(lambda x: float(x), parts[1:]) + [parts[0],])
        except:
            pass
    return model

def saveModel(filename, model, superaxis, other_stuff={}):
    """The structure is the following:
    empty lines are ignored.
    Keywords are preceded by a # on a separate line
    following lines without a # are saved on a dictionary.
    Special recognized keywords are ATOMS and AXIS.
    For other keywords a string argument must be provided."""
    f=open(filename,"w")
    f.write("#AXIS\n")
    f.write("%g\t%g\t%g\t%g\t%g\t%g\n" % tuple(superaxis))
    for i in other_stuff.keys():
        f.write("#%s\n" % i)
        f.write("%s\n" % other_stuff[i])
    f.write("#ATOMS\n")
    for i in model:
        f.write("%s\t%g\t%g\t%g\t%s\n" % tuple(i))
    f.close()
    return

def loadModel(filename):
    """The structure is the following:
    empty lines are ignored.
    Keywords are preceded by a # on a separate line
    following lines without a # are loaded on a dictionary.
    Special recognized keywords are ATOMS and AXIS. 
    axis, model and a dictionary are returned"""
    model=[]
    f=open(filename,"r")
    ll=f.readlines()
    f.close()
    i = 0
    other_stuff={}
    while(i < len(ll)):
        if ll[i].startswith("#ATOMS"):
            i += 1
            while(i<len(ll) and not ll[i].startswith("#")):
                ll0=ll[i].split()
                model.append([ll0[0], float(ll0[1]), float(ll0[2]), float(ll0[3]), ll0[4].strip()])
                i += 1
            i += -1
        elif ll[i].startswith("#AXIS"):
            i += 1
            axis = map(float, ll[1].strip().split())
        elif ll[i].startswith("#"):
            try:
                i += 1
                other_stuff[ll[i-1][1:].split()[0]] = ll[i]
            except:
                print "Error parsing line :"
                print ll[i]
        i += 1
    #print "Axis = ",axis
    return axis, model, other_stuff


def saveXYZ(filename, model):
    """Save model in  a text xyz file. Can be read by 'rasmol -xyz filename' software"""
    f=open(filename,"w")
    f.write("%i\n\n"%len(model))
    for atx in model:
        f.write("%2s %8.6f %8.6f %8.6f %2s\n"%tuple(atx))
    f.close()
    return

def modelExtend(model, axis, nx=1, ny=1, nz=1, check_overlap=True, 
ovl=1., index=False):
    """Extend model by +-nx, +-ny and +-nz repetitions along a,b and c axis.
    Erase atoms overlapped if check_overlap is True. 
    Return indexes of original model in a separate tuple if index=True:
    return extended_model or extended_model, indexes
    axis =[a,b,c,alpha,beta,gamma]"""
    out = []
    idx =[]
    idx_i=0
    for atx in model:
        for i in range(-nx, nx):
            for j in range(-ny, ny):
                for k in range(-nz, nz):
                    new = [atx[0],] + \
                    list(Fractional2Normal(array(Normal2Fractional(atx[1:4],\
                    axis)) + array([i, j, k]),axis))\
                    + [atx[4],]
                    OVERLAP =False
                    if check_overlap:
                        for old in out:
                            if ((new[1] - old[1])**2 + (new[2] - old[2])**2 \
                            + (new[3] - old[3])**2) <= ovl ** 2:
                                OVERLAP = True
                                break
                    if not(OVERLAP):
                        out.append(new)
                        if index:
                            if i == j == k == 0:
                                idx.append(idx_i) 
                        idx_i += 1
                    else:
                        print "OVERLAP!"
    if index:
        return out,idx
    else:
        return out


#Disorder a model with a gaussian distribution of width sigma

def disorderModel(model, sigma, sigmay=None, sigmaz=None):
    """Apply normal distribution displacement in the three directions of space 
    with amplitude sigma. If sigmay and sigmaz are specified, three different
    values are employed for x, y and z directions. if sigmay is specified, sigmaz must be, too."""
    m = copy.deepcopy(model)
    for i in m:
        i[1] = i[1] + random.standard_normal() * sigma
        if sigmay == None:
            i[2] = i[2] + random.standard_normal() * sigma
            i[3] = i[3] + random.standard_normal() * sigma
        elif sigmay != None and sigmaz != None:
            i[2] = i[2] + random.standard_normal() * sigmay
            i[3] = i[3] + random.standard_normal() * sigmaz
        else:
            raise Exception("If sigmay is specified, sigmaz must be as well.")
    return m

#Apply factor to model (x_i * fx, y_i * fy, z_i *fz)

def multiplyModel(model, f =[1.,1.,1.]):
    """ multiply each (x_i, y_i, z_i) by (fx, fy, fz) respectively"""
    m = copy.deepcopy(model)
    for i in m:
        i[1] = i[1] * f[0]
        i[2] = i[2] * f[1]
        i[3] = i[3] * f[2]
    return m

# Check structure


def reportDistances(atoms, rmax=5., rmin=1., use_site=False):
    """Calculate distances between atoms and class them for ipot (or labels if specified).
    rmax is used to not calculate distances above a certain value
    rmin is used to check for too short distances, it throws an exception if met.
    atoms is a list of atoms as follows:
    ["element", x, y, z, "label"], e.g. [["Au", 0., 0., 0., "Au0"], ...]"""
    if use_site:
        identity = 4
    else:
        identity = 0
    nats = len(atoms)
    outl={}
    site_counts={}
    for i in atoms:
        outl[i[identity]] = []
        if i[identity] not in site_counts.keys():
            site_counts[i[identity]] = 1
        else:
            site_counts[i[identity]] += 1
    for i in xrange(nats):
        for j in xrange(i+1,nats):
            atatdist = sqrt(sum((array(atoms[i][1: 4]) - array(atoms[j][1: 4])) ** 2 ))
            if atatdist < rmin:
                raise Exception("makeModel.reportDistances: \
                two atoms are closer than rmin, indices= %i, %i" % (i,j))
            if atatdist <= rmax:
                outl[atoms[i][identity]].append([atoms[j][0], atoms[j][4], atatdist])
    for i in outl.keys():
        tmp = []
        for j in outl[i]:
            if tmp == []:
                tmp.append(j + [1])
            elif j in tmp:
                tmp.index(j)[-1] += 1
            else:
                found = False
                for k in tmp:
                    if _equivalent_neighbors(k, j):
                        tmp[tmp.index(k)][-1] += 1
                        found = True
                        break
                if not found:
                    tmp.append(j + [1])
        outl[i] = tmp
    for i in outl.keys():
        for j in range(len(outl[i])):
            outl[i][j][-1] = float(outl[i][j][-1]) / site_counts[i]
    return outl

def reportDistancesForAtom(atom, atoms, rmax=5., use_site=False):
    """Calculate distances between atom and the rest and class them 
    for ipot (or labels if specified).
    rmax is used to not calculate distances above a certain value.
    The atoms format is:  
    ["element", x, y, z, "label"], e.g. [["Au", 0., 0., 0., "Au0"], ...]"""
    if use_site:
        identity = 4
    else:
        identity = 0
    nats = len(atoms)
    site_counts={}
    outl=[]
    for i in xrange(nats):
        if atoms[i] != atom:
            atatdist = sqrt(sum((array(atoms[i][1: 4]) - array(atom[1: 4])) ** 2 ))
            if atatdist <= rmax:
                outl.append([atoms[i][0], atoms[i][4], atatdist])
    return outl

def reportMinDistanceForAtom(atom, atoms):
    """Report minimum distance from chosen atom to any other.
    Distance < 1e-3 is not reported... a WARNING is issued.
    ["element", x, y, z, "label"], e.g. [["Au", 0., 0., 0., "Au0"], ...]"""
    nats = len(atoms)
    dist = 0
    for i in xrange(nats):
        if atoms[i] != atom:
            atatdist = sqrt(sum((array(atoms[i][1: 4]) - array(atom[1: 4])) ** 2 ))
            if dist == 0 and atatdist > 1e-3:
                dist = atatdist
            elif atatdist > 1e-3:
                dist = min(dist, atatdist)
            elif atatdist < 1e-3:
                print "WARNING: skipping rmin < 1e-3. atom does not belong to atoms or overlapping atoms"
    return dist

def _equivalent_neighbors(a, b, precision=0.01):
    return (a[0:2] == b[0:2]) and (abs(a[2]-b[2]) <= precision)

def _equivalent_atoms(a, b, precision=0.01):
    return a[0]==b[0] and abs(a[1]-b[1]) < precision and (a[2]-b[2]) < precision and abs(a[3]-b[3]) < precision
    
#Crystallographic utilities

def Fractional2Normal(fractional, axis):
    """fractional=[fa, fb, fc]
    axis=[a, b, c, alpha, beta, gamma]
    returns [x,y,z]
    angles are in degrees."""
    a, b, c, alpha, beta, gamma = axis
    alpha, beta, gamma = float(alpha)/180.*pi, float(beta)/180.*pi, float(gamma)/180.*pi
    V= npy.sqrt(1 - cos(alpha) ** 2  - cos(beta) ** 2 - cos(gamma) ** 2 + 2 * cos(alpha) * cos(beta) * cos(gamma))
    M_1=npy.matrix([[a, b * cos(gamma), c * cos(beta)],\
    [0, b * sin(gamma), c * (cos(alpha) - cos(beta) * cos(gamma)) / sin(gamma)],\
    [0., 0., c * V / sin(gamma)]])
    return array(npy.dot(M_1, array(fractional)))[0]

def Normal2Fractional(cartesian, axis):
    """cartesian=[x, y, z]
    axis=[a, b, c, alpha, beta, gamma]
    returns [fa,fb,fc] fractional coordinates
    angles are in degrees."""
    a, b, c, alpha, beta, gamma = axis
    a, b, c, alpha, beta, gamma = float(a), float(b), float(c),\
    float(alpha)/180.*pi, float(beta)/180.*pi, float(gamma)/180.*pi
    V= npy.sqrt(1 - cos(alpha) ** 2  - cos(beta) ** 2 - cos(gamma) ** 2 + 2 * cos(alpha) * cos(beta) * cos(gamma))
    M=npy.matrix([[1. / a, - cos(gamma) / (a * sin(gamma)),\
    (cos(alpha) * cos(gamma) - cos(beta)) / (a * V * sin(gamma))],\
    [0., 1. / (b * sin(gamma)), (cos(beta) * cos(gamma) - cos(alpha)) / (b * V * sin(gamma))],\
    [0., 0., sin(gamma) / (c * V)]])
    return array(npy.dot(M, array(cartesian)))[0]

#Check neighbours. Functions essentials for speeding up calculations on models.


def makeNeighTable(model, rmax=3.6, rmin=0.1, periodic=True, periodic_n=1, axis=[]):
    """
    WORK IN PROGRESS
    """
    if rmin < 0.1:
        rmin = 0.1
    if rmax < 1.:
        raise Exception ("makeNeighTable: too short rmax = %g set rmax above 1!" % rmax)
    #Make empty list
    neighs = []
    #If periodic extend model (request index to modelExtend)
    if periodic:
        m_ext, m_idx = modelExtend(model, axis, nx=periodic_n, \
        ny=periodic_n, nz=periodic_n, check_overlap = False, index =True)
    #else point to the same
    else:
        m_ext = model
        m_idx = range(len(model))
    for i in m_idx:
        neighs.append(makeNeighEntry(i, m_ext, rmax=rmax, rmin=rmin))
    return neighs
    #return map(lambda x: makeNeighEntry(x, m_ext, rmax=rmax, rmin=rmin), m_idx)

def makeNeighEntry(idx, model, rmax=3.6, rmin=0.1):
    """
    Returns the index in model of atoms closer to model[idx] than rmax 
    and not closer than rmin.
    idx: index of atom inÂ model
    model: model data structure x,y,z in A
    rmax: maximum distance <=rmax in A
    rmin: >=rmin cannot be less than 0.1A, it is forced to 0.1 if required.
    """
    if rmin < 0.1:
        rmin = 0.1
    atom0 = model[idx]
    rmin2 = rmin ** 2
    rmax2 = rmax ** 2
    neighs = []
    i = 0
    for atom in (model):
        d2 = (atom[1] - atom0[1]) ** 2 + (atom[2] - atom0[2]) ** 2 \
        + (atom[3] - atom0[3]) ** 2 
        if d2 >= rmin2 and d2 <= rmax2:
            neighs.append(i)
        i += 1
    return neighs

def analyseModel(m, absorber="", axis=None, histogram_bar=0.025, rmax=6.,\
    rmin=0.1, expand_model = True,na=1, nb=1, nc=1, plot = False):
    
    "Use report_distances and report neighbors histogram for absorber type"
    
    if expand_model:
        m_ext = modelExtend(m, axis, nx=na, ny=nb, nz=nc, check_overlap = True)
    else:
        m_ext = copy.deepcopy(m)
    distrep=[]
    n_absorbers = 0
    for i in m:
        if i[0] == absorber:
            n_absorbers += 1
            tmp = reportDistancesForAtom(i, m_ext, rmax = rmax)
            for j in tmp:
                if j[2] > 0.1:
                    distrep.append(j)
    species={}
    distrep_sep={}
    for i in distrep:
        if i[0] not in species.keys():
            species[i[0]] = 1
            distrep_sep[i[0]] = [i[2]]
        else:
            species[i[0]] += 1
            distrep_sep[i[0]].append(i[2])
    histograms = {}
    nbars = round(rmax / histogram_bar)
    for i in species:
        distrep_sep[i] = sort(distrep_sep[i])
        histograms[i] = list(npy.histogram(distrep_sep[i], nbars,\
        range=(0, rmax)))
        histograms[i][0] = histograms[i][0] / float(n_absorbers)
    del distrep_sep, distrep, m_ext
    #return distrep_sep
    if plot:
        pylab.figure()
        pylab.grid()
        pylab.title("Absorber = %s rmax = %6.3f" % (absorber, rmax))
        maxp = 0
        for i in species:
            pylab.plot(npy.linspace(0., rmax, nbars), histograms[i][0],\
            label = "%s" % i)
            maxp = max(max(histograms[i][0]), maxp)
        pylab.axis([1.,rmax,0.,maxp*1.1])
        pylab.legend()
    return histograms





#####################

def runTest(draw = False):
    m = makeModel(groups,occupancy,axis,1,1,1)
    mext = modelExtend(m, axis, 1, 1, 1, index=False )
    if draw: thread.start_new_thread(drawModel, (mext,))
    absorber = "Ga"
    feff_config = {"EXCHANGE":[0,0,0],"EXAFS":12,"RPATH":6.,"S02":0,"DEBYE":[80,250]}
    periodic = True
    mode = "EXAFS"
    all_site = False
    superaxis = [axis[0]*4., axis[1]*4., axis[2]*1., 90., 90., 90.]
    output=xas.computeXAS(m, superaxis, absorber, feff_config, periodic,\
    mode, all_site = all_site)
    print array(output).shape
    if draw:
        figure()
        exp=xas.exafsLoad("/home/fonda/xas/Mn2Ga_KRode/cleanup/HK539Ga_Mn2RuGa_78deg_LNT_cleaned.chi")
        plot(exp[0],exp[1]*exp[0]**2,linewidth=2,color="red",label="EXP")
        plot(output[0], output[1]*output[0]**2,label="FEFF")
        pylab.axis(xmin=2, xmax=14)
        pylab.legend()
        show()
    return makeNeighTable(m, rmax=3.6, rmin=0.1, periodic=True, periodic_n=2, axis=axis)
    
    

if __name__ == "__main__":
    runTest()
