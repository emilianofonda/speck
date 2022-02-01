print "Loading Vortex_SDD4 version pulse under XIA: preparing."

try:
    #Recognized detector names:
    #CdTe, Canberra_Ge36, Canberra_Ge7, Vortex_SDD4, Vortex_SDD1, Canberra_SDD13
    detector_details={"detector_name":"Vortex_SDD4","real_pixels_list":"1,2,3,4","comment":"Vortex 4 elements installed in CX1"}

    config = {"fileGeneration":False,"streamTargetPath":'D:\\FTP',\
    "mode":"MAP10", "streamNbAcqPerFile":630,"nbPixelsPerBuffer":63,"streamtargetfile":"xia1"}
    
    cx1xia1=dxmap("d09-1-cx1/dt/dtc-mca_xmap.1",FTPclient="d09-1-c00/ca/ftpclientxia.1",identifier = "fluo01",timeout=90.,\
    FTPserver="d09-1-c00/ca/ftpserverxia.1",spoolMountPoint="/nfs/srv5/spool1/xia1", config=config,detector_details = detector_details)
    
    print GREEN+"cx1xia1 --> DxMap card"+RESET
    
    mca1=cx1xia1

except Exception, tmp:
    print tmp

#The following post format is very heavy with large array detectors.
#A simplification could be provided if detectors provided already computed averages or corrected counts, but it is tricky 
#for detectors cut in several devices as our Germanium one. Even normalisation schemes may differ depending on experiment layout.

#Attention has to be paid here, since any detector change has an impact on these posts that rely on order of channels and naming conventions
#It is evident that it cannot be different, since these are user defined functions.

#### after addresses, constants and formulas, links could be a good idea to give  astandard name in posts to some quantities

try:
    ctPosts=[\
    {"name":"MUX","formula":"log(float(ch[0])/ch[1])","units":"","format":"%9.7f"},\
    {"name":"MUS","formula":"log(float(ch[1])/ch[2])","units":"","format":"%9.7f"},\
    {"name":"I1Norm","formula":"float(ch[1])/ch[0]","units":"","format":"%9.7e"},\
    {"name":"FLUO_RAW","formula":"float(sum(ch[7:10]))/ch[0]","units":"","format":"%9.7e"},
    ]  
    #>>>>>>>>>>>>>>>> Remember only formulas are saved to file <<<<<<<<<<<<<<<<<<<<<<<<
    XAS_dictionary = {
        "addresses":{
            "I0":"cx1sai1.I0",
            "I1":"cx1sai1.I1",
            "I2":"cx1sai1.I2",
            "I3":"cx1sai1.I3",
            "Theta":"encoder01.Theta",
            },
        "constants":{},
        "formulas":{
            "Theta":"Theta[:]",
            "energy":"dcm.theta2e(Theta[:])",
            "I0":"I0[:]",
            "I1":"I1[:]",
            "I2":"I2[:]",
            "I3":"I3[:]",
            "MUX":"numpy.log(I0[:]/I1[:])",
            "REF":"numpy.log(I1[:]/I2[:])",
            "FLUO_DIODE":"I3[:]/I0[:]",
            },
    }
    __cx1xia1_channels=range(0,4)
    __FLUO="("
    __FLUO_RAW="("
    for i in __cx1xia1_channels:
        XAS_dictionary["addresses"]["ROI%02i"%i] = "fluo01.roi%02i"%i
        XAS_dictionary["addresses"]["ICR%02i"%i] = "fluo01.icr%02i"%i
        XAS_dictionary["addresses"]["OCR%02i"%i] = "fluo01.ocr%02i"%i
        __FLUO+="+numpy.nan_to_num(ROI%02i[:]/OCR%02i[:]*ICR%02i[:])"%(i,i,i)
        __FLUO_RAW+="+ROI%02i[:]"%(i)
    __FLUO+=")/numpy.array(I0[:],'f')"
    __FLUO_RAW+=")/numpy.array(I0[:],'f')"
    XAS_dictionary["formulas"]["FLUO"] = __FLUO
    XAS_dictionary["formulas"]["FLUO_RAW"] = __FLUO_RAW
    del __FLUO
    del __FLUO_RAW
    #ct=pseudo_counter(masters=[pulseGen0,],slaves=[cx1sai,cx1xia1,cx1xia2,cpt3])

    ct_sdd4=pseudo_counter(masters=[pulseGen0,],slaves=[cx1sai,cx1xia1,cpt3],posts=ctPosts, postDictionary=XAS_dictionary)

except Exception, tmp:
    print tmp
    print "Failure defining ct0 config"

ct=ct_sdd4
ct.reinit()
#legacy definitions
def setroi(ch1, ch2):
    """Set roi an ALL channels between ch1 and ch2. This is a silly way to do it... must be redesigned"""
    try:
        mca1.setROIs(ch1, ch2)
    except:
        pass
    return 

