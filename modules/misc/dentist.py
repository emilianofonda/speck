import numpy
import xas
import pylab
import scipy

def polySc(x,*args):
    return pylab.polyval(args, x)   

def dentist(filename, e0=20060., \
pre1  = -300, pre2  = -40, nor1  =  45, nor2  = -1,\
poly1 =  15., poly2 =  -1, polyN =  -1, kweight = -1, rmax=6,\
mode="t", figN=1, overlap=False,out=False):
    """mode can be t = transmission or f = fluorescence or s = standard
    """
    baseFilename = filename[:filename.rfind(".")]
    m = pylab.loadtxt(filename).transpose()
    fig1 = pylab.figure(figN,figsize=[12,10],facecolor="w")
    if not overlap:
        fig1.clear()
    m=m[:,pylab.argsort(m[0])]
    ene = m[0]
    if mode == "t" or mode =="":
        xmu = m[2]
    elif mode == "f":
        xmu = m[3]
    elif mode == "s":
        xmu = m[4]
    else:
        raise Exception("unknown dentist mode.")

    if nor2 < 0 :
        nor2 = min(ene[-1] - e0, nor1+300)
    if poly2 <0 :
        poly2 = ene[-1] - e0
    
    if poly2 < poly1:
        poly2 = poly1 +10
    if nor2 < nor1:
        nor2 = nor1 +10
    if pre2 < pre1:
        pre2 = pre1 + 10
   
    ie0 = ene.searchsorted(e0)
    if ene[0] > e0-pre2:
        ipre1 = 0
        ipre2 = 30
    else:
        ipre1 = ene.searchsorted(e0+pre1)
        ipre2 = max(ipre1+10, ene.searchsorted(e0+pre2))
        
    inor1 = min(ene.searchsorted(e0+nor1), len(ene)-10)
    inor2 = min(ene.searchsorted(e0+nor2), len(ene)-1)
    ipoly1 = min(ene.searchsorted(e0+poly1), len(ene)-10)
    ipoly2 = min(ene.searchsorted(e0+poly2), len(ene)-1)
    if inor2 - inor1 < 5: inor1 = inor2 -30 
    
    ider1 = max(0, ene.searchsorted(e0 - 80))
    ider2 = min(len(ene), ene.searchsorted(e0 + 140))
    
    #InterpENE = numpy.array(list(numpy.arange(ene[1],ene[ipre2],2)) + list (ene[ipre2:inor1]) + list(numpy.arange(ene[inor1],ene[-2],1)) )
    #InterpXMU = scipy.interpolate.interp1d(ene,xmu, bounds_error=False)(InterpENE)
       
    #if out:
    #    numpy.savetxt(baseFilename+".xmu", numpy.transpose(numpy.array([InterpENE,InterpXMU])))
    preEdge = pylab.polyfit(ene[ipre1:ipre2],xmu[ipre1:ipre2],1)
    
    if ene[inor2] - ene[inor1] > 1000:
        norDeg = 3
    elif 500 <= ene[inor2] - ene[inor1] <=1000:
        norDeg = 2
    elif 75 <= ene[inor2] - ene[inor1] <500:
        norDeg = 1
    else:
        norDeg = 0
        
    norPoly = pylab.polyfit(ene[inor1:inor2],xmu[inor1:inor2], norDeg)
    
    Step = pylab.polyval(norPoly, e0) - pylab.polyval(preEdge, e0)
    
    print "Edge Step = ",Step
    
    chi = xmu[ipoly1:ipoly2]
    chiE = ene[ipoly1:ipoly2]
    
    chiK = pylab.sqrt(0.2625 * (chiE-e0))
    if kweight < 0:
        if chiK[-1] >=16:
            kweight = 3
        elif 12 < chiK[-1] < 16:
            kweight = 2
        elif chiK[-1]<12:
            kweight =1

    if polyN < 0:
        polyN = min(9, numpy.round(chiK[-1]/2.))
    
    #bkgPoly = pylab.polyfit(chiK, chi, polyN, w=chiK**kweight)
    bkgPoly = scipy.optimize.curve_fit(polySc,chiK, chi, [1.,]*polyN, sigma=1./chiK**kweight)[0]
    bkg = pylab.polyval(bkgPoly, chiK)
    exafs = (chi - bkg) / Step
    mOut = pylab.array([chiK, exafs],"f")
    mOutSG = pylab.array([chiK, xas.SavitzkyGolay(exafs,19,5)],"f")
    if out:
        pylab.savetxt(baseFilename+".chik", pylab.transpose(mOut))
    pylab.subplot(221)
    if not overlap:
        pylab.title(filename)
    pylab.grid()
    if not overlap:
        pylab.plot(ene,xmu,"b-",label="${\mu}$")
        pylab.plot(ene,pylab.polyval(norPoly, ene),"k-.",label="$ \mu_{post} $")
        pylab.plot(chiE,bkg,"r--",label="$\mu_{0}$")
        pylab.plot(ene,pylab.polyval(preEdge,ene),"g--",label="$ \mu_{pre} $")
    else:
        pylab.plot(ene,xmu,label="%s"%filename[:-4])
    if overlap:
        pylab.legend(loc="best",frameon=False)
    else:
        pylab.legend(loc="best",ncol=2, frameon=False)

    pylab.xlabel("Energy (eV)")

    pylab.subplot(222)
    if not overlap:
        pylab.title(filename)
    pylab.grid()
    xmuNOR = (xmu-pylab.polyval(preEdge,ene))/(pylab.polyval(norPoly,ene)-pylab.polyval(preEdge,ene))
    derNOR = pylab.diff(xmuNOR[ider1:ider2])/pylab.diff(ene[ider1:ider2])
    ###derNORsg = pylab.diff(xas.SavitzkyGolay(xmuNOR[ider1:ider2],23,3))/pylab.diff(ene[ider1:ider2])
    derNORsg = xas.SavitzkyGolay(pylab.diff(xas.SavitzkyGolay(xmuNOR[ider1:ider2],13,5))/pylab.diff(ene[ider1:ider2]),13,5)
    derNOR = derNOR / max(derNOR)
    derNORsg = derNORsg / max(derNORsg)
    derENE = ene[ider1:ider2-1] + pylab.diff(ene[ider1:ider2])*0.5
    iMaxDer = derNORsg.argmax()
    if not overlap:
        pylab.plot(ene, xmuNOR,"b-",label="$ \mu $")
        pylab.plot(derENE, derNOR - 0.5,"g-",label="$\delta \mu /\delta E$")
        pylab.plot(derENE, derNORsg - 0.5,"k-",linewidth=1)
        pylab.annotate("%8.2f" % e0, xy=(e0,0.9), xytext=(e0-60,0.9),\
        arrowprops={"width":0.1,"headwidth":5,"frac":0.5,"color":"r","shrink":0.9})
        pylab.annotate("%8.2f" % derENE[iMaxDer], xy=(derENE[iMaxDer],max(derNOR)-0.5), xytext=(derENE[iMaxDer]-60,max(derNOR)-0.5),\
        arrowprops={"width":0.1,"headwidth":5,"frac":0.5,"color":"g","shrink":0.9})
        #pylab.arrow(derENE[iMaxDer], derNOR[iMaxDer],-20,-0.2, label="%8.2f" % derENE[iMaxDer])
        pylab.legend(loc="best",ncol=2, frameon=False)
        pylab.arrow(ene[ie0],0,0,1.1,ls="dotted",color="red")
    else:
        pylab.plot(ene, xmuNOR,label="%s"%filename[:-4])
    pylab.xlim([e0-70.,e0+120])
    pylab.ylim([min(derNOR - 0.7),max(1.5,max(0.25 + xmuNOR[ipre2:inor1]))])
    pylab.xlabel("Energy (eV)")

    pylab.subplot(223)
    #pylab.plot(chiK, exafs * chiK**kweight,"b--",label="$k^%i\chi(k)$"%kweight)
    #pylab.plot(chiK, (bkg-pylab.polyval(norPoly,chiE))*chiK**kweight * 0.1 * \
    #(max(exafs)/(bkg-pylab.polyval(norPoly,chiE))), label="${\mu_0}/{10}$")
   
    pylab.xlabel("k ($\AA^{-1}$)")
    pylab.ylabel("$k^%i$$\chi$(k)"%kweight)
   
    int_dk = 0.04

    iexafs = xas.interpolate(mOut,dk=int_dk)
    iexafsSG = xas.interpolate(mOutSG,dk=int_dk)
    
    np = 10
    mft = xas.ft(iexafs,3,chiK[-1],kw=kweight,np=10)
    
    if overlap :
        pylab.plot(iexafs[0], iexafs[1] * iexafs[0]**kweight, linewidth=1,label="%s"%filename[:-4])
    else:
        pylab.plot(iexafs[0], iexafs[1] * iexafs[0]**kweight, "b-", linewidth=1,label="$k^%i\chi(k)$"%kweight)
    #if len(iexafsSG[0])/iexafsSG[0][-1]>50:
    #    pylab.plot(iexafsSG[0], iexafsSG[1] * iexafsSG[0]**kweight, "k--", linewidth=2,label="$Smoothed$")
    pylab.xlim([min(chiK),max(chiK)])
    if not overlap:
        pylab.legend(loc="best",ncol=1, frameon=False)
    pylab.grid()
    
    pylab.subplot(224)

    mft = mft[:,:int(len(mft[0])/2)]
    ps0 = int(len(mft[0])/2)
    if not overlap:
        pylab.plot(mft[0][:ps0],mft[1][:ps0],"r-",mft[0][:ps0],mft[3][:ps0],"b-",mft[0][:ps0],-mft[3][:ps0],"b-")
    else:
        pylab.plot(mft[0][:ps0],mft[3][:ps0])
    #print "FFT Number of Points = ", ps0
    pylab.xlabel("$R(\AA)$")
    pylab.ylabel("$FT[k^%i\chi(k)]$"%kweight)
    pylab.xlim([0,min(rmax,10)])
    pylab.grid()
    pylab.draw()
    if out:
        pylab.savetxt(baseFilename+".chir", pylab.transpose(mft))
    #return mOut
    return

