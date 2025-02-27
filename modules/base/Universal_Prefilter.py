#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
"""This code will be used to parse spec-like commands into regular function calls

EX.: <wm motor> will be parsed into <wm('motor')>

Contributors E. Fonda, S. Stanescu..."""
from __future__ import print_function
from __future__ import division

####
#### Import the function/modules as specified in hooks.py by Fernando Perez
####

from builtins import range
from past.utils import old_div
import os
from time import asctime,time
from distutils.version import StrictVersion

import IPython
#from IPython.core.ipapi import get as get_ipython
from IPython.core.getipython import get_ipython

shell = get_ipython()
old_run_cell = shell.run_cell

def myparser(cell):
    return universal_lineparser(cell)

def new_run_cell(cell, *args, **kwargs):
    new_cell = universal_lineparser(cell)
    return old_run_cell(new_cell, *args, **kwargs)

shell.run_cell = new_run_cell
#################################################################
#The real transform is here below and it is named mylineparser
################################################################

def mylineparser(line):
    keywords=["mv","mvr","tw","wa","wm","ct","count","ascan","a2scan","dscan","scan",\
    "xascan","xdscan","set_mon","where_mon","fw","bw","stop","start",\
    "BL_Close","BL_Open","pos","lm","lmset","lmunset","domacro","editmacro","timescan",
    "setroi"]

    parts = line.split()
    if parts[0] in keywords:
        str_list = []
        values_list = []
        for i in range(len(parts)):
            try:
                float(parts[i])
                values_list.append(parts[i])
            except:
                str_list.append(parts[i])
        if len(values_list)==0 and len(str_list)==1: #for lmset, ct
            output_line = parts[0]+"()"
        elif len(values_list)==0 and len(str_list)>1: #for lm, wm, pos, editmacro, domacro 
            output_line = parts[0] + "(" + "\'" + parts[1] + "\'" + ")"
        elif len(values_list)>0 and len(str_list)==1: #for timescan
            concatenatedValues = values_list[0]
            for values in values_list[1:]:
                concatenatedValues += ","+ values
                output_line = parts[0] + "(" + concatenatedValues + ")"
        elif len(values_list)>0 and len(str_list)>1: #for scans and moves
            concatenatedValues = ""
            for values in values_list:
                concatenatedValues += ","+ values
            output_line = parts[0] + "(" + "\'"+ parts[1] + "\'" + concatenatedValues + ")"
    else:
        output_line = line
    return output_line 

###Universal Starts
#simple keywords       e.g.   ct(); wa(); ct 1   or tscan 1 100 2
#Declare "ct":[]
#keyword with strings  e.g.   domacro toto    ---> domacro("toto")         
#Declare "domacro":[1]
#keywords with repeatable arguments: move(*args)   e.g.  mv mot1 1 mot2 2 mot3 sin(pi*0.33)
#Declare "mv":[[2, 1]] to obtain mv("mot1",1,"mot2",2,"mot3", sin(pi*0.33))
#The first number is the number of arguments to be repeated and the rest is the position of the arguments in the unit
#e.g  "toto":[[3, 1, 3]] means that the unit is made of three arguments, first and last must have hyphens
# e.g. "my_wms": [[1, 1]] means that all arguments need hyphens... whatever the number...
#Position of arguments starts always at 1 to be more readable! 
#
#                     WARNING! 
#   Known sides effects: 
#       1) spaces are not authorized in arguments mv x 1 + 2 is not accepted, while  mv x 1+2 is acceptable.
#       2) mixing commas and spaces make things behave unexpectedly mv x,1,y 3 cannot be parsed as 
#           mv x 1 y 3 since commas are not used in splitting
#       3) spaces and semi-columns in strings as "abacus;" and "charlie bis" must be avoided since there is no check for being or not into a string!!!
#  These limitations must be pointed out and explained to users of the interactive shell.

#__Universal_Syntax_Keywords={"mv":[[2,1]],"mvr":[[1]],"tw":[1],"wa":[],"wm":[1],"ct":[],\
#"count":[],"ascan":[],"a2scan":[1,4],"dscan":[1],"scan":[1],"xascan":[1],"escan":[1,2],\
#"xdscan":[1],"set_mon":[1],"where_mon":[1],"BL_Close":[],"BL_Open":[],"pos":[1],\
#"lm":[1],"lmset":[1],"domacro":[1],"editmacro":[1],"timescan":[]}

