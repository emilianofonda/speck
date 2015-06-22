from time import sleep

print
print "################################################################"
print "#                Executing user config.                        #" 
print "################################################################"


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

#NI6602
try:
    user_readconfig=[
    ["counter1",    "I0",         "%d",    "cts"],
    ["counter2",    "I1",         "%d",    "cts"],
    ["counter3",    "I2",         "%d",    "cts"],
    ["counter4",    "XBPM_S",     "%d",    "cts"],
    ["counter5",    "Empty01",    "%d",    "cts"],
    ["counter6",    "Empty02",    "%d",    "cts"],
    ["counter7",    "Empty03",    "%d",    "cts"],
    ["counter8",    "Empty04",    "%d",    "cts"],
    ["counter9",    "Empty05",    "%d",    "cts"],
    ["counter10",   "Empty06",    "%d",    "cts"],
    ["counter11",   "Empty07",    "%d",    "cts"],
    ["counter12",   "Empty08",    "%d",    "cts"],
    ["counter13",   "Empty09",    "%d",    "cts"],
    ["counter14",   "Empty10",    "%d",    "cts"],
    ["counter15",   "Clock",    "%5.2f",    "s"]
    ]
    cpt0=counter("d09-1-c00/ca/cpt.1",user_readconfig=user_readconfig, clock_channel=14)
except Exception, tmp:
    print "I cannot define counter master."
    print tmp

