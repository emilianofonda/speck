def mostab_fft(infinite=False, channel=2):
    sai=DeviceProxy("d09-1-c00/ca/sai.1")
    myfig = figure(1)
    title("FFT qui marche (?)")
    n = 1
    while(infinite or n==1):
       myfig.clear()
       y1 = numpy.fft.rfft(sai.channel3)
       y2 = numpy.fft.rfft(eval("sai.channel%i"%channel))
       y1 = sqrt(y1 * y1.conjugate())
       y2 = sqrt(y2 * y2.conjugate())
       subplot(2,1,1)
       plot(y1, label="Consigne")
       plot(y2, label="I")
       xlim(2,1000)
       ylim(0,max(max(y1[2:]),max(y2[2:])))
       legend()
       subplot(2,1,2)
       plot(log(sqrt(y1 * y1.conjugate())),label="Consigne")
       plot(log(sqrt(y2 * y2.conjugate())),label="I")
       xlim(2,1000)
       draw()
       n += 1
       sleep(1)
       
