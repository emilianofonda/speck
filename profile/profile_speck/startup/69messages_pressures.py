#
#       This part is really obsolete use Globalscreen for this
#

#This command is very old and rewritten just for commodity. Use GlobalScreen instead
def GetPressures():
    for i in __vacuum:
        print BOLD+i+RESET+": "+eval(i).__repr__()
    return 

try:
    try:
        __plc_msg=DeviceProxy("d09-1-c00/vi/plc.1-msg")
    except:
        pass
    try:
        __machinestatus=DeviceProxy("ans/ca/machinestatus")
    except:
        pass
    def messages():
        sleep(1.)
        print "Messages :\n"
        print "Date/Time:",asctime()
        print "From Machine:"
        for i in range(2):
            try: 
                print "operatorMessage :",__machinestatus.read_attribute("operatorMessage").value
                print "current         :",__machinestatus.read_attribute("current").value
                print "fillingMode     :",__machinestatus.read_attribute("fillingMode").value
                print "functionMode    :",__machinestatus.read_attribute("functionMode").value
                print "message         :",__machinestatus.read_attribute("message").value
                print "operatorMessage :",__machinestatus.read_attribute("operatorMessage").value
                print "isBeamUsable    :",__machinestatus.read_attribute("isBeamUsable").value
                print ""
                print "FE/obxg/obx     :",
                for i in [FE,obxg,obx]:
                    try:
                        print i.state(),"/",
                    except:
                        print "Unknown ",
                print "\n"
                break
            except: 
                print "Error retrieving machine data."
        print "\nFrom PLC:"
        try:
            tmp=__plc_msg.command_inout("Status")
            print tmp
            #print tmp[0:tmp.find("INTERLOCKS DISPARUS")]
        except:
            print "Cannot get message"
        return
    #print "\n"
    #print "#"*70
    #print "Type messages to get information on the machine state and PLC interlocks"
    #print "#"*70
    #print "\n"
    

except:
    print "Error in PLC message retrieval... no messages() defined."