def compare(filename, e0=20060., pre1  = -300, pre2  = -40, nor1  =  45, nor2  = -1,\
poly1 =  15., poly2 =  -1, polyN =  -1, kweight = -1, rmax=6, mode="t", figN=1):
    if type(filename) == str:
        return dentist(filename,e0=e0,pre1=pre1,pre2=pre2,nor1=nor1,nor2=nor2,poly1=poly1,poly2=poly2,polyN=polyN,kweight=kweight,rmax=rmax,\
mode=mode,figN=figN,overlap=False,out=False)
    elif type(filename) in [list,tuple,numpy.array]:
        f=pylab.figure(figN,figsize=[12,10],facecolor="w")
        f.clear()
        dentist(filename[0],e0=e0,pre1=pre1,pre2=pre2,nor1=nor1,nor2=nor2,poly1=poly1,poly2=poly2,polyN=polyN,kweight=kweight,rmax=rmax,\
        mode=mode,figN=figN,overlap=True,out=False)
        for i in filename[1:]:
            dentist(i,e0=e0,pre1=pre1,pre2=pre2,nor1=nor1,nor2=nor2,poly1=poly1,poly2=poly2,polyN=polyN,kweight=kweight,rmax=rmax,\
            mode=mode,figN=figN,overlap=True,out=False)
    return