#dxmap
try:
    user_readconfig0=[
    ["channel00",    "mca_00",    "%9d",    "cts"],
    ["channel01",    "mca_01",    "%9d",    "cts"],
    ["channel02",    "mca_02",    "%9d",    "cts"],
    ["channel03",    "mca_03",    "%9d",    "cts"],
    ["channel04",    "mca_04",    "%9d",    "cts"],
    ["channel05",    "mca_05",    "%9d",    "cts"],
    ["channel06",    "mca_06",    "%9d",    "cts"],
    ["channel07",    "mca_07",    "%9d",    "cts"],    
    ["outputCountRate00",    "ocr_00",    "%9d",    "cts"],
    ["outputCountRate01",    "ocr_01",    "%9d",    "cts"],
    ["outputCountRate02",    "ocr_02",    "%9d",    "cts"],
    ["outputCountRate03",    "ocr_03",    "%9d",    "cts"],
    ["outputCountRate04",    "ocr_04",    "%9d",    "cts"],
    ["outputCountRate05",    "ocr_05",    "%9d",    "cts"],
    ["outputCountRate06",    "ocr_06",    "%9d",    "cts"],
    ["outputCountRate07",    "ocr_07",    "%9d",    "cts"],
    ["inputCountRate00",    "icr_00",    "%9d",    "cts"],
    ["inputCountRate01",    "icr_01",    "%9d",    "cts"],
    ["inputCountRate02",    "icr_02",    "%9d",    "cts"],
    ["inputCountRate03",    "icr_03",    "%9d",    "cts"],
    ["inputCountRate04",    "icr_04",    "%9d",    "cts"],
    ["inputCountRate05",    "icr_05",    "%9d",    "cts"],
    ["inputCountRate06",    "icr_06",    "%9d",    "cts"],
    ["inputCountRate07",    "icr_07",    "%9d",    "cts"]]
    user_readconfig1=[
    ["channel00",    "mca_00",    "%9d",    "cts"],
    ["channel01",    "mca_01",    "%9d",    "cts"],
    ["channel02",    "mca_02",    "%9d",    "cts"],
    ["channel03",    "mca_03",    "%9d",    "cts"],
    ["channel04",    "mca_04",    "%9d",    "cts"],
    ["channel05",    "mca_05",    "%9d",    "cts"],
    ["channel06",    "mca_06",    "%9d",    "cts"],
    ["channel07",    "mca_07",    "%9d",    "cts"],    
    ["channel08",    "mca_08",    "%9d",    "cts"],
    ["channel09",    "mca_09",    "%9d",    "cts"],
    ["channel10",    "mca_10",    "%9d",    "cts"],
    ["channel11",    "mca_11",    "%9d",    "cts"],
    ["channel12",    "mca_12",    "%9d",    "cts"],
    ["channel13",    "mca_13",    "%9d",    "cts"],
    ["channel14",    "mca_14",    "%9d",    "cts"],
    ["channel15",    "mca_15",    "%9d",    "cts"],
    ["channel16",    "mca_16",    "%9d",    "cts"],
    ["channel17",    "mca_17",    "%9d",    "cts"],
    ["channel18",    "mca_18",    "%9d",    "cts"],
    ["channel19",    "mca_19",    "%9d",    "cts"],    
    ["roi00_01",    "roi_00_1",    "%9d",    "cts"],
    ["roi01_01",    "roi_01_1",    "%9d",    "cts"],
    ["roi02_01",    "roi_02_1",    "%9d",    "cts"],
    ["roi03_01",    "roi_03_1",    "%9d",    "cts"],
    ["roi04_01",    "roi_04_1",    "%9d",    "cts"],
    ["roi05_01",    "roi_05_1",    "%9d",    "cts"],
    ["roi06_01",    "roi_06_1",    "%9d",    "cts"],
    ["roi07_01",    "roi_07_1",    "%9d",    "cts"],    
    ["roi08_01",    "roi_08_1",    "%9d",    "cts"],
    ["roi09_01",    "roi_09_1",    "%9d",    "cts"],
    ["roi10_01",    "roi_10_1",    "%9d",    "cts"],
    ["roi11_01",    "roi_11_1",    "%9d",    "cts"],
    ["roi12_01",    "roi_12_1",    "%9d",    "cts"],
    ["roi13_01",    "roi_13_1",    "%9d",    "cts"],
    ["roi14_01",    "roi_14_1",    "%9d",    "cts"],
    ["roi15_01",    "roi_15_1",    "%9d",    "cts"],
    ["roi16_01",    "roi_16_1",    "%9d",    "cts"],
    ["roi17_01",    "roi_17_1",    "%9d",    "cts"],
    ["roi18_01",    "roi_18_1",    "%9d",    "cts"],
    ["roi19_01",    "roi_19_1",    "%9d",    "cts"],
    ["outputCountRate00",    "ocr_00",    "%9d",    "cts"],
    ["outputCountRate01",    "ocr_01",    "%9d",    "cts"],
    ["outputCountRate02",    "ocr_02",    "%9d",    "cts"],
    ["outputCountRate03",    "ocr_03",    "%9d",    "cts"],
    ["outputCountRate04",    "ocr_04",    "%9d",    "cts"],
    ["outputCountRate05",    "ocr_05",    "%9d",    "cts"],
    ["outputCountRate06",    "ocr_06",    "%9d",    "cts"],
    ["outputCountRate07",    "ocr_07",    "%9d",    "cts"],
    ["outputCountRate08",    "ocr_08",    "%9d",    "cts"],
    ["outputCountRate09",    "ocr_09",    "%9d",    "cts"],
    ["outputCountRate10",    "ocr_10",    "%9d",    "cts"],
    ["outputCountRate11",    "ocr_11",    "%9d",    "cts"],
    ["outputCountRate12",    "ocr_12",    "%9d",    "cts"],
    ["outputCountRate13",    "ocr_13",    "%9d",    "cts"],
    ["outputCountRate14",    "ocr_14",    "%9d",    "cts"],
    ["outputCountRate15",    "ocr_15",    "%9d",    "cts"],
    ["outputCountRate16",    "ocr_16",    "%9d",    "cts"],
    ["outputCountRate17",    "ocr_17",    "%9d",    "cts"],
    ["outputCountRate18",    "ocr_18",    "%9d",    "cts"],
    ["outputCountRate19",    "ocr_19",    "%9d",    "cts"],
    ["inputCountRate00",    "icr_00",    "%9d",    "cts"],
    ["inputCountRate01",    "icr_01",    "%9d",    "cts"],
    ["inputCountRate02",    "icr_02",    "%9d",    "cts"],
    ["inputCountRate03",    "icr_03",    "%9d",    "cts"],
    ["inputCountRate04",    "icr_04",    "%9d",    "cts"],
    ["inputCountRate05",    "icr_05",    "%9d",    "cts"],
    ["inputCountRate06",    "icr_06",    "%9d",    "cts"],
    ["inputCountRate07",    "icr_07",    "%9d",    "cts"],
    ["inputCountRate08",    "icr_08",    "%9d",    "cts"],
    ["inputCountRate09",    "icr_09",    "%9d",    "cts"],
    ["inputCountRate10",    "icr_10",    "%9d",    "cts"],
    ["inputCountRate11",    "icr_11",    "%9d",    "cts"],
    ["inputCountRate12",    "icr_12",    "%9d",    "cts"],
    ["inputCountRate13",    "icr_13",    "%9d",    "cts"],
    ["inputCountRate14",    "icr_14",    "%9d",    "cts"],
    ["inputCountRate15",    "icr_15",    "%9d",    "cts"],
    ["inputCountRate16",    "icr_16",    "%9d",    "cts"],
    ["inputCountRate17",    "icr_17",    "%9d",    "cts"],
    ["inputCountRate18",    "icr_18",    "%9d",    "cts"],
    ["inputCountRate19",    "icr_19",    "%9d",    "cts"]]
    user_readconfig2=[
    ["channel00",    "mca_20",    "%9d",    "cts"],
    ["channel01",    "mca_21",    "%9d",    "cts"],
    ["channel02",    "mca_22",    "%9d",    "cts"],
    ["channel03",    "mca_23",    "%9d",    "cts"],
    ["channel04",    "mca_24",    "%9d",    "cts"],
    ["channel05",    "mca_25",    "%9d",    "cts"],
    ["channel06",    "mca_26",    "%9d",    "cts"],
    ["channel07",    "mca_27",    "%9d",    "cts"],    
    ["channel08",    "mca_28",    "%9d",    "cts"],
    ["channel09",    "mca_29",    "%9d",    "cts"],
    ["channel10",    "mca_30",    "%9d",    "cts"],
    ["channel11",    "mca_31",    "%9d",    "cts"],
    ["channel12",    "mca_32",    "%9d",    "cts"],
    ["channel13",    "mca_33",    "%9d",    "cts"],
    ["channel14",    "mca_34",    "%9d",    "cts"],
    ["channel15",    "mca_35",    "%9d",    "cts"],
    ["roi00_01",    "roi_20_1",    "%9d",    "cts"],
    ["roi01_01",    "roi_21_1",    "%9d",    "cts"],
    ["roi02_01",    "roi_22_1",    "%9d",    "cts"],
    ["roi03_01",    "roi_23_1",    "%9d",    "cts"],
    ["roi04_01",    "roi_24_1",    "%9d",    "cts"],
    ["roi05_01",    "roi_25_1",    "%9d",    "cts"],
    ["roi06_01",    "roi_26_1",    "%9d",    "cts"],
    ["roi07_01",    "roi_27_1",    "%9d",    "cts"],    
    ["roi08_01",    "roi_28_1",    "%9d",    "cts"],
    ["roi09_01",    "roi_29_1",    "%9d",    "cts"],
    ["roi10_01",    "roi_30_1",    "%9d",    "cts"],
    ["roi11_01",    "roi_31_1",    "%9d",    "cts"],
    ["roi12_01",    "roi_32_1",    "%9d",    "cts"],
    ["roi13_01",    "roi_33_1",    "%9d",    "cts"],
    ["roi14_01",    "roi_34_1",    "%9d",    "cts"],
    ["roi15_01",    "roi_35_1",    "%9d",    "cts"],
    ["outputCountRate00",    "ocr_20",    "%9d",    "cts"],
    ["outputCountRate01",    "ocr_21",    "%9d",    "cts"],
    ["outputCountRate02",    "ocr_22",    "%9d",    "cts"],
    ["outputCountRate03",    "ocr_23",    "%9d",    "cts"],
    ["outputCountRate04",    "ocr_24",    "%9d",    "cts"],
    ["outputCountRate05",    "ocr_25",    "%9d",    "cts"],
    ["outputCountRate06",    "ocr_26",    "%9d",    "cts"],
    ["outputCountRate07",    "ocr_27",    "%9d",    "cts"],
    ["outputCountRate08",    "ocr_28",    "%9d",    "cts"],
    ["outputCountRate09",    "ocr_29",    "%9d",    "cts"],
    ["outputCountRate10",    "ocr_30",    "%9d",    "cts"],
    ["outputCountRate11",    "ocr_31",    "%9d",    "cts"],
    ["outputCountRate12",    "ocr_32",    "%9d",    "cts"],
    ["outputCountRate13",    "ocr_33",    "%9d",    "cts"],
    ["outputCountRate14",    "ocr_34",    "%9d",    "cts"],
    ["outputCountRate15",    "ocr_35",    "%9d",    "cts"],
    ["inputCountRate00",    "icr_20",    "%9d",    "cts"],
    ["inputCountRate01",    "icr_21",    "%9d",    "cts"],
    ["inputCountRate02",    "icr_22",    "%9d",    "cts"],
    ["inputCountRate03",    "icr_23",    "%9d",    "cts"],
    ["inputCountRate04",    "icr_24",    "%9d",    "cts"],
    ["inputCountRate05",    "icr_25",    "%9d",    "cts"],
    ["inputCountRate06",    "icr_26",    "%9d",    "cts"],
    ["inputCountRate07",    "icr_27",    "%9d",    "cts"],
    ["inputCountRate08",    "icr_28",    "%9d",    "cts"],
    ["inputCountRate09",    "icr_29",    "%9d",    "cts"],
    ["inputCountRate10",    "icr_30",    "%9d",    "cts"],
    ["inputCountRate11",    "icr_31",    "%9d",    "cts"],
    ["inputCountRate12",    "icr_32",    "%9d",    "cts"],
    ["inputCountRate13",    "icr_33",    "%9d",    "cts"],
    ["inputCountRate14",    "icr_34",    "%9d",    "cts"],
    ["inputCountRate15",    "icr_35",    "%9d",    "cts"]
    ]
    mca1=dxmap("d09-1-cx1/dt/dtc-mca_xmap.1",user_readconfig=user_readconfig1)
    mca2=dxmap("d09-1-cx1/dt/dtc-mca_xmap.2",user_readconfig=user_readconfig2)
    def setroi(ch1, ch2):
    	"""Set roi an ALL channels between ch1 and ch2. Works on mca1 and mca2"""
	if mca1 <> None:
		mca1.setROIs(-1, ch1, ch2)
	if mca2 <> None:
		mca2.setROIs(-1, ch1, ch2)
	return 
