from __future__ import division
from past.utils import old_div
def stepSAI(m,p1,p2,dp,dt=0.1,delay=0.,filename="stepSAI"):
    fName = findNextFileName(filename,"txt")
    cardAI.stop()
    cardAI.configurationId = 1
    cardAI.frequency=1000
    cardAI.integrationtime=dt * 1000.
    cardAI.databuffernumber=1
    cardAI.nexusfilegeneration = False
    mv(m,p1)
    dataMat = []
    for cPos in arange(p1,p2+dp,dp):
        mv(m,cPos)
        sleep(delay)
        cardAI.start()
        while(cardAI.state() in [DevState.RUNNING, DevState.MOVING]):
            sleep(dt / 10.)
        dataMat.append(
        array([m.pos(),cardAI.averagechannel0,cardAI.averagechannel1,\
        cardAI.averagechannel2,cardAI.averagechannel3],"f")\
        )
    dataMat = array(dataMat,"f")
    savetxt(fName, dataMat)
    return dataMat.transpose()

def XBPMscan(m,p1,p2,dp,dt=0.1,delay=0.,filename="XBPM"):
    dataMat = stepSAI(m,p1,p2,dp,dt,delay,filename="XBPM")
    fig1 = figure(1)
    fig1.clear()
    subplot(1,2,1)
    plot(dataMat[0],dataMat[3],label="1")
    plot(dataMat[0],dataMat[4],label="2")
    legend()
    subplot(1,2,2)
    plot(dataMat[0],old_div((dataMat[4]-dataMat[3]),(dataMat[4]+dataMat[3])),label="XBPM")
    legend()
    return dataMat
