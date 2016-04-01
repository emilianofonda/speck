import numpy
import xas
import pylab
import scipy

def polySc(x,*args):
    return pylab.polyval(args, x)   

def dentist(filename, e0=20060., \
pre1  = -300, pre2  = -60, nor1  =  60, nor2  = -1,\
poly1 =  20., poly2 =  -1, polyN =  -1, kweight = -1, mode="t"):
    """mode can be t = transmission or f = fluorescence or s = standard
    """
    baseFilename = filename[:filename.rfind(".")]
    m = pylab.loadtxt(filename).transpose()
    fig1 = pylab.figure(1,figsize=[12,10],facecolor="w")
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
        nor2 = ene[-1]
    if poly2 <0 :
        poly2 = ene[-1]
    
    if poly2 < poly1:
        poly2 = poly1 +10
    if nor2 < nor1:
        nor2 = nor1 +10
    if pre2 < pre1:
        pre2 = pre1 + 10
   
    ie0 = ene.searchsorted(e0)
    ipre1 = ene.searchsorted(e0+pre1)
    ipre2 = max(ipre1+10, ene.searchsorted(e0+pre2))
    inor1 = min(ene.searchsorted(e0+nor1), len(ene)-10)
    inor2 = min(ene.searchsorted(e0+nor2), len(ene)-1)
    ipoly1 = min(ene.searchsorted(e0+poly1), len(ene)-10)
    ipoly2 = min(ene.searchsorted(e0+poly2), len(ene)-1)
    if inor2 - inor1 < 5: inor1 = inor2 -30 
    
    InterpENE = numpy.array(list(numpy.arange(ene[1],ene[ipre2],2)) + list (ene[ipre2:inor1]) + list(numpy.arange(ene[inor1],ene[-2],1)) )
    InterpXMU = scipy.interpolate.interp1d(ene,xmu, bounds_error=False)(InterpENE)
       
    numpy.savetxt(baseFilename+".xmu", numpy.transpose(numpy.array([InterpENE,InterpXMU])))
    preEdge = pylab.polyfit(ene[ipre1:ipre2],xmu[ipre1:ipre2],1)
    
    if ene[inor2] - ene[inor1] > 1000:
        norDeg = 3
    elif 200 <= ene[inor2] - ene[inor1] <=1000:
        norDeg = 2
    elif 75 <= ene[inor2] - ene[inor1] <200:
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
    pylab.savetxt(baseFilename+".chik", pylab.transpose(mOut))
    pylab.subplot(221)
    pylab.title(filename)
    pylab.grid()
    pylab.plot(ene,xmu,"b-",label="${\mu}$")
    pylab.plot(ene,pylab.polyval(norPoly, ene),"k-.",label="$ \mu_{post} $")
    pylab.plot(chiE,bkg,"r--",label="$\mu_{0}$")
    pylab.plot(ene,pylab.polyval(preEdge,ene),"g--",label="$ \mu_{pre} $")
    pylab.legend(loc="best",ncol=2, frameon=False)
    pylab.xlabel("Energy (eV)")

    pylab.subplot(222)
    pylab.title(filename)
    pylab.grid()
    xmuNOR = (xmu-pylab.polyval(preEdge,ene))/(pylab.polyval(norPoly,ene)-pylab.polyval(preEdge,ene))
    derNOR = pylab.diff(xmuNOR[ipre2:inor1])/pylab.diff(ene[ipre2:inor1])
    derNOR = derNOR / max(derNOR)
    derENE = ene[ipre2:inor1-1] + pylab.diff(ene[ipre2:inor1])*0.5
    iMaxDer = derNOR.argmax()
    pylab.plot(ene, xmuNOR,"b-",label="$ \mu $")
    pylab.plot(derENE, derNOR - 0.5,"g-",label="$\delta \mu /\delta E$")
    pylab.annotate("%8.2f" % e0, xy=(e0,0.9), xytext=(e0-60,0.9),\
    arrowprops={"width":0.1,"headwidth":5,"frac":0.5,"color":"r","shrink":0.9})
    pylab.annotate("%8.2f" % derENE[iMaxDer], xy=(derENE[iMaxDer],max(derNOR)-0.5), xytext=(derENE[iMaxDer]-60,max(derNOR)-0.5),\
    arrowprops={"width":0.1,"headwidth":5,"frac":0.5,"color":"g","shrink":0.9})
    #pylab.arrow(derENE[iMaxDer], derNOR[iMaxDer],-20,-0.2, label="%8.2f" % derENE[iMaxDer])
    pylab.legend(loc="best",ncol=2, frameon=False)
    pylab.arrow(ene[ie0],0,0,1.1,ls="dotted",color="red")
    pylab.xlim([e0-70.,e0+120])
    pylab.ylim([-1.5,1.5])
    pylab.xlabel("Energy (eV)")

    pylab.subplot(223)
    pylab.plot(chiK, exafs * chiK**kweight,"b--",label="$k^%i\chi(k)$"%kweight)
    #pylab.plot(chiK, (bkg-pylab.polyval(norPoly,chiE))*chiK**kweight * 0.1 * \
    #(max(exafs)/(bkg-pylab.polyval(norPoly,chiE))), label="${\mu_0}/{10}$")
   
    pylab.xlabel("k ($\AA^{-1}$)")
    pylab.ylabel("$k^%i$$\chi$(k)"%kweight)
    
    iexafs = xas.interpolate(mOut,dk=0.04)
    mft = xas.ft(iexafs,3,chiK[-1],kw=kweight)
    
    pylab.plot(iexafs[0], iexafs[1] * iexafs[0]**kweight, "r-", linewidth=1,label="$Interp(k^%i\chi(k))$"%kweight)
    pylab.xlim([min(chiK),max(chiK)])
    pylab.legend(loc="best",ncol=1, frameon=False)
    pylab.grid()
    
    pylab.subplot(224)

    #mft = mft[:,int(len(mft[0])/2):]
    ps0 = int(len(mft[0])/2)
    pylab.plot(mft[0][:ps0],mft[1][:ps0],"r-",mft[0][:ps0],mft[3][:ps0],"b-",mft[0][:ps0],-mft[3][:ps0],"b-")
    pylab.xlabel("$R(\AA)$")
    pylab.ylabel("$FT[k^%i\chi(k)]$"%kweight)
    pylab.xlim([0,6])
    pylab.grid()
    pylab.draw()
    pylab.savetxt(baseFilename+".chir", pylab.transpose(mft))
    return
    #return mOut
    
    
    
    
    
    
    
