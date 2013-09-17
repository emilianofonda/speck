import os
from time import sleep

__pySamba_root=os.getenv("SPECK")

def print_file(filename):
    """Send a file to the predefined unix printer: required by GetPositions """
    try:
        print "Sending file to printer... "
        #os.spawnvp(os.P_NOWAIT,"/usr/bin/lpr",[" ",filename])
        os.system("/usr/bin/lpr "+filename+" &")
        return
    except os.EX_OSERR,tmp:
        print tmp
        return
    except Exception, tmp:
        print "Printing Error! Ignoring..."
        print tmp
        return

try:
    os.listdir(__pySamba_root+"/files/encoders")
except:
    print "Creating folder for encoder positions storage"
    os.system("mkdir -p "+__pySamba_root+"/files/encoders")

try:
    import tkFileDialog 
    NOTK=False
except:
    NOTK=True
from time import asctime, gmtime, localtime
import os

def PrintPositions():
    return GetPositions(fname="",hardcopy=True,verbose=1)

def GetPositions(fname="",hardcopy=False,verbose=1):
    try:
        __allmotors=get_ipython().user_ns["__allmotors"]
    except:
        print "No motors!"
        __allmotors=[]
    try:
        __allslits=get_ipython().user_ns["__allslits"]
    except:
        print "No slits!"
        __allslits=[]
    try:
        __allpiezos=get_ipython().user_ns["__allpiezos"]
    except:
        print "No Piezo Motors!"
        __allpiezos=[]
    if(verbose>0): print asctime()
    if(verbose>0): print "Getting motors position:"
    if(verbose>0): 
        for mot in __allmotors:
            try:
                print mot.label," = ",mot.pos()
            except:
                print "Cannot read motor :", mot.label
        print "Getting piezos position:"
        for mot in __allpiezos:
            try:
                print mot.label,"=",mot.pos()
            except:
                print "Cannot read motor :", mot.label
        print "Mirrors TPP positions:"
        try:
            print "mirror 1 TPP pitch=%8.6f roll=%8.6f zC=%8.6f\n" %(mir1.pitch(),mir1.roll(),mir1.zC())
        except:
            print "Cannot read mirror 1"
        try:
            print "mirror 2 TPP pitch=%8.6f roll=%8.6f zC=%8.6f\n" %(mir2.pitch(),mir2.roll(),mir2.zC())
        except:
            print "Cannot read mirror 2"
        for mot in __allslits:
            try:
                print mot.label," Gap=%6.4f Pos=%6.4f In/Up=%6.4f Out/Down=%6.4f\n"%(mot.gap(),mot.pos(),mot.Up(),mot.Down())
                #print mot.label," Gap=%6.4f Pos=%6.4f\n"%(mot.gap(),mot.pos())
            except:
                print "Cannot read slit:",mot.label
    gmt=localtime()
    datename="%4i%02i%02i_%02i:%02i:%02i"%(gmt.tm_year,gmt.tm_mon,gmt.tm_mday,gmt.tm_hour,gmt.tm_min,gmt.tm_sec)
    #if(fname==""): fname=__pySamba_root+"/files/encoders/GetPositions_results_"+asctime().replace(" ","_")+".txt"
    if(fname==""): fname=__pySamba_root+"/files/encoders/GetPositions_results_"+datename+".txt"
    try:
        __encoders_output_file=file(fname,"w")
    except:
        print "Cannot open file for output."
        return
    __encoders_output_file.write("#Table pythonically generated on "+asctime()+"\n")
    for mot in __allmotors:
        try:
            __encoders_output_file.write("%s = %8.6f \n"%(mot.label,mot.pos()))
        except:
            __encoders_output_file.write("#Cannot get motor:"+mot.label+"\n")
    for mot in __allpiezos:
        try:
            __encoders_output_file.write("%s = %8.6f \n"%(mot.label, mot.pos() ))
        except:
            __encoders_output_file.write("#Cannot get piezo"+mot.label+"\n")
    try:
        __encoders_output_file.write("#mirror 1 TPP pitch=%8.6f roll=%8.6f zC=%8.6f\n"%( mir1.pitch(),mir1.roll(),mir1.zC()))
    except:
        __encoders_output_file.write("#Cannot get mirror 1\n")
    try:
        __encoders_output_file.write("#mirror 2 TPP pitch=%8.6f roll=%8.6f zC=%8.6f\n"%( mir2.pitch(),mir2.roll(),mir2.zC()))
    except:
        __encoders_output_file.write("#Cannot get mirror 2\n")
    for mot in __allslits:
        try:
            __encoders_output_file.write("#"+mot.label+" Gap=%6.4f Pos=%6.4f In/Up=%6.4f Out/Down=%6.4f\n"\
            %(mot.gap(),mot.pos(),mot.Up(),mot.Down()))
            #__encoders_output_file.write(mot.label+" Gap=%6.4f Pos=%6.4f"%(mot.gap(),mot.pos()))
        except:
            __encoders_output_file.write("#Cannot read slit:"+mot.label)
    __encoders_output_file.close()
    if(hardcopy): print_file(fname)
    #Remove files in excess (more than 100)
    ll=os.listdir(__pySamba_root+"/files/encoders/")
    try:
        if len(ll) > 99:
            ll.sort()
            for i in ll:
                if not(i.startswith("GetPositions_results_")):
                    ll.remove(i)
            if len(ll) > 99:
                for i in ll[0:len(ll)-99]:
                    os.remove(__pySamba_root+"/files/encoders/"+i)
    except:
        print "Cannot cleanup encoder log folder..."
    return fname

