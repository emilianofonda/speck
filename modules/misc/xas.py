#Interviewer:  Good evening. Well, we have in the studio tonight a man who says things
#              in a very roundabout way. Isn't that so, Mr Pudifoot?
#Mr. Pudifoot: Yes.
#Interviewer:  Have you always said things in a very roundabout way?
#Mr. Pudifoot: Yes.
#Interviewer:  Well, I can't help noticing that, for someone who claims to say things 
#              in a very roundabout way, your last two answers have had very little of 
#              the discursive quality about them.

#Import world modules
import time
import os
import exceptions as exc
import multiprocessing

import scipy
from scipy import interpolate as intp
from scipy import optimize
import numpy as npy
from numpy import pi,round,array,sqrt,sum,arange,loadtxt,savetxt, cos, sin, shape
from numpy import fft


#Import Emiliano modules
import pymucal
import makeModel

# File Utilities
def exafsLoad(filename,k=0,chi=1,**kwargs):
    """load file and interpolate it. 
    keywords arguments are passed to interpolate function (see xas.interpolate)."""
    xf = loadtxt(filename).transpose()
    return interpolate(array([xf[k], xf[chi]]), **kwargs)


def xmuLoad(filename,k=1,chi=3,k1=-25,k2=45,dk=0.1,interp_order=3):
    """load file and interpolate it. 
    keywords arguments are passed to interpolate function (see xas.interpolate)."""
    xf = loadtxt(filename).transpose()
    return interpolate(array([xf[k], xf[chi]]), k1, k2, dk,interp_order)


#Math on spectra
def linFit(y, components, fractions = [], i1=0, i2=-1):
    """y is the array data
    components are a list of previously homogeneously data of standards, 
    fractions is the list of their respective fractions,  
    i1, i2 are the limits of the region used for the fit (default is 0 and -1).
    Fractions are obliged to be positive. 
    The returned value is a list of fractions."""
    cs = npy.transpose(npy.transpose(array(components))[i1:i2])
    if fractions == []:
        fractions = 0.5 * ones(len(components))
    fs = abs(array(fractions))
    
    def residual(fs, y, cs):
        fs = abs(fs) / sum( abs(fs) )
        residual = y - sum(npy.transpose(npy.transpose(cs) * fs), axis = 0)
        return residual
    
    mess = []
    fractions, mess = optimize.leastsq(residual, fs, args = (y[i1:i2], cs), full_output=0)
    fractions = abs(fractions) / sum(abs(fractions))
    return abs(fractions), sum(residual(fractions, y[i1:i2], cs)**2)

def interpolate(chi, k1=0., k2=40., dk=0.05, interp_order = 1):
    """Just interpolate! do not ask yourself any question: interpolate!
    before using any of the xas module functions interpolate!"""
    fchi = intp.interp1d(chi[0], chi[1], interp_order, bounds_error=False, fill_value=0.)
    xr = npy.arange(k1, k2 + dk, dk)
    return array([xr, fchi(xr)])

def genericInterpolate(x, y, x1, x2, dx, interp_order = 1):
    """return interpolated y data on even grid linspace(x1,x2,dx)"""
    fy = intp.interp1d(x, y, interp_order, bounds_error=False, fill_value=0.)
    xr = npy.arange(x1, x2 + dx, dx)
    return fy(xr)

def ft(chi,k1,k2,kw=1,tau=2,np=1024,kaiser=True):
    """Usable on exafs data for forward fourier transform. The chi is an array of the 
    kind array([k,exafs]) where k and exafs should be arrays as well. tau is the tau of the kaiser window.
    k1 and k2 are the limits of the window. When kaiser is not used a box window is used instead.
    Returns the frequencies, imaginary part, real part and envelope"""
    ddk=npy.diff(chi[0])
    if not(npy.allclose(ddk[0],ddk)):
            raise Exception("xas.ft: Data Not Interpolated on Equally Spaced Grid! try xas.interpolate")
    else:
        dk = ddk[0]
    if kaiser:
        pos  = int(npy.round((k1 - chi[0][0]) / dk))
        lenk = (int(npy.round(k2 - k1) / dk))
        win  = npy.zeros(len(chi[0]))
        win[pos: pos + lenk]=npy.kaiser(lenk, tau)
    else:
        win = npy.ones(len(chi[0]))
        win[(chi[0] < k1) + (chi[0] > k2)] = 0.
    #ftout = npy.fft.fft(array(chi[1]) * array(chi[0])**kw * win, len(chi[1]))
    ftout = npy.fft.fft(array(chi[1]) * array(chi[0])**kw * win )
    return [npy.fft.fftfreq(len(chi[1]), d=dk/pi), npy.imag(ftout), npy.real(ftout), sqrt(npy.imag(ftout)**2 + npy.real(ftout) **2)]

