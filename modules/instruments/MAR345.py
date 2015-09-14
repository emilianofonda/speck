#Short function to use the MAR345

try:
    mar345=DeviceProxy("D09-1/dt/mar345")
    def wait_mar(filename="",dt=10):
        if filename=="":
            raise Exception("mar345: filename must be specified.")
        mar345.root=filename
        shopen()
        sleep(dt)
        shclose()
        mar345.Scan()
        while(mar345.state()==DevState.RUNNING):
            sleep(1)
        print "I am copying the file now...",
        #Maybe, wait one minute more to be sure...
        sleep(3)
        #marimage=mar345.image
        #print "Image read: %i X %i"%(len(marimage),len(marimage[0]))
        #savetxt(filename,marimage)
        os.system("rsync --ignore-existing -auv --temp-dir=/tmp -r detecteur@dt-pcmar1.samba.rcl:/usr/MARHOME/data/samba /nfs/ruche-samba/samba-soleil/com-samba/MAR345")
        os.system("rsync --ignore-existing -auv --temp-dir=/tmp -r detecteur@dt-pcmar1.samba.rcl:/usr/MARHOME/data/samba /nfs/ruche-samba/share-temp/SAMBA/MAR345")
        print "OK"
        return
except Exception, tmp:
    print "Error initializing MAR345"
    print tmp


