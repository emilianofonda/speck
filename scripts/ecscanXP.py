import dentist
import thread
import tables
import os
import numpy
import time as myTime
from time import sleep
from spec_syntax import wait_motor
from GracePlotter import GracePlotter
from spec_syntax import dark as ctDark
from wait_functions import checkTDL, wait_injection

try:
    import Tkinter
    NoTk=False
except:
    print "Warning from escan: Tkinter not installed."
    NoTk=True


cardCT = DeviceProxy("d09-1-c00/ca/cpt.3_old")
cardAI = DeviceProxy("d09-1-c00/ca/sai.1")

def stopscanXP(shutter=False):
    try:
        if shutter:
            sh_fast.close()
    except:
        pass
    cardAI.stop()
    cardCT.stop()
    dcm.stop()
    wait_motor(dcm)
    return

class CPlotter:
    def h_init__(self):
        return

__CPlotter__ = CPlotter()

def ecscanXP(fileName,e1,e2,n=1,dt=0.04,velocity=10, e0=-1, mode="",shutter=False,beamCheck=True):
    try:
        ecscanXPActor(fileName,e1,e2,n,dt,velocity, e0, mode,shutter,beamCheck)
    except KeyboardInterrupt:
        print "Halting on user request...",
        stopscanXP(shutter)
        print "OK"
        raise KeyboardInterrupt
    except Exception, tmp:
        stopscanXP(shutter)
        raise tmp
    return 

