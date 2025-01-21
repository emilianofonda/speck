def calibrate_dcm(observed,tabulated):
    """calibrate the dcm and set the value on the pandabox cpt3 card associated
    Use this command instead of the mono1PBR internal one theta does not take 
    into account the pandabox encoder."""

    energy.calibrate(observed,tabulated)
    sleep(0.1)
    cpt3.set_encoders()
    return
