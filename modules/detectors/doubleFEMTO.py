from __future__ import print_function
from moveable import moveable

class doubleFEMTO:
    def __init__(self, mov1, mov2):
        self.mov1 = mov1
        self.mov2 = mov2
        self.DP = mov1.DP
        self.label = mov1.label 
        self.deadtime = mov1.deadtime
        self.timeout = mov1.timeout
        self.ac = mov1.ac
        if self.ac == "":
            self.ac = "%g"
        return

    def __repr__(self):
        return self.mov1.__repr__() + self.mov2.__repr__()
        
    def __call__(self,x=None):
        print(self.__repr__())
        return self.pos()

    def pos(self,x=None,wait=True):
        self.mov1.pos(x, wait)
        self.mov2.pos(x, wait)
        return self.mov1.pos()
        
    def lm(self):
        print("MOV1:", self.mov1.lm())
        print("MOV2:", self.mov2.lm())
        return self.mov1.lm()

    def lmset(self, min_value = None , max_value = None):
        self.mov1.lmset(min_value, max_value)
        self.mov2.lmset(min_value, max_value)
        return self.lm()

    def go(self,x=None,wait=False):
        return self.pos(x,wait)

    def stop(self):
        return self.state()

    def on(self):
        return self.state()
        
    def off(self):
        return self.state()

    def state(self):
        s = self.mov1.state() or self.mov2.state()
        return s

