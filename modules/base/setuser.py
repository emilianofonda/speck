#!/usr/bin/ipython
import os,sys,string,time
from ascan import filename2ruche
from IPython.core import ipapi

#dn = os.path.dirname(os.path.realpath(__file__))
#dn=dn[:dn.rfind(os.sep)]

__Default_Data_Folder = os.getenv("SPECK_DATA_FOLDER")
IPy = ipapi.get()

def backup():
    print "\n"*3
    print "WARNING: This backup should be executed only at the END of your experiment! (or not repeated often!)"
    print "\n"*3
    try:
        __Default_Data_Folder = os.getenv("SPECK_DATA_FOLDER")
        __Default_Backup_Folder = os.getenv("SPECK_BACKUP_FOLDER")
        if __Default_Backup_Folder == "":
            print "NO BACKUP: no backup folder defined."
            raise Exception("GoodBye")
        currentDataFolder=os.path.realpath(os.getcwd())
        print "Data Folder is :",currentDataFolder
        if currentDataFolder.startswith(__Default_Data_Folder) and len(currentDataFolder.split(os.sep)) > len(__Default_Data_Folder.split(os.sep)):
            currentBackupFolder=__Default_Backup_Folder+"/"+\
            currentDataFolder.lstrip(__Default_Data_Folder.rstrip("/"))
            cbf=currentBackupFolder
            currentBackupFolder=cbf[:cbf.rstrip("/").rfind("/")]
        else:
            print "No backup!"
            raise Exception("No backup out of predefined data folders")
        print "Backup Folder is :",currentBackupFolder
    except (KeyboardInterrupt,SystemExit), tmp:
        print "Backup halted on user request"
        raise tmp
    try:
        #command="rsync --ignore-existing -auv --temp-dir=/tmp '"+currentDataFolder+"' '"+currentBackupFolder+"'"
        command="rsync -auv --temp-dir=/tmp '"+currentDataFolder+"' '"+currentBackupFolder+"'"
        os.system(command)
    except (KeyboardInterrupt,SystemExit), tmp:
        print "Backup halted on user request"
        raise tmp
    


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
                #os.system("screen -X logfile %s" % (os.getcwd() + os.sep + "logScreen.txt"))
                #os.system("screen -X log on")
                IPy.magic("logstop")
                IPy.magic("logstart -ort %s global"%(os.getcwd() + os.sep + "logBook.txt"))
            except:
                pass
        else:
            print "setuser: No previous user folder defined!"
            return
    else:
        try:
            #os.system("screen -X log off")
            IPy.magic("logstop")
        except:
            pass
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
            #os.system("screen -X logfile %s" % (os.getcwd() + os.sep + "logScreen.log"))
            #os.system("screen -X log on")
            IPy.magic("logstart -ort %s global"%(os.getcwd() + os.sep + "logBook.txt"))
        except Exception, tmp:
            print tmp
            pass
        try:
            os.makedirs(filename2ruche(""))
            os.symlink(filename2ruche(""),"./ruche")
        except:
            print "CANNOT MAKE RUCHE FOLDER: "+filename2ruche("")
    return