def ecscanXPActor(fileName,e1,e2,n=1,dt=0.04,velocity=10, e0=-1, mode="",shutter=False,beamCheck=True):
    """Start from e1 (eV) to e2 (eV) and count over dt (s) per point.
    velocity: Allowed velocity doesn't exceed 40eV/s.
    The backup folder MUST be defined for the code to run.
    Global variables: FE and obxg must exist and should point to Front End and Shutter
    """
    shell=get_ipython()
    FE = shell.user_ns["FE"]
    obxg = shell.user_ns["obxg"]

    TotalScanTime = myTime.time()
    NofScans = n
    cardCTsavedAttributes = ["totalNbPoint","integrationTime","continuousAcquisition","bufferDepth"]
    cardAIsavedAttributes = ["configurationId","frequency","integrationTime","dataBufferNumber"]
    if fileName == None: 
        raise Exception("filename and limits must be specified")
    if velocity <= 0.:
        raise Exception("Monochromator velocity too low!")
    if velocity > 100.:
        raise Exception("Monochromator velocity exceeded!")
    
    #Configure cards
    TotalTime = float(abs(e2-e1)) / velocity
    print "Expected time = %g s" % TotalTime
    NumberOfPoints = int (float(abs(e2-e1)) / velocity / dt)
    print "Number of points: ",NumberOfPoints
    print "One point every %4.2feV." % (velocity * dt)
    
    #Card CT
    cardCT.totalNbPoint = NumberOfPoints
    cardCT.nexusNbAcqPerFile = NumberOfPoints
    cardCT.integrationTime = dt
    cardCT.bufferDepth = 1
    cardCT.continuousAcquisition = False
    cardCT.nexusFileGeneration = False
    cardCT.set_timeout_millis(30000)

    #Card AI
    if cardAI.configurationId <> 3:
        cardAI.configurationId = 3
        myTime.sleep(5)
    cardAI.integrationTime = dt * 1000 -2.
    cardAI.nexusFileGeneration = False
    cardAI.nexusNbAcqPerFile = NumberOfPoints
    cardAI.dataBufferNumber = NumberOfPoints
    cardAI.statHistoryBufferDepth = NumberOfPoints
    cardAI.set_timeout_millis(30000)
    cardAI_dark0,cardAI_dark1,cardAI_dark2,cardAI_dark3 =\
    map(float, cardAI.get_property(["SPECK_DARK"])["SPECK_DARK"])

    #DCM Setup
    if dcm.state() == DevState.DISABLE:
        dcm.DP.on()
    for i in range(5):
        try:
            dcm.mode(1)
            break
        except:
            myTime.sleep(1)
    #Start graphic windows    
    try:
        CP = __CPlotter__
        CP.GraceWin = GracePlotter()
        for CurrentScan in xrange(NofScans):
            if beamCheck and not(checkTDL(FE)):
                wait_injection(FE,[obxg,])
                myTime.sleep(10.)
            ActualFileNameData = findNextFileName(fileName,"txt")
            shell.logger.log_write("Saving data in: %s\n" % ActualFileNameData, kind='output')
            ActualFileNameInfo = ActualFileNameData[:ActualFileNameData.rfind(".")] + ".info"
            f=file(ActualFileNameData,"w")
            f.close()
            #Configure and move mono
            if dcm.state() == DevState.MOVING:
                wait_motor(dcm)
            myTime.sleep(0.2)
            dcm.velocity(60)
            myTime.sleep(0.2)
            #dcm.mode(1)
            #myTime.sleep(0.2)
            dcm.pos(e1-1., wait=False)
        
            #Print Name:
            print "Measuring : %s\n"%ActualFileNameData
            #Start Measurement
            CP.GraceWin.wins[0].command('ARRANGE(4,1,0.1,0.1,0.25)\nREDRAW\n')
            CP.GraceWin.wins[0].command('with g0\nxaxis ticklabel char size 0.7\n')
            CP.GraceWin.wins[0].command('with g0\nyaxis ticklabel char size 0.7\n')
            CP.GraceWin.wins[0].command('with g0\nyaxis label char size 0.7\nyaxis label "XMU"')
            CP.GraceWin.wins[0].command('with g1\nxaxis ticklabel char size 0.7\n')
            CP.GraceWin.wins[0].command('with g1\nyaxis ticklabel char size 0.7\n')
            CP.GraceWin.wins[0].command('with g1\nyaxis label char size 0.7\nyaxis label "I0, I1"')
            CP.GraceWin.wins[0].command('with g2\nxaxis ticklabel char size 0.7\n')
            CP.GraceWin.wins[0].command('with g2\nyaxis ticklabel char size 0.7\n')
            CP.GraceWin.wins[0].command('with g2\nyaxis label char size 0.7\nyaxis label "X-Pips"')
            CP.GraceWin.wins[0].command('with g3\nxaxis ticklabel char size 0.7\n')
            CP.GraceWin.wins[0].command('with g3\nyaxis ticklabel char size 0.7\n')
            CP.GraceWin.wins[0].command('with g3\nyaxis label char size 0.7\nyaxis label "STD"')
            while(dcm.state() == DevState.MOVING):
                myTime.sleep(0.1)
            while(dcm.state() == DevState.MOVING):
                myTime.sleep(0.1)
            timeAtStart = asctime()
            cardAI.start()
            myTime.sleep(1)
            #dcm.mode(1)
            #myTime.sleep(0.2)
            dcm.velocity(velocity)
            myTime.sleep(0.5)
            dcm.pos(e1)
            myTime.sleep(1)
            try:
                if shutter:
                    sh_fast.open()
            except KeyboardInterrupt:
                #stopscanXP(shutter)
                raise
            except:
                pass
            dcm.pos(e2, wait=False)
            cardCT.start()
            myTime.sleep(2)
            while(dcm.state() == DevState.MOVING):
                try: 
                    #thread.start_new_thread(update_graphsXP, (CP, dcm, cardAI, cardCT, cardXIA1, cardXIA2,\
                    #roiStart, roiEnd, XIA1NexusPath, XIA2NexusPath, XIA1filesList, XIA2filesList,\
                    #fluoXIA1, fluoXIA2))
                    update_graphsXP(CP, dcm, cardAI, cardCT)
                except KeyboardInterrupt:
                    raise
                except Exception, tmp:
                    print tmp
                    pass
                myTime.sleep(4)
            try:
                if shutter:
                    sh_fast.close()
            except KeyboardInterrupt:
                raise
            except:
                pass
            while(DevState.RUNNING in [cardCT.state(),]):
                myTime.sleep(0.1)
            timeAtStop = asctime()
            timeout0 = time()
            while(DevState.RUNNING in [cardAI.state(),] and time()-timeout0 < 3):
                myTime.sleep(0.1)
            if time()-timeout0 > 3:
                print "cardAI of ecscan failed to stop!"
            cardAI.stop()
            theta = cardCT.Theta

            #Begin of new block: test for I0 data, sometimes nan are returned .... why?
            I0 = array(cardAI.historizedchannel0,"f")
            if all(I0 <> numpy.nan_to_num(I0)):
                shell.logger.log_write(mycurses.RED+mycurses.BOLD + ActualFileNameData + ": file is corrupt." + mycurses.RESET, kind='output')
                print mycurses.RED+mycurses.BOLD + ActualFileNameData +": file is corrupt." + mycurses.RESET
                CorruptData = True
            else:
                CorruptData = False
            # End of new block
            
            I0 = numpy.nan_to_num((I0) - cardAI_dark0)
            I1 = numpy.nan_to_num(array(cardAI.historizedchannel1,"f") - cardAI_dark1)
            I2 = numpy.nan_to_num(array(cardAI.historizedchannel2,"f") - cardAI_dark2)
            I3 = numpy.nan_to_num(array(cardAI.historizedchannel3,"f") - cardAI_dark3)
            xmu = numpy.nan_to_num(log(I0/I1))
            ene = numpy.nan_to_num(dcm.theta2e(theta))
            #
            if NofScans >= 1: 
                print myTime.asctime(), " : sending dcm back to starting point."
                dcm.velocity(60)
                myTime.sleep(0.2)
                #dcm.mode(1)
                dcm.pos(e1-1., wait=False)
            #
            print myTime.asctime(), " : Saving Data..."