except Exception, tmp:
    print "Failure defining dxmap: d09-1-cx1/dt/dtc-mca_xmap.1"
    print "Failure defining dxmap: d09-1-cx1/dt/dtc-mca_xmap.2"

try:
    from simple_camera import camera
    kam = camera("d09-1-cx1/dt/vg2-basler")
except Exception, tmp:
    print "Cannot Define kam as a camera: from class simple_camera"
    raise tmp
    
try:
    from sensor_group import sensor_group
    mux=sensor("d09-1-c00/ex/tangoparser.1","mux")
    mus=sensor("d09-1-c00/ex/tangoparser.1","mus")
    MUXES=sensor_group([["d09-1-c00/ex/tangoparser.1",["mux","mus","muf"]],])
    #MUXES=sensor_group([["d09-1-c00/ex/tangoparser.1",["mux","mus","muf","muPL"]],])
    #cam2_intensity = sensor_group([["d09-1-c04/dt/vg1.1-analyzer", ["MeanIntensity",]],])
    KamRoi = sensor_group([["d09-1-cx1/dt/vg2-basler-roicounters",["sum0","sum1"]],])
except Exception, tmp:
    print tmp
    print "Cannot define mux and mus on TangoParser"
    atk(mux)

#ct
try:
    cpt=pseudo_counter(masters=[cpt0,],slaves=[MUXES,])
    ct=pseudo_counter(masters=[cpt0,],slaves2arm2stop=[mca1,mca2],slaves=[MUXES,])
    #ct=pseudo_counter(masters=[cpt0, kam],slaves2arm2stop=[mca1,mca2],slaves=[MUXES,KamRoi])
    #cpt=pseudo_counter(masters=[cpt0,],slaves=[,])
    #ct=pseudo_counter(masters=[cpt0,],slaves2arm2stop=[mca1,mca2],slaves=[])
