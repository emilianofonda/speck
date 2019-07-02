#Macro to define the SEXAFS instrument:
__IP = get_ipython()
####### REMOVE OBJECTS FROM EXAFS SETUP #############
#This part should be replaced by an automatic method
#associated to the instrument
##################################################

##-------------------------------------------------------------------------------------
##Define ReadOut Electronics Here
##-------------------------------------------------------------------------------------

#Counters

#mca1 and mca2 have to be already defined

try:

    falconConfig=[\
    ["channel00",    "FalconMCA1",    "%9d",    "cts"],
    ["channel01",    "FalconMCA2",    "%9d",    "cts"],
    ["channel02",    "FalconMCA3",    "%9d",    "cts"],
    ["channel03",    "FalconMCA4",    "%9d",    "cts"],
    ["roi00_01",    "FalconROI1",    "%9d",    "cts"],
    ["roi01_01",    "FalconROI2",    "%9d",    "cts"],
    ["roi02_01",    "FalconROI3",    "%9d",    "cts"],
    ["roi03_01",    "FalconROI4",    "%9d",    "cts"],
    ["deadTime00",   "FalconDT1",    "%9d",    "%"],
    ["deadTime01",   "FalconDT2",    "%9d",    "%"],
    ["deadTime02",   "FalconDT3",    "%9d",    "%"],
    ["deadTime03",   "FalconDT4",    "%9d",    "%"],
    ["inputCountRate00",    "FalconICR1",    "%9d",    "cps"],
    ["inputCountRate01",    "FalconICR2",    "%9d",    "cps"],
    ["inputCountRate02",    "FalconICR3",    "%9d",    "cps"],
    ["inputCountRate03",    "FalconICR4",    "%9d",    "cps"],
    ["outputCountRate00",   "FalconOCR1",    "%9d",    "cps"],
    ["outputCountRate01",   "FalconOCR2",    "%9d",    "cps"],
    ["outputCountRate02",   "FalconOCR3",    "%9d",    "cps"],
    ["outputCountRate03",   "FalconOCR4",    "%9d",    "cps"]\
    ]
    falcon=dxmap("tmp/test/xiadxp_falconx.1",user_readconfig=falconConfig,FTPclient="d09-1-c00/ca/ftpclientFalcon",FTPserver="d09-1-c00/ca/ftpserverFalcon",spoolMountPoint="/nfs/srv5/spool1/falcon")
    print GREEN+"FalconX1 OK"+RESET
except Exception, tmp:
    print tmp
    print RED+"Failure defining dxmap: tmp/test/xiadxp_falconx.1"+RESET

#ct
try:
    ctPosts=[\
    {"name":"MUX","formula":"log(float(ch[0])/ch[1])","units":"","format":"%9.7f"},\
    {"name":"MUS","formula":"log(float(ch[1])/ch[2])","units":"","format":"%9.7f"},\
    {"name":"I1Norm","formula":"float(ch[1])/ch[0]","units":"","format":"%9.7e"},\
    {"name":"MUF","formula":"float(sum(ch[7:19]))/ch[0]","units":"","format":"%9.7e"},]

    cpt=pseudo_counter(masters=[cpt0,])
    #ct=pseudo_counter(masters=[cpt0,],slaves2arm2stop=[mca1,mca2,falcon],slaves=[], posts= ctPosts)
    ct=pseudo_counter(masters=[cpt0,],slaves2arm2stop=[mca1,mca2,falcon],slaves=[], posts=[])
    #ct=pseudo_counter(masters=[cpt0,],slaves2arm2stop=[falcon],slaves=[], posts=[])
except:
    print "Failure defining ct speclike_syntax command"
    print "Defaulting to cpt... ct=cpt... pysamba survival kit... is XIA dead?"
    ct=cpt

##--------------------------------------------------------------------------------------
##Define motors here
##--------------------------------------------------------------------------------------




##-------------------------------------------------------------------------------------
##Define Main Optic Components Here
##-------------------------------------------------------------------------------------


##--------------------------------------------------------------------------------------
##PSS
##--------------------------------------------------------------------------------------

##--------------------------------------------------------------------------------------
##VALVES
##--------------------------------------------------------------------------------------


###
### Import classes containing defaults pointing to objects declared above (e.g. dcm, cpt, ct, mca...)
###


######################################################################################
#        INCLUDE SCANS SECTION                                                #
######################################################################################



##########################################################################
# finally include the escan class to perform energy scans   !            #
##########################################################################


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


##############################
#    Changing the prompt     #
##############################
#try:
#    get_ipython().magic('config PromptManager.in_template=u\'\\w\\nSpeck: SEXAFS #\\#>\'')
#except:
#    pass
