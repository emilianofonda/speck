from __future__ import print_function
#Macro to reset the femtos amplifiers of SAMBA
def resetFEMTO():
    """Procedure to reset FEMTO amplifiers after computer reboot"""
    __ListOfFemtos=[I0_gain, I1_gain, I2_gain, I3_gain]
    for i in __ListOfFemtos:
        try:
            i.gainMode = False
            i.gainMode = True
            gain = i.gain
            i.gain = 3
            i.gain = 4
            i.gain = gain
            i.upperbwlimit = 1
            i.upperbwlimit = 0
            i.coupling = False
            i.coupling = True
        except:
            print("Failed on FEMTO %i"%(__ListOfFemtos.index(i)))
            pass
    return

