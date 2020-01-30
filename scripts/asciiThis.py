import xas
import dentist
import os
import tables

def asciiThis(forename, name="", e0= 0,mode="t", exclude=[]):
#Prepare lists
    sep = forename.rfind(os.sep)
    if sep <> -1:
        folder = forename[:forename.rfind(os.sep)]
        forename = forename[forename.rfind(os.sep)+1:]
    else:
        folder = ""
    ll = xas.makeFileList(folder=folder,prefix = forename, extension=".hdf",exclude=exclude)
    print ll
    if name == "":
        name = forename+"_average.txt"
    if not name.endswith(".txt"):
        name += ".txt"
#Make them ASCII
    corrupt=[]
    for i in ll:
        try:
            f = tables.open_file(folder + os.sep + i,"r")
            m=numpy.nan_to_num(array([
            f.root.post.energy.read(),f.root.data.encoder_rx1.Theta.read(),
            
            #f.root.post.XMU.read(),f.root.post.REF.read(),
            #f.root.post.XMU.read(),f.root.post.REF.read(),
            
            f.root.post.XMU.read(),f.root.post.FLUO.read(),f.root.post.REF.read(),
            f.root.post.FLUO_RAW.read(),
            
            f.root.data.cx2sai1.I0.read(),
            f.root.data.cx2sai1.I1.read(),
            f.root.data.cx2sai1.I2.read(),
            f.root.data.cx2sai1.I3.read(),
            
            ],"f"))
            f.close()
            savetxt(folder + os.sep + i[:-4]+".txt",m.transpose(),
            header = "Energy, Angle, XMU, FLUO, REFERENCE, FLUO_RAW, I0, I1, I2")
        except:
            corrupt.append(i)
    #Interpolate and average
    for i in corrupt: ll.remove(i)
    ll = [folder + os.sep + i[:-4]+".txt" for i in ll]
    #Interpolation suggested linear, slinear, quadratic or cubic
    xas.averageXASFiles(name, fileNames = ll, checkColumn=6, kind="slinear")
    try:
        os.system("cp %s ./ruche" % name)
    except:
        print "Cannot backup average to ruche"
    if e0 > 0 :
        dentist.dentist(folder + os.sep + name, e0=e0, mode=mode)
    return

