from PyTango import DevState
from mycurses import *
import time as wtime
import sys

if not("FE" in dir()):
    FE=None
if not("obxg" in dir()):
    obxg=None

def wait_until(dts,deadtime=1.):
    """Wait until specified time and date.
    Please respect format: hour:minute[:second] [day/month/year] 
    []=optional"""
    dts=dts.strip()
    dts=dts.split()
    if (len(dts)>2):
        raise exceptions.SyntaxError("Please respect format: hour:minute[:second] [day/month/year] []=optional")
    if(len(dts)==2):
        if("/" in dts[0]):
            sdate=dts[0]
            stime=dts[1]
        else:
            sdate=dts[1]
            stime=dts[0]
    else:
        if("/" in dts[0]):
            sdate=dts[0]
            stime=""
        else:
            sdate=""
            stime=dts[0]
    print "sdate: %s\nstime: %s"%(sdate,stime)
    hour=0
    minute=0
    second=0
    if (stime<>""):
        stime=stime.split(":")
        if(len(stime)==3):
            hour,minute,second=float(stime[0]),float(stime[1]),float(stime[2])
        if(len(stime)==2):
            hour,minute,second=float(stime[0]),float(stime[1]),None
        if(len(stime)==1):
            hour,minute,second=float(stime[0]),None,None
    year=None
    month=None
    day=None
    if (sdate<>""):
        sdate=sdate.split("/")
        if(len(sdate)==3):
            day,month,year=float(sdate[0]),float(sdate[1]),float(sdate[2])
        if(len(sdate)==2):
            day,month,year=float(sdate[0]),float(sdate[1]),None
        if(len(sdate)==1):
            day,month,year=float(sdate[0]),None,None
    t=wtime.strptime(wtime.asctime())
    if(year==None): year=t[0]
    elif(year<t[0]): return wtime.asctime()
    if(hour==None): hour=t[3]
    if(minute==None): minute=t[4]
    if(second==None): second=0.
    if(day==None): day=t[2]
    if(month==None): month=t[1]
    print "I will wait until Year,Month,Day,hour,minute,second=",year,month,day,hour,minute,second
    while(year>t[0]):
        t=wtime.strptime(wtime.asctime())
        wtime.sleep(deadtime)
    while(month>t[1]):
        t=wtime.strptime(wtime.asctime())
        wtime.sleep(deadtime)
    while(day>t[2]):
        t=wtime.strptime(wtime.asctime())
        wtime.sleep(deadtime)
    while(hour>t[3]):
        t=wtime.strptime(wtime.asctime())
        wtime.sleep(deadtime)
    while(minute>t[4]):
        t=wtime.strptime(wtime.asctime())
        wtime.sleep(deadtime)
    while(second>t[5]):
        t=wtime.strptime(wtime.asctime())
        wtime.sleep(deadtime)
    return wtime.asctime()



def wait_injection(TDL=FE,ol=[obxg,],vs=[],pi=[],maxpressure=1e-5,deadtime=1):
    #Empiric method for waiting injection. To be improved
    try:
        get_ipython().user_ns["mostab"].stop()
        print "Stop on mostab... OK"
    except:
        pass
    permission=False
    if pi<>[]:
        print "Checking pressures...."
        permission=False
        while(not permission):
            permission=True
            for i in pi:
                if i.pos()>maxpressure:
                    permission=False
                    print "%s has pressure %6.2e mbar higher than fixed limit %6.2e mbar"%(i.label,i.pos(),maxpressure)
            wtime.sleep(deadtime)
        print "Pressures OK!"
        sys.stdout.flush()
    if vs<>[]:
        if permission:
            print "Opening valves...",
            sys.stdout.flush()
            vstates=[]
            for i in vs:
                if i.state()==DevState.FAULT:
                    try:
                        i.DP.faultack()
                        sleep(deadtime)
                    except:
                        raise Exception(RED+"Unresolved Vacuum Problem: call 9797 and local contact!"+RESET)
                vstates.append(i.open())
            wtime.sleep(deadtime)
            if DevState.CLOSE in vstates:
                print RED+"One valve still closed!"+RESET
                print RED+BOLD+"Call 9797!"+RESET
                permission=False
                raise Exception("Unresolved Vacuum Problem: call 9797 and local contact!")
            else:
                permission=True
                print "OK"
                sys.stdout.flush()
    print "Waiting for injection since ",wtime.asctime(),"\n"
    sys.stdout.flush()
    if(TDL.state() == DevState.CLOSE): 
        for i in ol: i.close()
    while(interlockTDL(TDL)):
        wtime.sleep(1)
    while(TDL.state() in [DevState.DISABLE]):
        wtime.sleep(1)
    while(not(TDL.state() in [DevState.CLOSE,DevState.OPEN])):
        wtime.sleep(1)
    TDL.open()
    for i in ol: i.open()
    l=[TDL.state(),]
    for i in ol: l.append(i.state())
    print "Delaying 5' for beamline warm-up..."
    sys.stdout.flush()
    wtime.sleep(300.)
    try:
        get_ipython().user_ns["mostab"].start()
    except:
        pass
    return l

def checkTDL(TDL=FE):
    """Wait for the FrontEnd to be operative again, but ignores UNKNOWN state
    when getting an exception a True state is returned anyway...
    in many cases we prefer to ignore indefinite states since FacadeDevices are crappy"""
    try:
        s=TDL.state()
    except:
        print "Device Error: Unknown Front End state"
        return True
    if(s in [DevState.OPEN,]):
        return True
    else:
        return False

def interlockTDL(TDL=FE):
    return FE.interlock()

#def interlockTDL(TDL=FE):
#    try:
#        interlock=(TDL.DP.read_attribute("beamLinePSSInterlock").value) or (TDL.DP.read_attribute("rfInterlock").value) or\
#        (TDL.DP.read_attribute("beamLineInterlock").value) or (TDL.DP.read_attribute("arcInterlock").value or \
#        (TDL.DP.frontEndStateValue in [2,]))
#        interlock2=TDL.interlock()
#        return interlock or interlock2
#    except:
#        return False


