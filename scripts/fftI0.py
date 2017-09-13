#Need the cardAI to be defined in the global namespace
domacro("analyseSAI.py")

def fftI0(name="fftI0", freq = 10000, figN=10):

    cardAI.configurationId=1
    sleep(0.1)
    while(cardAI.state() <> DevState.STANDBY):
        sleep(1)
    cardAI.frequency=freq
    cardAI.integrationtime=1000
    cardAI.nexusfilegeneration=True
    cardAI.dataBufferNumber=10
    cardAI.nexusNbAcqPerFile=10
    
    cardAI.start()
    sleep(0.1)
    while(cardAI.state()==DevState.RUNNING):
        sleep(1)
    sleep(3)
    Path = "/nfs/" + cardAI.nexusTargetPath.replace("\\","/")

    ll = os.listdir(Path)
    ll = [i for i in ll if i.startswith("sai")]
    ll.sort()
    lastfile = ll[-1]

    print lastfile
    txtOut = findNextFileName("./ruche/"+name,"txt")
    nxsOut = findNextFileName("./ruche/"+name,"nxs")
    os.system("mv " + Path + "/" + lastfile + " " + nxsOut)

    f = tables.openFile(nxsOut,"r")
    thisFT = make_fft(f.root.entry.scan_data.channel0[:].flatten(),cardAI.frequency)
    f.close()
    
    savetxt(txtOut, array(thisFT).transpose())
    figure(figN)
    halflen = len(thisFT[0])/2
    subplot(2,1,1)
    plot(thisFT[0][1:halflen/10],log10(thisFT[1][1:halflen/10]),label=txtOut)
    xlabel("")
    ylabel("log10(|FT|)")
    legend(fontsize="x-small")
    subplot(2,1,2)
    plot(thisFT[0][1:halflen/10],(thisFT[1][1:halflen/10]),label=txtOut)
    del thisFT
    legend(fontsize="x-small")
    xlabel("Hz")
    ylabel("|FT|")
    return


