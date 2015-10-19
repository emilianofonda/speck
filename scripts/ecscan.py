#Import modules
import os, sys, numpy, scipy, tables

#Environment Setup
ecsConfig ={}
ecsConfig["cptCard"]="d09-1-c00/ca/cpt.3"
ecsConfig["cptConfig"] = "BUFFERED"

ecsConfig["saiCard"]="d09-1-c00/ca/sai.1"
ecsConfig["saiConfig"] = 2

#Helper functions

def ecsConfigureCards(ecsConfig):
    return

def ecsCleanSpool(ecsConfig):
    return

def ecsReadNXSData(ecsConfig):
    return

def ecsGetDataStreamConfig(ecsConfig):
    return

def ecsPrepare(ecsConfig):
    return

def ecsLoad(fileName):
    return

def ecsSave(filename,ecsConfig):
    return

#Main Begins

def ecscan(filename,ecsConfig):
    return

#Main Ends

thetaList = [i for i in os.listdir(cptDir) if i.startswith(cptName)]
saiList = [i for i in os.listdir(saiDir) if  i.startswith(saiName)]

thetaList.sort()
saiList.sort()
print len(thetaList)
print len(saiList)

theta=[]
I0=[]
I1=[]

for thetaF,saiF in zip(thetaList,saiList):
    tF = tables.openFile(cptDir + os.sep + thetaF,"r")
    tmpT = tF.root.entry.scan_data.Theta.read()
    for i in tmpT: theta += list(i) 
    tF.close()
    sF = tables.openFile(saiDir + os.sep + saiF,"r")
    tmpI = sF.root.entry.scan_data.channel0_RAW.read()
    for i in tmpI: I0 += list(i) 
    tmpI = sF.root.entry.scan_data.channel1_RAW.read()
    for i in tmpI: I1 += list(i) 
    #I0 += list(sF.root.entry.scan_data.channel0_RAW.read()[0])
    #I1 += list(sF.root.entry.scan_data.channel1_RAW.read()[0])
    sF.close()

print "len I0    = %6.5e" % len(I0)
print "len theta = %6.5e" % len(theta)