def kshift(chi,de=0,**kwargs):
    a=1. * chi
    a[0] = a[0] ** 2 + de * 0.2625
    ge = npy.greater_equal(a[0], 0.)
    a[1] = a[1] * ge
    a[0] = sqrt(a[0] * ge)
    #for i in xrange(len(a[0])):
    #    if a[0][i] < 0 or a[0][i] in [npy.nan, npy.inf]:
    #        a[0][i] = 0
    return interpolate(a,**kwargs)

def chisquare(chi1, chi2, k1, k2, r1, r2, epsdat=1e-3, ftw=1.,\
kw=1, tau=2, np=1024, kaiser=True, nidp=1):
    """chisquare returns the chi square value (see EXAFS literature) obtained by comparing 
    chi1 and chi2 within k1 and k2 and r1 and r2. the default is to use r-space comparison.
    chi1 and chi2 must be already on the same grid
    
    The comparison is made in EXAFS and FT space in the limits specified.
    To perform the comparison in one space or the other simply use the ftw ft-weight: 
    0 means no ft comparison.
    1 means only ft comparison.
    
    epsdat is the standard deviation (sigma**2) that must be evaluated by user on data (k-space or E-space). 
    It affects the absolute value of chisquare."""
    if ftw>1:
        raise Exception("xas.chi2: ftw factor must be comprised between 0 and 1")
    
    #Following lines assume interpolated data and equal lengths!
    i1k1 = chi1[0].searchsorted(k1)
    i1k2 = chi1[0].searchsorted(k2)
    i2k1 = chi2[0].searchsorted(k1)
    i2k2 = chi2[0].searchsorted(k2)

    dk = chi1[0][1] - chi1[0][0]
    wink = npy.ones(len( chi1[0][i1k1:i1k2] ))
    #wink[(chi1[0] < k1) + (chi1[0] > k2)] = 0.
    nwink=round((k2 - k1) / dk) + 1
    #
    if int(ftw * 100) > 0:
        epsr = epsdat / sqrt( pi * (2. * kw + 1.)/(dk * (k2 ** (2 * kw + 1.) - k1 ** (2 * kw + 1.))))
        print "epsr=",epsr
        chi1r, chi2r = ft(chi1, k1, k2, kw, tau, np, kaiser),ft(chi2, k1, k2, kw, tau, np, kaiser)
        winr = npy.ones( len(chi1r[0]) )
        winr[ (chi1r[0] < r1) + (chi1r[0] > r2) ]=0.
        nwinr = round((r2 - r1) / (2 * pi / np)) + 1
        diff2r = (sum(winr * (chi1r[1].imag - chi2r[1].imag)**2)+\
        sum(winr * (chi1r[1].real - chi2r[1].real) ** 2)) / (epsr ** 2 * nwinr)*nidp
        diff2 = sum(wink * (chi1[1][i1k1:i1k2] * chi1[0][i1k1:i1k2] **kw\
        - chi2[1][i2k1:i2k2] * chi2[0][i2k1:i2k2] ** kw) ** 2) / (epsdat ** 2 * nwink)
        print "r-chi2 =",diff2r,"k-chi2=",diff2
        return diff2 * (1. - ftw) + diff2r * ftw
    else:
        diff2 = sum(wink * (chi1[1][i1k1:i1k2] - chi2[1][i2k1:i2k2]) ** 2)/(epsdat ** 2 * nwink)
        return diff2

