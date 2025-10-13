#!/usr/bin/python
# -*- coding: latin-1 -*-
from __future__ import print_function
import sys,os
import numpy as npy
from numpy import array, pi, sin, cos, sqrt, sort
from numpy import random, matrix, transpose
from numpy.matlib import repmat, repeat

import copy

try:
    import pylab
    from pylab import plot, figure, show
except:
    pass
#import threading

#Import Emiliano's modules

import pymucal
import xas


def makePrimitive(groups, occupancy, axis = [1, 1, 1, 90., 90., 90.], base = [0., 0., 0.], site_label=True):
    """The primitive cell has the structure of the model:
    model = {"atoms":[], "xyz":[], "labels":[]} where xyz is a list of [[X,Y,Z],...]"""
    p_cell={"atoms":[], "xyz":[], "labels":[]}
    for i in groups.keys():
        for j in groups[i]:
            if occupancy[i][1] == 1:
                if site_label:
                    label = i
                else:
                    label = occupancy[i][0]
                p_cell["atoms"].append(occupancy[i][0])
                p_cell["xyz"] += (array(base) + Fractional2Normal(j, axis)).tolist()
                p_cell["labels"].append(label)
            else:
                r=random.random()
                for k in range(0,len(occupancy[i]),2):
                    if r <= sum(occupancy[i][1:k+2:2]):
                        if site_label:
                            label = i
                        else:
                            label = occupancy[i][k]
                        p_cell["atoms"].append(occupancy[i][k]) 
                        p_cell["xyz"] += (array(base) + Fractional2Normal(j, axis) ).tolist()
                        p_cell["labels"].append(label)
                        break
                
    return p_cell


def makeModel(groups, occupancy, axis = [1, 1, 1, 90., 90., 90.], na = 1, nb = 1, nc = 1, site_label=True):
    model = {"atoms":[], "xyz":[], "labels":[]}
    for i in range(-(na - 1) / 2,(na - 1) / 2 + 1, 1):
        for j in range(-(nb - 1) / 2,(nb - 1) / 2 + 1, 1):
            for k in range(-(nc - 1) / 2,(nc - 1) / 2 + 1, 1):
                m = makePrimitive(groups, occupancy, axis,\
                base = Fractional2Normal([i,j,k], axis),\
                site_label = site_label)
                model["atoms"] += m["atoms"]
                model["xyz"] += m["xyz"]
                model["labels"] += m["labels"]
    return model

#def save2xyz(model,filename):
#    """Writes model to xyz type file"""
#    f = open(filename, "w")
#    f.write("%i\ni\n" % len(model))
#    fmt = "%s    %-8.6f    %-8.6f    %-8.6f    %s\n"
#    for i in range(len(model["atoms"])):
#        f.write(fmt % tuple(model["atoms"][i] + model["xyz"][i] + model["labels"][i]))
#    f.close()
#    return


def drawModel(model, radius_type = "covalent", r_factor = 0.6, temporary_file_name = "./temp.in.bs"):
    if not(radius_type in ["covalent", "vanderwaals"]):
        raise Exception("draw model error: radius_type can be covalent or vanderwaals only.")
    temporary_file = open(temporary_file_name, "w")
    atom_types = []
    for i in range(len(model["atoms"])):
        if not(model["atoms"][i] in atom_types):
            atom_types.append(model["atoms"][i])
        temporary_file.write("atom %s %8.6f %8.6f %8.6f %s\n" % tuple([model["atoms"][i],] + model["xyz"][i] + [model["labels"][i],]))

    for i in atom_types:
        atom_type_i = pymucal.atomic_data(i)
        temporary_file.write("spec %s  %4.3f %2.1f %2.1f %2.1f\n"%(i, atom_type_i.radius()[radius_type],\
        atom_type_i.rgb[0],atom_type_i.rgb[1],atom_type_i.rgb[2]))

    for i in  atom_types:
        for j in atom_types:
            lbond = \
            pymucal.atomic_data(i).radius()[radius_type] + pymucal.atomic_data(j).radius()[radius_type]
            temporary_file.write("bonds %s %s %f %f 0.1 0.2 0.2 0.2\n" % (i, j, lbond * 0.5, lbond * 1.09))
       
    temporary_file.write("inc 2.5\n")
    temporary_file.write("rfac %f\n"%r_factor)
    temporary_file.close()
    os.system("xbs "+temporary_file_name+" &")
    return


