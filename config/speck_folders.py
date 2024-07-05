#!/bin/python

#This file is executed at statrtup to define the following variables then stored in __SPECK_CONFIG

#This version does not use  a backup folder (it is set to empty string for legacy)
#but requires a temporary folder for saving files before moving them to ruche.

###Modify only these values as you desire, folders should already exist
#SPECK_DATA_FOLDER="/nfs/.autofs/srv5/spool1/ExperimentalData"
#SPECK_DATA_FOLDER="/nfs/.autofs/tempdata/samba/com-samba/ExperimentalData"
#SPECK_BACKUP_FOLDER=""

#SPECK_DATA_FOLDER="/home/experiences/samba/com-samba/ExperimentalData"
#SPECK_BACKUP_FOLDER="/nfs/ruche-samba/samba-soleil/com-samba/"
#SPECK_BACKUP_FOLDER="/nfs/ruche-samba/share-temp/SAMBA"

SPECK_DATA_FOLDER="/nfs/ruche-samba/samba-soleil/com-samba"
SPECK_BACKUP_FOLDER=""
SPECK_TEMPORARY_HOME="/nfs/srv5/spool1/ExperimentalData"
SPECK_TEMPORARY_FOLDER="/nfs/srv5/spool1/speck_temp"

#####################################################################
#import os
#Following lines are dangerous, this mechanism is useless after all
#These information can be stored in TANGO database or this file can be executed when needed.

#os.putenv("SPECK_DATA_FOLDER",SPECK_DATA_FOLDER)
#os.system("export SPECK_DATA_FOLDER=%s"%(SPECK_DATA_FOLDER))
#os.putenv("SPECK_BACKUP_FOLDER",SPECK_BACKUP_FOLDER)
#os.system("export SPECK_BACKUP_FOLDER=%s"%(SPECK_BACKUP_FOLDER))
#os.putenv("SPECK_TEMPORARY_FOLDER",SPECK_BACKUP_FOLDER)
#os.system("export SPECK_TEMPORARY_FOLDER=%s"%(SPECK_BACKUP_FOLDER))