except Exception, tmp:
    print "Failure defining ct "
    print "Defaulting to cpt... ct=cpt... "
    ct=cpt
    print tmp

#HV power supplies
try:
    HV_I0    =NHQ_HVsupply("d09-1-cx1/ex/mi_cio-hvps.1","A")
    HV_I1    =NHQ_HVsupply("d09-1-cx1/ex/mi_cio-hvps.1","B")
except Exception, tmp:
    #print tmp
    print "Error on defining NHQ module 1 SHV of chambers I0 and I1"
try:
    HV_I2    =NHQ_HVsupply("d09-1-cx1/ex/mi_cio-hvps.2","B")
    HV_xbpm    =NHQ_HVsupply("d09-1-cx1/ex/mi_cio-hvps.2","A")
except Exception, tmp:
    #print tmp
    print "Error on defining NHQ module 2 SHV of chambers I2 and xbpm"


##--------------------------------------------------------------------------------------
##RS232 controlled custom equipment
##--------------------------------------------------------------------------------------
## RONTEC MCA
#try:
#    rontec=rontec_MCA("d09-1-cx1/dt/dtc_sdd-mca_rontec.1")
#except:
#    print "No rontec available"

# I200 (home made python controller)
#try:
#    from I200 import I200_tango as I200
#    print "I200 unit :",
#    i200=I200("d09-1-cx1/ca/mca_rontec_rs232_8.5")
#    itune=i200.tune
#    #print i200.currents()
#    #print i200.status()
#except Exception, tmp:
#    print "Error initializing I200."
#    print tmp

# MOSTAB (home made python controller)
try:
    from MOSTAB import MOSTAB_tango as MOSTAB
    print "MOSTAB unit :",
    mostab=MOSTAB("d09-1-cx1/ca/mca_rontec_rs232_8.5",init_file = __IP.user_ns["__pySamba_root"] + "/config/mostab.cfg")
    def itune(*args,**kwargs):
        opr = 3.56/(0.10 * dcm.pos() * 1e-3 - 0.16) * 0.9
        if "oprange" in kwargs.keys():
            return mostab.tune(*args,**kwargs)
        else:
            kwargs["oprange"] = opr
            return mostab.tune(*args,**kwargs)
    #itune=mostab.tune
    #print i200.currents()
    #print i200.status()
except Exception, tmp:
    print "Error initializing mostab unit..."
    print tmp
    
#ACE Avalanche Photodiode Controller (home made python controller)
try:
    from ACE_APD import ACE_APD
    ace=ACE_APD("d09-1-c00/ca/serial.com8")
except Exception, tmp:
    print tmp
    print "ACE_APD: ace=d09-1-c00/ca/serial.com8 not defined!"

##--------------------------------------------------------------------------------------
##Define motors here
##--------------------------------------------------------------------------------------

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

