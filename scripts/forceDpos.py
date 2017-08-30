
def forceDpos():
    """
    This code is a test script to force all motor to initialise
    to present value. It can be used for hacking the ControlBox 
    new init condition. Use at your own risk, if you know what it is.
    __allmotors variable is used, but wa could be a nicer replacement."""
    for i in __allmotors:
        try:
            p = i.pos()
            i.on()
            Dpos(i,p)
        except:
            print "Nice try!"
        for i in __allmotors:
            try:
                i.init()
            except:
                pass
            try:
                i.state()
            except:
                pass
        return


