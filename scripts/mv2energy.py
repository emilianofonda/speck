def mv2energy(dest):
    if dcm.pos()>dest:
        mv(dcm,dest)
        mvr(bender,30e3)
        mvr(bender,-30e3)
    else:
        mv(dcm,dest)
    return dcm.pos()
