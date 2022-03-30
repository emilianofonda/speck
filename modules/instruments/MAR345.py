from __future__ import print_function
#Short function to use the MAR345

try:
    from PIL import Image
    mar345=DeviceProxy("D09-1/dt/mar345")
    mar345.set_timeout_millis(30000)
    def readMAR(filename="",dt=60,energy=None):
        if filename=="":
            raise Exception("mar345: filename must be specified.")
        #outName = "ruche" + os.sep + findNextFileName(filename,"tiff")[2:]
        outName = findNextFileName("./ruche"+os.sep+filename,"tiff")
        #mar345.root=filename
        if energy != None:
            mv(dcm,energy)
        shopen()
        sleep(dt)
        shclose()
        mar345.scan()
        sleep(120)
        while(mar345.state()==DevState.RUNNING):
            sleep(2)
        print("Saving file in %s" % outName)
        #print "I am copying the file now...",
        #Maybe, wait one minute more to be sure...
        sleep(10)
        tiff = Image.fromarray(mar345.image, mode="I")
        tiff.save(outName, format="tiff")
        
        #savetxt(filename,marimage)
        #os.system("rsync --ignore-existing -auv --temp-dir=/tmp -r detecteur@dt-pcmar1.samba.rcl:/usr/MARHOME/data/samba /nfs/ruche-samba/samba-soleil/com-samba/MAR345")
        #os.system("rsync --ignore-existing -auv --temp-dir=/tmp -r detecteur@dt-pcmar1.samba.rcl:/usr/MARHOME/data/samba /nfs/ruche-samba/share-temp/SAMBA/MAR345")
        print("OK")
        return
except Exception as tmp:
    print("Error initializing MAR345")
    print(tmp)


