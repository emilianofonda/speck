#from mono1 import *
#from counter_class import *
from time import clock,sleep,asctime,time
from numpy import cos,sin,pi,log,mod
import PyTango
import exceptions
#import Gnuplot

class follow_rocca_scan:
	def __init__(self,e1,e2,de,dt,dcm=dcm,bender=bender,cpt=cpt,xbpm=xbpm,deadtime=0.01,Ts2_Moves=False):
		self.e1=e1
		self.e2=e2
		self.de=de
		self.dt=dt
		self.dcm=dcm
		self.bender=bender
		self.cpt=cpt
		self.BENDER=False
		self.deadtime=deadtime
		self.Ts2_Moves=Ts2_Moves
		self.xbpm=xbpm
		return
		

	def set_ts2(self):
		#This replaces the time consuming previous method here below
		#self.dcm.move((self.e1+self.e2)/2.,wait=True,Ts2_Moves=True,Tz2_Moves=True)
		dest=self.dcm.ts2(self.dcm.e2theta((self.e1+self.e2)*0.5))
		return self.dcm.m_ts2.pos(dest)

	def combined_move(self,energy,alarm=False):
		#try:
		self.dcm.move(energy,False,self.Ts2_Moves)
		if(self.BENDER): self.bender.go(self.bender.calculate_bender(energy))
		#except:
		#	self.bender.stop()
		#	sleep(3)
		#	if(alarm):
		#		raise PyTango.DevFailed
		#	else:
		#		self.combined_move(energy,alarm=True)
		if(self.BENDER):
			while((self.dcm.state()==PyTango.DevState.MOVING) or (self.bender.check()==PyTango.DevState.MOVING)):
				sleep(self.deadtime)
		else:
			while(self.dcm.state()==PyTango.DevState.MOVING):
				sleep(self.deadtime)
		return self.dcm.pos()	


	def use_bender(self,flag=None):
		if(flag==None):
			return self.BENDER
		if(flag in [True,False]):
			self.BENDER=flag
			return self.BENDER
		else:
			raise exceptions.SyntaxError
	

	def start(self,filename):
		__GNUPLOT_UPDATE_EVERY=2
		p=self.dcm.m_rx2fine.pos()
		f=file(filename,"w")
		f.write("Energy\tAngle\tmu\tmus\tI0\tI1\t...counters...\tPIEZO(Write)\tPIEZO(Read)\tBender\txbpm\tTimeMove(s)\n")
		f.flush()
		np=int((self.e2-self.e1)/self.de+1.)
		en=self.e1
		if(not(self.Ts2_Moves)): self.set_ts2()
		self.combined_move(en-10.)
		self.combined_move(en-5.)
		#Prepare graphics
		energy2plot=[]
		mux2plot=[]
		mux2plot_ref=[]
		i02plot=[]
		i12plot=[]
		piezowrite=[]
		piezoread=[]
		__GNUPLOT_FAULTY=False
		__GNUPLOT_CALLS=0
		try:
			W1=Gnuplot.Gnuplot(persist=1)
			W2=Gnuplot.Gnuplot(persist=0)
			W3=Gnuplot.Gnuplot(persist=0)
			W4=Gnuplot.Gnuplot(persist=0)
			W1("set title 'Absorption: "+filename+"'")
			W1("set xlabel 'Energy(eV)' ")
			W4("set title 'Absorption: reference sample'")
			W4("set xlabel 'Energy(eV)' ")
			W2("set title 'Counts' ")
			W2("set xlabel 'Energy(eV)' ")
			W3("set title 'Piezo Values' ")
			W3("set xlabel 'Energy(eV)' ")
			W1("set style data lines")
			W4("set style data lines")
			W2("set style data lines")
			W3("set style data lines")
		except:
			print "Problems with Gnuplot module. I will not plot, but I continue anyway."
			__GNUPLOT_FAULTY=True
		
		for i in range(np):
			f=file(filename,"a")
			try:
				print "Moving...",
				self.dcm.m_rx1.state()
				t=time()
				self.combined_move(en)
				p=self.dcm.tune()
				t=time()-t
				print "OK."
				sleep(self.deadtime)
				cnts=self.cpt.count(self.dt)
				[i0,i1,i2,i3,i4]=cnts[0:5]
				theta=self.dcm.m_rx1.pos()
				etheta=self.dcm.theta2e(theta)
				try:
					mu=log(i0/i1)
				except:
					mu=0.
				try:
					mus=log(i1/i2)
				except:
					mus=0.
				f.write("%8.2f\t%8.6f\t%8.6f\t%8.6f\t"%(etheta,theta,mu,mus))
				for i in cnts:
					f.write("%7i\t"%(i))
				f.write("%8.6f\t%8.6f\t%6.4f\t%6.4f\t%6.2f"%(p,dcm.m_rx2fine.pos(),bender.pos(),xbpm.read(),t)+"\n")
				en+=self.de
				f.flush()
			except (KeyboardInterrupt,SystemExit):
				self.dcm.stop()
				f.close()
				print "Scan finished on user request."
				return
			except PyTango.DevFailed, tmp:
				print "Error during scan. Exception caught, Ignoring..."
				print tmp.args
				print "Sleeping 2 seconds... ",
				sleep(2)
				print "the show must go on..."
				#Do nothing
				#sleep(2)
				#Bad way to save the scan, just ignore devices... to be changed?
				#if(tmp.args["reason"]=="TIMEOUT_EXPIRED"):
				#	sleep(2)
				#else:
				#	self.dcm.stop()
				#	f.close()
				#	raise tmp
			#except: 
			#	print "Unknown error during scan!"
			#	self.dcm.stop()
			#	f.close
			#	return
			f.flush()
			energy2plot.append(etheta)
			try:
				mux2plot.append(log(i0/i1))
			except:
				mux2plot.append(nan)
			try:
				mux2plot_ref.append(log(i1/i2))
			except:
				mux2plot_ref.append(nan)
			i02plot.append(i0)
			i12plot.append(i1)
			piezowrite.append(p)
			piezoread.append(self.dcm.m_rx2fine.pos())
			__GNUPLOT_CALLS+=1
			if(not(__GNUPLOT_FAULTY) and (mod(__GNUPLOT_CALLS,__GNUPLOT_UPDATE_EVERY)==0)):
				try:
					w1=Gnuplot.Data(energy2plot,mux2plot)
					w4=Gnuplot.Data(energy2plot,mux2plot_ref)
					w2a=Gnuplot.Data(energy2plot,i02plot)
					w2b=Gnuplot.Data(energy2plot,i12plot)
					w3a=Gnuplot.Data(energy2plot,piezowrite)
					w3b=Gnuplot.Data(energy2plot,piezoread)
					W1.plot(w1)
					W4.plot(w4)
					W2.plot(w2a,w2b)
					W3.plot(w3a,w3b)
				except:
					print "Gnuplot problem. I stop plotting! Scan will continue anyway."
					__GNUPLOT_FAULTY=True
		f.close()
		print "Scan finished, you, lucky man :-)"
		return

