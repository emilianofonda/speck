# -*- coding: utf-8 -*-
from __future__ import print_function
from builtins import range
from time import sleep
from p_spec_syntax import *

print()
print("################################################################")
print("#                Executing user config.                        #") 
print("################################################################")


#To mantain syntax compatibility with this old file:

__IP=get_ipython()
##Usefull constants
#Values of d below are used everywhere... hopefully.
__d220=1.92015585
__d111=3.1356
__d311=1.6375
__samplePos=13.95


##-------------------------------------------------------------------------------------
##Define ReadOut Electronics Here
##-------------------------------------------------------------------------------------

#Counters
# The commented version refers to the old way of having separate counters defined and a counter master.
# Now a single counter is the master AND virtually includes the others.


    
#ct

#HV power supplies
try:
    HV_I0    =NHQ_HVsupply("d09-1-cx1/ex/mi_cio-hvps.1","A")
    HV_I1    =NHQ_HVsupply("d09-1-cx1/ex/mi_cio-hvps.1","B")
except Exception as tmp:
    print("Error on defining NHQ module 1 SHV of chambers I0 and I1")
try:
    HV_I2    =NHQ_HVsupply("d09-1-cx1/ex/mi_cio-hvps.2","B")
    HV_xbpm    =NHQ_HVsupply("d09-1-cx1/ex/mi_cio-hvps.2","A")
except Exception as tmp:
    print("Error on defining NHQ module 2 SHV of chambers I2 and xbpm")


##--------------------------------------------------------------------------------------
##RS232 controlled custom equipment
##--------------------------------------------------------------------------------------

# I200 (home made python controller)
#try:
#    from I200 import I200_tango as I200
#    print "I200 unit :",
#    i200=I200("d09-1-cx1/ca/moco2.1")
#    itune=i200.tune
#    #print i200.currents()
#    #print i200.status()
#except Exception, tmp:
#    print "Error initializing I200."
#    print tmp

# MOSTAB (home made python controller)
try:
    from MOSTAB import MOSTAB_tango as MOSTAB
    print("MOSTAB unit :", end=' ')
    mostab=MOSTAB("d09-1-cx1/ca/moco2.1",init_file = __IP.user_ns["__pySamba_root"] + "/config/mostab.cfg", forceOutBeam="OUTBEAM VOLT NORM UNIP 10 NOAUTO")
    def itune(*args,**kwargs):
        #Multipiled by 4 on 18/11/2015
        opr = 3.56/(0.10 * dcm.pos() * 1e-3 - 0.16) * 0.9 *4
        if "oprange" in list(kwargs.keys()):
            return mostab.tune(*args,**kwargs)
        else:
            kwargs["oprange"] = opr
            return mostab.tune(*args,**kwargs)
    print("OK")
except Exception as tmp:
    print("Error initializing mostab unit...")
    print(tmp)
    
#ACE Avalanche Photodiode Controller (home made python controller)
#try:
#    from ACE_APD import ACE_APD
#    ace=ACE_APD("d09-1-c00/ca/serial.com8")
#except Exception, tmp:
#    print tmp
#    print "ACE_APD: ace=d09-1-c00/ca/serial.com8 not defined!"

##--------------------------------------------------------------------------------------
##Define motors here
##--------------------------------------------------------------------------------------


#################################################
#             Moveables
################################################

