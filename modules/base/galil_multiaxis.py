from __future__ import print_function
from __future__ import division
#from motor_class import wait_motor
from builtins import range
from builtins import object
from past.utils import old_div
from spec_syntax import wait_motor
from PyTango import DeviceProxy, DevState, DevFailed,Database
from time import sleep, time, asctime
from numpy import mod, reshape, sort, inf, nan, all, any

class galil_axisgroup(object):
    """This class is used to speed up multiaxis movements on the Galil 8 axis Controller. 
    The SOLEIL microcode must be installed in the Galil Box.
    The microcode variables YA,YB,YC are read and the low level commands PAx;BGx;STx
    Must be used with a proper initialisation and only when is vital to reduce the time consumed
    in the communication.
    To init the class you should specify a list containing the motor instances
    
    The encoder motor ratio (emr) of motor x is obtained by:
        MG _YCx/(_YAE*_YBE)
    The movement is calculated in this way:
        DirectMotorCoeff=dmc=emr/AxisPositionRatio
        DeltaMotorSteps=DeltaPositionRequested*dmc
    Then we send the command:
        PRx=DeltaMotorSteps
        """
    def __init__(self,mot_list,deadtime=0.025,timeout=0.15, settlingTime=0):
        self.TANGODataBase=Database()
        self.deadtime = deadtime
        self.timeout = timeout
        self.settlingTime = settlingTime
        self.mot_dict = {}
        self.cb_dict = {}
        for i in mot_list:
            self.mot_dict[i] = self.retrieve_motor_info(i)
            box=self.mot_dict[i]["box"]
            if not box in list(self.cb_dict.keys()):
                self.cb_dict[box] = {"DP":DeviceProxy(box),"axis":self.mot_dict[i]["AxisNumber"]}
            else:
                self.cb_dict[box]["axis"] += self.mot_dict[i]["AxisNumber"]
        for i in self.cb_dict:
            self.cb_dict[i]["stop all"] = "ST" + self.cb_dict[i]["axis"]
        return

    def init(self):
        """Use this function to reload the motor config, attribute limits included"""
        for i in self.mot_dict:
            self.mot_dict[i] = self.retrieve_motor_info(i)
        return

    def pos(self,*args):
        #Put arguments in shape
        l_args = len(args)
        if len(args) == 0:
            return None
            #return map(lambda x: x.pos(), self.mot_dict)
        if mod(l_args,2) != 0:
            raise Exception("galil_axisgroup: Bad number of arguments")
        if DevState.MOVING in [x.state() for x in args[0::2]]:
            raise Exception("galil_axisgroup: One of the axis is already moving")
        mots=reshape(args, [old_div(l_args, 2), 2])
#       if DevState.MOVING in map(lambda(x): x.state(),args[0::2]):
#           for i in range(2):
#               sleep(0.1)
#               if not DevState.MOVING in map(lambda(x): x.state(),args[0::2]):
#                   break
#           if i >=2: 
#               raise Exception("galil_axisgroup: One of the axis is already moving")
#       mots=reshape(args,[l_args/2,2])
        #Backlash list:
        mots2move=[]
        mots_backlash=[]
        for i in mots:
            if abs(i[0].pos() - i[1]) >= self.mot_dict[i[0]]["accuracy"] and ((i[1] - i[0].pos()) * self.mot_dict[i[0]]["backlash"]) < 0 :
                mots2move.append([i[0], i[1]-self.mot_dict[i[0]]["backlash"]])
                mots_backlash.append([i[0], i[1]])
            elif abs(i[0].pos() - i[1]) >= self.mot_dict[i[0]]["accuracy"]:
                mots2move.append([i[0], i[1]])
        if mots2move != []:
            #print mots2move
            tmp=self.pos_low_level(mots2move)
        if mots_backlash !=[]:
            #print mots_backlash
            return self.pos_low_level(mots_backlash)
        else:
            return None
        
    def pos_low_level(self,mots):
        """The galil_axisgroup is used to move motors over several control boxes
        in the most efficient way. This flexibility is paid by the following algorithm
        complexity. Time consumed in the axis groups calculation should be negligible
        in most common cases. GalilAxis attribute limits are verified."""
        ##Put arguments in shape
        #l_args=len(args)
        #if mod(l_args,2)<>0:
        #    raise Exception("galil_axisgroup: Bad number of arguments")
        #tt0=time()
        if DevState.MOVING in [x[0].state() for x in mots]:
            raise Exception("galil_axisgroup: One of the axis is already moving")
        #mots=reshape(args,[l_args/2,2])
        #Group motors by control box in a dictionary of CB deviceproxies pointing to tuples
        #containing axis number and deltasteps per motor
        box_list={}
        box_list=box_list.fromkeys(list(self.cb_dict.keys()),[])
        for i in mots:    
            if i[0] not in list(self.mot_dict.keys()):
                raise Exception("galil_axisgroup: you tried to move a motor not in galil_axisgroup")
            if i[1]>self.mot_dict[i[0]]["max"] or i[1]<self.mot_dict[i[0]]["min"]:
                print("Motor ",i[0].label, " attempt to move out of bounds!")
                raise Exception("galil_axisgroup: you tried to move a motor out of its bounds")
            box = self.mot_dict[i[0]]["box"]
            box_list[box] = box_list[box] + \
            [[self.mot_dict[i[0]]["AxisNumber"], (i[1]-i[0].pos())*self.mot_dict[i[0]]["dmc"]]]
        #print "Printing box_list"
        #print box_list
        #print "-------------------"
        #Send asynchronous commands per control box
        #This is one of the two critical points where motors should be stopped by ctrl-c
        try:
            for i in box_list:
                cb_pr_str = ""
                cb_bg_str = "BG"
                if box_list[i]!=[]:
                    for j in box_list[i]:
                        cb_pr_str+="PR"+j[0]+"=%i;"%(int(j[1]))
                        cb_bg_str+=j[0]
                    #execute low level command: you should test if async is necessary or not
                    #print self.cb_dict[i],cb_pr_str+cb_bg_str
                    self.LowLevel(self.cb_dict[i]["DP"], cb_pr_str + cb_bg_str, async=True)
        except KeyboardInterrupt as tmp:
            print("KeyboardInterrupt Exception catched in galil_axisgroup.pos: stopping motors.")
            self.stop()
            raise tmp
        except Exception as tmp:
            raise tmp
        #Wait movement end
        self.wait([x[0] for x in mots])
        #workaround: additional SettlingTime
        sleep(self.settlingTime)
        #Return actual positions
        #print "Movement takes:",time()-tt0
        return [x[0].pos() for x in mots]

    def stop(self):
        """Stop all axis of the group by a low level command.""" 
        for i in self.cb_dict:
            self.LowLevel(self.cb_dict[i]["DP"], self.cb_dict[i]["stop all"])
        return

    def wait(self,mot_list):
        """Differs from wait_motor since this calls the galil_axisgroup stop when an exception is raised"""
        #tt0=time()
        try:
            #Wait for motors to start
