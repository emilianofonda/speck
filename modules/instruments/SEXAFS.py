#Macro to define the SEXAFS instrument:
__IP = get_ipython()
####### REMOVE OBJECTS FROM EXAFS SETUP #############
#This part should be replaced by an automatic method
#associated to the instrument
__tmp=["x","z","phi","filter",\
"fluo_x","fluo_z","fluo_s",\
"sample_rx","sample_rx2","theta"]
for i in __tmp:
	try:
		exec("del "+i)
	except:
		print "Cannot remove %s from environment."%i
		pass
##################################################
print "################################################################"
print "#                Performing SEXAFS definitions                 #" 
print "################################################################"

print "dcm.sample_at should be at 19.54 when beam in SEXAFS."

##-------------------------------------------------------------------------------------
##Define ReadOut Electronics Here
##-------------------------------------------------------------------------------------

#Counters

#NI6602
try:
	user_readconfig=[
	["counter1",	"I0",		"%d",	"cts"],
	["counter2",	"I1",		"%d",	"cts"],
	["counter3",	"TEY",		"%d",	"cts"],
	["counter4",	"CT3",		"%d",	"cts"],
	["counter5",	"CT4",	        "%d",	"cts"],
	["counter6",	"CT5",	        "%d",	"cts"],
	["counter7",	"Time",	        "%5.2f",	"s"]
	]
	cpt=counter("d09-1-c00/ca/cpt.2",user_readconfig=user_readconfig, clock_channel= 6)
except Exception, tmp:
	print RED+"I cannot define the main counter!"+RESET
	print tmp

#dxmap
try:
	user_readconfig1=[
	["channel00",	"mca_00",	"%9d",	"cts"],
	["channel01",	"mca_01",	"%9d",	"cts"],
	["channel02",	"mca_02",	"%9d",	"cts"],
	["channel03",	"mca_03",	"%9d",	"cts"],
	["channel04",	"mca_04",	"%9d",	"cts"],
	["channel05",	"mca_05",	"%9d",	"cts"],
	["channel06",	"mca_06",	"%9d",	"cts"],
	["channel07",	"mca_07",	"%9d",	"cts"],	
	["roi00_01",	"roi_00_1",	"%9d",	"cts"],
	["roi01_01",	"roi_01_1",	"%9d",	"cts"],
	["roi02_01",	"roi_02_1",	"%9d",	"cts"],
	["roi03_01",	"roi_03_1",	"%9d",	"cts"],
	["roi04_01",	"roi_04_1",	"%9d",	"cts"],
	["roi05_01",	"roi_05_1",	"%9d",	"cts"],
	["roi06_01",	"roi_06_1",	"%9d",	"cts"],
	["roi07_01",	"roi_07_1",	"%9d",	"cts"],	
	["outputCountRate00",	"ocr_00",	"%9d",	"cts"],
	["outputCountRate01",	"ocr_01",	"%9d",	"cts"],
	["outputCountRate02",	"ocr_02",	"%9d",	"cts"],
	["outputCountRate03",	"ocr_03",	"%9d",	"cts"],
	["outputCountRate04",	"ocr_04",	"%9d",	"cts"],
	["outputCountRate05",	"ocr_05",	"%9d",	"cts"],
	["outputCountRate06",	"ocr_06",	"%9d",	"cts"],
	["outputCountRate07",	"ocr_07",	"%9d",	"cts"],
	["inputCountRate00",	"icr_00",	"%9d",	"cts"],
	["inputCountRate01",	"icr_01",	"%9d",	"cts"],
	["inputCountRate02",	"icr_02",	"%9d",	"cts"],
	["inputCountRate03",	"icr_03",	"%9d",	"cts"],
	["inputCountRate04",	"icr_04",	"%9d",	"cts"],
	["inputCountRate05",	"icr_05",	"%9d",	"cts"],
	["inputCountRate06",	"icr_06",	"%9d",	"cts"],
	["inputCountRate07",	"icr_07",	"%9d",	"cts"]]
	mca1=dxmap("d09-1-cx2/dt/dtc-mca_xmap.3",user_readconfig=user_readconfig1)
	mca2=None
	print GREEN+"mca1 --> DxMap card"+RESET
except:
	print RED+"Failure defining dxmap: d09-1-cx2/dt/dtc-mca_xmap.3"+RESET

try:
    __tmp = sensor_group([["d09-1-c00/ex/tangoparser.2",["smuf"]]])
except:
    print "Error defining tangoparser"

#ct
try:
	cpt=pseudo_counter(masters=[cpt,])
	ct=pseudo_counter(masters=[cpt,],slaves2arm2stop=[mca1,],slaves=[__tmp,])
except:
	print "Failure defining ct speclike_syntax command"
	print "Defaulting to cpt... ct=cpt... pysamba survival kit... is XIA dead?"
	ct=cpt

##--------------------------------------------------------------------------------------
##Define motors here
##--------------------------------------------------------------------------------------


#Normal moveables (missing special options)
__tmp={
"sx"            :["d09-1-cx2/ex/sex-mt_tx.1","position"],
"sy"            :["d09-1-cx2/ex/sex-mt_ty.1","position"],
"sz"            :["d09-1-cx2/ex/sex-mt_tz.1","position"],
"sphi"          :["d09-1-cx2/ex/sex-mt_rz.1","position"]}

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
																			
###
### Define aliases below
###

aliases={
"sx":"x",
"sy":"y",
"sz":"z",
"sphi":"phi"
}

for i in aliases:
	if i in __IP.user_ns:
		try:
			__IP.user_ns[aliases[i]]=__IP.user_ns[i]
		except:
			print "Error defining ",aliases[i]," as alias for ",i


##-------------------------------------------------------------------------------------
##Define Main Optic Components Here
##-------------------------------------------------------------------------------------

#Replace the counter for the tuning with the new one
dcm.counter=cpt

##--------------------------------------------------------------------------------------
##PSS
##--------------------------------------------------------------------------------------

##--------------------------------------------------------------------------------------
##VALVES
##--------------------------------------------------------------------------------------

sh_fast=None

###
### Import classes containing defaults pointing to objects declared above (e.g. dcm, cpt, ct, mca...)
###


######################################################################################
#		INCLUDE SCANS SECTION                                                #
######################################################################################

####DEFINE HERE THE DARK VALUES USED BY ESCAN
#Modified 19/11/2013
try:
    USER_DARK_VALUES = {
    0 : [I0_gain, 0., 0., 0., 0., 0., 0., 0.],
    1 : [I1_gain, 0., 0., 0., 0., 0., 0., 0.],
    2 : [I2_gain, 0., 0., 0., 0., 0., 0., 0.]
    }
except Exception, tmp:
    print "Error defining dark current values... maybe amplifiers have not been defined..."
    print tmp



##########################################################################
# finally include the escan class to perform energy scans   !            #
##########################################################################

##########################################################################
#Include non permanent function declarations or actions here below       #
##########################################################################


#########################################
#		Tests                   #
#########################################



#########################################
#		Local defs		#
#########################################



##############################
#user configs		     #
##############################

vslit=vgap5
hslit=hgap5

##############################
#    Changing the prompt     #
##############################
try:
	get_ipython().magic('config PromptManager.in_template=u\'\\w\\nSpeck: SEXAFS #\\#>\'')
    #set_spooky_prompt("SEXAFS")
except:
	pass