#################################################
#             Moveables
################################################

#Normal moveables (missing special options)
__tmp={
"T_dcm_set": ["d09-1-c03/op/bath.1","temperatureSetPoint"],
"po1"        :["d09-1-c02/ex/po.1-mt.1","position","delay=1.","timeout=3."],
"po2"        :["d09-1-c06/ex/po.1-mt_tz.1","position","delay=1.","timeout=3."],
"po3"        :["d09-1-cx1/ex/po.1-mt_tz.1","position","delay=1.","timeout=3."],
"po4"        :["d09-1-c07/ex/po.1-mt_tz.1","position"],
"po5"        :["d09-1-cx2/ex/po.1-mt_tz.1","position"],
"bender_c1"    :["d09-1-c03/op/mono1-mt_c.1","position"],
"bender_c2"    :["d09-1-c03/op/mono1-mt_c.2","position"],
"sample_x"    :["d09-1-cx1/ex/tab-mt_tx.1","position"],
"sample_z"    :["d09-1-cx1/ex/tab-mt_tz.1","position"],
"sample_rx"    :["d09-1-cx1/ex/tab-mt_rx.1","position"],
"sample_rx2"    :["d09-1-cx1/ex/tab-mt_rx.2","position"],
"sample_rz"        :["d09-1-cx1/ex/tab-mt_rz.1","position"],
"tbt_z"        :["d09-1-cx1/ex/cryo-tbt-mt_tz.1","position"],
"fluo_x"    :["d09-1-cx1/dt/dtc_ge.1-mt_tx.1","position"],
"fluo_s"    :["d09-1-cx1/dt/dtc_ge.1-mt_ts.1","position"],
"fluo_z"    :["d09-1-cx1/dt/dtc_ge.1-mt_tz.1","position"],
"raman_x"    :["d09-1-cx1/ex/raman-tx.1","position"],
"raman_z"    :["d09-1-cx1/ex/raman-tz.1","position"],
"filter"    :["d09-1-cx1/ex/pfi.1-mt_rs.1","position"],
"sx"        :["d09-1-cx2/ex/sex-mt_tx.1","position"],
"sy"        :["d09-1-cx2/ex/sex-mt_ty.1","position"],
"sz"        :["d09-1-cx2/ex/sex-mt_tz.1","position"],
"sphi"        :["d09-1-cx2/ex/sex-mt_rz.1","position"],
"imag1"        :["D09-1-C02/DT/IMAG1-MT_Tz.1","position"],
"imag2"        :["D09-1-C04/DT/IMAG2-MT_Tz.1","position"],
"imag3"        :["D09-1-C06/DT/IMAG3-MT_Tz.1","position"],
"dac0"        :["d09-1-c00/ca/mao.1","channel0"],
"dac1"        :["d09-1-c00/ca/mao.1","channel1"],
"dac2"        :["d09-1-c00/ca/mao.1","channel2"],
"dac3"        :["d09-1-c00/ca/mao.1","channel3"],
"dac4"        :["d09-1-c00/ca/mao.1","channel4"],
"dac5"        :["d09-1-c00/ca/mao.1","channel5"],
"dac6"        :["d09-1-c00/ca/mao.1","channel6"],
"dac7"        :["d09-1-c00/ca/mao.1","channel7"],
"ttlF"        :["d09-1-c00/ca/dio.1","PortF"],
"cam1"        :["d09-1-c02/dt/vg1.0","ExposureTime"],
"cam2"        :["d09-1-c04/dt/vg1.1","ExposureTime"],
"cam3"        :["d09-1-c06/dt/vg1.2","ExposureTime"],
"cam4"        :["d09-1-cx1/dt/vg2-basler","ExposureTime"],
"I0_gain"    :["d09-1-cx1/ex/amp_iv.1","gain"],
"I1_gain"    :["d09-1-cx1/ex/amp_iv.2","gain"],
"I2_gain"    :["d09-1-cx1/ex/amp_iv.3","gain"],
"mostab_gain1"    :["d09-1-cx1/ex/amp_iv.10","gain"],
#"mostab_gain2"    :["d09-1-cx1/ex/amp_iv.4","gain"],
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
"cryo4z" :["d09-1-cx1/ex/option1-mt_tz.1","position"],
#"cryo4set" :["d09-1-cx1/ex/cryo4.1-ctrl","temperatureSetPoint"],
#"keith_I0"      :["d09-1-cx1/ex/amp_iv.7","gain"],
#"keith_I1"      :["d09-1-cx1/ex/amp_iv.8","gain"],
#"keith_I2"      :["d09-1-cx1/ex/amp_iv.9","gain"],
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
    except Exception, tmp:
        print RED+"Failed"+RESET+" defining: %s/%s as %s"%tuple(__tmp[i][0:2]+[i,])
        print RED+"-->"+RESET,tmp
        print UNDERLINE+__cmdstring+RESET

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
"T_dcm"        :["d09-1-c03/op/bath.1","temperature"],
#"cryo4temp1" :["d09-1-cx1/ex/cryo4.1-ctrl","temperature1"],
#"cryo4temp2" :["d09-1-cx1/ex/cryo4.1-ctrl","temperature2"],
}                                                

