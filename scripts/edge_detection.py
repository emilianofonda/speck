from numpy import *
from pylab import *
import tables


def ttl_edges(y,rising=True,phase=0):
    """Use maximum and minimum value to determine amplitude and base of signal,
    provides indices of rising edges if rising=True or lowering if False
    provides average period (number of points) as second output
    return indices(array),period(scalar)
    phase is a shift of the period in degrees"""
    
    level = 0.5 * (min(y) + max(y))
    
    if rising:
        idx = [where(y<level)[0][i] for i in where(diff(where(y<level))[0]>1)[0]]
    else:
        idx = [where(y>level)[0][i] for i in where(diff(where(y>level))[0]>1)[0]]
    
    period = int(mean(diff(idx)))
    
    delta=int(round(period * phase /360.))
    idx = [i+delta for i in idx if i+delta+period < len(y)]
    return idx, period

def fold_edges(y_signal,y_ttl,rising=True,timescale=(),phase=0):
    """Use ttl_edges to fold a signal over itself by analysing an associated ttl
    if timescale is not None it must have the same length of y_signal 
    and being an equispaced sampling time
    if timescale == (): returns y_fold
    if len timescale > 0 : returns y_fold, x_fold
    phase is a shift in degrees"""    
    
    indices,period = ttl_edges(y_ttl,rising=rising)

    if indices[-1]+period > len(y_signal):
        last = -1
    else:
        last = None
    y_fold = sum([y_signal[i:i+period] for i in indices[:last]],axis=0)/len(indices)
    if timescale == () or len(timescale) == 0 :
        return y_fold
    else:
        x_fold = sum(\
        [timescale[i:i+period]-timescale[i] for i in indices[:last]],axis=0)\
        /len(indices)
        return y_fold, x_fold

def fold_signal(filename,
    signal="/post/FLUO",ttl="/post/I3",timescale="/data/X1",
    rising=True,phase=0):
    
    """open the hdf file and fold the signal provided following the ttl cycles
    rising means rising ttl edge as trigger
    
    works only on .hdf files!
    phase is a shift in degrees"""
    
    datasource = tables.open_file(filename, "r")

    y_signal = datasource.get_node(signal).read()
    y_ttl = datasource.get_node(ttl).read()
    x_signal = datasource.get_node(timescale).read()

    datasource.close()
    
    y_fold, x_fold = fold_edges(y_signal, y_ttl, rising, timescale = x_signal)
    
    savetxt(filename[:filename.rfind(".")]+"_folded.txt",transpose((x_fold,y_fold)))

    return x_fold,y_fold


def test(rising=True,phase=0.):
    np = 8000
    period = 80
    base = 4
    amplitude = 4
    noise = amplitude*0.25

    x = arange(np)
    
    y = array([base+(sign(i)+1)*0.5*amplitude\
     for i in sin(x/period*2*pi)])+rand(np)*noise

    level = base + amplitude * 0.5
    
    if rising:
        idx = [where(y<level)[0][i] for i in where(diff(where(y<level))[0]>1)[0]]
    else:
        idx = [where(y>level)[0][i] for i in where(diff(where(y>level))[0]>1)[0]]

    p_d = int(mean(diff(idx)))
    delta = int(round(p_d * phase / 360.))
    idx = [i + delta for i in idx if i+delta+p_d<len(y)]
    y_ave = sum([y[i:i+p_d] for i in idx],axis=0)/len(idx)
    x_ave = arange(p_d)
    
    ax1=subplot(2,1,1)
    ax2=subplot(2,1,2)
    ax1.plot(x,y)
    ax1.plot(x.take(idx),y.take(idx),"x")
    ax2.plot(x_ave,y_ave,'k-')
    show()
    return 1    

