#Requires ipython
import exceptions
import os
import grace_np
from numpy import mod, arange

def xplot(x,y=None,curve=-1,graph=0,color=-1):
    """If a grace object exists plots on it"""
    if y == None:
        x, y = arange(len(x)), x
    if not("GracePlotter_x" in globals()):
        try:
            print "Opening New Grace Window"
            __IP.user_ns["GracePlotter_x"]=GracePlotter()
        except:
            #ipy=globals()["get_ipython"]()
            #ipy.ex("GracePlotter_x=GracePlotter()")
            exec "GracePlotter_x=GracePlotter()" in globals()
    #GracePlotter_x.GPlot(x,y,gw=0,curve=curve,graph=graph,color=color)
    if graph > len(GracePlotter_x.wins) + 1: 
        graph = len(GracePlotter_x.wins) + 1
    try:
        GracePlotter_x.GPlot(x, y, gw=graph, curve=curve, graph=0, color=color)
        xauto(graph)
    except:
        try:
            GracePlotter_x.GPlot(x, y, gw=graph, curve=curve, graph=0, color=color)
            xauto(graph)
        except Exception, tmp:
            raise tmp
    return

def xtitle(curve=0,graph=0):
    """Put a title over curve""" 
    return

def xauto(i=None):
    """If a grace object exists autoscale it"""
    if i==None: i=0
    if not("GracePlotter_x" in globals()):
        try:
            __IP.user_ns["GracePlotter_x"]=GracePlotter()
        except:
            #ipy=get_ipython()
            #ipy.ex("GracePlotter_x=GracePlotter()")
            exec "GracePlotter_x=GracePlotter()" in globals()
    if i==None: i=0
    if i<0 or i>=len(GracePlotter_x.wins): i=-1
    GracePlotter_x.wins[i]("autoscale\nredraw\n")
    return

def xarrange():
    """Should find number of graphs and arrange them well..."""
    return

class GracePlotter:
    def __init__(self):
        self.curves=[]
        self.wins=[]
        #self.curves=[[,],]
        self.wins.append(grace_np.GraceProcess())
        return

    def __del__(self):
        """Kills by PID every grace windows"""
        for i in self.wins:
            try:
                i('EXIT\n')
            except:
                pass
        #for i in self.wins:
        #    os.kill(self.wins[i].pid,15)
        return

    def GPlot(self,x,y,gw=None,graph=0,curve=0,legend=None,color=1,noredraw=False):
        """kills and replot a curve on a given graceprocess,graph,signal with an optional legend
        Could be executed in a thread to kill scan deadtime"""
        if curve<0: 
            if self.curves==[]:
                curve=0
                self.curves.append(curve)
                if color<0: color=1
            else:
                self.curves.sort()
                curve=self.curves[-1]+1
                self.curves.append(curve)
                if color<0: color=curve+1
        else:
            if not(curve in self.curves):
                self.curves.append(curve)
                if color<0: color=curve+1
        l=min(len(x),len(y))
        color=1+mod(abs(color)-1,16)
        if color>=5: color+=1
        if color>=7: color+=1
        pipe_string="kill g%i.s%i"%(graph,curve)+"\n"+"with g%i\n"%(graph)
        for i in range(l):
            pipe_string+='g%i.s%i point %g,%g\n'%(graph,curve,x[i],y[i])
        #pipe_string+="autoscale\n"
        if legend<>None:
            pipe_string+='g%i.s%i legend "%s"\n'%(graph,curve,legend)
        pipe_string+="g%i.s%i LINE COLOR %i\n"%(graph,curve,color)
        pipe_string+="g%i.s%i LINE LINEWIDTH 2\n"%(graph,curve) #,width)
        if gw==None or self.wins == []:
            if self.wins==[]:
                self.wins.append(grace_np.GraceProcess())
                gw = 0
        elif gw >= len(self.wins):
            self.wins.append(grace_np.GraceProcess())
            gw = len(self.wins) - 1
        try:
            if noredraw:
                self.wins[gw].command(pipe_string)
            else:
                self.wins[gw].command(pipe_string+'redraw\n')
            return
        except Exception, tmp:
            self.wins[gw]=grace_np.GraceProcess()
            if noredraw:
                self.wins[gw](pipe_string)
            else:
                self.wins[gw](pipe_string+'redraw\n')
            print tmp
            return
        return

