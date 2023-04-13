#!/bin/python

#This file is executed at statrtup to define the following variables then stored in __SPECK_CONFIG

#This version does not use  a backup folder (it is set to empty string for legacy)
#but requires a temporary folder for saving files before moving them to ruche.

#This mess should be moved to a speck tango device centralizing information and implementing multi sessions for speck... one of these days :-)


#The root for the users' home folder
USER_HOME_ROOT="/nfs/.autofs/srv5/spool1/ExperimentalData"

#The location for temporary speck files (important)
SPECK_TEMPORARY_FOLDER="/nfs/.autofs/srv5/spool1/speck_temp"

#The root for data location if a project is specified
USER_DATA_ROOT="/nfs/ruche-samba/samba-users"

#The default root for data location if nothing else is specified
SOLEIL_DATA_ROOT="/nfs/ruche-samba/samba-soleil/com-samba"

