def mv2energy(dest=None,backlash=10000.):
    if dest == None:
        return dcm.pos()
    if dcm.pos()>dest:
        mv(dcm,dest)
        mvr(bender,backlash)
        mvr(bender,-backlash)
    else:
        mv(dcm,dest)
    return dcm.pos()
