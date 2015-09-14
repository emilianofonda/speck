#Macro to define the MARCCD instrument:

##################################################
print "################################################################"
print "#                Performing MARCCD  definitions                #" 
print "################################################################"


##--------------------------------------------------------------------------------------
##Define motors here
##--------------------------------------------------------------------------------------

try:
       import simple_MARCCD
       marccd = simple_MARCCD.ccdmar("d09-1/dt/marccd.1","image")
       snap_marccd = marccd.snap
       print "\nMARCCD loaded as marccd\n"
except Exception, tmp:
       print tmp
       pass