#Normal moveables (missing special options)
__tmp={
#"T_dcm_set": ["d09-1-c03/op/bath.1","temperatureSetPoint"],
"po1"        :["d09-1-c02/ex/po.1-mt.1","position","delay=1.","timeout=3."],
"po2"        :["d09-1-c06/ex/po.1-mt_tz.1","position","delay=1.","timeout=3."],
"po3"        :["d09-1-cx1/ex/po.1-mt_tz.1","position","delay=1.","timeout=3."],
"po4"        :["d09-1-c07/ex/po.1-mt_tz.1","position"],
"po5"        :["d09-1-cx2/ex/po.1-mt_tz.1","position"],\
"sample_x"    :["d09-1-cx1/ex/tab-mt_tx.1","position"],
"sample_z"    :["d09-1-cx1/ex/tab-mt_tz.1","position"],
"sample_rx"    :["d09-1-cx1/ex/tab-mt_rx.1","position"],
"sample_rx2"    :["d09-1-cx1/ex/tab-mt_rx.2","position"],
"sample_rz"        :["d09-1-cx1/ex/tab-mt_rz.1","position"],
"tab2x"    :["d09-1-cx1/ex/tab2-tx.1","position"],
"tab2s"    :["d09-1-cx1/ex/tab2-ts.1","position"],
"tab2z"    :["d09-1-cx1/ex/tab2-tz.1","position"],
"tbt_z"        :["d09-1-cx1/ex/cryo-tbt-mt_tz.1","position"],
"fluo_x"    :["d09-1-cx1/dt/dtc_ge.1-mt_tx.1","position"],
"fluo_s"    :["d09-1-cx1/dt/dtc_ge.1-mt_ts.1","position"],
"fluo_z"    :["d09-1-cx1/dt/dtc_ge.1-mt_tz.1","position"],
#"raman_x"    :["d09-1-cx1/ex/raman-tx.1","position"],
#"z2"    :["d09-1-cx1/ex/raman-tz.1","position"],
"thetaBoral"    :["d09-1-cx1/ex/pfi.1-mt_rs.1","position"],
"imag1"        :["D09-1-C02/DT/IMAG1-MT_Tz.1","position"],
"imag2"        :["D09-1-C04/DT/IMAG2-MT_Tz.1","position"],
"imag3"        :["D09-1-C06/DT/IMAG3-MT_Tz.1","position"],
"dac0"        :["d09-1-c00/ca/mao.1","channel0"],
"HePump"        :["d09-1-c00/ca/mao.1","channel1"],
"dac2"        :["d09-1-c00/ca/mao.1","channel2"],
"HeFlow"        :["d09-1-c00/ca/mao.1","channel3"],
"dac4"        :["d09-1-c00/ca/mao.1","channel4"],
"dac5"        :["d09-1-c00/ca/mao.1","channel5"],
"dac6"        :["d09-1-c00/ca/mao.1","channel6"],
"dac7"        :["d09-1-c00/ca/mao.1","channel7"],
"ttlF"        :["d09-1-c00/ca/dio.1","PortF"],
"cam1"        :["d09-1-c02/dt/vg1.0","ExposureTime"],
"cam2"        :["d09-1-c04/dt/vg1.1","ExposureTime"],
"cam3"        :["d09-1-c06/dt/vg1.2","ExposureTime"],
"cam4"        :["d09-1-cx1/dt/vg2-basler","ExposureTime"],
"cam5"        :["d09-1-cx2/dt/vg2-basler","ExposureTime"],
"I0_gain"    :["d09-1-cx1/ex/amp_iv.1","gain"],
"I1_gain"    :["d09-1-cx1/ex/amp_iv.2","gain"],
"I2_gain"    :["d09-1-cx1/ex/amp_iv.3","gain"],
"I3_gain"    :["d09-1-cx1/ex/amp_iv.4","gain"],
"mostab_gain1"    :["d09-1-cx1/ex/amp_iv.10","gain"],
"mostab_gain2"    :["d09-1-cx1/ex/amp_iv.11","gain"],
"mir1_pitch"    :["d09-1-c02/op/mir1-tpp","pitch"],
"mir1_roll"    :["d09-1-c02/op/mir1-tpp","roll"],
"mir1_z"    :["d09-1-c02/op/mir1-tpp","zC"],
"mir1_t1z"    :["d09-1-c02/op/mir1-mt_t1","position"],
"mir1_t2z"    :["d09-1-c02/op/mir1-mt_t2","position"],
"mir1_t3z"    :["d09-1-c02/op/mir1-mt_t3","position"],
"mir1_c"    :["d09-1-c02/op/mir1-mt_c.1","position"],
"mir2_pitch"    :["d09-1-c05/op/mir2-tpp","pitch"],
"mir2_roll"    :["d09-1-c05/op/mir2-tpp","roll"],
"mir2_z"    :["d09-1-c05/op/mir2-tpp","zC"],
"mir2_t1z"    :["d09-1-c05/op/mir2-mt_t1","position"],
"mir2_t2z"    :["d09-1-c05/op/mir2-mt_t2","position"],
"mir2_t3z"    :["d09-1-c05/op/mir2-mt_t3","position"],
"mir2_c"    :["d09-1-c05/op/mir2-mt_c.1","position"],
"vpos5" :["d09-1-c06/ex/fent_v.2-mt_pos","position"],
"vgap5" :["d09-1-c06/ex/fent_v.2-mt_gap","position"],
"hpos5" :["d09-1-c06/ex/fent_h.2-mt_pos","position"],
"hgap5" :["d09-1-c06/ex/fent_h.2-mt_gap","position"],
"cryoz" :["d09-1-cx1/ex/konti-mt_tz.1","position"],
"cryophi" :["d09-1-cx1/ex/konti-mt_rz.1","position"],
#Positionneur CX2
"cx2_x"    :["d09-1-cx2/ex/sex-mt_tx.1","position"],
"cx2_z"    :["d09-1-cx2/ex/sex-mt_tz.2","position"],
"cx2_z2"    :["d09-1-cx2/ex/sex-mt_tz.1","position"],
"cx2_phi"    :["d09-1-cx2/ex/sex-mt_rz.1","position"],
#Analyseur CX2
"cx2_xCrystal"    :["d09-1-cx2/dt/cristal-mt_tx.1","position"],
"cx2_thetaCrystal"    :["d09-1-cx2/dt/cristal-mt_rs.1","position"],
"cx2_xDetector"    :["d09-1-cx2/dt/det-mt_tx.1","position"],
"cx2_zDetector"    :["d09-1-cx2/dt/det-mt_tz.1","position"],
"cx2_thetaDetector"    :["d09-1-cx2/dt/det-mt_rs.1","position"],
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

#############################################################
# DOUBLE FEMTO
#############################################################

from doubleFEMTO import doubleFEMTO
mostab_gain = doubleFEMTO(mostab_gain1, mostab_gain2)

##############################################################
#        Sensors
##############################################################
#Vacuum
__vacuum=[]
__tmp={
"jpen1_2"    :["d09-1-c01/vi/jpen.2","pressure"],
"jpen2_1"    :["d09-1-c02/vi/jpen.1","pressure"],
"jpen3_1"    :["d09-1-c03/vi/jpen.1","pressure"],
"jaul3_1"    :["d09-1-c03/vi/jaul.1","pressure"],
"jpen4_1"    :["d09-1-c04/vi/jpen.1","pressure"],
"jpen5_1"    :["d09-1-c05/vi/jpen.1","pressure"],
"jpen6_1"    :["d09-1-c06/vi/jpen.1","pressure"],
"jpen6_2"    :["d09-1-c06/vi/jpen.2","pressure"],
"pi1_1"        :["d09-1-c01/vi/pi.1","pressure"],
"pi1_2"        :["d09-1-c01/vi/pi.2","pressure"],
"pi2_1"        :["d09-1-c02/vi/pi.1","pressure"],
"pi2_2"        :["d09-1-c02/vi/pi.2","pressure"],
"pi3_1"        :["d09-1-c03/vi/pi.1","pressure"],
"pi4_1"        :["d09-1-c04/vi/pi.1","pressure"],
"pi5_1"        :["d09-1-c05/vi/pi.1","pressure"],
"pi6_1"        :["d09-1-c06/vi/pi.1","pressure"],
"pi6_2"        :["d09-1-c06/vi/pi.2","pressure"],
"tc1"	       :["d09-1-cx1/ex/tc.1","temperature"],
#"T_dcm"        :["d09-1-c03/op/bath.1","temperature"],
#"cryo4temp1" :["d09-1-cx1/ex/cryo4.1-ctrl","temperature1"],
#"cryo4temp2" :["d09-1-cx1/ex/cryo4.1-ctrl","temperature2"],
}                                                

__ll=list(__tmp.keys())
__ll.sort()
for i in __ll:
    try:
        if len(__tmp[i])>2:
            __fmtstring="%s=sensor('%s','%s',"+"%s,"*(len(__tmp[i])-3)+"%s)"
        else:
            __fmtstring="%s=sensor('%s','%s')"
        __cmdstring=__fmtstring%tuple([i,]+__tmp[i])
        exec(__cmdstring)
        __vacuum.append(i)
    except Exception as tmp:
        print(RED+"Failed"+RESET+" defining: %s/%s as %s"%tuple(__tmp[i][0:2]+[i,]))
        print(RED+"-->"+RESET,tmp)
        print(UNDERLINE+__cmdstring+RESET)
del __tmp,__ll

#Slits 

__tmp={
"vup1"  :["d09-1-c01/ex/fent_v.1","d09-1-c01/ex/fent_v.1-mt_u","d09-1-c01/ex/fent_v.1-mt_d","up"],
"vdown1":["d09-1-c01/ex/fent_v.1","d09-1-c01/ex/fent_v.1-mt_u","d09-1-c01/ex/fent_v.1-mt_d","down"],
"vpos1" :["d09-1-c01/ex/fent_v.1","d09-1-c01/ex/fent_v.1-mt_u","d09-1-c01/ex/fent_v.1-mt_d","pos"],
"vgap1" :["d09-1-c01/ex/fent_v.1","d09-1-c01/ex/fent_v.1-mt_u","d09-1-c01/ex/fent_v.1-mt_d","gap"],
"hpos1" :["d09-1-c01/ex/fent_h.1","d09-1-c01/ex/fent_h.1-mt_i","d09-1-c01/ex/fent_h.1-mt_o","pos"],
"hgap1" :["d09-1-c01/ex/fent_h.1","d09-1-c01/ex/fent_h.1-mt_i","d09-1-c01/ex/fent_h.1-mt_o","gap"],
"hout1" :["d09-1-c01/ex/fent_h.1","d09-1-c01/ex/fent_h.1-mt_i","d09-1-c01/ex/fent_h.1-mt_o","out"],
"hin1"  :["d09-1-c01/ex/fent_h.1","d09-1-c01/ex/fent_h.1-mt_i","d09-1-c01/ex/fent_h.1-mt_o","in"],
"vpos2" :["d09-1-c04/ex/fent_v.1","d09-1-c04/ex/fent_v.1-mt_u","d09-1-c04/ex/fent_v.1-mt_d","pos"],
"vgap2" :["d09-1-c04/ex/fent_v.1","d09-1-c04/ex/fent_v.1-mt_u","d09-1-c04/ex/fent_v.1-mt_d","gap"],
"vup2"  :["d09-1-c04/ex/fent_v.1","d09-1-c04/ex/fent_v.1-mt_u","d09-1-c04/ex/fent_v.1-mt_d","up"],
"vdown2":["d09-1-c04/ex/fent_v.1","d09-1-c04/ex/fent_v.1-mt_u","d09-1-c04/ex/fent_v.1-mt_d","down"],
#"vpos3" :["d09-1-c06/ex/fent_v.1","d09-1-c06/ex/fent_v.1-mt_u","d09-1-c06/ex/fent_v.1-mt_d","pos"],
#"vgap3" :["d09-1-c06/ex/fent_v.1","d09-1-c06/ex/fent_v.1-mt_u","d09-1-c06/ex/fent_v.1-mt_d","gap"],
#"hin3"  :["d09-1-c06/ex/fent_h.1","d09-1-c06/ex/fent_h.1-mt_i","d09-1-c06/ex/fent_h.1-mt_o","in"],
#"hout3" :["d09-1-c06/ex/fent_h.1","d09-1-c06/ex/fent_h.1-mt_i","d09-1-c06/ex/fent_h.1-mt_o","out"],
#"vup3"  :["d09-1-c06/ex/fent_v.1","d09-1-c06/ex/fent_v.1-mt_u","d09-1-c06/ex/fent_v.1-mt_d","up"],
#"vdown3":["d09-1-c06/ex/fent_v.1","d09-1-c06/ex/fent_v.1-mt_u","d09-1-c06/ex/fent_v.1-mt_d","down"],
#"hpos3" :["d09-1-c06/ex/fent_h.1","d09-1-c06/ex/fent_h.1-mt_i","d09-1-c06/ex/fent_h.1-mt_o","pos"],
#"hgap3" :["d09-1-c06/ex/fent_h.1","d09-1-c06/ex/fent_h.1-mt_i","d09-1-c06/ex/fent_h.1-mt_o","gap"],
"vpos4" :["d09-1-cx1/ex/fent_v.1","d09-1-cx1/ex/fent_v.1-mt_u","d09-1-cx1/ex/fent_v.1-mt_d","pos"],
"vgap4" :["d09-1-cx1/ex/fent_v.1","d09-1-cx1/ex/fent_v.1-mt_u","d09-1-cx1/ex/fent_v.1-mt_d","gap"],
"hin4"  :["d09-1-cx1/ex/fent_h.1","d09-1-cx1/ex/fent_h.1-mt_i","d09-1-cx1/ex/fent_h.1-mt_o","in"],
"hout4" :["d09-1-cx1/ex/fent_h.1","d09-1-cx1/ex/fent_h.1-mt_i","d09-1-cx1/ex/fent_h.1-mt_o","out"],
"vup4"  :["d09-1-cx1/ex/fent_v.1","d09-1-cx1/ex/fent_v.1-mt_u","d09-1-cx1/ex/fent_v.1-mt_d","up"],
"vdown4":["d09-1-cx1/ex/fent_v.1","d09-1-cx1/ex/fent_v.1-mt_u","d09-1-cx1/ex/fent_v.1-mt_d","down"],
"hpos4" :["d09-1-cx1/ex/fent_h.1","d09-1-cx1/ex/fent_h.1-mt_i","d09-1-cx1/ex/fent_h.1-mt_o","pos"],
"hgap4" :["d09-1-cx1/ex/fent_h.1","d09-1-cx1/ex/fent_h.1-mt_i","d09-1-cx1/ex/fent_h.1-mt_o","gap"],
"vpos6" :["d09-1-cx2/ex/fent_v.1","d09-1-cx2/ex/fent_v.1-mt_u.1","d09-1-cx2/ex/fent_v.1-mt_d.1","pos"],
"vgap6" :["d09-1-cx2/ex/fent_v.1","d09-1-cx2/ex/fent_v.1-mt_u.1","d09-1-cx2/ex/fent_v.1-mt_d.1","gap"],
"hpos6" :["d09-1-cx2/ex/fent_h.1","d09-1-cx2/ex/fent_h.1-mt_i.1","d09-1-cx2/ex/fent_h.1-mt_o.1","pos"],
"hgap6" :["d09-1-cx2/ex/fent_h.1","d09-1-cx2/ex/fent_h.1-mt_i.1","d09-1-cx2/ex/fent_h.1-mt_o.1","gap"],
"vup6"  :["d09-1-cx2/ex/fent_v.1","d09-1-cx2/ex/fent_v.1-mt_u.1","d09-1-cx2/ex/fent_v.1-mt_d.1","up"],
"vdown6":["d09-1-cx2/ex/fent_v.1","d09-1-cx2/ex/fent_v.1-mt_u.1","d09-1-cx2/ex/fent_v.1-mt_d.1","down"],
"hin6"  :["d09-1-cx2/ex/fent_h.1","d09-1-cx2/ex/fent_h.1-mt_i.1","d09-1-cx2/ex/fent_h.1-mt_o.1","in"],
"hout6" :["d09-1-cx2/ex/fent_h.1","d09-1-cx2/ex/fent_h.1-mt_i.1","d09-1-cx2/ex/fent_h.1-mt_o.1","out"]}
for i in __tmp:
    try:
        __IP.user_ns[i]=motor_slit(__tmp[i][0],__tmp[i][1],__tmp[i][2],__tmp[i][3])
        __allmotors+=[__IP.user_ns[i],]
    except Exception as tmp:
        print(tmp)
        print(RED+"Cannot define"+RESET+" %s =motor(%s)"%(i,__tmp[i]))


###
### Define aliases below
###

aliases={
"sample_x":"x",
"sample_z":"z",
"sample_rz":"phi",
"sample_rx":"theta",
"sample_rx2":"omega",
"cryo4z": "becher",
"cryo4z": "x2",
}

for i in aliases:
    if i in __IP.user_ns:
        try:
            __IP.user_ns[aliases[i]]=__IP.user_ns[i]
        except Exception as tmp:
            print(tmp)
            print("Error defining ",aliases[i]," as alias for ",i)


##-------------------------------------------------------------------------------------
##Define Main Optic Components Here
##-------------------------------------------------------------------------------------

#Defines the DCM as controlled by Delta TAU Power Brick 
#Monochromator1
                        
__tmp={
"rx2"      :["d09-1-c03/op/Axis9_Rx2","position","deadtime=0.05"],
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
    from mono1PBR import sagittal_bender
    bender = sagittal_bender(bender1_name = "d09-1-c03/op/Axis5_C1", bender2_name = "d09-1-c03/op/Axis6_C2",\
    DataViewer = "d09-1-c03/op/DATAVIEWER")
    bender.timeout=0
    bender.deadtime=0.1

    __allmotors+=[bender.c1,bender.c2]
except:
    print("Cannot define Power Brick Bender")

try:
    print("Defining dcm...",)
    from mono1PBR import mono1
    dcm = mono1(monoName="d09-1-c03/op/ENERGY", DataViewer="d09-1-c03/op/DATAVIEWER",\
    rx1=rx1,tz2=tz2,ts2=ts2,rx2=rx2,rs2=rs2,rx2fine=None,rz2=rz2, bender=bender,\
    counter_label="", counter_channel=0,\
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




##--------------------------------------------------------------------------------------
##PSS
##--------------------------------------------------------------------------------------

try:
    FE=FrontEnd("tdl-d09-1/vi/tdl.1")
    obxg=PSS.obx("d09-1-c06/vi/obxg.1")
    obx=PSS.obx("d09-1-c07/ex/obx.1")
except Exception as tmp:
    print(tmp)
##--------------------------------------------------------------------------------------
##VALVES
##--------------------------------------------------------------------------------------

__tmp={
"vs1":    "d09-1-c01/vi/vs.1",
"vs2":    "d09-1-c02/vi/vs.1",
"vs3":    "d09-1-c03/vi/vs.1",
"vs4":    "d09-1-c04/vi/vs.1",
"vs5":    "d09-1-c05/vi/vs.1",
#"vs6":    "d09-1-cx1/vi/vs.1"
}

for i in __tmp:
    try:
        if type(__tmp[i]) in [tuple,list]:
            __exstr="valve(\""+__tmp[i][0]+"\","
            for j in range(1,len(__tmp[i])-1): __exstr+=__tmp[i][j]
            __exstr+=")"
            __IP.user_ns[i]=eval(__exstr)
            del __exstr
        else:
            __IP.user_ns[i]=valve(__tmp[i])
        __valves+=[__IP.user_ns[i],]
        __vacuum+=[i,]
    except Exception as tmp:
        print(tmp)
        print("Cannot define %s =valve(%s)"%(i,__tmp[i]))
del __tmp

#attenuateur 
try:
    att=absorbing_system("d09-1-c01/ex/att.1")
except Exception as tmp:
    print(tmp)
    print("Cannot configure d09-1-c01/ex/att.1")

#Fast shutter
try:
    from pseudo_valve import pseudo_valve
    #print "Fast shutter is sh_fast"
    sh_fast=pseudo_valve(label="d09-1-c00/ca/dio_0.1",channel="G",delay=0.1,deadtime=0.,timeout=0,reverse=True)
    fc = sh_fast.close
    fo = sh_fast.open
except Exception as tmp:
    print(tmp)
    print("No fast shutter defined!")


###
### Import classes containing defaults pointing to objects declared above (e.g. dcm, cpt1...)
###

######################################################################################
#        INCLUDE SCANS SECTION                                                #
######################################################################################



##########################################################################
#Include non permanent function declarations or actions here below       #
##########################################################################





#########################################
#        Shutters and waitings          #
#########################################

try:
    #in the right order...
    __allshutters=[FE, obxg, obx]
except Exception as tmp:
    print(tmp)
    print("Check state of shutters... something wrong in script...")


def shopen(level=1):
    """Open shutters up to level specified starting from lower level"""
    for i in range(level+1):
        if "frontEndStateValue" in __allshutters[i].DP.get_attribute_list() and __allshutters[i].DP.frontEndStateValue == 2:
            print("Front End is locked by Machine Operator")
            print("I will wait for electron beam injection...")
            wait_injection()
        if "beamLineOccInterlock" in __allshutters[i].DP.get_attribute_list() and __allshutters[i].DP.beamlineoccinterlock:
                print("Front End is beam line locked: calling wait_injection()")
                wait_injection(FE,__allshutters[:level+1])
                #raise Exception("Front End locked, verify PSS or try again later.")
        if "beamLinePSSInterlock" in __allshutters[i].DP.get_attribute_list() and __allshutters[i].DP.beamlinepssinterlock:
                print("Front End is beam line locked: calling wait_injection()")
                wait_injection()
                #raise Exception("Front End locked, verify PSS or try again later.")
        if "isInterlocked" in __allshutters[i].DP.get_attribute_list() and __allshutters[i].DP.isInterlocked:
                #raise Exception("Shutter locked, verify PSS or try again later.")
                while(__allshutters[i].DP.isInterlocked):
                    print("Waiting for PSS permission to open shutter... " + asctime() + "\r", end=' ')
                    sys.stdout.flush()
                    sleep(1)
        print("")
        __allshutters[i].open()
        try:
            __allshutters[i].DP.automaticMode = True
        except:
            pass
        print(__allshutters[i].label," ",__allshutters[i].state())
    if level >= 1:
        try:
            sleep(0.2)
            mostab.start()
            print("mostab: start executed")
        except:
            pass
    return __allshutters[level].state()

def shclose(level=1):
    """Close shutters down to level specified starting from maximum level"""
    try:
        mostab.stop()
        print("mostab: stop executed")
    except:
        pass
    for i in range(len(__allshutters)-1,level-1,-1):
        __allshutters[i].close()
    print(__allshutters[i].label," ",__allshutters[i].state())
    return __allshutters[level].state()

def shstate():
    """Provide state of last open shutter starting from lower.
    -1 means closed beamline
    0 means front end open
    1 means level 1 open 
    2 means level 2 open ..."""
    for i in range(len(__allshutters)):
        if __allshutters[i].state() != DevState.OPEN:
            break
    if i == 0:
        print("Beamline is closed")
    else:
        print("Beamline is open up to level:", i - 1)
    return i - 1

##
##  Functions to wait for a certain time, date, for the beam to come back...
##  This module has been changed by the user so it is in the user_config.py.
##
try:
    from wait_functions import wait_until
    import wait_functions
    def wait_injection(TDL=FE,ol=[obxg,],vs=[vs1,vs2,vs3,vs4,vs5],pi=[pi1_1,pi1_2,pi2_1,pi2_2,pi3_1,pi4_1,pi5_1,pi6_1,pi6_2],maxpressure=1e-5,deadtime=1):
        return wait_functions.wait_injection(TDL,ol,vs,pi,maxpressure,deadtime)
    def wait_until(dts,deadtime=1.):
        return wait_functions.wait_until(dts,deadtime)
    def checkTDL(TDL=FE):
        return wait_functions.checkTDL(TDL)
    def interlockTDL(TDL=FE):
        return wait_functions.interlockTDL(FE)
except Exception as tmp:
    print("wait_functions.py module is in error.")
    print(tmp)
    print("Ignoring...")


##############################
#user configs
##############################

#
#    SOME temporary defs
#


try:
    vg_x=sensor("d09-1-cx1/dt/vg2-basler-analyzer","ChamberXProjFitCenter")
    vg_y=sensor("d09-1-cx1/dt/vg2-basler-analyzer","ChamberYProjFitCenter")
except Exception as tmp:
    print(tmp)
    print("videograbber d09-1-cx1/dt/vg2-basler-analyzer error!")



#print "Instruments: default is"+RED+" EXAFS"+RESET+". Type "+RED+"SEXAFS"+RESET+" to use the second experimental hutch."


####
#### Define here below lists of moveables for a quick view with "wm"
####

#instrument("VortexME4")

#Load marccd 
#instrument("MARCCD")

#Load mar345
#instrument("MAR345")

#load sai into ct
#instrument("SAI")

#load cameras into ct
#instrument("CAMERAS")

#load Eurotherm controllers
#instrument("FORNO")

#Enable setMCAconfig and getMCAconfig
domacro("changePeakingTime")

#Load Energy Continuous Scan
#domacro("ecscanFTP")
#domacro("ecscanFTP_covid")
#domacro("ecscanXP")
#domacro("averageThis")
domacro("resetFEMTO")
domacro("fftI0")

def resetFluo():
   domacro("resetFLUO")

try:
    domacro("ControlSystem")
except:
    pass
    