__Universal_Syntax_Keywords={"mv":[],"mvr":[],"fw":[],"bw":[],"start":[],"stop":[],"tw":[],"wa":[],"wm":[],\
"Iref":[],"Dpos":[],"ct":[],\
"ascan":[],"a2scan":[],"dscan":[],"init":[],"xascan":[],"escan":[1,2],\
"xdscan":[],"set_mon":[],"where_mon":[],"shopen":[],"shclose":[], "shstate":[], "pos":[],"on":[],"off":[],\
"lm":[],"lmset":[],"lmunset":[],"domacro":[1],"editmacro":[1],"tscan":[],"timescan":[],"close":[],"open":[],"setroi":[],
"setuser":[1],"state":[],"status":[],"instrument":[1],"ps":[]}

def universal_lineparser(line):
    try:
        #__Universal_Syntax_Keywords...
        #Cut with semicolons and clean each part of unnecessary spaces
        lines = line.split(";")
        output_line=""
        for thisline in lines:
            #save front spaces to use special syntax in indented code!
            frontspaces = thisline[:thisline.find(thisline.lstrip())]
            ls_thisline = thisline.lstrip()
            parts = ls_thisline.split()
            if len(parts) > 0 and parts[0] in list(__Universal_Syntax_Keywords.keys()):
                if len(__Universal_Syntax_Keywords[parts[0]]) > 0 and type(__Universal_Syntax_Keywords[parts[0]][0]) == list:
                    unit_length = __Universal_Syntax_Keywords[parts[0]][0][0] 
                    units = old_div(len(parts[1:]), unit_length)
                    #If the number of arguments does not correspond what should we do ? force it ? raise exception ? print error on screen?
                    need_guimet_extended = []
                    for i in range(units):
                        need_guimet_extended += [x + i * unit_length for x in __Universal_Syntax_Keywords[parts[0]][0][1:]]
                    for need_guimet in need_guimet_extended :
                        if not(parts[need_guimet].startswith("\"") or parts[need_guimet].startswith("\'")):
                            parts[need_guimet] = "\"" + parts[need_guimet] + "\""
                    #If you do not put the righ number of parameters... expect strange behavious!!!!
                elif len(__Universal_Syntax_Keywords[parts[0]]) > 0 and len(parts)>1:
                    for need_guimet in __Universal_Syntax_Keywords[parts[0]]:
                        if not(parts[need_guimet].startswith("\"") or parts[need_guimet].startswith("\'")):
                            parts[need_guimet] = "\"" + parts[need_guimet] + "\""
                if len(parts) == 1:
                    output_line += frontspaces + parts[0] +"()"
                else:
                    fmt = "%s," * len(parts[1:])
                    fmt = "(" + fmt[:-1] + ")"
                    output_line += frontspaces + parts[0] + fmt % tuple(parts[1:])
            else:
                output_line += thisline
            if thisline != lines[-1]:
                output_line += ";"
        #print output_line
        return output_line
    except Exception as tmp:
        print(tmp)
        print("universal_lineparser error")
        return line
###Universal Ends


def fileparser(filename_in,filename_out):
    """Use the myparser to convert the file in a new file with a standard syntax.
    It is used by the domacro function to execute pyHermes code with spec like syntax."""
    fin=open(filename_in,"r")
    linesin=fin.readlines()
    fin.close()
    fout=open(filename_out,"w")
    for lin in linesin:
        lin=lin.rstrip('\n')
        lout=universal_lineparser(lin)
        fout.write(lout+"\n")
    fout.close()
    return

def process_macro_file(filename,uns, n=1):
    """This command open your macro convert it to standard language in macro.tmp file and then execute it.
    Parameter n may be used to repeat the macro n times."""
    macro_tmp_file="macro_%07.4f.tmp"%time()
    #print "Parsing macro ",filename," into temporary file ",macro_tmp_file
    fileparser(filename,macro_tmp_file)
    #print "Executing file ",macro_tmp_file
    for __repeat_this_macro in range(n):
        exec(open(macro_tmp_file,"r").read(),uns)
    #print "Removing temporary file ",macro_tmp_file
    os.remove(macro_tmp_file)
    return

#General Cleanup

del myparser
