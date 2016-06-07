#!/usr/bin/ipython
import os,sys,string,time
from ascan import filename2ruche
from IPython.core import ipapi

#dn = os.path.dirname(os.path.realpath(__file__))
#dn=dn[:dn.rfind(os.sep)]

__Default_Data_Folder = os.getenv("SPECK_DATA_FOLDER")
IPy = ipapi.get()

def setuser(name=None):
    try:
        ll=file(os.getenv("SPECK") + "/config/user.cfg","r").readlines()
    except:
        print "Missing user.cfg file in:",dn,"/config/"
        cfgfile=file(os.getenv("SPECK") + "/config/user.cfg","w")
        cfgfile.close()
    
    cfg={}
    for i in ll:
        _i = i.strip().split("=")
        cfg[_i[0]] = _i[1]
    
    if name == None:
        if "FOLDER" in cfg.keys():
            os.chdir(__Default_Data_Folder + os.sep + cfg["FOLDER"])
            #Start logging in speckle session
            try:
                pass
                #os.system("screen -X log off")
                #os.system("screen -X logfile %s" % (os.getcwd() + os.sep + "speckle.log"))
                #os.system("screen -X log on")
                IPy.magic("logstop")
                IPy.magic("logstart -ort logBook.txt")
            except:
                pass
        else:
            print "setuser: No previous user folder defined!"
            return
    else:
        print "New folder is: " + __Default_Data_Folder + os.sep +"%4i" % time.localtime()[0] +os.sep + "%4i%02i%02i" % time.localtime()[0:3] + "_%s" % name
        try:
            os.makedirs(__Default_Data_Folder + os.sep +"%4i" % time.localtime()[0] + os.sep + "%4i%02i%02i" % time.localtime()[0:3] + "_%s" % name)
        except Exception, tmp:
            print tmp
        os.chdir(__Default_Data_Folder + os.sep +"%4i" % time.localtime()[0] + os.sep + "%4i%02i%02i" % time.localtime()[0:3] + "_%s" % name)
        cfg["NAME"] = name
        cfg["FOLDER"] = "%4i" % time.localtime()[0] +os.sep + "%4i%02i%02i" % time.localtime()[0:3] + "_%s" % name
        cfgfile=file(os.getenv("SPECK") + "/config/user.cfg","w")
        for i in cfg.keys():
            cfgfile.write("%s=%s\n" % (i,cfg[i]))
        cfgfile.close()
        try:
            pass
            #os.system("screen -X log off")
            #os.system("screen -X logfile %s" % (os.getcwd() + os.sep + "speckle.log"))
            #os.system("screen -X log on")
            IPy.magic("logstop")
            IPy.magic("logstart -ort logBook.txt")
        except Exception, tmp:
            print tmp
            pass
        try:
            os.makedirs(filename2ruche(""))
            os.symlink(filename2ruche(""),"./ruche")
        except:
            print "CANNOT MAKE RUCHE FOLDER: "+filename2ruche("")
    return


