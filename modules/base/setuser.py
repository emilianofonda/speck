#!/usr/bin/ipython
from __future__ import print_function
import os,sys,string,time
import subprocess
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
        Backup_Folder = IPy.user_ns["__SPECK_CONFIG"]['USER_DATA']
        
        Data_Folder = IPy.user_ns["__SPECK_CONFIG"]['USER_HOME']
        
        if Backup_Folder == "":
           raise Exception("No Backup Folder defined! GoodBye")
        command="rsync -uv --temp-dir=/tmp '" + Data_Folder + "' '" + Backup_Folder + "'"
        os.system(command)
    except (KeyboardInterrupt,SystemExit) as tmp:
        print("Backup halted on user request")
        raise tmp


def check_project(project_number=""):

    information = {}
    keys = ["title","manager","participants"]
    def match(s,k):
        return True in [i+":" in s for i in k]
    
    if project_number == "":
        return False
    
    result = subprocess.run([r'ldapsearch',r'-x','-s','sub','cn=%s'%project_number],stdout=subprocess.PIPE)
    ll=str(result.stdout)
    #Locate numEntries
    if not("# numEntries" in ll):
            return False
    #Locate title
    i0 = ll.index("title:")+6
    i1 = ll[i0:].find("\\n\\n")
    information["title"]=ll[i0:i1+i0].replace("\\n ","")
    #Locate manager
    i0 = ll.index("manager:")+8
    i1 = ll[i0:].find("\\n")
    information["manager"]=ll[i0:i1+i0][ll[i0:i1+i0].find("uid=")+4:].replace("\\n","")

    #return information
    
    keys=['o',"displayName","homePostalAddress"]
    result = subprocess.run([r'ldapsearch',r'-x','-s','sub','cn=%s'%information["manager"]],stdout=subprocess.PIPE)
    ll=str(result.stdout)
    print(ll)
    if not("numEntries" in ll):
        return information
    for i in keys:
        i0 = ll.find("\\n"+i+":")+len(i)+4
        d0 = ll[i0:].find("\\n")
        information[i] = ll[i0:i0+d0].replace("\\n","").strip()
    
    information["manager"] = information["displayName"]
    information["institute"] = information["o"]
    for i in ["o","displayName","numEntries"]:
        try:
            tmp = information.pop(i)
        except:
            pass
    result = subprocess.run([r'ldapsearch',r'-x','-s','sub','cn=g%s'%project_number],stdout=subprocess.PIPE)
    ll = [i[11:].strip() for i in str(result.stdout).split('\\n') if "memberUid:" in i]
    members=[]
    for member in ll:
        result = (subprocess.run([r'ldapsearch',r'-x','-s','sub','uid=%s'%member,'displayName'],stdout=subprocess.PIPE))
        i0=str(result.stdout).find("displayName:")+12
        d0=str(result.stdout)[i0:].find("\\n")
        members.append(str(result.stdout)[i0:i0+d0].strip())
    tmp=members.pop(members.index(project_number))
    information["members"]=members
    del tmp
    return information


def setuser(name="",project_number=""):
    """ At the end of the game it provides values in the __SPECK_CONFIG dictionary:
    USER_HOME: temporary home, full path
    USER_DATA: final data destination, full path
    PROJECTID: project number
    """
    
    IPy = get_ipython()
    #Recover data from config file if it exists or create an empty one
    try:
        ll=open(IPy.user_ns["__SPECK_CONFIG"]['SPECK_FOLDER'] + "/config/user.cfg","r").readlines()
    except:
        print("Missing user.cfg file in:",IPy.user_ns["__SPECK_CONFIG"]['SPECK_FOLDER'],"/config/")
        cfgfile=open(IPy.user_ns["__SPECK_CONFIG"]['SPECK_FOLDER'] + "/config/user.cfg","w")
        cfgfile.close()
    
    cfg={}
    for i in ll:
        _i = i.strip().split("=")
        cfg[_i[0]] = _i[1]

    #Or a name or a project must be provided if not even a folder name can be recovered from config file
    if name == "" and project_number == "" and (not("FOLDER" in cfg.keys()) or cfg["FOLDER"]==""):
        raise Exception("No user defined nor previous user or project stored, cannot operate. specify user or project via setuser.")

#From now on we start from the FOLDER specified in user.cfg as a subfolder of 
#USER_HOME_ROOT and SOLEIL_DATA_ROOT (if no project is specified)
#USER_HOME_ROOT and USER_DATA_ROOT (if a project is specified)

#Case 1: setuser is employed with no arguments, it should default to previous name and project if they exist
# in this case there is no check on the existence of the project, it is already in user.cfg... it should be ok.

    if name == "" and project_number=="":
        if "PROJECT" in list(cfg.keys()) and cfg["PROJECT"] != "":
            IPy.user_ns["__SPECK_CONFIG"]["PROJECTID"]=cfg["PROJECT"]

#In the user home the year is left
            IPy.user_ns["__SPECK_CONFIG"]["USER_HOME"] = IPy.user_ns["__SPECK_CONFIG"]["USER_HOME_ROOT"]\
            +os.sep + cfg["FOLDER"]