def saveModel(filename, model, superaxis=[], other_stuff={}):
    """The structure is the following:
    empty lines are ignored.
    Keywords are preceded by a # on a separate line
    following lines without a # are saved on a dictionary.
    Special recognized keywords are ATOMS and AXIS.
    For other keywords a string argument must be provided."""

    f=open(filename,"w")

    f.write("#AXIS\n")
    if superaxis != []:
        f.write("%g\t%g\t%g\t%g\t%g\t%g\n" % tuple(superaxis))
    elif not(model["axis"].all()):
        f.write("%g\t%g\t%g\t%g\t%g\t%g\n" % tuple(superaxis))
    else:
        f.write("%g\t%g\t%g\t%g\t%g\t%g\n" % (1.,1.,1.,90.,90.,90.))
        
    for i in other_stuff.keys():
        f.write("#%s\n" % i)
        f.write("%s\n" % other_stuff[i])
    f.write("#ATOMS\n")

    for i in range(len(model["atoms"])):
        f.write("%s\t%g\t%g\t%g\t%s\n" % tuple(model["atoms"][i] + model["xyz"][i] + model["labels"][i]))
    f.close()
    return

def loadModel(filename):
    """The structure is the following:
    empty lines are ignored.
    Keywords are preceded by a # on a separate line
    following lines without a # are loaded on a dictionary.
    Special recognized keywords are ATOMS and AXIS. 
    axis, model and a dictionary are returned"""
    model={"atoms":[],"xyz":[],"labels":[]}
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
                model["atoms"].append(ll0[0])
                model["xyz"].append([float(ll0[1]), float(ll0[2]), float(ll0[3])])
                model["labels"].append( ll0[4].strip() )
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
                print("Error parsing line :")
                print(ll[i])
        i += 1
    #print "Axis = ",axis
    model["axis"] = array(axis, "f")
    return model, other_stuff


def saveXYZ(filename, model):
    """Save model in  a text xyz file. Can be read by 'rasmol -xyz filename' software.
    The axis data are not saved and lost."""
    f=open(filename,"w")
    f.write("%i\n\n"%len(model))
    for  i in range(len(model["atoms"])):
        f.write("%2s %8.6f %8.6f %8.6f %2s\n" % tuple(model["atoms"][i] + model["xyz"][i] + model["labels"][i]))
    f.close()
    return


def loadXYZ(filename):
    """Load a text xyz file and returns a model structure.
    A model is a dictionary as described in xas.computeXAS.
    Axis data are not contained in the XYZ file and they are 
    arbitrary set to array([1,1,1,90,90,90],"f"). Modify them as necessary."""
    f=open(filename,"r")
    ll=f.readlines()
    f.close()
    del f
    model = {"atoms":[], "xyz":[], "labels":[],"axis": npy.zeros(6)}
    for linea in ll:
        parts = linea.split()
        try:
            if parts[0] in pymucal.atomic_data.atoms.keys():
                model.append([parts[0],] + \
                map(lambda x: float(x), parts[1:]) + [parts[0],])
                model["atoms"].append(parts[0])
                model["xyz"].append(map(float, parts[1:4]))
                model["labels"].append(parts[0])
        except:
            pass
    model["axis"] = array([1.,1.,1.,90.,90.,90.])
    return model

def modelExtendOld(model, axis=npy.zeros(6), nx=1, ny=1, nz=1, check_overlap=False, 
ovl=1., index=False):
    """Extend model by applying nx, ny and nz repetitions along a,b and c axis.
    Erase atoms overlapped if check_overlap is True. 
    Return indexes of original model in a separate tuple if index=True:
    return extended_model or extended_model, indexes
    axis =[a,b,c,alpha,beta,gamma]"""

