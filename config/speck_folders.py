#!/bin/python
import os

###Modify only these values as you desire, folders should already exist
#SPECK_DATA_FOLDER="/home/fonda/ExperimentalData"
#SPECK_BACKUP_FOLDER=""

SPECK_DATA_FOLDER="/home/experiences/samba/com-samba/ExperimentalData"
#SPECK_BACKUP_FOLDER="/nfs/ruche-samba/samba-soleil/com-samba/"
#SPECK_BACKUP_FOLDER=""
SPECK_BACKUP_FOLDER="/nfs/ruche-samba/share-temp/SAMBA"

#####################################################################
os.putenv("SPECK_DATA_FOLDER",SPECK_DATA_FOLDER)
os.system("export SPECK_DATA_FOLDER=%s"%(SPECK_DATA_FOLDER))
os.putenv("SPECK_BACKUP_FOLDER",SPECK_BACKUP_FOLDER)
os.system("export SPECK_BACKUP_FOLDER=%s"%(SPECK_BACKUP_FOLDER))
