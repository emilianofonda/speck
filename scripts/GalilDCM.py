#Monochromator1
try:
    __m="rx2fine"
    rx2fine=piezo("d09-1-c03/op/mono1-mt_rx_fine.2")
    __allpiezos+=[rx2fine]
    #rx2fine = mostab
except Exception, tmp:
    #print tmp
    print "I could not define ",__m ,"of the monochromator!"

__tmp={
"rx1":"d09-1-c03/op/mono1-mt_rx.1",
"rx2":"d09-1-c03/op/mono1-mt_rx.2",
"rs2":"d09-1-c03/op/mono1-mt_rs.2",
"rz2":"d09-1-c03/op/mono1-mt_rz.2",
"tz1":"d09-1-c03/op/mono1-mt_tz.1",
"tz2":"d09-1-c03/op/mono1-mt_tz.2",
"ts2":"d09-1-c03/op/mono1-mt_ts.2"}
for i in __tmp:
    try:
        __IP.user_ns[i]=motor(__tmp[i])
        __allmotors+=[__IP.user_ns[i],]
        #print "%s = motor(%s)"%(i,__tmp[i])
        #exec("%s = motor(\"%s\")"%(i,__tmp[i]))
    except Exception, tmp:
        #print tmp
        print "Cannot define %s =motor(%s)"%(i,__tmp[i])




bender_c1 = moveable("d09-1-c03/op/mono1-mt_c.1","position")
__allmotors.append(bender_c1)
bender_c2 = moveable("d09-1-c03/op/mono1-mt_c.2","position")
__allmotors.append(bender_c2)

try:
    #print "Defining bender...",
    #Quite tricky, but all the calibration for the bender is described here: be careful!
    #These paremeter are NOT copied to tango devices... do it by hand when necessary.
    #C1=A1_1*1/R+A0_1
    #C2=A1_2*1/R+A0_2
    #Rz2=p0 + p1 * theta + p2 * theta**2
    #Rs2=Rs2_par[0]+Rs2_par[1]*energy+Rs2_par[2]*energy**2+...
    #Rx2=Rx2_par[0]+Rx2_par[1]*(1/R)+...

    #Si220
    #Bender (steps versus 1/R)
    A1_1 = 499995. #501530. #481888.35048462    #493068. #488717.
    A0_1 = 92538. #90173.9 #91054.1663915865   #99208. #101943.
    A1_2 = 501407.#492346. #493502.288067641   #487333. #492917.
    A0_2 = 129223. #112661. #111904.850053559   #107675. #104935.
    #Rz2 ()
    Rz2_par = [-16095, -95.087]#[-17703.5, 138.964, -4.18379]
    #Rs2 ()
    Rs2_par = [-1050.,]#[-1343.,]
    #Rx2 ()
    Rx2_par = [-10401.+3000, 1334.7, -2304.7] #[-12985.6,]#[-7504.85, 727.716, -1756.17]

    #Si111
    #A1_1= 561133.0   #545784.
    #A0_1=-106981.0   #-21607.9
    #A1_2= 475432.0   #478509.
    #A0_2= -42899.8   #-42891.0
    #Rz2
    #Rz2_par=[14090.] #Rz2_par=[18829.7,-335.001] #[-97804.,]  Do not use: law changed!
    #Rs2
    #Rs2_par=[-4664.] #Rs2_par=[-4550.,]
    #Rx2
    #Rx2_par=[-13204.] #Rx2_par=[-17150.,]
    #Galil Version
    bender=sagittal_bender(bender1_name="d09-1-c03/op/mono1-mt_c.1",bender2_name="d09-1-c03/op/mono1-mt_c.2",\
    controlbox_rawdata1="d09-1-c00/ca/bai.1121-mos.1-cb-rawdata",controlbox_rawdata2="d09-1-c00/ca/bai.1121-mos.1-cb-rawdata.2",\
    axis1=6,axis2=7,\
    A1_1=A1_1,A0_1=A0_1,A1_2=A1_2,A0_2=A0_2)

    #PowerBrick Version
    #overwrite bender sagittal_definition
    #from mono1PBR import sagittal_bender
    #bender = sagittal_bender(bender1_name = "DT/TEST_DEVICE/Axis5_C1", bender2_name = "DT/TEST_DEVICE/Axis6_C2",\
    #A1_1 = A1_1, A0_1 = A0_1, A1_2 = A1_2, A0_2 = A0_2)
    #bender.timeout=0
    #bender.deadtime=0.01

    #When you want to set no bender
    #bender=None

    #__allmotors+=[bender.c1,bender.c2]
    #print "OK!"