#Common
            outtaName = filename2ruche(ActualFileNameData)
            outtaHDF = tables.openFile(outtaName[:outtaName.rfind(".")] + ".hdf","w")
#Finalize derived quantities
            fluoX = numpy.nan_to_num(I3 / I0)
            xmuS = numpy.nan_to_num(log(I1/I2))
            outtaHDF.createGroup("/","Spectra")
            outtaHDF.createArray("/Spectra", "xmuTransmission", xmu)
            outtaHDF.createArray("/Spectra", "xmuStandard", xmuS)
            outtaHDF.createArray("/Spectra", "xmuFluoXP", fluoX)
            outtaHDF.createGroup("/","Raw")
            outtaHDF.createArray("/Raw", "Energy", ene)
            outtaHDF.createArray("/Raw", "I0", I0)
            outtaHDF.createArray("/Raw", "I1", I1)
            outtaHDF.createArray("/Raw", "I2", I2)
            outtaHDF.createArray("/Raw", "I3", I3)
#Stop feeding the monster. Close HDF
            outtaHDF.close()
            print "HDF closed."
            shell.logger.log_write("Saving data in: %s\n" % (outtaName[:outtaName.rfind(".")] + ".hdf"), kind='output')
#Now that data are saved try to plot it for the last time
            try:
                #thread.start_new_thread(update_graphsXP, (CP, dcm, cardAI, cardCT, cardXIA1, cardXIA2,\
                #roiStart, roiEnd, XIA1NexusPath, XIA2NexusPath, XIA1filesList, XIA2filesList,\
                #fluoXIA1, fluoXIA2))
                update_graphsXP(CP, dcm, cardAI, cardCT)
                print "Graph Final Update OK"
            except KeyboardInterrupt:
                raise
            except:
                pass
