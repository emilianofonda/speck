from __future__ import division
from __future__ import print_function
#Need the cardAI to be defined in the global namespace
from past.utils import old_div
domacro("analyseSAI.py")

def fftI0(name="fftI0", freq = 10000, figN=10, spool="/nfs/srv5/spool1/sai"):
    config = {"configurationId":1,"frequency":freq,"integrationTime":1,"nexusFileGeneration":True,\
    "nexusTargetPath":'D:\FTP',"nexusNbAcqPerFile":10,"dataBufferNumber":10,\
    "statHistoryBufferDepth":60}
    #cardAI = p_sai("d09-1-c00/ca/sai.1", timeout=10., deadtime=0.1, spoolMountPoint="/nfs/srv5/spool1/cx1sai1",\
    cardAI = p_sai("d09-1-c00/ca/sai.1", timeout=10., deadtime=0.1, spoolMountPoint="/nfs/srv5/spool1/cx1sai1",\
    FTPclient="d09-1-c00/ca/ftpclientai.1",FTPserver="d09-1-c00/ca/ftpserverai.1",
    config=config, identifier="cx1sai1",GateDownTime=1.)
    #cardAI.configurationId=1
    #sleep(0.1)
    #while(cardAI.state() <> DevState.STANDBY):
    #    sleep(1)
    #cardAI.frequency=freq
    #cardAI.integrationtime=1000
    #cardAI.nexusfilegeneration=True
    #cardAI.dataBufferNumber=10
    #cardAI.nexusNbAcqPerFile=10
    
    cardAI.prepare(dt=1,NbFrames=cardAI.config["statHistoryBufferDepth"],nexusFileGeneration=True,stepMode=False,upperDimensions=())
    sleep(0.1)
    while(cardAI.state()==DevState.RUNNING):
        sleep(1)
    sleep(3)
    #Path = "/nfs/" + cardAI.nexusTargetPath.replace("\\","/")
    Path = cardAI.spoolMountPoint
    ll = os.listdir(Path)
    ll = [i for i in ll if i.startswith("sai")]
    ll.sort()
    lastfile = ll[-1]

    print(lastfile)
    txtOut = findNextFileName(filename2ruche(name),"txt")
    nxsOut = findNextFileName(filename2ruche(name),"nxs")
    pngOut = findNextFileName(filename2ruche(name),"png")
    os.system("mv " + Path + "/" + lastfile + " " + nxsOut)

    f = tables.openFile(nxsOut,"r")
    thisFT = make_fft(f.root.entry.scan_data.channel0[:].flatten(),freq)
    f.close()
    
    savetxt(txtOut, array(thisFT).transpose())
    fig=figure(figN)
    fig.clear()
    halflen = old_div(len(thisFT[0]),2)
    title(txtOut)
    subplot(2,1,1)
    plot(thisFT[0][1:old_div(halflen,10)],log10(thisFT[1][1:old_div(halflen,10)]),label="")
    xlabel("")
    ylabel("log10(|FT|)")
    #legend(fontsize="x-small")
    subplot(2,1,2)
    plot(thisFT[0][1:old_div(halflen,10)],(thisFT[1][1:old_div(halflen,10)]),label="")
    del thisFT
    #legend(fontsize="x-small")
    xlabel("Hz")
    ylabel("|FT|")
    savefig(pngOut)
    return