########def start_grace_process(self):
########    #If self.gracewins==[] the plotting will never work: but the checkout should be done
########    #always on plotSetting for the rest of the code so we set it to none in case of error
########    if self.plotSetting==None:
########        return
########    if ("__GRACE_FAULTY" in dir()):
########        self.plotSetting=None
########        return
########    try:
########        if self.detectionMode<>"sexafs":
########            if self.detectionMode in ["fluo","rontec","vortex"]:
########                #Start gracewin3: rontec and multichannel (2nd counter card)
########                gracewin3=grace_np.GraceProcess()
########                gracewin3("timestamp 0., 0.\ntimestamp char size 0.5\ntimestamp on")
########                gracewin3("default char size 0.75")
########                gracewin3('arrange(4,2,0.08,0.15,0.)')
########                for i in range(8):
########                    gracewin3('with g%i'%(i))
########                    gracewin3('world xmin %g'%(self.e1))
########                    gracewin3('world xmax %g'%(self.e2))
########                    majortick=max(1.,int((self.e2-self.e1)/5.))
########                    gracewin3('xaxis tick major %g'%(majortick))
########                    gracewin3('xaxis ticklabel char size 0.75')
########                    gracewin3('xaxis ticklabel color 2')
########                    gracewin3('world ymin 0')
########                    gracewin3('world ymax 2')
########                    majortick=0.25
########                    gracewin3('yaxis tick major %g'%(majortick))
########                    gracewin3('yaxis ticklabel char size 0.5')
########                    gracewin3('yaxis ticklabel color 2')
########                    gracewin3('xaxis tick minor off\nyaxis tick minor off')
########                for i in range(6):
########                    gracewin3('with g%i'%(i))
########                    gracewin3('xaxis ticklabel off')
########                for i in [6,7]:
########                    gracewin3("with g%i"%(i))
########                    gracewin3('xaxis label char size 0.75')
########                    gracewin3('xaxis label color 2')
########                    gracewin3('xaxis label "Energy (eV)"')
########                for i in range(0,1):
########                    gracewin3("with g%i"%(i))
########                    gracewin3('yaxis label char size 0.6')
########                    gracewin3('yaxis label color 4')
########                    if self.detectionMode=="vortex":
########                        gracewin3('yaxis label "Vortex%i"'%(i))
########                    else:
########                        gracewin3('yaxis label "Rontec%i"'%(i))
########                for i in range(1,8):
########                    gracewin3("with g%i"%(i))
########                    gracewin3('yaxis label char size 0.6')
########                    gracewin3('yaxis label color 2')
########                    gracewin3('yaxis label "Fluo%i"'%(i))
########                    gracewin3('redraw')

########    except:
########        print "Error starting Grace processes: no plotting. Scan will continue."
########        self.plotSetting=None
########    return


########def restart_grace_processes(self):
########    """Kills living grace processes by PID with signal 15 and restart them."""
########    #Kills by PID
########    for i in self.gracewins:
########        try:
########            os.kill(self.gracewins[i].pid,15)
########        except KeyboardInterrupt, tmp:
########            raise tmp
########        except:
########            print "restart_grace_processes: cannot kill pid=",self.gracewins[i]," by signal 15"
########    #Restart them
########    self.start_grace_processes()
########    return