# Use FEFF

class FEFFcalculation:
    def __init__(self, folder = ""):
        """
        The feff code must be specified in the code here below
        as self.executable= or be found in the system variable XAS_FEFF
        The XAS_FEFF system variable override hardcoded value at init.

        Atoms card is reversed: tuple atom contains label, ipot,x,y,z
        example self.config["ATOMS"] = [["AU", 0, 0, 0, 0],]

        Ipot card is replaced by POTENTIALS
        POTENTIALS=[[0,44,"Ru",-1,-1,0.001],[1,44,"Ru",-1,-1,1],etcetera...]
        """
        self.executable = os.getenv("HOME") + "/bin/feff84"
        if os.getenv("XAS_FEFF"): 
            self.executable = os.getenv("XAS_FEFF")
        #THE ATOMS, POTENTIALS AND END CARDS 
        #ARE NOT TO APPEAR IN THE FOLLOWING LIST
        self.key_order = [
        "TITLE", "EDGE", "S02", "CONTROL", "PRINT",
        "EXAFS", "XANES", "SCF", "FMS",
        "AFOLP",
        "EXCHANGE", "CORRECTIONS",
        "NLEG", "RPATH",
        "SIG2", "DEBYE",
        "POLARIZATION",
        "INTERSTITIAL"
        ]
        self.version = 8
        #ATOMS   simbol, ipot, x, y, z
        self.config = {
        "CONTROL": [1, 1, 1, 1, 1, 1],
        "PRINT": [1, 0, 0, 0, 0, 1],
        "TITLE": [],
        "ATOMS": [],
        "POTENTIALS": [],
        "S02": 0.,
        "EXCHANGE": [0,0,0],
        "SCF": [],
        "EXAFS": [],
        "XANES": [],
        "EDGE": "K",
        "POLARIZATION": [],
        "FMS": [],
        "RPATH": 6.,
        "NLEG": 6,
        "CORRECTIONS": [],
        "DEBYE": [],
        "SIG2": None,
        "FREETEXT":"",
        "RMULTIPLIER": 1,
        "AFOLP":None,
        "INTERSTITIAL":[]}
        if folder <> "":
            self.folder = folder
        else:
            self.folder = os.getcwd()+ os.sep + "xas_feff"
        return

    def run(self, writeInput = True):
        """The FEFF calculation is written, started, waits for end 
        and returns exafs or xanes depending on configuration."""
        if writeInput:
            self.writeInput()
        os.system("cd %s && %s $1>FEFF_CALC.log" % (self.folder, self.executable))
        if self.config["CONTROL"][-1] <> 0:
            if self.config["XANES"] <> []:
                return self.readXanes()
            else:
                return self.readExafs()
        
        
    def writeInput(self):
        "It writes actual feff.inp file in self.folder."

        #Modify or check cards
        if self.config["XANES"]<>[] and self.config["FMS"] <> []:
            if self.config["RPATH"] > 0.5:
                print "Warning: FMS active and RPATH > 0.5 ... (intentional ?)"

        #Prepare text for file
        text = []
        for i in self.key_order:
            line = ""
            ivalue = self.config[i]
            if type(ivalue) == bool and ivalue == True:
                line = "i"
            elif type(ivalue) == str and ivalue <> "":
                line = i + " " + ivalue
            elif type(ivalue) in [float,int]:
                line = i + " %g" % ivalue
            elif type(ivalue) == list and ivalue <> []:
                fmtstr = " %g" * len(ivalue)
                line = i + fmtstr % tuple(ivalue)
            if line <> "": text.append(line)
        
        #FREETEXT
        text.append( self.config["FREETEXT"] )
        
        #POTENTIALS
        text.append("POTENTIALS")
        #    Check if all potentials have been defined and eventually generate them
        self.verifyPotentials()
        #    Write potentials
        for i in self.config["POTENTIALS"]:
                #IPOT Z  LABEL  LMAX1 LMAX2 XNATPH
            text.append(" " * 3 + "%2i %2i %2s %3g %3g %4.2f" % tuple(i))

        #ATOMS
        text.append("ATOMS")
        i0=self.config["ATOMS"][0]
        for i in self.config["ATOMS"]:
            text.append(" "*2+"%+7.4f  %+7.4f  %+7.4f  %2i  %6s  %7.4f" % (i[2], i[3], i[4], i[1], i[0],sqrt(sum((array(i[2:5])-i0[2:5])**2))))
        
        #Make Folder
        try:
            os.listdir(self.folder)
        except OSError, tmp:
            os.makedirs(self.folder)
        f = file(self.folder + os.sep + "feff.inp", "w")
        for i in text:
            f.write(i + "\n")
        f.close()
        #It should return nothing, but for debugging it keeps the list.
        self.feff_inp=text
        return

    def readExafs(self):
        "returns calculated exafs spectrum"
        out = []
        for i in range(5):
            try:
                out = npy.loadtxt(self.folder + os.sep + "chi.dat").transpose()
                break
            except:
                time.sleep(0.5)
        if out == []:
            print os.listdir(self.folder)
            raise Exception("%s not found!" % (self.folder + os.sep + "chi.dat"))
        return out

    def readXanes(self):
        "returns calculated xanes spectrum"
        out = []
        for i in range(5):
            try:
                out = npy.loadtxt(self.folder + os.sep + "xmu.dat").transpose()
                break
            except:
                time.sleep(0.5)
        if out == []:
            print os.listdir(self.folder)
            raise Exception("%s not found!" % (self.folder + os.sep + "chi.dat"))
        return out

    def cleanup(self):
        """wipe off calculation folder"""
        if self.folder == "":
            print "No folder to clean"
        else:
            try:
                os.rmdir( self.folder )
            except exc.OSError:
                print "xas.feff_calculation.cleanup: Folder cannot be removed."
        return

    def verifyPotentials(self):
        """Check if ipots have been entered for all atoms"""
        ipots=[]
        for i in self.config["POTENTIALS"]:
            ipots.append(i[0])
        for i in self.config["ATOMS"]:
            if not (i[1] in ipots):
                print "Error checking for ipots! One potential has not been defined!"
                print "Using auto potentials instead!"
                self.autoPotentials()
                return
        return
    
    def autoPotentials(self):
        """
        Generates automatically ipots with default cards.
        The stechiometry is calculated from model
        typical ipot_line looks like
        Ipot  Z  tag Lmax1 Lmax2 occupancy
        1 44  Ru -1 -1 0.33
        """
        ipots_found={}
        for i in self.config["ATOMS"]:
            if not i[1] in ipots_found.keys():
                ipots_found[i[1]] = [pymucal.atomic_data.atoms[i[0]],1]
            else:
                ipots_found[i[1]] = [pymucal.atomic_data.atoms[i[0]],ipots_found[i[1]][1]+1]
        #Erase any previous POTENTIALS config
        self.config["POTENTIALS"] = []
        no_atoms=len(self.config["ATOMS"])
        for i in npy.sort(ipots_found.keys()):
            self.config["POTENTIALS"].append([i, ipots_found[i][0],\
            pymucal.atomic_data.atoms_by_z[ipots_found[i][0]], -1, -1,\
            float(ipots_found[i][1])/no_atoms])
        return

    def clean_config(self):
        self.config = {
        "CONTROL": [1, 1, 1, 1, 1, 1],
        "PRINT": [1, 0, 0, 0, 0, 1],
        "TITLE": [],
        "OVERLAP": "",
        "ATOMS": [],
        "POTENTIALS": [],
        "S02": 0.,
        "EXCHANGE": [],
        "SCF": [],
        "EXAFS": [],
        "XANES": [],
        "EDGE": "K",
        "POLARIZATION": [],
        "FMS": [],
        "RPATH": 6.,
        "NLEG": 6,
        "CORRECTIONS": [],
        "DEBYE": [],
        "SIG2": 0,
        "FREETEXT":""
        }
        return

    def import_feff(self,filename):
        f = open(filename,"r")
        ll=map(lambda x:x.strip(), f.readlines())
        f.close()
        il=iter(ll)
        #Read control keys
        i = ""
        i_split = []
        while(i<>"ATOMS"):
            try:
                i = il.next().strip()
            except StopIteration:
                break
            i_split = i.split()
            if len(i_split) == 0:
                pass
            elif i.startswith("*"):
                pass
            elif i == "":
                pass
            elif i.startswith("ATOMS"): 
                i = "ATOMS"
                break
            elif i_split[0] in self.config.keys():
                if i_split[0] in ["CONTROL", "PRINT", "EXCHANGE", \
                "POLARIZATION", "CORRECTIONS", "DEBYE", "SCF", \
                "FMS", "EXAFS","XANES"]:
                    pass
                elif i_split[0] == "TITLE":
                    self.config[i_split[0]].append(i[6:])
                elif i_split[0] == "EDGE":
                    self.config[i_split[0]] = i_split[1]
                elif i_split[0] == "POTENTIALS":
                    while(True):
                        i = il.next().strip()
                        i_split = i.split()
                        if i == "" or i.startswith("*"):
                            pass
                        elif i_split[0] in self.config.keys():
                            break
                        else:
                            if len(i_split) <3:
                                i_split+=[pymucal.atomic_data.atoms_by_z[i_split[1]],\
                                -1,-1]
                            self.config["POTENTIALS"].append(
                            [int(i_split[0]), int(i_split[1]), 
                            i_split[2]]+i_split[3:len(i_split)]
                            )
                elif i_split[0] in ["S02", "RPATH", "NLEG", "SIG2"]:
                    self.config[i_split[0]] = float(i_split[1])
                else:
                    raise Exception("Unrecognized keyword parsing file: "\
                    + filename)
        #Start reading atom coordinates
        while(i<>"END"):
            try:
                i=il.next().strip()
            except StopIteration:
                i = "END"
                break
            if i.startswith("*") or i=="":
                pass
            elif i.startswith("END"):
                break
            else:
                nat = i.split()
                if len(nat) == 4:
                    x, y, z, ipot = nat
                    r = 0.
                    symbol = ""
                elif len(nat) == 5:
                    x, y, z, ipot, symbol = nat
                    r = 0.
                elif len(nat) > 5:
                    x, y, z, ipot, symbol, r = nat
                else:
                    raise Exception("Incomplete or invalid atom entry! line="+i)
                self.config["ATOMS"].append([symbol, int(ipot), 
                float(x), float(y), float(z)])
        del ll,f,il
        return

    def import_model(self, model, absorber = ["Au", 0., 0., 0., "Au0"], cutoff = 10., site=False):
        """Convert a model list into an ATOMS list, then generate a config.
        Absorbing atom (ipot 0 in FEFF) must be specified as second argument
        The absorber is specified as a complete entry of the model list. 
        Only one absorber accepted.
        if site is True: a different ipot is generated for every different site label."""
        self.config["ATOMS"]=[]
        ipot=0
        cutoff_2 = cutoff ** 2
        atom_types_found = []
        atoms_found = []
        distances2 = []
        center = array(absorber[1:4])
        temp_atoms = []
        for i in model:
            if sum((array(i[1: 4]) - array(absorber[1: 4])) ** 2 ) <= cutoff_2:
                temp_atoms.append(i)
                distances2.append(sum((array([i[1], i[2], i[3]])-center)**2))
        for i in npy.argsort(distances2):
            at = temp_atoms[i]
            if at == absorber:
               self.config["ATOMS"].append([at[0], 0, at[1]-center[0], at[2]-center[1], at[3]-center[2], at[4]])
            elif site and [at[0], at[4]] not in atom_types_found:
               ipot += 1
               atom_types_found.append([at[0], at[4]])
               self.config["ATOMS"].append([at[0], ipot, at[1]-center[0], at[2]-center[1], at[3]-center[2], at[4]])
            elif not site and at[0] not in atoms_found:
               ipot += 1
               atoms_found.append(at[0])
               self.config["ATOMS"].append([at[0], ipot, at[1]-center[0], at[2]-center[1], at[3]-center[2], at[4]])
            else:
                if site:
                    self.config["ATOMS"].append([at[0], atom_types_found.index([at[0], at[4]]) + 1, at[1]-center[0], at[2]-center[1], at[3]-center[2], at[4]])
                else:
                    self.config["ATOMS"].append([at[0], atoms_found.index(at[0]) + 1, at[1]-center[0], at[2]-center[1], at[3]-center[2], at[4]])

        del temp_atoms, distances2
        self.autoPotentials()
        return

