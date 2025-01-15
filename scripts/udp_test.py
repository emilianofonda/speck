#Conceptual preparation of a UDP collect of data

udpas=DeviceProxy("flyscan/sensor/sampler.1")
udptb=DeviceProxy("flyscan/clock/pandabox-udp-timebase.1")
flytb=DeviceProxy("flyscan/clock/pandabox-timebase.1")


udpas.configuration=("[sampler]",

"attribute:","name=d09-1-cx1/dt/vg2-basler/image",
"nx_name=image","nx_sampling_name=image_sampling_time","read_error_threshold=10.","-",

"attribute:","name=d09-1-c03/op/axis3_tz2/position",
"nx_name=t2z","nx_sampling_name=t2z_sampling_time","read_error_threshold=10.","-"

)


udpas.Start(20)
udptb.Start(20)

flytb.sequenceLength=20
flytb.pulsePeriod=100

flytb.Prepare()
flytb.Start()

#Collect recorded data and merge must follow ...