__ll=__tmp.keys()
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
    except Exception, tmp:
        print RED+"Failed"+RESET+" defining: %s/%s as %s"%tuple(__tmp[i][0:2]+[i,])
        print RED+"-->"+RESET,tmp
        print UNDERLINE+__cmdstring+RESET
del __tmp,__ll

##################################################################

#MM4005 motors:
#__tmp={
#"mm1":"d09-1-c00/ca/gpib.0-02:1",
#"mm2":"d09-1-c00/ca/gpib.0-02:2",
#"mm3":"d09-1-c00/ca/gpib.0-02:3"}
#
#try:
#    from mm4005 import mm4005_motor
#    for i in __tmp:
#        try:
#            if type(__tmp[i]) in [tuple,list]:
#                __exstr="mm4005_motor(\""+__tmp[i][0]+"\","
#                for j in range(1,len(__tmp[i])-1): __exstr+=__tmp[i][j]
#                __exstr+=")"
#                __IP.user_ns[i]=eval(__exstr)
#                del __exstr
#            else:
#                __IP.user_ns[i]=mm4005_motor(__tmp[i])
#            __allmotors+=[__IP.user_ns[i],]
#        except:
#            print "Cannot define %s =mm4005_motor(%s)"%(i,__tmp[i])
#except:
#    print "Cannot import mm4005_motor from mm4005 module" 
#    

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
    except Exception, tmp:
        print tmp
        print RED+"Cannot define"+RESET+" %s =motor(%s)"%(i,__tmp[i])


###
### Define aliases below
###

aliases={
"sample_x":"x",
"sample_z":"z",
"sample_rz":"phi",
"sample_rx":"theta",
"sample_rx2":"phi2"
}

for i in aliases:
    if i in __IP.user_ns:
        try:
            __IP.user_ns[aliases[i]]=__IP.user_ns[i]
        except Exception, tmp:
            print tmp
            print "Error defining ",aliases[i]," as alias for ",i


##-------------------------------------------------------------------------------------
##Define Main Optic Components Here
##-------------------------------------------------------------------------------------
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
    A1_1 = 501530. #481888.35048462    #493068. #488717. #A1_1=504940.0 #503280.0 #+520646.0 #521776.
    A0_1 = 90173.9 #91054.1663915865   #99208. #101943. #A0_1=81255.0 #53248.0  #-55962.1  #-59292.2
    A1_2 = 492346. #493502.288067641   #487333. #492917. #A1_2=486220.0 #507372.0 #+511363.0 #535801.0
    A0_2 = 112661. #111904.850053559   #107675. #104935. #A0_2=69396.0 #58929.8  #-10790.7  #-21530   
    #Rz2 ()
    Rz2_par = [-17703.5, 138.964, -4.18379]  
    #Rs2 ()
    Rs2_par=[-1050.,]#[-1343.,]
    #Rx2 ()
    Rx2_par=[-13015.3, 669.076, -1647.08] #[-12985.6,]#[-7504.85, 727.716, -1756.17]#[-8257.2,229.33,-14.074,0.36688,-0.003593,]

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
    
    bender=sagittal_bender(bender1_name="d09-1-c03/op/mono1-mt_c.1",bender2_name="d09-1-c03/op/mono1-mt_c.2",\
    controlbox_rawdata1="d09-1-c00/ca/bai.1121-mos.1-cb-rawdata",controlbox_rawdata2="d09-1-c00/ca/bai.1121-mos.1-cb-rawdata.2",\
    axis1=6,axis2=7,\
    A1_1=A1_1,A0_1=A0_1,A1_2=A1_2,A0_2=A0_2)
    
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
    #WhiteBeam={"rx1":0.,"tz2":24.,"tz1":8.},emin=4500.,emax=40000.)

    dcm=mono1(d=d,H=26.0,mono_name="d09-1-c03/op/mono1",
    rx1=rx1,tz2=tz2,ts2=ts2,rx2=rx2,rs2=rs2,rx2fine=rx2fine,rz2=rz2, tz1=tz1, bender=bender,
    sourceDistance=16.119,delay=0.3,Rz2_par=Rz2_par,Rs2_par=Rs2_par,Rx2_par=Rx2_par,
    WhiteBeam={"rx1":0.,"tz2":24.,"tz1":8.},emin=4500.,emax=43000.)

    #Bender disable:
    #dcm=mono1(d=d,H=25.0,mono_name="d09-1-c03/op/mono1",
    #rx1=rx1,tz2=tz2,ts2=ts2,rx2=rx2,rs2=rs2,rx2fine=rx2fine,rz2=None, tz1=tz1, bender=None,
    #sourceDistance=16.119,delay=0.3,Rz2_par=Rz2_par,Rs2_par=Rs2_par,Rx2_par=Rx2_par,
    #WhiteBeam={"rx1":0.,"tz2":24.,"tz1":8.})
    
    #Aliases for dcm operation
    energy=dcm
    seten=dcm.seten
    tune=dcm.tune
    print "OK!"
