#def mv2energy(dest=None,backlash=15000.):
def mv2energy(dest=None,backlash=0):
    if dest == None:
        return dcm.pos()
    if dcm.pos()>dest and backlash != 0:
        mv(dcm,dest)
        mvr(bender,backlash)
        mvr(bender,-backlash)
    else:
        mv(dcm,dest)
    return dcm.pos()
