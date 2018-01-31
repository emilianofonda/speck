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


#dxmap: configured for Bruker SDD of Lucia
try:
    mca1=None
    mca2=dxmap("d09-1-cx1/dt/dtc-mca_xmap.2",FTPclient="d09-1-c00/ca/ftpclientxia.2",FTPserver="d09-1-c00/ca/ftpserverxia.2",spoolMountPoint="/nfs/srv5/spool1/xia2")
    print GREEN+"mca2 --> DxMap card"+RESET
except Exception, tmp:
    print tmp
    print RED+"Failure defining dxmap: d09-1-cx1/dt/dtc-mca_xmap.2"+RESET

#ct
try:
    ctPosts=[\
    {"name":"MUX","formula":"log(float(ch[0])/ch[1])","units":"","format":"%9.7f"},\
    {"name":"MUS","formula":"log(float(ch[1])/ch[2])","units":"","format":"%9.7f"},\
    {"name":"I1Norm","formula":"float(ch[1])/ch[0]","units":"","format":"%9.7e"},\
    {"name":"MUF","formula":"float(sum(ch[7:19]))/ch[0]","units":"","format":"%9.7e"},]

    cpt=pseudo_counter(masters=[cpt0,])
    ct=pseudo_counter(masters=[cpt0,],slaves2arm2stop=[mca2,],slaves=[], posts= ctPosts)
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

#Replace the counter for the tuning with the new one
dcm.counter=cpt

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
