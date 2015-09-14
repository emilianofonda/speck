from numpy import mod
def GPlot(gw,graph,curve,x,y,legend=None,color=1,noredraw=False,autoscale=True):
	"""kills and replot a curve on a given graceprocess,graph,signal with an optional legend
	Could be executed in a thread to kill scan deadtime"""
	l=min(len(x),len(y))
	xmax,xmin,ymax,ymin=max(x),min(x),max(y),min(y)
	color=int(max(0,color))
	pipe_string="kill g%i.s%i"%(graph,curve)+"\n"+"with g%i\n"%(graph)
	for i in range(l):
		pipe_string+='g%i.s%i point %g,%g\n'%(graph,curve,x[i],y[i])
	if "viewport" in gw:
		if not("graph%02i"%graph in gw.viewport):
			gw.viewport["graph%02i"%graph]={
			"xmax":xmax,"xmin":xmin,"ymax":ymax,"ymin":ymin}
		if xmax>gw.viewport["graph%02i"%graph]["xmax"] or \
		xmin<gw.viewport["graph%02i"%graph]["xmin"]:
			gw.viewport["graph%02i"%graph]["xmin"]=xmin
			gw.viewport["graph%02i"%graph]["xmax"]=xmax
			pipe_string+='with g%i\n'%(graph)
		        pipe_string+='world xmin %g\n'%(xmin)
			pipe_string+='world xmax %g\n'%(xmax)
		if ymax>gw.viewport["graph%02i"%graph]["ymax"] or \
		ymin<gw.viewport["graph%02i"%graph]["ymin"]:
			gw.viewport["graph%02i"%graph]["ymin"]=ymin
			gw.viewport["graph%02i"%graph]["ymax"]=ymax
			pipe_string+='with g%i\n'%(graph)
		        pipe_string+='world xmin %g\n'%(ymin)
			pipe_string+='world xmax %g\n'%(ymax)
	else:
		gw.viewport={}
		gw.viewport["graph%02i"%graph]={"xmin":min(x),"xmax":max(x),"ymin":min(y),"ymax":max(y)}
		#pipe_string+="autoscale\n"
	if legend<>None:
		pipe_string+='g%i.s%i legend "%s"\n'%(graph,curve,legend)
	if color>0:
		pipe_string+="g%i.s%i LINE COLOR %i\n"%(graph,curve,mod(color,24)+1)
	else:
		pipe_string+="g%i.s%i LINE COLOR 0\n"%(graph,curve)
	if noredraw:
		gw(pipe_string)
	else:
		gw(pipe_string+'redraw\n')
	return