#In the project ruche folder, the year is stripped (too redundant)
            IPy.user_ns["__SPECK_CONFIG"]["USER_DATA"] = IPy.user_ns["__SPECK_CONFIG"]["USER_DATA_ROOT"]\
            + os.sep +cfg["PROJECT"] + os.sep + cfg["FOLDER"][cfg["FOLDER"].rfind(o.sep)+1:]

        else:

            IPy.user_ns["__SPECK_CONFIG"]["PROJECTID"]=""
            cfg["PROJECT"] = ""

#In the user home the year is left
            IPy.user_ns["__SPECK_CONFIG"]["USER_HOME"] = IPy.user_ns["__SPECK_CONFIG"]["USER_HOME_ROOT"]\
            +os.sep + cfg["FOLDER"]

#In the local ruche folder, the year is kept
            IPy.user_ns["__SPECK_CONFIG"]["USER_DATA"] = IPy.user_ns["__SPECK_CONFIG"]["SOLEIL_DATA_ROOT"]\
            + os.sep +cfg["FOLDER"]
            
#Case 2: a name is provided, but there is no project associated
#In this case a folder has to be created 
    elif name != "" and project =="":
        
        IPy.user_ns["__SPECK_CONFIG"]["PROJECTID"]=""
        
        cfg["PROJECT"] = ""
        cfg["NAME"] = name
        cfg["FOLDER"] = "%4i" % time.localtime()[0] +os.sep + "%4i%02i%02i" % time.localtime()[0:3] + "_%s" % name
        
        print("New folder is: " + cfg["FOLDER"])
        
        IPy.user_ns["__SPECK_CONFIG"]["USER_HOME"] = IPy.user_ns["__SPECK_CONFIG"]['USER_HOME_ROOT'] + os.sep +cfg["FOLDER"]
        IPy.user_ns["__SPECK_CONFIG"]["USER_DATA"] = IPy.user_ns["__SPECK_CONFIG"]['SOLEIL_DATA_ROOT'] + os.sep +cfg["FOLDER"]

        try:
            os.makedirs(IPy.user_ns["__SPECK_CONFIG"]["USER_HOME"])
        except Exception as tmp:
            print(tmp)
        try:
            os.makedirs(IPy.user_ns["__SPECK_CONFIG"]["USER_DATA"])
        except Exception as tmp:
            print(tmp)

#Cases 3 and 4: the project is provided with or without a name, if there is no name the date of the day
#is used for home folder but no subfolder is made in ruche

    else project != "":

        information = check_project(project)
        if information:
            print("Project number : %s"%project)
            print("Title          : %s" % information["title"])
            print("Main proposer  : %s"%information["manager"])
            
            IPy.user_ns["__SPECK_CONFIG"]["PROJECTID"] = project
            cfg["PROJECT"] = project
        else:
            raise Exception("Wrong project number provided.")
        
        if name != "":
            cfg["NAME"] = name
            cfg["FOLDER"] = "%4i" % time.localtime()[0] +os.sep + "%4i%02i%02i" % time.localtime()[0:3] + "_%s" % name
        else:
            cfg["NAME"] = ""
            cfg["FOLDER"] = "%4i" % time.localtime()[0] +os.sep + "%4i%02i%02i" % time.localtime()[0:3]
        
        print("New folder is: " + cfg["FOLDER"])
        
        IPy.user_ns["__SPECK_CONFIG"]["USER_HOME"] = IPy.user_ns["__SPECK_CONFIG"]['USER_HOME_ROOT'] + os.sep +cfg["FOLDER"]
        IPy.user_ns["__SPECK_CONFIG"]["USER_DATA"] = IPy.user_ns["__SPECK_CONFIG"]["USER_DATA_ROOT"]\
        + os.sep +cfg["PROJECT"] + os.sep + cfg["FOLDER"][cfg["FOLDER"].rfind(o.sep)+1:]

    if name != "" or project != "":
        try:
            os.makedirs(IPy.user_ns["__SPECK_CONFIG"]["USER_HOME"])
        except Exception as tmp:
            print(tmp)
        try:
            os.makedirs(IPy.user_ns["__SPECK_CONFIG"]["USER_DATA"])
        except Exception as tmp:
            print(tmp)

#Folders are defined and if required they have been created
#Now data have to be written to user.cfg and we should move to the home folder correctly (log/backup/...)
#STOP HERE on Friday
        user_home = IPy.user_ns["__SPECK_CONFIG"]["USER_HOME"]
        user_data = IPy.user_ns["__SPECK_CONFIG"]["USER_DATA"]

#Stop logging
        try:
            IPy.magic("logstop")
        except Exception as tmp:
            print(tmp)

#After stoppin' log I perform a backup of current folder and then we move to the new one.
        try:
            backup()
        except Exception as tmp:
            print(tmp)

#Move to the new home 
        os.chdir(user_home)

      
#Store information in config file
        cfgfile=open(IPy.user_ns["__SPECK_CONFIG"]['SPECK_FOLDER'] + "/config/user.cfg","w")
        for i in list(cfg.keys()):
#Do not store project informations in configuration file (it requires more complex structure and there are privacy issues
            if i != "PROJECTINFO":
                cfgfile.write("%s=%s\n" % (i,cfg[i]))
        cfgfile.close()

#Restart logging
        try:
            IPy.magic("logstart -ort %s global"%(user_home + os.sep + "logBook.txt"))
        except Exception as tmp:
            print(tmp)
            pass
    return