## To be rewritten using matrices

    out = {"atoms":[], "xyz":[],"labels":[],"axis":npy.zeros(6)}
    if not(axis.all()) and not(model["axis"].all()):
        raise Exception("modelExtend cannot work if axis is not specified in model or function call.")
    elif not(axis.all()):
        axis = array(model["axis"],"f")
    out["axis"] = axis * array([nx,ny,nz,1,1,1],"f")
    idx =[]
    idx_i=0
    for atx in range(len(model["atoms"])):
        for i in range(0, nx):
            for j in range(0, ny):
                for k in range(0, nz):
                    newXYZ = Fractional2Normal(array(Normal2Fractional(model["xyz"][atx],\
                    axis)) + array([i, j, k]),axis)
                    OVERLAP =False
                    if check_overlap:
                        for old in out["xyz"]:
                            if ((newXYZ[0] - old[0])**2 + (newXYZ[1] - old[1])**2 \
                            + (newXYZ[2] - old[2])**2) <= ovl ** 2:
                                OVERLAP = True
                                break
                    if not(OVERLAP):
                        out["atoms"].append(model["atoms"][atx])
                        out["xyz"].append(newXYZ)
                        out["labels"].append(model["labels"][atx])
                        if index:
                            if i == nx and j == ny and k == nz:
                                idx.append(idx_i) 
                        idx_i += 1
                    else:
                        print("OVERLAP!")
    if index:
        return out,idx
    else:
        return out

def modelExtend(model, axis=npy.zeros(6), nx=1, ny=1, nz=1, check_overlap=False, 
ovl=1., index=False):
    """Extend model by applying nx, ny and nz repetitions along a,b and c axis.
    Erase atoms overlapped if check_overlap is True. 
    Return indexes of original model in a separate tuple if index=True:
    return extended_model or extended_model, indexes
    axis =[a,b,c,alpha,beta,gamma]
    The index makes sense for nx=ny=nz = 2n+1
    gives the central part indices
    nx, ny, nz > 0"""

    out = {"atoms":[], "xyz":[],"labels":[],"axis":npy.zeros(6)}
    if not(axis.all()) and not(model["axis"].all()):
        raise Exception("modelExtend cannot work if axis is not specified in model or function call.")
    elif not(axis.all()):
        axis = array(model["axis"],"f")
    out["axis"] = axis * array([nx,ny,nz,1,1,1],"f")
    frac0 = Normal2Fractional(array(model["xyz"],"f"), axis)
    #print "frac0 shape is : ", npy.shape(frac0)
    frac=[]
    for i in range(nx):
        for j in range(ny):
            for k in range(nz):
                frac += (frac0 + array([i, j, k])).tolist()
    #print "frac shape is : ",npy.shape(frac)
    out["atoms"] = model["atoms"] * nx * ny * nz
    out["labels"] = model["labels"] * nx * ny * nz
    out["xyz"] = Fractional2Normal(frac, axis)
    if index:
        return out, npy.arange(len(model["atoms"])) + ((nx-1)/2 + nx*(ny -1)/2 + nx*ny*(nz-1)/2)
    else:
        return out


#Functions used by rmc or xas to simulate disorder

#Disorder a model with a gaussian distribution of width sigma
def disorderModel(model, sigma=[0.,0.,0.], pbc = False):
    """Apply normal distribution displacement in the three directions of space 
    with amplitude sigma = [sig2x, sig2y, sig2z]
    If pbc is true, the axis must be specified in the model dictionary accordingly.
    Original coordinates must be above zero if pbc. Coordinates are intended not fractionary
    but comprised between 0 and the axis length."""
    m = copy.deepcopy(model)
    xyz = array(m["xyz"], "f") + random.standard_normal(npy.shape(m["xyz"])) * array(sigma)
    if pbc:
        xyz = npy.mod(xyz / m["axis"][:3], 1) * m["axis"][:3]
    m["xyz"] = xyz.tolist()
    return m


#Disorder a group of atoms by a rigid rotation/translation
#constraints must be applied
def disorderSet(Set, model, center, sig, pbc = False):
    """Set is a subset of model
    center is the center of the rotation
    sig2 is the amplitude of the random translation/rotation
    sig2 = (Sx,Sy,Sz,Srx,Sry,Srz)
    Srx,y,z are in degrees.
    All sigmas must be specified even if zeros.
    Function return the new coordinates of set as a list
    Original coordinates must be above zero if pbc. Coordinates are intended not fractionary
    but comprised between 0 and the axis length.
    
    WARNING: This works only with alpha=beta=gamma=90° and cartesian coordinates!!!!"""
    vector = random.standard_normal(3) * sig[:3]
    angles = random.standard_normal(3) * sig[3:7]
    if pbc:
        return  mod((RotoTranslateXYZ(Set["xyz"], vector, center, angles))/model["axis"][:3],1)*model["axis"][:3]
    else:
        return  RotoTranslateXYZ(Set["xyz"], vector, center, angles)


#Apply factor to model (x_i * fx, y_i * fy, z_i *fz)

