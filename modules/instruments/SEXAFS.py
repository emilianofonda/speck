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

#print "dcm.sample_at should be at 19.54 when beam in SEXAFS."

##-------------------------------------------------------------------------------------
##Define ReadOut Electronics Here
##-------------------------------------------------------------------------------------

#Counters

#NI6602
#try:
#    user_readconfig=[
#    ["counter1",    "I0",        "%d",    "cts"],
#    ["counter2",    "I1",        "%d",    "cts"],
#    ["counter3",    "TEY",        "%d",    "cts"],
#    ["counter4",    "CT3",        "%d",    "cts"],
#    ["counter5",    "CT4",            "%d",    "cts"],
#    ["counter6",    "CT5",            "%d",    "cts"],
#    ["counter7",    "Time",            "%5.2f",    "s"]
#    ]
#    cpt=counter("d09-1-c00/ca/cpt.2",user_readconfig=user_readconfig, clock_channel= 6)
#except Exception, tmp:
#    print RED+"I cannot define the main counter!"+RESET
#    print tmp

#dxmap: configured for Bruker SDD of Lucia
try:
    #user_readconfig1=[
    #["channel00",    "mca_00",    "%9d",    "cts"],
    #["roi00_01",    "roi_00_1",    "%9d",    "cts"],
    #["outputCountRate00",    "ocr_00",    "%9d",    "cts"],
    #["inputCountRate00",    "icr_00",    "%9d",    "cts"]]
    mca1=dxmap("d091-1-cx2/dt/dtc-mca_xmap.1")
    mca2=None
    print GREEN+"mca1 --> DxMap card"+RESET
except Exception, tmp:
    print tmp
    print RED+"Failure defining dxmap: d09-1-cx2/dt/dtc-mca_xmap.1"+RESET

#ct
try:
    cpt=pseudo_counter(masters=[cpt0,])
    ct=pseudo_counter(masters=[cpt0,],slaves2arm2stop=[mca1,],slaves=[])
except:
    print "Failure defining ct speclike_syntax command"
    print "Defaulting to cpt... ct=cpt... pysamba survival kit... is XIA dead?"
    ct=cpt

def setSTEP(mode="MCA", config="STEP"):
    return setMODE(mode, config, mca=[__IP.user_ns["mca1"],])

def setMAP(mode="MAPPING", config="MAP"):
    return setMODE(mode, config, mca=[__IP.user_ns["mca1"],])

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
#        INCLUDE SCANS SECTION                                                #
######################################################################################



##########################################################################
# finally include the escan class to perform energy scans   !            #
##########################################################################

domacro("ecscanSEXAFS.py")

##########################################################################
#Include non permanent function declarations or actions here below       #
##########################################################################


#########################################
#        Tests                   #
#########################################



#########################################
#        Local defs        #
#########################################



##############################
#user configs             #
##############################

vslit=vgap6
hslit=hgap6

##############################
#    Changing the prompt     #
##############################
try:
    get_ipython().magic('config PromptManager.in_template=u\'\\w\\nSpeck: SEXAFS #\\#>\'')
    #set_spooky_prompt("SEXAFS")
except:
    pass
