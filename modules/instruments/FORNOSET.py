#from modules.base.moveable import sensor, moveable

try:
    forno_set = moveable("d09-1-cx1/ex/eur2408_ctrl.1","temperature", moving_state=DevState.RUNNING, deadtime = 0.1, timeout = 1)
    print "forno_set: OK"
except Exception, tmp:
    print tmp

try:    
    forno_ramp = moveable("d09-1-cx1/ex/eur2408_ctrl.1","ramptime", moving_state=None, deadtime = 1)
    print "forno_ramp: OK"
except Exception, tmp:
    print tmp


