from __future__ import print_function
import tables, numpy

class dataBlock:
    """

    Used in conjunction with pseudo_counter when HDF files are used 

    Example of working input follows. 

    When using addresses in a HDF file the [:] must be used in formulas to point to values and not to pointers

    XAS_dictionary={
        "addresses":{
            "I_zero_zero":"sai1.channel00"
            },
        "constants":{
            "I0":"10.",
            "I1":"20.",
            },
        "formulas":{
            "XMU":"numpy.log(I0/I1)",
            "XMU00":"numpy.log(I_zero_zero[:]/I1)"
            },
    }

    Only formulas will be saved in the HDF file.

    """
    def __init__(self, dictionary, HDFfile=None,domain="post", HDFfilters=tables.Filters(complevel = 1, complib='zlib')):
        self.dictionary = dictionary
        self.computed =  {}
        self.HDFfile = HDFfile
        self.HDFfilters = HDFfilters
        self.domain = domain
        return

    def evaluate(self):
        __IPy = get_ipython()
        try:
            outGroup = self.HDFfile.getNode("/" + self.domain )
        except:
            self.HDFfile.createGroup("/", self.domain)
            outGroup = self.HDFfile.getNode("/" + self.domain )
        #self.computed["HDFfile"] = self.HDFfile
        for i in self.dictionary["addresses"].keys():
            try:
                self.computed[i] = eval("self.HDFfile.root.data." + self.dictionary["addresses"][i])
            except Exception as tmp:
                print("post calculation error: %s = %s"%(i,"self.HDFfile.root.data." + self.dictionary["addresses"][i]))
                print(tmp)
        for i in self.dictionary["constants"].keys():
            try:
                self.computed[i] = eval(self.dictionary["constants"][i])
            except Exception as tmp:
                print("post calculation error: %s = %s"%(i,self.dictionary["constants"][i]))
                print(tmp)
        glob = __IPy.user_ns
        for i in self.dictionary["formulas"].keys():
            try:
                value = numpy.array(eval(self.dictionary["formulas"][i],glob,self.computed))
                #print(i,value)
                #value = numpy.array(eval(self.dictionary["formulas"][i],globals(),self.computed))
                self.HDFfile.createCArray(outGroup, i , title = i,\
                #shape = numpy.shape(value), atom = tables.Atom.from_dtype(value.dtype))
                shape = numpy.shape(value), atom = tables.Atom.from_dtype(value.dtype), filters = self.HDFfilters)
                outNode = self.HDFfile.getNode("/" + self.domain +"/" + i)
                outNode[:] = value
                del value
            except Exception as tmp:
                print("post calculation error: %s = %s"%(i, self.dictionary["formulas"][i]))
                print(tmp.message)
        try:
            del outNode, c
        except:
            pass
        return

def test():
    XAS_dictionary={
        "addresses":{
            "I_zero_zero":"sai1.channel00"
            },
        "constants":{
            "I0":"10.",
            "I1":"20.",
            },
        "formulas":{
            "XMU":"numpy.log(I0/I1)",
            "XMU00":"numpy.log(I_zero_zero[:]/I1)"
            },
    }
    dada = dataBlock(XAS_dictionary)
    dada.evaluate()
    print(dada.computed)
    return


   
