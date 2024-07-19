from numpy import *
from pylab import *
import tables

def chopper_series(prefix,folder="./",trashfirst=0,chopper="/post/I3",\
data="/post/FLUO",timescale="/data/X1",data2="/post/I2",phase=0,graphics=True,usablefiles=[]):

    def test_file(ff):
        f=tables.open_file(ff,"r")
        try:
            toto=f.get_node(chopper).read()
            toto = True
            #print("%s is readable."%ff)
        except:
            toto = False
        finally:
            f.close()
        return toto

    files = [i for i in os.listdir(folder) if i.startswith(prefix) and i.endswith(".hdf") \
    and test_file(folder+os.sep+i)]
    files.sort()
    print(files)
    if usablefiles != []:
        files = [i for i in files if int(i[-8:-4]) in usablefiles]
    
    toto=chopper_chop(folder+os.sep+files[0],trashfirst,chopper,data,timescale,data2,phase,graphics=False,period=-1)
    period = len(toto[0])
    
    matout = array([chopper_chop(folder+os.sep+filename,trashfirst,\
    chopper,data,timescale,data2,phase,graphics=False,period=period) for filename in files])

    #print(shape(matout))
    n=len(files)
    t_out, sig_out, trig_out, y2_out = \
    sum(matout[:,0,:],axis=0)/n,sum(matout[:,1,:],axis=0)/n,\
    sum(matout[:,2,:],axis=0)/n,sum(matout[:,3,:],axis=0)/n
    
#Cheating !!!
    #time_g = concatenate([t_out,t_out+2*t_out[-1]-t_out[-2]])
    #sign_g = concatenate([sig_out,]*2)
    #trig_g = concatenate([trig_out,]*2)
    #dat2_g = concatenate([y2_out,]*2)
#Reality
    time_g = array(t_out)
    sign_g = array(sig_out)
    trig_g = array(trig_out)
    dat2_g = array(y2_out)



    if graphics == True:
        fig1 = pylab.figure(figsize=(8,11),edgecolor="white",facecolor="white",)
        fig1.clear()
        ax1=pylab.subplot(3,1,1)
        ax1.set_title(prefix)
        ax1.plot(time_g,sign_g)
        ax1.grid()
        ax1.set_ylabel(data)
        
        ax2=pylab.subplot(3,1,2,sharex=ax1)
        ax2.plot(time_g,trig_g,label=chopper)
        ax2.legend()
        ax2.grid()
        ax2.set_xlabel("t(s)")
        ax2.set_ylabel(chopper)
        
        ax3=pylab.subplot(3,1,3,sharex=ax1)
        ax3.plot(time_g,dat2_g,label=data2)
        ax3.legend()
        ax3.grid()
        ax3.set_xlabel("t(s)")
        ax3.set_ylabel(data2)

    return t_out, sig_out, trig_out, y2_out

def chopper_chop(filename,trashfirst=0,chopper="/post/I3",data="/post/FLUO",\
timescale="/data/X1",data2="/post/I2",phase=0,graphics=False,period=-1):
#Load data
    datasource = tables.open_file(filename, "r")

# trigger or chopper signal are y
    y = datasource.get_node(chopper).read()[trashfirst:]
    y2 = datasource.get_node(data2).read()[trashfirst:]
# signal is the data to fold over the chopper or trigger
    signal = datasource.get_node(data).read()[trashfirst:]
#time coordinate
    t_scale = datasource.get_node(timescale).read()[trashfirst:]

    datasource.close()
#Process trigger 

    #Set a level just above "dark"
    level=(max(y)-min(y))*0.1+min(y)
    
    idx = [where(y>level)[0][i]+1 for i in where(diff(where(y>level))[0]>1)[0]]
    if period == -1:
        period = int(round(mean(diff(idx))))*2
    last=idx[1] + int(len(y[idx[1]:])/period)*period
    #print(period)

# Obtain output

    trig = reshape(y[idx[1]:last],(int((last-idx[1])/period),period))
    trig = sum(trig,axis=0)/shape(trig)[0]
    sig = reshape(signal[idx[1]:last],(int((last-idx[1])/period),period))
    sig = sum(sig,axis=0)/shape(sig)[0]
    sig2 = reshape(y2[idx[1]:last],(int((last-idx[1])/period),period))
    sig2 = sum(sig2,axis=0)/shape(sig2)[0]
    t_out = [t-t[0] for t in reshape(t_scale[idx[1]:last],(int((last-idx[1])/period),period))]
    t_out = sum(t_out,axis=0)/shape(t_out)[0]
    if graphics == True:
        fig1 = pylab.figure(101,figsize=(8,11),edgecolor="white",facecolor="white",)
        fig1.clear()
        ax1=pylab.subplot(2,1,1)
        ax1.plot(t_out,sig)
        ax1.grid()
        ax1.set_ylabel("FLUO")
        ax2=pylab.subplot(2,1,2,sharex=ax1)
        ax2.plot(t_out,trig,label="trigger")
        ax2.plot(t_out,sig2,label="diode")
        #ax2.plot(t_out,y[idx[1]:idx[1]+period],label="trigger_raw")
        ax2.legend()
        ax2.grid()
        ax2.set_xlabel("t(s)")
        ax2.set_ylabel("trigger level")
    return (t_out,sig,trig,sig2)

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