#<<<<<<< HEAD
#           timeOut = time() + self.timeout
#           nomovement = True
#           while nomovement and time() < timeOut:
#               for i in mot_list:
#                   if i.state() == DevState.MOVING: 
#                       nomovement = False
#                       break
#               if nomovement and self.deadtime > 0:
#                   sleep(self.deadtime)
#           #Wait for motors to stop
#           lMots = list(mot_list)
#           tEnd = time()
#           while len(lMots) >= 0:
#               for i in range(len(lMots)):
#                   if i.state() <> DevState.MOVING:
#                       tEnd = time() + self.mot_dict[lMots[i]]["SettlingTime"]
#                       __tmp = lMots.pop(i)
#                       break
#           sleep(max(0., tEnd - time()))
#======
            timeOut = time() + self.timeout
            nomovement=True
            while time() < timeOut and nomovement:
                if any([x.state() == DevState.MOVING for x in mot_list]):
                    break
                if self.deadtime > 0:
                    sleep(self.deadtime)
            #Wait for motors to stop
            i=0
            l=len(mot_list)
            for retries in range(3):
                while True:
                    if all([x.state() != DevState.MOVING for x in mot_list]):
                        break
                    #if mot_list[i].state() <> DevState.MOVING:
                    #    i += 1
                    #    if i == len(mot_list):
                    #        break
                    if self.deadtime > 0:
                        sleep(self.deadtime)
                i=0
            #print "Waited for :",time()-tt0
        except KeyboardInterrupt as tmp:
            print("KeyboardInterrupt Exception catched in galil_axisgroup.wait: stopping motors.")
            self.stop()
            raise tmp
        except Exception as tmp:
            print("Exception catched in galil_axisgroup.wait")
            self.stop()
            raise tmp

    def show(self):
        #Should return a list, now just print out strings for debug
        for i in self.mot_dict:
            print(i.label," is at ",i.pos()," and is connected on axis ",\
            self.mot_dict[i]["AxisNumber"]," of ",self.mot_dict[i]["box"])
            print("---------------- O ----------------")
        return

    def LowLevel(self,cb_DP,command_string,async=False):
        """Return outcome of command or callback depending on the synch or asynch nature of the request"""
        #Command_inout shortcut
        if not(async):
            return cb_DP.command_inout("ExecLowLevelCmd",command_string)
        else:
            return cb_DP.command_inout_asynch("ExecLowLevelCmd",command_string)
    
    def retrieve_motor_info(self,mot):
        mot_server_id = mot.DP.info().server_id
        cb_name = self.TANGODataBase.get_device_class_list(mot_server_id)
        cb_name = cb_name[list(cb_name).index('ControlBox') - 1]
        cb_DP = DeviceProxy(cb_name)
        mot_dict = {"box": cb_name}
        for i in ["AxisPositionRatio","AxisNumber"]:
            mot_dict[i] = mot.DP.get_property([i,])[i][0]
        try:
            mot_dict["SettlingTime"] = mot.DP.get_property(["SettlingTime",])["SettlingTime"][0]
        except:
            mot_dict["SettlingTime"] = 0.0
        AN = mot_dict["AxisNumber"]
        #Calculate ratios
        mot_dict["emr"] = float(self.LowLevel(cb_DP, "MG _YC" + AN + "/(_YA" + AN + "*_YB" + AN + ")").split()[0])
        mot_dict["dmc"] = old_div(1, (mot_dict["emr"] * float(mot_dict["AxisPositionRatio"])))
        #Obtain user position limits
        try: 
            mot_dict["min"] = float(mot.DP.get_attribute_config("position").min_value)
        except:
            #print "motor ",mot.label," has no lower bound!"
            mot_dict["min"] = -inf
        try:
            mot_dict["max"] = float(mot.DP.get_attribute_config("position").max_value)
        except:
            #print "motor ",mot.label," has no higher bound!"
            mot_dict["max"] = inf
        #
        mot_dict["backlash"] = mot.DP.read_attribute("backlash").value
        mot_dict["accuracy"] = mot.DP.read_attribute("accuracy").value
        return mot_dict
    