except Exception, tmp: 
    print tmp
    print "Cannot define dcm (monochromator not set)."

#QEXAFS to be removed
#try:
#    q2_energy=channel_cut(d=__d111,theta=q2_theta,tz=q2_tz)
#    q3_energy=channel_cut(d=__d311,theta=q3_theta,tz=q3_tz)
#except Exception, tmp: 
#    print tmp
#    print "cannot initialize q2_energy or q3_energy"
#





##--------------------------------------------------------------------------------------
##PSS
##--------------------------------------------------------------------------------------

try:
    FE=FrontEnd("tdl-d09-1/vi/tdl.1")
    obxg=PSS.obx("d09-1-c06/vi/obxg.1")
    obx=PSS.obx("d09-1-c07/ex/obx.1")
except Exception, tmp:
    print tmp
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
    except Exception, tmp:
        print tmp
        print "Cannot define %s =valve(%s)"%(i,__tmp[i])
del __tmp

#attenuateur 
try:
    att=absorbing_system("d09-1-c01/ex/att.1")
except Exception, tmp:
    print tmp
    print "Cannot configure d09-1-c01/ex/att.1"

#Fast shutter
try:
    from pseudo_valve import pseudo_valve
    #print "Fast shutter is sh_fast"
    sh_fast=pseudo_valve(label="d09-1-c00/ca/dio_0.1",channel="G",delay=0.1,deadtime=0.,timeout=0,reverse=True)
except Exception, tmp:
    print tmp
    print "No fast shutter defined!"


###
### Import classes containing defaults pointing to objects declared above (e.g. dcm, cpt1...)
###

######################################################################################
#        INCLUDE SCANS SECTION                                                #
######################################################################################

####DEFINE HERE THE DARK VALUES USED BY ESCAN
#Modified 19/11/2013
try:
    USER_DARK_VALUES = {
    0 : [I0_gain, 0., 0., 0., 0., 0., 0., 78.5],
#    0 : [I0_gain, 0., 0., 0., 72.1, 73.8, 80.6, 160.2],
#    0 : [I0_gain, 0., 0., 0., 346.5, 346.9, 352.9, 412.1],
    1 : [I1_gain, 0., 0., 0., 644.4, 646.6, 654.5, 736.9],
    2 : [I2_gain, 0., 0., 0., 79.7, 80.6, 87.5, 161.9]
    }
except Exception, tmp:
    print "Error defining dark current values... maybe amplifiers have not been defined..."
    print tmp


##########################################################################
#Include non permanent function declarations or actions here below       #
##########################################################################

#try:
#    execfile(__pySamba_root+"/modules/qexafs_functions.py")
#except:
#    print "Error in QEXAFS file try to execute it by hand"

try:
    def tablescan(p1,p2,dp=0.25,dt=0.25,channel=0,returndata=False):
        """Calls the samplescan with default channel=0 instead of 1. Just a shortcut. """
        return ascan(po3,p1,p2,dp,dt,channel,returndata=False)
except Exception, tmp:
    print "error defining tablescan"
    print tmp



#########################################
#        Shutters and waitings          #
#########################################

try:
    #in the right order...
    __allshutters=[FE, obxg, obx]
    #FEopen=FE.open
    #shclose=obxg.close
    #sexclose=obx.close
except Exception, tmp:
    print tmp
    print "Check state of shutters... something wrong in script..."


def shopen(level=1):
    """Open shutters up to level specified starting from lower level"""
    for i in range(level+1):
        if "frontEndStateValue" in __allshutters[i].DP.get_attribute_list() and __allshutters[i].DP.frontEndStateValue == 2:
            print "Front End is locked by Machine Operator"
            print "I will wait for electron beam injection..."
            wait_injection()
        if "beamLineOccInterlock" in __allshutters[i].DP.get_attribute_list() and __allshutters[i].DP.beamlineoccinterlock:
                print "Front End is beam line locked: calling wait_injection()"
                wait_injection()
                #raise Exception("Front End locked, verify PSS or try again later.")
        if "beamLinePSSInterlock" in __allshutters[i].DP.get_attribute_list() and __allshutters[i].DP.beamlinepssinterlock:
                print "Front End is beam line locked: calling wait_injection()"
                wait_injection()
                #raise Exception("Front End locked, verify PSS or try again later.")
        if "isInterlocked" in __allshutters[i].DP.get_attribute_list() and __allshutters[i].DP.isInterlocked:
                #raise Exception("Shutter locked, verify PSS or try again later.")
                while(__allshutters[i].DP.isInterlocked):
                    print "Waiting for PSS permission to open shutter... " + asctime() + "\r",
                    sys.stdout.flush()
                    sleep(1)
        print ""
        __allshutters[i].open()
	print __allshutters[i].label," ",__allshutters[i].state()
    if level >= 1:
        try:
            mostab.start()
            print "mostab: start executed"
        except:
            pass
    return __allshutters[level].state()