def multiplyModel(model, f =array([1.,1.,1.],"f")):
    """ multiply each (x_i, y_i, z_i) by (fx, fy, fz) respectively"""
    mout = copy.deepcopy(model)
    mout["xyz"] = (array(mout["xyz"]) * f).tolist()
    if "axis" in mout.keys():
        mout["axis"] = mout["axis"] * f
    return mout


#Define operations on set of atoms

def RotoTranslateXYZ(XYZ, vector, center, angles):
    """Works on a list of XYZ coordinates (e.g. as in a Model["xyz"])
    It rotates around center and moves of vector translation
    Angles are in deg.
    angles=array([Rx,Ry,Rz])"""
    cosx, sinx = cos(angles[0]/180.*pi), sin(angles[0]/180.*pi)
    cosy, siny = cos(angles[1]/180.*pi), sin(angles[1]/180.*pi)
    cosz, sinz = cos(angles[2]/180.*pi), sin(angles[2]/180.*pi)
    RotM = npy.matrix([[1.,0.,0.],[0.,cosx,-sinx],[0.,sinx,cosx]])\
    * npy.matrix([[cosy,0.,siny],[0.,1.,0.],[-siny,0.,cosy]])\
    * npy.matrix([[cosz,-sinz,0.],[sinz,cosz,0.],[0.,0.,1.]])
    #print RotM
    return ((npy.matrix(XYZ) - center) * transpose(RotM) + center + vector).tolist()


# Check structure

def reportDistances(atoms, rmax=5., use_site=False, precision =0.01):
    """Calculate distances between atoms and class them for ipot (or labels if specified).
    rmax is used to not calculate distances above a certain value
    atoms is an ordered list of atoms as a model:
    model={"atoms"=[],"xyz":[], "labels": []], e.g. [["Au", 0., 0., 0., "Au0"], ...]"""
    ###With the new structure of the model entity, we can optimise this code a lot... think about it!!!
    rmin = 0.1
    if use_site:
        identity = "labels"
    else:
        identity = "atoms"
    nats = len(atoms["atoms"])
    outl={}
    site_counts={}
    for i in range(nats):
        outl[atoms[identity][i]] = []
        if atoms[identity][i] not in site_counts.keys():
            site_counts[atoms[identity][i]] = 1
        else:
            site_counts[atoms[identity][i]] += 1
    for i in range(nats):
        for j in range(i+1,nats):
            atatdist = sqrt(sum((array(atoms["xyz"][i]) - array(atoms["xyz"][j])) ** 2 ))
            if atatdist < rmin:
                raise Exception("makeModel.reportDistances: \
                two atoms are closer than rmin, indices= %i, %i" % (i,j))
            if atatdist <= rmax:
                outl[atoms[identity][i]].append([atoms["atoms"][j], atoms["labels"][j], atatdist])
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
                    if (k[0:2] == j[0:2]) and (abs(k[2]-j[2]) <= precision):
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

def __equivalent_neighbors(a, b, precision=0.01):
    return (a[0:2] == b[0:2]) and (abs(a[2]-b[2]) <= precision)

def __equivalent_atoms(a, b, precision=0.01):
    return a[0]==b[0] and abs(a[1]-b[1]) < precision and (a[2]-b[2]) < precision and abs(a[3]-b[3]) < precision

def reportDistancesForAtom(i, atoms, rmax=5., use_site=False):
    """Calculate distances between one atom of index i and the others below rmax.
    The atoms format is like for a model:
    atoms={"atoms":["Ru","Fe",...], "xyz":[[1.,2.,0.],...], "label":["Ru0","Fe0"]]
    The output is a list of atoms of the form [["Au","Au0",2.52],...]"""
    dd = npy.sqrt(npy.sum((array(atoms["xyz"]) - array(atoms["xyz"][i]))**2, axis =1))
    wdd = npy.sort(npy.where(dd <= rmax))[1:]
    return zip(array(atoms["atoms"]).choose(wdd).tolist(),array(atoms["atoms"]).choose(wdd).tolist(),dd.choose(wdd).tolist())

def reportMinDistanceForAtom(i, atoms):
    """Report minimum distance from chosen atom at index i to any other.
    Distance < 1e-3 is not reported... a WARNING is issued.
    See model structure for atoms: {"atoms":[],"xyz":[],"labels":[]}.
    """
    return npy.sort(npy.sqrt(npy.sum((array(atoms["xyz"]) - array(atoms["xyz"][i]))**2, axis =1)))[1]
    
