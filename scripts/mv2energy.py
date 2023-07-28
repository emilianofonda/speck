def mv2energy(dest=None):
    if dest == None:
        return dcm.pos()
    if dcm.pos()>dest:
        mv(dcm,dest)
        mvr(bender,30e3)
        mvr(bender,-30e3)
    else:
        mv(dcm,dest)
    return dcm.pos()
