#And now for something completely different...
"""This code will be used to parse pySamba spec-like commands into regular pySamba function calls
move arg1 arg2 should be changed into move(arg1,arg2)

Since ipython is evolvin RADICALLY I had to implement two methods, one for the old ipython
as on the beamline (0.10 family) and one for the modern guys (just now 0.13 and on)

May the farce be with you!  (Mel Brooks)"""

import os
from time import asctime,time

#Get version as put by speck into environment
ver=os.getenv("VERSION")

if ver>0.10:
	#The following is a workaround method that should work with ipython>0.10

	shell = get_ipython()
	old_run_cell = shell.run_cell

	def myparser(cell):
	    return mylineparser(cell)

	def new_run_cell(cell, *args, **kwargs):
	    new_cell = mylineparser(cell)
	    return old_run_cell(new_cell, *args, **kwargs)

	shell.run_cell = new_run_cell
else:
	####
	#### Import the function/modules as specified in hooks.py by Fernando Perez
	####
	try: 
		import IPython.ipapi
	except:
		import IPython.core.ipapi

	try:
		ip=IPython.ipapi.get()
		__NewVersion=True
	except:
		print "...old ipython mode...",
		__NewVersion=False
	####

	def myparser(self, line,continuation=""):
		if __NewVersion:
			return mylineparser(line)
		else:
			return self._prefilter(mylineparser(line),continuation)
		

	####
	#### Finally replace the input_prefilter with my custom function myparser
	####

	if __NewVersion:
		ip.set_hook("input_prefilter",myparser)
		#Cleanup namespace
		del ip
	else:
		try:
			from IPython.core import interactiveshell as InteractiveShell
		except:
			from IPython.iplib import InteractiveShell
		InteractiveShell.prefilter=myparser
		#Clean up namespace
		del InteractiveShell


def fileparser(filename_in,filename_out):
	"""Use the myparser to convert the file in a new file with a standard syntax.
	It is used by the domacro function to execute pysamba code with spec like syntax."""
	fin=file(filename_in,"r")
	linesin=fin.readlines()
	fin.close()
	fout=file(filename_out,"w")
	fout.write("""__pySamba_root="%s"\n"""%(os.getenv("pySamba_root")))
	fout.write("""execfile(__pySamba_root+"/modules/base/spec_syntax.py")\n""")
	for lin in linesin:
		lout=mylineparser(lin)
		fout.write(lout+"\n")
	fout.close()
	return

def process_macro_file(filename,uns):
	"""This command open your macro convert it to standard language in macro.tmp file and the execute it"""
	macro_tmp_file="macro_%07.4f.tmp"%time()
	#print "Parsing macro ",filename," into temporary file ",macro_tmp_file
	fileparser(filename,macro_tmp_file)
	#print "Executing file ",macro_tmp_file
	execfile(macro_tmp_file,uns)
	#print "Removing temporary file ",macro_tmp_file
	os.remove(macro_tmp_file)
	return

#General Cleanup

del myparser

####

#The real transform is here below and it is named mylineparser

####

def mylineparser(line):
	"""Import this module at the beginning or during your ipython session with import filename
	myparser should return line untouched if no pySamba spec-like function is not recognized.
	In the keywords list put ALL the speclike commands you need. 
	After a general parsing for all keywords, a special treatment is then applied to the some keywords.
	This customized treatment can be applied to a few keywords like escan that are intensively used 
	and that require for instance string arguments and where we would like to omit hyphens sometimes.
	
	NOTA: Known limitations: you are not allowed to put a semicolumn (;) into a string!!!!!!!"""
	
	#This code must be rewritten and generalized for merging domacro and instrument or fitting generic syntaxes through a template
	keywords=["mv","mvr","tw","wa","wm",\
	"st","fw","bw","offset",
	"ct","count",\
	"escan","ascan","dscan","tscan",\
	"close","open",
	"on","off",
	"domacro",
	"instrument"]
	lines=line.split(";")
	output_line=""
	frontspaces=""
	for thisline in lines:
		#Take frontspaces and save them
		frontspaces=thisline[:thisline.find(thisline.lstrip())]
		thisline=thisline.strip()
		for k in keywords:
			Found=False
			if thisline.strip()==k:
				output_line+=thisline+"();"
				Found=True
				break
			elif thisline.split(" ")[0]==k:
				#Do general parsing
				if thisline[len(k)]==" ":
					thisline=thisline[:len(k)]+"("+thisline[len(k):].lstrip()
					thisline+=")"
				icar=len(k)-1
				while icar<len(thisline):
					if thisline[icar] in [",","(",")"]:
						icar+=1
						while(icar<len(thisline) and thisline[icar]==" "):
							icar+=1	
					elif thisline[icar]=="\"":
						icar+=1
						while(icar<len(thisline) and thisline[icar]<>"\""):
							icar+=1
						icar+=1
					elif thisline[icar]==" ":
						thisline=thisline[:icar]+","+thisline[icar:].lstrip()
						icar+=1
						while(icar<len(thisline) and thisline[icar]==" "):
							icar+=1	
					else:
						icar+=1
				#Do additional specific parsing
				if thisline.startswith("close ") or thisline.startswith("close("):
					thisline="C"+thisline[1:]
				if thisline.startswith("escan"):
					parts=thisline[thisline.find("(")+1:thisline.rfind(")")].split(",")
					if len(parts)>0:
						thisline="escan("
						for i in range(min(max(2,len(parts)-1),2)):
							if parts[i].count("\"")==0:
								parts[i]="\""+parts[i]+"\""
								parts[i]=parts[i].replace(" ","")
							thisline+=parts[i]+","
						for i in range(min(max(2,len(parts)-1),2),len(parts)):
							thisline+=parts[i]+","
						thisline=thisline[:-1]+")"
				if thisline.startswith("instrument"):
					parts=thisline[thisline.find("(")+1:thisline.rfind(")")].split(",")
					if len(parts)>0:
						thisline="instrument("
						if parts[0].count("\"")==0:
							parts[0]="\""+parts[0]+"\""
							parts[0]=parts[0].replace(" ","")
							thisline+=parts[0]
						thisline=thisline+")"
				if thisline.startswith("domacro"):
					parts=thisline[thisline.find("(")+1:thisline.rfind(")")].split(",")
					if len(parts)>0:
						thisline="domacro("
						if parts[0].count("\"")==0:
							parts[0]="\""+parts[0]+"\""
							parts[0]=parts[0].replace(" ","")
							thisline+=parts[0]
						thisline=thisline+")"
				#Repaste frontspaces before attaching parsed line.
				output_line+=thisline+";"
				Found=True
				break
		if not(Found): output_line+=thisline+";"
		output_line=frontspaces+output_line
	if output_line.endswith(";"): output_line=output_line[:-1]
	#print output_line
	return output_line