#Crystallographic utilities

def Fractional2Normal(fractional, axis):
    """fractional=[fa, fb, fc]
    axis=[a, b, c, alpha, beta, gamma]
    returns a matrix of [x,y,z]
    angles are in degrees."""
    a, b, c, alpha, beta, gamma = axis
    alpha, beta, gamma = float(alpha)/180.*pi, float(beta)/180.*pi, float(gamma)/180.*pi
    V= npy.sqrt(1 - cos(alpha) ** 2  - cos(beta) ** 2 - cos(gamma) ** 2 + 2 * cos(alpha) * cos(beta) * cos(gamma))
    M_1=npy.matrix([[a, b * cos(gamma), c * cos(beta)],\
    [0, b * sin(gamma), c * (cos(alpha) - cos(beta) * cos(gamma)) / sin(gamma)],\
    [0., 0., c * V / sin(gamma)]])
    return array(npy.dot(array(fractional), M_1))

def Normal2Fractional(cartesian, axis):
    """cartesian=[x, y, z]
    axis=[a, b, c, alpha, beta, gamma]
    returns a matrix of [fa,fb,fc] fractional coordinates
    angles are in degrees."""
    a, b, c, alpha, beta, gamma = axis
    a, b, c, alpha, beta, gamma = float(a), float(b), float(c),\
    float(alpha)/180.*pi, float(beta)/180.*pi, float(gamma)/180.*pi
    V= npy.sqrt(1 - cos(alpha) ** 2  - cos(beta) ** 2 - cos(gamma) ** 2 + 2 * cos(alpha) * cos(beta) * cos(gamma))
    M=npy.matrix([[1. / a, - cos(gamma) / (a * sin(gamma)),\
    (cos(alpha) * cos(gamma) - cos(beta)) / (a * V * sin(gamma))],\
    [0., 1. / (b * sin(gamma)), (cos(beta) * cos(gamma) - cos(alpha)) / (b * V * sin(gamma))],\
    [0., 0., sin(gamma) / (c * V)]])
    return array(npy.dot(array(cartesian), M))

#Check neighbours. Functions essentials for speeding up calculations on models.


def makeNeighTable(model, rmax=3.6, periodic=True, periodic_n=1, axis=[]):
    """
    Return a table of indices of neighbors for every atom in model.
    Every atom has a list of indices associated.
    """
    rmin = 0.01
    if rmax < 1.:
        raise Exception ("makeNeighTable: too short rmax = %g set rmax above 1!" % rmax)
    #If periodic extend model (request index to modelExtend)
    if periodic:
        m_ext, m_idx = modelExtend(model, axis, nx=periodic_n, \
        ny=periodic_n, nz=periodic_n, check_overlap = False, index =True)
    #else point to the same
    else:
        m_ext = model
        m_idx = range(len(model))
    neighs = []
    for i in m_idx:
        neighs.append(makeNeighEntry(i, m_ext, rmax=rmax))
    return neighs

def makeNeighEntry(idx, model, rmax=3.6):
    """
    Returns the index in model of atoms closer to model[idx] than rmax.
    idx: index of atom inÂ model
    model: model data structure x,y,z in A
    rmax: maximum distance <=rmax in A
    """
    ###Using numpy.where this can be fairly more compact and fast
    atom0 = array(model["xyz"][idx],"f")
    dd2 = npy.sum( (array(model["xyz"], "f") - atom0) **  2, axis=1)
    neighs = npy.where(dd2 <rmax**2)[0].tolist()
    neighs.remove(idx)
    if len(npy.where(dd2 < 0.1)[0])>1:
        print("Atoms too close, check model!")
    return neighs

#Check neighbours. Functions essentials for speeding up calculations on models.

def analyseModel(m, absorber="", axis=None, histogram_bar=0.025, rmax=6.,\
    expand_model = True,na=1, nb=1, nc=1, plot = False):
    
    "Use report_distances and report neighbors histogram for absorber type"
    ###This routine should be rewritten following the new matrix model and numpy.where + hist
    if expand_model:
        m_ext = modelExtend(m, axis, nx=na, ny=nb, nz=nc, check_overlap = True)
    else:
        m_ext = copy.deepcopy(m)
    distrep=[]
    n_absorbers = 0
    for i in range(len(m["atoms"])):
        if m["atoms"][i] == absorber:
            n_absorbers += 1
            tmp = reportDistancesForAtom(m["xyz"][i], m_ext, rmax = rmax)
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