def SetPositions(filename=""):
    try:
        __allmotors=get_ipython().user_ns["__allmotors"]
    except:
        print "No motors!"
        __allmotors=[]
    try:
        __allslits=get_ipython().user_ns["__allslits"]
    except:
        print "No slits!"
        __allslits=[]
    try:
        __allpiezos=get_ipython().user_ns["__allpiezos"]
    except:
        print "No Piezo Motors!"
        __allpiezos=[]
    if(filename==""):
        if not(NOTK):
            filename=tkFileDialog.askopenfilename(initialdir=__pySamba_root+"/files/encoders/",title="Choose the CORRECT getposition file")
            print "Loading from -->",filename
            if(filename==()): 
                raise Exception("File name not specified!")
        else:
            raise Exception("File name not specified!")
    fpos=file(filename,'r')
    ll=fpos.readlines()
    ll_out=[]
    for i in ll:
        i=i.strip()
        if(not(i.startswith("#"))):     
            j=[]
            for k in i.split("="): j.append(k.strip())
            ll_out.append(j)
    print "Storing current positions before applying new encoder values in file: \n", GetPositions(hardcopy=False,verbose=0)
    NewMotPos=[]
    for i in __allmotors:
        NotFound=True
        for j in ll_out:
            if(i.label.lower()==j[0].lower()):
                NotFound=False
                try:
                    NewMotPos.append([i,float(j[1])])
                except:
                    print "Cannot get postion for motor ",i.label
        if(NotFound): print "Cannot find data for motor :",i.label
    print "New encoders values to apply are:"
    for i in NewMotPos:
        print i[0].label,"-->",i[1]
    print "\nBefore applying these values I will Init and MotorOn all these motors.\n"
    print "WARNING: Be sure that no motor is moving among those concerned!\n\n"
    print "VALUES OF THE ENCODERS WILL BE CHANGED.\n\n"
    answer=raw_input("Do you REALLY want to apply these values now? [Yes/]")
    if(answer=="Yes"):
        failures=0
        failedmotors=[]
        for i in NewMotPos:
            _noinit=True
            _nosh=True
            _nodef=True
            if "DefinePosition" in dir(i[0]):
                try: 
                    i[0].init()
                    sleep(3.)
                    _noinit=False
                    i[0].on()
                    sleep(1.)
                    _nosh=False
                    i[0].DefinePosition(i[1])
                    _nodef=False
                    sleep(1.)
                    print i[0].label," is at ",i[0].pos()," should be at ",i[1]
                except:
                    failures+=1
                    i[0].state()
                    if(_noinit):
                        print "Init failed on motor:",i[0].label
                    if(_nosh):
                        print "MotorON failed on motor:",i[0].label
                    if(_nodef):
                        print "Define failed on motor:",i[0].label
                    failedmotors.append(i[0])
                    sleep(.25)
        if(failures>0):
            print "WARNING: I got ",failures," failures."
            raise Exception("SetPositionsFailure failures=%i failedmotors=%i"%(failures,failedmotors))
    return



