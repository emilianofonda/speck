def movie_acquire(cam=cam4,framerate=100,nb_of_frames=1000,frames_per_file=100):
    #Prepare
    cam.DP.stop()

    cam.DP.nbframes=nb_of_frames
    cam.DP.framerate=framerate
    cam.DP.filegeneration=True
    sleep(3)
    cam.DP.snap()
    sleep(10)
    while(cam.DP.state()==DevState.RUNNING):
        sleep(1)

    ll=os.listdir(cam4.DP.fileTargetPath)
    for i in ll:
        tmp=filename2ruche(i[i.rfind(os.sep):])
        os.system("mv %s %s"%(i,tmp))
    #Restore
    cam.DP.filegeneration=False
    cam.DP.nbframes=1
    cam.start()
    return


def calculate_baricenter(list_of_files=[],roi=()):
    "roi=(x0,x1,y0,y1)"
    if roi==():
        x0=0
        x1=-1
        y0=0
        y1=-1
    else:
        x0,x1,y0,y1=roi
    xb = []
    yb = []
    for i in list_of_files:
        print(i)
        try:
            mm=tables.open_file(i,"r")
            #ll,sy,sx=shape(mm.root.entry.scan_data.Image_image)
            mmx=array([sum(j,axis=0)[x0:x1] for j in mm.root.entry.scan_data.Image_image])
            mmy=array([sum(j,axis=1)[y0:y1] for j in mm.root.entry.scan_data.Image_image])
            xb.append(sum(mmx*arange(len(mmx[0])),axis=1)/sum(mmx,axis=1))
            yb.append(sum(mmy*arange(len(mmy[0])),axis=1)/sum(mmy,axis=1))
        finally:
            mm.close()
    xb=reshape(array(xb),(len(xb)*len(xb[0],)))
    yb=reshape(array(yb),(len(yb)*len(yb[0],)))
    return xb,yb