class rocca:
	def __init__(self,p1=1.,p2=9.,dp=0.05,dt=0.1,piezo=rx2fine,cpt=cpt,deadtime=0.01):
		self.p1=p1
		self.p2=p2
		self.dp=dp
		self.dt=dt
		self.piezo=piezo
		self.cpt=cpt
		self.deadtime=deadtime
		return

	def start(self,filename=""):
		if(filename==""):
			print "Empty filename!"
			print "Syntax: yourscan.start('filename')"
			raise exceptions.SyntaxError("Nofilename in starting rocca scan")
		__GNUPLOT_UPDATE_EVERY=2
		f=file(filename,"w")
		f.write("PIEZO(Write)\tPIEZO(Read)\tCounts...\n")
		f.flush()
		np=int((self.p2-self.p1)/self.dp+1.)
		p=self.p1
		self.piezo.pos(0.)
		#Prepare graphics
		i02plot=[]
		piezowrite=[]
		piezoread=[]
		__GNUPLOT_FAULTY=False
		__GNUPLOT_CALLS=0
		try:
			W1=Gnuplot.Gnuplot(persist=1)
			#W2=Gnuplot.Gnuplot(persist=1)
			W1("set xlabel 'Piezo (V)' ")
			W1("set title 'Rocking curve' ")
			#W2("set xlabel 'Piezo Write' ")
			#W2("set title 'Piezo Read' ")
			W1("set style data lines")
			#W2("set style data lines")
		except:
			print "Problems with Gnuplot module. I will not plot, but I continue anyway."
			__GNUPLOT_FAULTY=True
		
		for i in range(np):
			f=file(filename,"a")
			try:
				pread=self.piezo.pos(p)
				cnts=self.cpt.count(self.dt)
				[i0,i1,i2,i3,i4]=cnts[0:5]
				f.write("%g\t%g"%(p,pread))
				for i in cnts:
					f.write("\t%7i"%(i))
				f.write("\n")
				p+=self.dp
				f.flush()
			except (KeyboardInterrupt,SystemExit):
				f.close()
				print "Scan finished on user request."
				return
			except PyTango.DevFailed, tmp:
				print "Error during scan. Exception caught, Ignoring..."
				print tmp
				print "Sleeping 2 seconds... ",
				sleep(2)
				print "the show must go on..."
				#Do nothing
				#sleep(2)
				#Bad way to save the scan, just ignore devices... to be changed?
				#if(tmp.args["reason"]=="TIMEOUT_EXPIRED"):
				#	sleep(2)
				#else:
				#	self.dcm.stop()
				#	f.close()
				#	raise tmp
			#except: 
			#	print "Unknown error during scan!"
			#	self.dcm.stop()
			#	f.close
			#	return
			f.flush()
			i02plot.append(i0)
			piezowrite.append(p)
			piezoread.append(pread)
			__GNUPLOT_CALLS+=1
			if(not(__GNUPLOT_FAULTY) and (mod(__GNUPLOT_CALLS,__GNUPLOT_UPDATE_EVERY)==0)):
				try:
					w1=Gnuplot.Data(piezowrite,i02plot)
					#w2=Gnuplot.Data(piezowrite,piezoread)
					W1.plot(w1)
					#W2.plot(w2)
				except:
					print "Gnuplot problem. I stop plotting! Scan will continue anyway."
					__GNUPLOT_FAULTY=True
		f.close()
		print "Rocca finished, you, lucky man :-)"
		return

def roccascan(filename="",p1=1.,p2=9.,dp=0.05,dt=0.1):
	"""This function trace on the screen and save in a file the rocking curve. It is convenient to use the default 
	trajectory, just type the right filename."""
	s=rocca(p1,p2,dp,dt)
	s.start(filename)
	return

