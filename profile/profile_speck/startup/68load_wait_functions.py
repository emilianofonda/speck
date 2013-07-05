##
##  Functions to wait for a certain time, date, for the beam to come back...
##  This module has been changed by the user so it is in the user_config.py.
##
try:
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


