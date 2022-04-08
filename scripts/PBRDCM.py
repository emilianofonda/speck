from __future__ import print_function
#Defines the DCM as controlled by Delta TAU Power Brick 
#Monochromator1

#Legacy definition of piezo controlled by Galil
#In case the old piezo control was again necessary I leave this code here
try:
    __m="rx2fine"
    rx2fine=piezo("d09-1-c03/op/mono1-mt_rx_fine.2")
    __allpiezos+=[rx2fine]
    #rx2fine = mostab
except Exception as tmp:
    #print tmp
    print("I could not define ",__m ,"of the monochromator!")
#End of legacy
                        
__tmp={
#"rx2"      :["d09-1-c03/op/mono1-mt_rx.2","position","deadtime=0.05"],
"rx2"      :["d09-1-c03/op/Axis9_Rx2","position","deadtime=0.05"],
#"tz1"      :["d09-1-c03/op/mono1-mt_tz.1","position","deadtime=0.05"],
"rz2"      :["d09-1-c03/op/Axis1_Rz2","position","deadtime=0.05"],
"ts2"      :["d09-1-c03/op/Axis2_TS2","position","deadtime=0.05"],
"tz2"      :["d09-1-c03/op/Axis3_TZ2","position","deadtime=0.05"],
"rx1"      :["d09-1-c03/op/Axis4_RX1","position","deadtime=0.05"],
"bender_c1":["d09-1-c03/op/Axis5_C1","position","deadtime=0.05"],
"bender_c2":["d09-1-c03/op/Axis6_C2","position","deadtime=0.05"],
"rs2"      :["d09-1-c03/op/Axis8_RS2","position","deadtime=0.05"],
}

for i in __tmp:
    try:
        if len(__tmp[i])>2:
            __fmtstring="%s=moveable('%s','%s',"+"%s,"*(len(__tmp[i])-3)+"%s)"
        else:
            __fmtstring="%s=moveable('%s','%s')"
        __cmdstring=__fmtstring%tuple([i,]+__tmp[i])
        exec(__cmdstring)
        __allmotors.append(__IP.user_ns[i])
    except Exception as tmp:
        print(RED+"Failed"+RESET+" defining: %s/%s as %s"%tuple(__tmp[i][0:2]+[i,]))
        print(RED+"-->"+RESET,tmp)
        print(UNDERLINE+__cmdstring+RESET)


try:
    #Si220
    #PowerBrick Version
    from mono1PBR import sagittal_bender
    bender = sagittal_bender(bender1_name = "d09-1-c03/op/Axis5_C1", bender2_name = "d09-1-c03/op/Axis6_C2",\
    DataViewer = "d09-1-c03/op/DATAVIEWER")
    bender.timeout=0
    bender.deadtime=0.1

    #When you want to set no bender
    #bender=None

    __allmotors+=[bender.c1,bender.c2]
except:
    print("Cannot define Power Brick Bender")

try:
    print("Defining dcm...", end=' ')
    from mono1PBR import mono1
    dcm = mono1(monoName="d09-1-c03/op/ENERGY", DataViewer="d09-1-c03/op/DATAVIEWER",\
    rx1=rx1,tz2=tz2,ts2=ts2,rx2=rx2,rs2=rs2,rx2fine=rx2fine,rz2=rz2, bender=bender,\
    counter_label="d09-1-c00/ca/cpt.1", counter_channel=0,\
    delay=0.0, emin=5250.,emax=43000.)
    dcm.deadtime = 0.05
    dcm.timeout = 3.0
    
    #Aliases for dcm operation
    energy=dcm
    seten=dcm.seten
    tune=dcm.tune
    print("OK!")
except Exception as tmp:
    print(tmp)
    print("Cannot define dcm (monochromator not set).")