########def update_grace_windows(self,iscan):
########    """Append new points to the curves. This is a separate function, so that it can be easily executed in a separate thread.
########    The iscan value is used to decide on which curve send data. Every iscan has a curve sor as to observe evolutions.
########    I reserve the s0 curve for average even if not yet used."""
########    #Verify that all arrays have same lenght: this is not necessary using my GPlot function!
########    #
########    #Shortcuts
########    gws=self.gracewins
########    gp=self.GPlot
########    en=self.graph_data["energy"]
########    en_ave=self.graph_data["energy_average"]
########    gd=self.graph_data
########    #current curve index
########    iplot=iscan+1
########    #
########    for i in gws:
########        if not(gws[i].is_open()):
########            self.restart_grace_processes()
########    try:
########        if self.detectionMode in ["absorption","fluo","tey","rontec","vortex"]:
########            #
########            #Window exafs_1
########            #
########            if self.plotSetting=="kinetic":
########                #    Many plots mode
########                gp(gws["exafs_1"],0,iplot,en,gd["mux"],legend="n=%i"%(iplot),color=iplot,noredraw=True)
########                gp(gws["exafs_1"],1,iplot,en,gd["fluochannels"][0],color=iplot)
########            elif self.plotSetting=="average":
########                #    Average mode
########                gp(gws["exafs_1"],0,1,en,gd["mux"],legend="n=%i"%(iplot),color=3,noredraw=True)
########                gp(gws["exafs_1"],1,1,en,gd["fluochannels"][0],color=3,noredraw=True)
########                gp(gws["exafs_1"],0,0,en_ave,gd["mux_average"],legend="Average",color=1,noredraw=True)
########                gp(gws["exafs_1"],1,0,en_ave,gd["fluo_average"],color=1)
########            #
########            #Window exafs_2
########            #
########            #For the currents always overwrite the same curve for short
########            names=["i0","i1","i2","i_tey"]
########            for i in range(len(names)):
########                gp(gws["exafs_2"],1,i,en,gd[names[i]],legend=names[i],color=i+1,noredraw=True)
########            gp(gws["exafs_2"],0,iplot,en,gd["mux_ref"],legend=("n=%i"%(iplot)),color=iplot)
########            if self.detectionMode in ["fluo","rontec","vortex"]:
########                #
########                #Window exafs_3
########                #
########                #For the fluo counts always overwrite the same curve for short
########                for i in range(1,8):
########                    gp(gws["exafs_3"],i,1,en,gd["fluochannels"][i],color=2,noredraw=True)
########                gp(gws["exafs_3"],0,1,en,gd["rontec"],color=3)
########                #
########        elif self.detectionMode in ["sexafs",]:
########            #
########            #Window sexafs_1: reference data are TEY data when in sexafs (just to reuse variables)
########            #
########            #    Many plots mode
########            #gp(gws["sexafs_1"],0,iplot,en,gd["mux"],legend=("n=%i"%(iplot)),color=iplot,noredraw=True)
########            #gp(gws["sexafs_1"],1,iplot,en,gd["mux_ref"],color=iplot)
########            #    Average mode
########            gp(gws["sexafs_1"],0,1,en,gd["mux"],legend=("n=%i"%(iplot)),color=3,noredraw=True)
########            gp(gws["sexafs_1"],1,1,en,gd["mux_ref"],color=3,noredraw=True)
########            gp(gws["sexafs_1"],0,0,en_ave,gd["mux_average"],legend="Average",color=1,noredraw=True)
########            gp(gws["sexafs_1"],1,0,en_ave,gd["tey_average"],color=1)
########            #
########            #Window sexafs_2
########            #
########            #For the fluo counts always overwrite the same curve for short
########            for i in range(1,8):
########                gp(gws["sexafs_2"],i,1,en,gd["fluochannels"][i],noredraw=True)
########            gp(gws["sexafs_2"],0,1,en,gd["i0"],color=1,legend="i0",noredraw=True)
########            gp(gws["sexafs_2"],0,2,en,gd["i1"],color=2,legend="i1")
########            #
########        else:
########            pass
########    except KeyboardInterrupt, tmp:
########        raise tmp
########    except grace_np.Disconnected:
########        print "One or more grace windows have been disconnected or closed !"
########        print "Restarting windows...",
########        self.restart_grace_processes()
########        print "OK"
########    except Exception, tmp:
########        for i in gws:
########            if not(gws[i].is_open()):
########                print "Restarting windows...",
########                self.restart_grace_processes()
########                print "OK"
########                return
########        self.plotSetting=None
########        print "Unknown error in update_grace_windows... no more plotting in grace"
########        print tmp.args
########    #cleanup namespace and then returns
########    del gws,gp,gd,en        
########    return
########    
########

