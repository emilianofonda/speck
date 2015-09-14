#Macro to define the PI Hexapode instrument:

##################################################
print "################################################################"
print "#                Performing PI HEXA definitions                #" 
print "################################################################"


##--------------------------------------------------------------------------------------
##Define motors here
##--------------------------------------------------------------------------------------

try:

       hx=moveable("d09-1-cx1/ex/hexa.1","x")
       hy=moveable("d09-1-cx1/ex/hexa.1","y")
       hz=moveable("d09-1-cx1/ex/hexa.1","z")
       hu=moveable("d09-1-cx1/ex/hexa.1","u")
       hv=moveable("d09-1-cx1/ex/hexa.1","v")
       hw=moveable("d09-1-cx1/ex/hexa.1","w")
except:
       print RED+"Hexapode"+RESET+"not responding or error initializing moveable classes"
       pass

print
print "HEXAPODE PI loaded"
print "New motors: hu,hv,hw for rotations hx,hy,hz for translations" 
print

