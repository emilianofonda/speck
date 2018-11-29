import xas
import dentist
import os

def averageThis(forename, name="", delta = 0.4, e0= 0,mode="t", exclude=[]):
    """averageThis is used to average scan text files.
    The series of scans have a common name forename as specified in the ecscan command
    if you want to change the output name, specify it using name="ThisIsTheNewName"
    delta is the energy step for the interpolation grid
    e0 is used for plotting as well as the mode that can be:
    f for fluorescence
    t for transmission
    s for standard
    the exclude is a list of file numbers you do not want to use.
    exclude = [100,103,104]
    or exclude = [10,19] + range(100,150)
    these are quite useful syntaxes.
    """
    ll = xas.makeFileList(prefix = forename,exclude=exclude)
    print ll
    if name == "":
        name = forename+"_average.txt"
    if not name.endswith(".txt"):
        name += ".txt"
    xas.mergeXASFiles(name, fileNames = ll, delta=delta, checkColumn=6)
    try:
        os.system("cp %s ./ruche" % name)
    except:
        print "Cannot backup average to ruche"
    if e0 > 0 :
        dentist.dentist(name, e0=e0, mode=mode)
    return