#Local data saving
            dataBlock = array([ene,theta,xmu,fluoX,xmuS,\
            I0,I1,I2,I3],"f")
            numpy.savetxt(ActualFileNameData, transpose(dataBlock))
            FInfo = file(ActualFileNameInfo,"w")
            FInfo.write("#.txt file columns content is:\n")
            FInfo.write("#1) Energy\n")
            FInfo.write("#2) Angle\n")
            FInfo.write("#3) Transmission\n")
            FInfo.write("#4) Fluorescence\n")
            FInfo.write("#5) Standard\n")
            FInfo.write("#6) I0\n")
            FInfo.write("#7) I1\n")
            FInfo.write("#8) I2\n")
            FInfo.write("#9) I3\n")
            FInfo.write("#TimeAtStart = %s\n" % (timeAtStart))
            FInfo.write("#TimeAtStop  = %s\n" % (timeAtStop))
            FInfo.write("#Scan from %g to %g at velocity= %g eV/s\n" % (e1, e2, velocity))
            FInfo.write("#Counter Card Config\n")
            for i in cardCTsavedAttributes:
                FInfo.write("#%s = %g\n" % (i,cardCT.read_attribute(i).value))
            FInfo.write("#Analog  Card Config\n")
            #Report in file Info dark currents applied
            FInfo.write("Dark_I0= %9.8f\nDark_I1= %9.8f\nDark_I2= %9.8f\nDark_I3= %9.8f\n"\
            %(cardAI_dark0,cardAI_dark1,cardAI_dark2,cardAI_dark3,))
            #
            for i in cardAIsavedAttributes:
                FInfo.write("#%s = %g\n" % (i, cardAI.read_attribute(i).value))
            for i in wa(returns=True, verbose=False):
                FInfo.write("#" + i + "\n")
            FInfo.close()
            os.system("cp " + ActualFileNameData +" " +filename2ruche(ActualFileNameData))
            os.system("cp " + ActualFileNameInfo +" " +filename2ruche(ActualFileNameInfo))            
            print myTime.asctime(), " : Data saved to backup."
            shell.logger.log_write("Data saved in %s at %s\n" % (ActualFileNameData, myTime.asctime()), kind='output')
            try:
                if e1 < e0 <e2:
                    #thread.start_new_thread(dentist.dentist, (ActualFileNameData,), {"e0":e0,})
                    if mode.startswith("f"):
                        dentist.dentist(ActualFileNameData, e0 =e0, mode="f")
                    else:
                        dentist.dentist(ActualFileNameData, e0 =e0, mode="")
            except KeyboardInterrupt:
                raise
            except Exception, tmp:
                print tmp
    except Exception, tmp:
        print "Acquisition Halted on Exception: wait for dcm to stop."
        stopscanXP(shutter)
        print "Halt"
        shell.logger.log_write("Error during ecscan:\n %s\n\n" % tmp, kind='output')
        raise tmp
    shell.logger.log_write("Total Elapsed Time = %i s" % (myTime.time() - TotalScanTime), kind='output')
    print "Total Elapsed Time = %i s" % (myTime.time() - TotalScanTime) 
    AlarmBeep()
    return

def update_graphsXP(CP, dcm, cardAI, cardCT):
    
    cardAI_dark0,cardAI_dark1,cardAI_dark2,cardAI_dark3 =\
    map(float, cardAI.get_property(["SPECK_DARK"])["SPECK_DARK"])
 
    LastPoint = cardAI.dataCounter
    I0 = cardAI.historizedchannel0[:LastPoint] - cardAI_dark0
    I1 = cardAI.historizedchannel1[:LastPoint] - cardAI_dark1
    I2 = cardAI.historizedchannel2[:LastPoint] - cardAI_dark2
    I3 = cardAI.historizedchannel3[:LastPoint] - cardAI_dark3
    xmu = numpy.nan_to_num(log(1.0*I0/I1))
    std = numpy.nan_to_num(log(1.0*I1/I2))
    ene = dcm.theta2e(cardCT.Theta)
    ll = min(len(ene), len(xmu))
    CP.GraceWin.GPlot(ene[:ll],xmu[:ll], gw=0, graph=0, curve=0, legend="",color=1, noredraw=True)
    CP.GraceWin.GPlot(ene[:ll], I0[:ll], gw=0, graph=1, curve=0, legend="", color=2, noredraw=True)
    CP.GraceWin.wins[0].command('with g0\nautoscale\nredraw\n')
    CP.GraceWin.GPlot(ene[:ll], I1[:ll], gw=0, graph=1, curve=1, legend="", color=3, noredraw=True)
    CP.GraceWin.wins[0].command('with g1\nautoscale\nredraw\n')
    CP.GraceWin.GPlot(ene[:ll], std[:ll], gw=0, graph=3, curve=1, legend="", color=1, noredraw=True)
    CP.GraceWin.wins[0].command('with g3\nautoscale\nredraw\n')
    CP.GraceWin.GPlot(ene[:ll],numpy.nan_to_num(I3[:ll]/I0[:ll]),\
    gw=0, graph=2, curve=0, legend="", color=1, noredraw=False)
    
    CP.GraceWin.wins[0]('with g2\nautoscale\nredraw\n')
    return