def shclose(level=1):
    """Close shutters down to level specified starting from maximum level"""
    try:
        mostab.stop()
        print "mostab: stop executed"
    except:
        pass
    for i in range(len(__allshutters)-1,level-1,-1):
    	__allshutters[i].close()
	print __allshutters[i].label," ",__allshutters[i].state()
    return __allshutters[level].state()

def shstate():
    """Provide state of last open shutter starting from lower.
    -1 means closed beamline
    0 means front end open
    1 means level 1 open 
    2 means level 2 open ..."""
    for i in range(len(__allshutters)):
        if __allshutters[i].state() <> DevState.OPEN:
            break
    if i == 0:
        print "Beamline is closed"
    else:
        print "Beamline is open up to level:", i - 1
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
except Exception, tmp:
    print "wait_functions.py module is in error."
    print tmp
    print "Ignoring..."


##############################
#user configs
##############################

#
#    SOME temporary defs
#


try:
    vg_x=sensor("d09-1-cx1/dt/vg2-basler-analyzer","ChamberXProjFitCenter")
    vg_y=sensor("d09-1-cx1/dt/vg2-basler-analyzer","ChamberYProjFitCenter")
except Exception, tmp:
    print tmp
    print "videograbber d09-1-cx1/dt/vg2-basler-analyzer error!"


try:
    domacro("LoadMeshScan.py")
    print 'mesh(motor, debut, fin, n, motor2, debut2, fin2, n2, dt=1.0, timeBases=["d09-1-c00/ca/cpt.1"], delay=0.0)'
except Exception, tmp:
    print tmp

#try:
#    import diffscan as diffscan_class
#    def diffscan(filename,trajectory,dicro_motor,UpDownValues,Repetitions,Integration,WaitDCM=0,WaitDicro=0,dcm=dcm,ct=ct):
#        this_scan=diffscan_class.diffscan_class(trajectory,dicro_motor,UpDownValues,Repetitions,Integration,WaitDCM,WaitDicro,dcm,ct)
#        return    this_scan.start(filename)
#    import voltage_controller
#    dicro=voltage_controller.voltage_controller(dac0,ttlF,-5,5,10,0.02)
#except Exception, tmp:
#    print "Error loading diffscan"
#    print tmp


print "Instruments: default is"+RED+" EXAFS"+RESET+". Type "+RED+"SEXAFS"+RESET+" to use the second experimental hutch."

def SEXAFS():
    return instrument("SEXAFS")


####
#### Define here below lists of moveables for a quick view with "wm"
####


#slits=[vgap1,vpos1,hgap1,hpos1,vgap2,vpos2,vgap3,vpos3,hgap3,hpos3,vgap4,vpos4,hgap4,hpos4,vgap5,vpos5,hgap5,hpos5]
#slits=[vgap1,vpos1,hgap1,hpos1,vgap2,vpos2,vgap3,vpos3,vgap4,vpos4,hgap4,hpos4,vgap5,vpos5,hgap5,hpos5]
slits=[vgap1,vpos1,hgap1,hpos1,vgap2,vpos2,vgap4,vpos4,hgap4,hpos4,vgap5,vpos5,hgap5,hpos5,vgap6,vpos6,hgap6,hpos6]
sample=[x, z, phi, theta]
fluo=[fluo_x, fluo_s, fluo_z]
sexafs=[sx,sy,sz,sphi]
optics=[dcm,rx1,rx2,rz2,rx2,rx2fine,tz2,ts2,mir1_pitch,mir1_roll,mir1_z,mir1_c,mir2_pitch,mir2_roll,mir2_z,mir2_c]

##
#try:
#    __cryostat__=DeviceProxy("d09-1-cx1/ex/cryo4.1-ctrl")
#    def set_temp(t=None):
#        __c=__cryostat__
#        if t==None:
#            print "Temperature is :",__c.temperature
#            print "Set Point is :",__c.temperatureSetPoint
#            return
#        __c.temperatureSetPoint=t
#        sleep(3)
#        return __c.temperatureSetPoint
#
#except:
#    print "Error defining set_temp"

#Load marccd 
#instrument("MARCCD")
#Load mar345
#instrument("MAR345")
#load sai into ct
#instrument("SAI")
#load cameras into ct
#instrument("CAMERAS")
#load Eurotherm controllers
instrument("FORNO")