#Calculate over a model (average signal over a number of sites) parallel version
def computeXAS(model, axis = None, absorber = None, feff_config = None, periodic = True, mode = "EXAFS", all_site=False, cutoff = 8, np=4, tmpdir=None, repeat=1):
    """Calculate the average EXAFS or XANES spectrum over the desired absober in a model.
    
    The model must be described as a list of list:
    e.g.  [["Au",0.,0.,0.,"site1"],["O",1.25,1.25,1.25,"site2"]....]
    the first is the atom name (standard IUPAC)
    the coordinates (in Angstrom) follow,
    the site1, site2 labels may be anything, even a repetition of the atomic symbol.
    
    The model is replicated once in all directions, if the periodic card is set to True;
    but the calculation is performed only on atoms inside the original model box.
    
    The axis is a tuple informing how to replicate the model to obtain periodicity
    [a, b, c, alpha, beta, gamma] 
    alpha, beta and gamma are the angles as in cristallographic notation and in degrees.
    a, b, c are the dimensions along the axis of the model, not of the unit cell.

    NOTA: axis c is always intended aligned along z.  axis a is in the xz plane.

    The absorber is the name of the atom (e.g. "Au").

    The feff_config is a dictionary that may be passed on to the xas.FEFFcalculation object
    if feff_config is defined, only the card specified will replace the default cards of xas.FEFFcalculation .
        E.g.  feff_config={"XANES": 4, "FMS": 6, "SCF": 3.5, "RPATH": 0.1}
    
    If periodic is unset (False) the calculation is made on the model as it is.

    If the mode is set to EXAFS the average EXAFS signal is returned, if it is set to XANES, 
    the average XANES is returned.

    if all_site is True the average spectrum is returned toghether with a list of 
    all absorber sites and their corresponding spectrum:  [average, [ [[site1],[spectrum]],... ]]
    
    cutoff is used to feed a cluster not larger than cutoff (A) around each absorber to FEFF.

    np: number of simultaneous FEFF processes 

    repeat = number of times the cell is repated for periodic calculation, 
    very useful for small cells

    -------
    Concept
    -------
    1) Find all absorbers (coordinates and so on)
    2) Expand model
    3) cycle through absorbers (MPI not implemented yet)
        i) Make FEFF_object for absorber
        ii) Adjust FEFF_config to requested calculation
        iii) run and collect result
    4) Average results and return average + collection of individual signals classed for central atom
    """
    #Find absorbers in model
    absorbers_in_model = []
    for i in model:
        if i[0] == absorber:
            absorbers_in_model.append(i)
    #Make larger model if periodic

    if periodic:
        extended_model = []
        generatrice = []
        celle = [(i, j, k) for i in range(-repeat, repeat+1) for j in range(-repeat, repeat+1) for k in range(-repeat, repeat+1)]
        for i in celle:
            generatrice.append(makeModel.Fractional2Normal(i, axis))
        for shift in generatrice:
            for atom in model:
                extended_model.append([atom[0], atom[1] + shift[0], atom[2] + shift[1], atom[3] + shift[2], atom[4]])
        del generatrice, celle
    else:
        extended_model = model + []
    lista_calcoli = []  

    calcolo_index = 0
    if tmpdir <> None:
        _feff_dir = tmpdir
    else:
        _feff_dir = os.getcwd()
    for abs_at in absorbers_in_model:
        calcolo_index += 1
        calcolo = FEFFcalculation(folder =  _feff_dir + os.sep + "%04i"%(calcolo_index))
        calcolo.import_model(extended_model, absorber = abs_at, cutoff = cutoff)
        calcolo.__absorber = abs_at
        if mode == "EXAFS":
            calcolo.config["EXAFS"] = 20.
        elif mode == "XANES":
            calcolo.config["XANES"] = 4.
        for i in feff_config:
            if i not in ["ATOMS", "POTENTIALS"]:
                calcolo.config[i] = feff_config[i]
        lista_calcoli.append(calcolo)
    del calcolo, calcolo_index

    np = min(multiprocessing.cpu_count(), np)
    feff_pool = multiprocessing.Pool(np)
    print "Using  %i processess over %i available cores for %i calculations." %\
    (np, multiprocessing.cpu_count(), len(lista_calcoli))

    results_basket = feff_pool.map(runSingleFEFF, lista_calcoli)
    feff_pool.close()
    del lista_calcoli
    #print shape(results_basket[0])
    if all_site == True:
        return npy.average(map(lambda x: array(x[1]), results_basket), axis = 0), results_basket
    else:
        return npy.average(map(lambda x: array(x[1]), results_basket), axis = 0)