def dark(dt=10.):
    #Configure cards
    NumberOfPoints = 1000
    #Card CT
    cardCT.totalNbPoint = NumberOfPoints
    cardCT.nexusNbAcqPerFile = NumberOfPoints
    cardCT.integrationTime = dt / float(NumberOfPoints)
    cardCT.bufferDepth = 1
    cardCT.continuousAcquisition = False
    cardCT.nexusFileGeneration = False
    cardCT.set_timeout_millis(30000)

    #Card AI
    if cardAI.configurationId <> 3:
        cardAI.configurationId = 3
        myTime.sleep(5)
    cardAI.integrationTime = dt -1.
    cardAI.nexusFileGeneration = False
    cardAI.nexusNbAcqPerFile = NumberOfPoints
    cardAI.dataBufferNumber = NumberOfPoints
    cardAI.statHistoryBufferDepth = NumberOfPoints
    cardAI.set_timeout_millis(30000)

    shell=get_ipython()
    shclose=shell.user_ns["shclose"]
    shopen=shell.user_ns["shopen"]
    shstate=shell.user_ns["shstate"]
    ct=shell.user_ns["ct"]
    if dt == 0:
        ct.clearDark()
    else:
        previous = shstate()
        shclose(1)
        myTime.sleep(1)
        ct.count(dt)
        ct.writeDark()
        cardAI.start()
        myTime.sleep(1)
        cardCT.start()
        while(cardCT.state() == DevState.RUNNING):
            myTime.sleep(0.1)
        cardAI.stop()
        darkAI0 = numpy.average(cardAI.historizedchannel0)
        darkAI1 = numpy.average(cardAI.historizedchannel1)
        darkAI2 = numpy.average(cardAI.historizedchannel2)
        darkAI3 = numpy.average(cardAI.historizedchannel3)
        cardAI.put_property({"SPECK_DARK":[darkAI0,darkAI1,darkAI2,darkAI3]})
        print "Dark values:"
        print "I_0(AnalogInput) = %6.5fV" % darkAI0
        print "I_1(AnalogInput) = %6.5fV" % darkAI1
        print "I_2(AnalogInput) = %6.5fV" % darkAI2
        print "I_3(AnalogInput) = %6.5fV" % darkAI3
        shopen(previous)
    print ct.readDark()
    return

def cleanup(speed=20):
    e1=dcm.pos()-1000.
    e2=dcm.pos()+2500.
    dcm.velocity(speed)
    print "I will scan from %6.4feV to %6.4feV five times at %3.1feV/s to cleanup the zone."%(e1,e2,speed)
    for i in range(5):
        dcm.pos(e1)
        dcm.pos(e2)
    return


def AlarmBeep():
    """Uses Tkinter to alert user that the run is finished... just in case he was sleeping..."""
    #try:
    #    pass
    #    Beep(5,0.1);Beep(5,0.2)
    #    Beep(5,0.1);Beep(5,0.2)
    #except:
    #    print "WARNING: Error alerting for end of scan... \n"
    #    print "BUT: Ignore this message if escan is working well,\n just report this to your local contact\n"
    try:
        a=Tkinter.Tk()
        for j in range(5):
            for i in range(3):
                a.bell()
                myTime.sleep(0.025)
            myTime.sleep(0.35)
        a.destroy()
    except:
        print "WARNING: Error alerting for end of scan... no Tkinter?\n"
        print "BUT: Ignore this message if escan is working well,\n just report this to your local contact\n"
    return


