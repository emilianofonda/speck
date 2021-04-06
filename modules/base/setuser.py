#!/usr/bin/ipython
import os,sys,string,time
#from ascan import filename2ruche
#from IPython.core import ipapi
from IPython.core.getipython import get_ipython

#Dangerous legacy definitions
IPy = get_ipython()
__Default_Data_Folder = IPy.user_ns["__SPECK_CONFIG"]['TEMPORARY_HOME'] #os.getenv("SPECK_DATA_FOLDER")
__Default_Backup_Folder = IPy.user_ns["__SPECK_CONFIG"]['DATA_FOLDER'] #os.getenv("SPECK_DATA_FOLDER")

def backup():
    IPy = get_ipython()
    print("\n"*1)
    print("Executing Backup.")
    print("\n"*1)
    try:
        __Default_Backup_Folder = IPy.user_ns["__SPECK_CONFIG"]['DATA_FOLDER']
        #os.getenv("SPECK_DATA_FOLDER")
        __Default_Data_Folder = IPy.user_ns["__SPECK_CONFIG"]['TEMPORARY_HOME']
        #os.getenv("SPECK_BACKUP_FOLDER")
        if __Default_Backup_Folder == "":
           raise Exception("No Backup Folder defined! GoodBye")
        currentDataFolder=os.path.realpath(os.getcwd())
        print("Data Folder is :",currentDataFolder)
        if currentDataFolder.startswith(__Default_Data_Folder) and len(currentDataFolder.split(os.sep)) > len(__Default_Data_Folder.split(os.sep)):
            currentBackupFolder=__Default_Backup_Folder+"/"+\
            currentDataFolder.lstrip(__Default_Data_Folder.rstrip("/"))
            cbf=currentBackupFolder
            currentBackupFolder=cbf[:cbf.rstrip("/").rfind("/")]
        else:
            print("No backup!")
            raise Exception("No backup out of predefined data folders")
        print("Backup Folder is :",currentBackupFolder)
    except (KeyboardInterrupt,SystemExit) as tmp:
        print("Backup halted on user request")
        raise tmp
    try:
        #command="rsync --ignore-existing -auv --temp-dir=/tmp '"+currentDataFolder+"' '"+currentBackupFolder+"'"
        command="rsync -auv --temp-dir=/tmp '"+currentDataFolder+"' '"+currentBackupFolder+"'"
        os.system(command)
    except (KeyboardInterrupt,SystemExit) as tmp:
        print("Backup halted on user request")
        raise tmp
    


def setuser(name=None):
    IPy = get_ipython()
    try:
        ll=file(IPy.user_ns["__SPECK_CONFIG"]['SPECK_FOLDER'] + "/config/user.cfg","r").readlines()
    except:
        print "Missing user.cfg file in:",IPy.user_ns["__SPECK_CONFIG"]['SPECK_FOLDER'],"/config/"
        cfgfile=file(IPy.user_ns["__SPECK_CONFIG"]['SPECK_FOLDER'] + "/config/user.cfg","w")
        cfgfile.close()
    
    cfg={}
    for i in ll:
        _i = i.strip().split("=")
        cfg[_i[0]] = _i[1]
    
    if name == None:
        if "FOLDER" in cfg.keys():
            os.chdir( IPy.user_ns["__SPECK_CONFIG"]['TEMPORARY_HOME']+ os.sep + cfg["FOLDER"])
            #Store information in shell SPECK dictionary
            try:
                IPy.user_ns["__SPECK_CONFIG"]["USER_FOLDER"]= IPy.user_ns["__SPECK_CONFIG"]['TEMPORARY_HOME']+ os.sep +cfg["FOLDER"]
            except Exception as tmp:
                print(tmp)

#Start logging in speckle session
            try:
                pass
                IPy.magic("logstop")
                IPy.magic("logstart -ort %s global"%(os.getcwd() + os.sep + "logBook.txt"))
            except:
                pass
        else:
            print("setuser: No previous user folder defined!")
            return
    else:
        try:
            setuser(name=None)
        except:
            pass
        try:
            #os.system("screen -X log off")
            IPy.magic("logstop")
        except Exception as tmp:
            print(tmp)
        #After stoppin' log I perform a backup of current folder and then we move to the new one.
        try:
            backup()
        except Exception as tmp:
            print(tmp)
        
        cfg["NAME"] = name
        cfg["FOLDER"] = "%4i" % time.localtime()[0] +os.sep + "%4i%02i%02i" % time.localtime()[0:3] + "_%s" % name
        

        print "New folder is: " + cfg["FOLDER"]
        try:
            os.makedirs(IPy.user_ns["__SPECK_CONFIG"]['DATA_FOLDER']+ os.sep +cfg["FOLDER"])
        except Exception, tmp:
            print tmp
        try:
            os.makedirs(IPy.user_ns["__SPECK_CONFIG"]['DATA_FOLDER'] + os.sep +cfg["FOLDER"])
        except Exception, tmp:
            print tmp
        os.chdir(IPy.user_ns["__SPECK_CONFIG"]['TEMPORARY_HOME'] + os.sep +cfg["FOLDER"])
        #Store information in shell SPECK dictionary
        if type(IPy.user_global_ns["__SPECK_CONFIG"]) == dict:
            IPy.user_global_ns["__SPECK_CONFIG"]["USER_FOLDER"]= IPy.user_ns["__SPECK_CONFIG"]['TEMPORARY_HOME']+ os.sep +cfg["FOLDER"]
        else:
            raise Exception("__SPECK_CONFIG global variable is not a dictionary.")
       
        #Store information in config file
        cfgfile=file(IPy.user_ns["__SPECK_CONFIG"]['SPECK_FOLDER'] + "/config/user.cfg","w")
        for i in cfg.keys():
            cfgfile.write("%s=%s\n" % (i,cfg[i]))
        cfgfile.close()
        try:
            IPy.magic("logstart -ort %s global"%(os.getcwd() + os.sep + "logBook.txt"))
        except Exception, tmp:
            print tmp
            pass
    return