#Calculate over a model as before, but uses an already extended model and calculates only on a given list of absorbers (indexes)
def computeXASlist(model, absorber="", absorberList = [], feff_config = None, mode = "EXAFS", cutoff = 8, np=4, tmpdir=None):
    """Calculate the average EXAFS or XANES spectrum over an already extended model and calculates only on a given list of absorbers (indexes)
    separate signals are returned. Do not mix different absorber types.

    The model must be described as a list of list:
    e.g.  [["Au",0.,0.,0.,"site1"],["O",1.25,1.25,1.25,"site2"]....]
    the first is the atom name (standard IUPAC)
    the coordinates (in Angstrom) follow,
    the site1, site2 labels may be anything, even a repetition of the atomic symbol.
    
    The absorber is the name of the atom (e.g. "Au").

    The feff_config is a dictionary that may be passed on to the xas.FEFFcalculation object
    if feff_config is defined, only the card specified will replace the default cards of xas.FEFFcalculation .
        E.g.  feff_config={"XANES": 4, "FMS": 6, "SCF": 3.5, "RPATH": 0.1}
    
    If the mode is set to EXAFS the average EXAFS signal is returned, if it is set to XANES, 
    the average XANES is returned.

    cutoff is used to feed a cluster not larger than cutoff (A) around each absorber to FEFF.

    np: number of simultaneous FEFF processes 

    """
    #Check absorbers
    absorbers_in_model = []
    for i in absorberList:
        if model[i][0] <> absorber:
            raise Exception("Absorber is not what expected at site: %i" % i)

    lista_calcoli = []  

    calcolo_index = 0
    if tmpdir <> None:
        _feff_dir = tmpdir
    else:
        _feff_dir = os.getcwd()
    for iAbsAt in absorberList:
        absAt = model[iAbsAt]
        calcolo_index += 1
        calcolo = FEFFcalculation(folder =  _feff_dir + os.sep + "%04i"%(calcolo_index))
        calcolo.import_model(model, absorber = absAt, cutoff = cutoff)
        calcolo.__absorber = absAt
        if mode == "EXAFS":
            calcolo.config["EXAFS"] = 20.
        elif mode == "XANES":
            calcolo.config["XANES"] = 4.
        for i in feff_config:
            calcolo.config[i] = feff_config[i]
        lista_calcoli.append(calcolo)
    del calcolo, calcolo_index

    np = min(multiprocessing.cpu_count(), np)
    feff_pool = multiprocessing.Pool(np)
    print "Using  %i processess over %i available cores for %i calculations." %\
    (np, multiprocessing.cpu_count(), len(lista_calcoli))

    results_basket = feff_pool.map(runSingleFEFF, lista_calcoli)
    feff_pool.close()
    del lista_calcoli

    return results_basket

def runSingleFEFF(calcolo):      
    tmp = list(calcolo.run())
    #Cut bad 0 point that exists in some cases
    if abs(tmp[0][0]) < 1e-6:
        for i in range(len(tmp)):
            tmp[i] = tmp[i][1:]
    for i in os.listdir(calcolo.folder):
        os.remove(calcolo.folder + os.sep + i)
    os.rmdir(calcolo.folder)
    return calcolo.__absorber, array(tmp)