#Build structured Euclidean distance matrix using numpy acceleration

def Distance(x,y):
    return sqrt(sum(x-y)**2)

def DistanceMatrix():
    return

def DistanceMatrix(points):
    numPoints = len(points)
    distMat = sqrt(sum((repmat(points, numPoints, 1) - repeat(points, numPoints, axis=0))**2, axis=1))
    return distMat.reshape((numPoints,numPoints))

#
#Constraints: all functions return true or false depending if conditions met or not.
#
#pbc or not pbc should always be an option
#
#---------------------------------
#General constraints
#---------------------------------
#Keep In Box: provided an origin and axis [a,b,c,alpha,beta,gamma], atoms should not get out.
#option: function may provide indices of out of box atoms, these can be moved in following pbc
#constraints. It should not be useful for pbc calculations...
#
#Minimum distance: applies to all, never two atoms closer than R
#
#Isolated atom: applies to all, all atoms must have at least one neighbor closer than R
#
#Separate: two identical atoms (same species) should never be neighbors (closer than R)
#
#---------------------------------
#Specific constraints
#---------------------------------
#These are calculated on a atomic or label class (option)
#
#SpecificCoordination: for a given atom/label [["Atom/Label",Rmin,Rmax,Nmin,Nmax],...]
#               this fixes a minimum and maximum coordination of two types of atoms between two limit distances
#               example Coordination={"Sn":[["I",Rmin,Rmax,Nmin,Nmax],["O",1.5,2.5,1,3]}
#
#GenericCoordination: for a given atom/label it restrains between Nmin and Nmax the coordination between Rmin and Rmax
#                       example {"Sn":[Rmin,Rmax,Nmin,Nmax]} the tin must have four neighbors between 2 and 3, any type of neighbor.
#
#... be careful if you exceed with constraints you will end up with a continuous reject of model and an infinite loop.



#####################
#Test Values

axis = array([5.95, 5.95, 5.95, 90., 90., 90.],"f")

groups = {"x1": [[0., 0., 0.],[0.5, 0.5, 0.],[0.5, 0., 0.5],[0., 0.5, 0.5]],
"x2": [[0., 0., 0.5],[0., 0.5, 0.],[0.5, 0., 0.],[0.5, 0.5, 0.5]],
"y": [[0.25, 0.25, 0.25],[0.75, 0.75, 0.25],[0.75, 0.25, 0.75],[0.25, 0.75, 0.75]],
"z": [[0.75, 0.75, 0.75],[0.25, 0.75, 0.25],[0.75, 0.25, 0.25],[0.25, 0.25, 0.75]]}

occupancy = {"x1":["Mn",1.], "x2":["Ru",1.0], "y":["Mn",1.], "z":["Ga",1.]}

#The model structure changes in this version
#model = {"atoms":[], "xyz":[], "labels":[]}
#I suggest that axis could be associated as an option into the model to simplify all other calculations.
#model["axis"]=[a,b,c,alpha,beta,gamma]


def runTest(draw = True):
    m = makeModel(groups,occupancy,axis,1,1,1)
    mext = modelExtend(m, axis, 3, 3, 3, index=False )
    mext = disorderModel(mext,[0.1,0.1,0.1],pbc=True)

    #if draw: threading.start_new_thread(drawModel, (mext,))
    absorber = "Ga"
    feff_config = {"EXCHANGE":[0,0,0],"EXAFS":12,"RPATH":6.,"S02":0,"DEBYE":[80,250]}
    periodic = True
    mode = "EXAFS"
    all_site = False
    superaxis = [axis[0]*3., axis[1]*3., axis[2]*3., 90., 90., 90.]
    output = xas.computeXAS(m, superaxis, absorber, feff_config, periodic,\
    mode, all_site = all_site)
    if draw:
        figure()
        exp = xas.exafsLoad("/home/fonda/xas/Mn2Ga_KRode/cleanup/HK539Ga_Mn2RuGa_78deg_LNT_cleaned.chi")
        plot(exp[0],exp[1]*exp[0]**2,linewidth=2,color="red",label="EXP")
        plot(output[0], output[1]*output[0]**2,label="FEFF")
        pylab.axis(xmin=2, xmax=14)
        pylab.legend()
        show()
    #return m, makeNeighTable(m, rmax=3.6, periodic=True, periodic_n=2, axis=axis)
    return
    

if __name__ == "__main__":
    runTest()
