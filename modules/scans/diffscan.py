#DCM_Trajectory=[]
#Dicro_motor=pseudo motor
#Dicro_positions=[position_Down,position_Up]   only two and not less than two positions must be supplied
#Dicro_Repetition=n
#Integration_time_per_point= t in seconds
#DCM_Delay (before dicro sequence)
#Dicro_Delay (before measuring each dicro step)

#Sequence:
#perform backlash as in escan for first point.
#Do not execute tuning, rely on active feedback
#Move to point dcm, wait for delay
#Move Dicro to first Dicro Position wait Dicro delay measure.... Move to UP/DOWN....repeat N

#All monochromator movements are set to noTz2 and noTs2 when scan is started
from numpy import array,zeros
from time import sleep
from ascan import *
import GracePlotter as GP

class diffscan_class:
	def __init__(self,dcm_trajectory=[],dicro_motor=None,dicro_positions=[None,None],dicro_repetition=1,integration_time=1,dcm_delay=0,dicro_delay=0,dcm=None,ct=None,labels=["I0","I1","I2","If","ICR","OCR"],channels=[0,1,2,31,39,47]):
		self.dcm=dcm
		self.ct=ct
		self.dcm_trajectory=dcm_trajectory
		self.dicro_motor=dicro_motor
		self.dicro_positions=dicro_positions
		self.dicro_repetition=dicro_repetition
		self.integration_time=integration_time
		self.dcm_delay=dcm_delay
		self.dicro_delay=dicro_delay
		self.labels=labels
		self.channels=channels
		#self.GetPositions=glob["GetPositions"]
		#self.wa=glob["wa"]
		return

	
	def __fibonacci(self,n):
		"returns the first n terms (starting from 1, 0 is neglected)"
		S=[0,1,1,2,3,5,8,13]
		if n>8:
		        for i in range(7,n+7):
       		 	        S.append(S[i]+S[i-1])
		return S[0:n]

	def backlash_recovery(self,energy,de,dummypoints=9,deadtime=0.1):
       		"""Execute a backlash recovery for the monochromator and then set it to e-de:
     		de=2, dummypoints=3;  moves to energy-de*2, energy-de*2, energy-de"""
    		points=array(self.__fibonacci(dummypoints+2)[-1:1:-1])*(-de)+energy
	       #print "Performing backlash recovery over: ",points
		for en in points:
        	        self.dcm.pos(en,Ts2_Moves=False)
                	sleep(deadtime)
	        return

	def start(self,filename):
		wins=GP.GracePlotter()
		try:
			wins.GPlot(self.dcm_trajectory,zeros(len(self.dcm_trajectory)),gw=None,curve=1,legend="Fluorescence")
			wins.GPlot(self.dcm_trajectory,zeros(len(self.dcm_trajectory)),gw=1,curve=1,legend="Dichroism")
		except Exception, tmp:
			print "Error opening grace windows"
			print tmp
		name=findNextFileName(filename,"txt")
		print name
		datafile=open(name,"w")
		
		buffer=""
		#self.GetPositions(verbose=0)
		#for i in self.wa(verbose=False,returns=True):
		#	buffer+="#"+i+"\n"
		#datafile.write(buffer);buffer=""
		self.dcm.disable_ts2()
		self.dcm.disable_tz2()
		de=self.dcm_trajectory[1]-self.dcm_trajectory[0]
		self.backlash_recovery(self.dcm_trajectory[0],de,9,0.2)
		#Header
		buffer="#"
		for i in range(self.dicro_repetition*2):
			buffer+="Energy\tDicro\t"
			for j in self.labels:
				buffer+=j+"_%02i\t"%(i+1)
		buffer+="\n"
		datafile.write(buffer);buffer=""
		#
		ascissa=[]; datatable=[];dicroism=[];If_up=[];If_down=[]
		#
		for energy in self.dcm_trajectory[:]:
			line=[]
			tmp=self.dcm.pos(energy)
			sleep(self.dcm_delay)
			ascissa.append(self.dcm.pos())
			print "%08.2f\r"%(self.dcm.pos()),
			for dicro_repetition in range(self.dicro_repetition):
				for dicro in self.dicro_positions:
					tmp=self.dicro_motor.pos(dicro)
					sleep(self.dicro_delay)
					readout=self.ct.count(self.integration_time)
					dcmpos=self.dcm.pos()
					buffer+="%014.7f\t%014.7f\t"%(dcmpos,self.dicro_motor.pos())
					for channel in self.channels:
						buffer+="%016.7f\t"%readout[channel]
						line.append(readout[channel])
				datatable.append(line)
			buffer+="\n"
			datafile.write(buffer);buffer=""
			datafile.flush()
			try:
				xtable=array(datatable).transpose()
				#print xtable
				dic_point=0.;up_point=0.;down_point=0.
				for i in range(0,len(xtable),6*2):
					up_point+=(xtable[i+6+3][-1]/xtable[i+6][-1])
					down_point+=(xtable[i+0+3][-1]/xtable[i+0][-1])
				dic_point=up_point-down_point
				dicroism.append(dic_point)
				If_up.append(up_point)
				If_down.append(down_point)
				wins.GPlot(ascissa,If_up,gw=0,curve=1,color=1,legend="Up")
				wins.GPlot(ascissa,If_down,gw=0,curve=2,color=3,legend="Down")
				wins.GPlot(ascissa,dicroism,gw=1,curve=1,color=0,legend="Dicroismo")
				for win in wins.wins:
					win('autoscale\nredraw\n')
			except Exception, tmp:
				print "Error plotting"
				print tmp
				pass
		#print If_up
		datafile.close()
		print "Diff scan over"
		return 
	

