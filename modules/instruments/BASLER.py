#Macro to append the basler camera to the ct function 

##################################################
print "################################################################"
print "#                Performing BASLER  definition                 #" 
print "################################################################"


##--------------------------------------------------------------------------------------
##Define motors here
##--------------------------------------------------------------------------------------

try:
	import simple_camera
	basler=simple_camera.camera("d09-1-cx1/dt/vg2-basler")
	if not(basler in cpt.all):
		cpt=pseudo_counter(masters=cpt.masters,\
		slaves2arm2stop=cpt.slaves2arm2stop,\
		slaves2arm=cpt.slaves2arm,\
		slaves=cpt.slaves+[basler,])
		print
		print "BASLER loaded in cpt"
		print
	else:
		print "BASLER was already loaded in cpt!"
except:
	print RED+"basler"+RESET+"not responding or error initializing or loading in cpt"

try:	
	if not(basler in ct.all):
		ct=pseudo_counter(masters=ct.masters,\
		slaves2arm2stop=ct.slaves2arm2stop,\
		slaves2arm=ct.slaves2arm,\
		slaves=ct.slaves+[basler,])
		print
		print "BASLER loaded in ct"
		print
	else:
		print "BASLER was already loaded in ct!"
except:
	print RED+"basler"+RESET+"not responding or error initializing or loading in ct"