except Exception, tmp:
    print "Cannot define bender of mono1"
    bender=None
    print tmp


try:
    print "Defining dcm...",
    #Si220
    d=__d220
    #Si111
    #d=__d111

    #When nothing should be defined just set it to None
    #dcm=None

    #dcm=mono1(d=d,H=25.0,mono_name="d09-1-c03/op/mono1",
    #rx1=rx1,tz2=tz2,ts2=ts2,rx2=rx2,rs2=rs2,rx2fine=i200,rz2=rz2, tz1=tz1, bender=bender,
    #sourceDistance=16.119,delay=0.3,Rz2_par=Rz2_par,Rs2_par=Rs2_par,Rx2_par=Rx2_par,
    #WhiteBeam={"rx1":0.,"tz2":24.,"tz1":8.},emin=4750.,emax=40000.)

    #dcm=mono1(d=d,H=26.0,mono_name="d09-1-c03/op/mono1",
    #rx1=rx1,tz2=tz2,ts2=ts2,rx2=rx2,rs2=rs2,rx2fine=rx2fine,rz2=rz2, tz1=tz1, bender=bender,
    #sourceDistance=16.119,delay=0.3,Rz2_par=Rz2_par,Rs2_par=Rs2_par,Rx2_par=Rx2_par,
    #WhiteBeam={"rx1":0.,"tz2":24.,"tz1":8.},emin=4750.,emax=43000.)


    #Mono Test for Galil  BEGINS

    from mono1d import mono1 as monoTest

    dcm=monoTest(d=d,H=26.0,mono_name="d09-1-c03/op/mono1",\
    rx1=rx1,tz2=tz2,ts2=ts2,rx2=rx2,rs2=rs2,rx2fine=rx2fine,rz2=rz2, tz1=tz1, bender=bender,\
    sourceDistance=16.119,delay=0.25,Rz2_par=Rz2_par,Rs2_par=Rs2_par,Rx2_par=Rx2_par,\
    WhiteBeam={"rx1":0.,"tz2":24.,"tz1":8.},emin=4750.,emax=43000.)

    #Mono Test for Galil ENDS

    ##Bender disable:  activate only if you want to remove the bender
    ##dcm=mono1(d=d,H=25.0,mono_name="d09-1-c03/op/mono1",
    ##rx1=rx1,tz2=tz2,ts2=ts2,rx2=rx2,rs2=rs2,rx2fine=rx2fine,rz2=None, tz1=tz1, bender=None,
    ##sourceDistance=16.119,delay=0.3,Rz2_par=Rz2_par,Rs2_par=Rs2_par,Rx2_par=Rx2_par,
    ##WhiteBeam={"rx1":0.,"tz2":24.,"tz1":8.})

    #Mono Test for PowerBrick BEGINS
    #from mono1PBR import mono1 as monoTest

    #dcm=monoTest(d=d,H=26.0,mono_name="d09-1-c03/op/mono1",\
    #rx1=pbrRX1,tz2=pbrTZ2,ts2=pbrTS2,rx2=rx2,rs2=pbrRS2,rx2fine=rx2fine,rz2=pbrRZ2, tz1=tz1, bender=bender,\
    #sourceDistance=16.119,delay=0.,Rz2_par=Rz2_par,Rs2_par=Rs2_par,Rx2_par=Rx2_par,\
    #emin=4750.,emax=43000.)
    #dcm.deadtime = 0.02
    #dcm.timeout = 0.0
    #Mono Test for PowerBrick ENDS

    #Aliases for dcm operation
    energy=dcm
    seten=dcm.seten
    tune=dcm.tune
    print "OK!"
except Exception, tmp:
    print tmp
    print "Cannot define dcm (monochromator not set)."




