from numpy import fft
import tables

sai = DeviceProxy("d09-1-c00/ca/sai.1")

def make_fft(buffer, sampling, it=1):
    """sampling in Hz, integration time in seconds"""
    #it = integration_time *1000.
    f = fft.fftfreq(len(buffer),1./sampling)
    ft = fft.fft(buffer)
    ft_module = sqrt(ft.imag **2 + ft.real **2)
    return f, ft_module, ft.imag, ft.real 

def plot_fft(freq, ft_module, label=""):
    plot(freq[1:len(freq)/2], ft_module[1:len(freq)/2], label=label)
    return

def load_sai_channel(name,branch="root.entry.scan_data.channel",channel=0, dataInRuche = True):
    if dataInRuche:
        sai = tables.openFile(filename2ruche(name))
    else:
        sai = tables.openFile(name)
    pt2data = eval("sai."+branch+"%i"%channel)
    dd = pt2data.read()
    sai.close()
    return dd

def makeFTfigure(filename, sampling, integration_time, figN=1, channel=0, branch="root.entry.scan_data.channel", fmax=500,ymax=None):
    figure(figN)
    figure(figN).clear()
    data = load_sai_channel(filename,branch,channel)
    yoff = 0
    subplot(2,1,1)
    for i in data:
        ftdata = make_fft(i, sampling, integration_time)
        plot_fft(ftdata[0], ftdata[1] + yoff)
        yoff += max(ftdata[1][1:-1])*0.04
    title(filename)
    xlim(xmax = fmax/5)
    if ymax <> None: ylim(ymax = ymax)
    xlabel("Hz")
    ylabel("I0 FFT modulus")
    grid()
    yoff = 0
    subplot(2,1,2)
    for i in data:
        ftdata = make_fft(i, sampling, integration_time)
        plot_fft(ftdata[0], ftdata[1] + yoff)
        yoff += max(ftdata[1][1:-1])*0.04
    #title(filename)
    xlim(xmax = fmax)
    ylim(ymax = ymax)
    xlabel("Hz")
    ylabel("I0 FFT modulus")
    grid()
    draw()
    savefig(filename+".png")
    return

def compareFTfigure(fileList, sampling, integration_time, figN=1, channel=0, branch="root.entry.scan_data.channel", fmax=500,ymax=None):
    figure(figN)
    figure(figN).clear()
    for filename in fileList:
        data = load_sai_channel(filename,branch,channel)
        yoff = 0
        subplot(2,1,1)
        ftdata = []
        for i in data:
            ftdata.append( make_fft(i, sampling, integration_time) )
        ftdata=array(ftdata)
        ftdata = mean(ftdata, axis=0)
        plot_fft(ftdata[0], ftdata[1], label= filename)
        xlim(xmax = fmax/5)
        if ymax <> None: ylim(ymax = ymax)
        xlabel("Hz")
        ylabel("I0 FFT modulus")
        grid()
        legend(loc="best")
        yoff = 0
        subplot(2,1,2)
        ftdata = []
        for i in data:
            ftdata.append( make_fft(i, sampling, integration_time) )
        ftdata=array(ftdata)
        ftdata = mean(ftdata, axis=0)
        plot_fft(ftdata[0], ftdata[1], label= filename)
        #title(filename)
        xlim(xmax = fmax)
        ylim(ymax = ymax)
        xlabel("Hz")
        ylabel("I0 FFT modulus")
        grid()
    draw()
    savefig(fileList[0]+"_compare.png")
    return

def acquire_sai(fileName="",integrationTime=1,sampling=10000.,AcqPerNexus=10,dataBufferNumber=10,card="sai"):
    """integration time is in seconds
    sampling is in Hz"""
    iT = integrationTime * 1000
    saiCard = eval("sai")
    spoolPath=saiCard.nexusTargetPath
    saiCard.nexusFileGenerattion = True
    sai.nexusresetbufferindex()
    configList = saiCard.get_property(saiCard.configurationName)[saiCard.configurationName]
    saiCard.start()
    running = True
    while( running ):
        sleep(0.1)
        if saiCard.state() in [DevState.FAULT, DevState.STANDBY, DevState.ALARM, DevState.INIT, DevState.UNKNOWN]:
            break
    sleep(0.1)
    if saiCard.state() == DevState.STANDBY:
        pass
    return


def single_shot(filename="sai", card="sai"):
    sai = eval(card)
    sai.nexusFileGeneration = True
    sai.start()
    sleep(0.5)
    while(sai.state() <> DevState.STANDBY):
        sleep(0.1)
    sleep(1)
    ll=[]
    timeout=time() + 10
    while(ll == [] and time() < timeout):
        ll = os.listdir("/nfs/srv5/spool1/sai")
    ll.sort()
    for i in ll:
        totoFile = findNextFileName(filename2ruche(filename),"nxs")
        os.system("cp /nfs/srv5/spool1/sai/%s "%i + totoFile + "&& rm /nfs/srv5/spool1/sai/%s"%i )
    print "Saving data in: ", totoFile
    return

