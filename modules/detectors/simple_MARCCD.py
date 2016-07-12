import PyTango
from PyTango import DevState, DeviceProxy,DevFailed
from time import sleep
import time
import os, sys

from valve_class import valve
from moveable import sensor
from ascan import findNextFileName

class ccdmar(sensor):
	"""BEWARE: All times are translated in seconds!"""
	
	def __repr__(self):
      	 	repr=self.label+"\n"
		return repr
					
      	def __call__(self, x=None):
      		print self.__repr__()
      		return self.state()						      

	def snap(self, dt=1, filename = "ccdmar_image",folder=".", filetype=0, shutter="d09-1-c06/vi/obxg.1"):
		"""filetype = 0 corresponds to marccd (.mccd) files,
		filetype = 1 to nxs files"""
		if shutter <> "":
			shutter_valve=valve(shutter)
		if self.state() <> DevState.STANDBY:
			raise Exception("ccdmar: cannot snap if device not in STANDBY state.")
		if self.DP.read_attribute("exposureTime").value / 1000 <> dt + 3.:
			self.DP.write_attribute("exposureTime",(dt + 3.) * 1000)
		if shutter <> "":
			shutter_valve.open()
		sleep(1)
		self.DP.command_inout("Snap")
		sleep(dt)
		if shutter <> "":
			shutter_valve.close()
		timeout = 3. + self.DP.latencyTime/1000. + time.time() + 10.
		while self.state() <> DevState.STANDBY:
			sleep(0.1)
			if time.time() > timeout:
				print time.time(), timeout
				raise Exception("ccdmar: timeout while performing a snap!!!")
		if self.DP.fileGeneration:
			#Which file?
			if filetype == 1:
				source = self.DP.get_property("FileTargetPath")["FileTargetPath"][0]
			elif filetype == 0:
				source = DeviceProxy(self.label + "-specific").get_property("DetectorTargetPath")["DetectorTargetPath"][0]
			
			ll = os.listdir(source)
			ll.sort()
			if len(ll) < 1:
				raise Exception("ccdmar: data file not found!")
			if filetype == 1:
				if ll[-1].startswith("image"):
					sourcefile = source + os.sep + ll[-1]
				else:
					raise Exception("ccdmar: spurious file found in spool !" + ll[-1])
			elif filetype == 0:
				if ll[-1].startswith("buffer"):
					sourcefile = source + os.sep + ll[-1]
				else:
					raise Exception("ccdmar: spurious file found in spool !" + ll[-1])
			#Move file where?
			if filetype == 1:
				destination = findNextFileName(folder + os.sep + filename,"nxs")
			elif filetype == 0:
				destination = findNextFileName(folder + os.sep + filename,"mccd")
			os.system("mv " + sourcefile +" "+destination)
			print "Data saved in :", destination
		tmp=self.stats()
		print "Minimum Intensity = ", tmp[0]
		print "Maximum Intensity = ", tmp[1]
		print "Average Intensity = ", tmp[2]
		return
		
	def stop(self):
		if self.state()==DevState.RUNNING:
			self.DP.command_inout("Stop")
		return self.state()
	
	def read(self):
		return self.pos()
	
	def stats(self):
		tmp=self.pos()
		return tmp.min(), tmp.max(), tmp.mean()
	
	def count(self, dt=1, filename = "ccdmar_image",folder=".", noreturn = True):
		self.snap(dt, filename = filename, folder = folder)
		if noreturn:
			return
		else:
			return self.read()

