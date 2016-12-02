#from modules.base.moveable import sensor, moveable
try:
    forno = sensor("D09-1-CX1/EX/eur2408i.1","temperature")
    try:
        __idiot = forno.pos()
    except:
        print BOLD + "forno: not available"
        del(forno)
    forno_set = moveable("d09-1-cx1/ex/eur2408_ctrl.1","temperature", moving_state=DevState.RUNNING, deadtime = 0.1, timeout = 1)
    try:
        __idiot = forno_set.pos()
    except:
        print BOLD + "forno_set: not available"
        del(forno_set)
    forno_ramp = moveable("d09-1-cx1/ex/eur2408_ctrl.1","ramptime", moving_state=None, deadtime = 1)
    try:
        __idiot = forno_ramp.pos()
    except:
        print BOLD + "forno_ramp: not available"
        del(forno_ramp)
    #print RED + "Use forno to read sample temperature and forno_set to set and read the furnace set-point\n" + RESET
except Exception, tmp:
    print RED+"Error loading forno and forno_set\n" + RESET
    print tmp


