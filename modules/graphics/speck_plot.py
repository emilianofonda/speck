from matplotlib import pyplot as plt
import numpy
from numpy import arange, linspace,pi,cos,sin
from numpy.random import randn
from time import sleep

class speck_figure:
    def __init__(self,fign=1, title="speck", grid=(1,1),sharex=True,sharey=False,**kwds):
        if grid[0]<=1 and grid[1]<=1:
            ncols=1
            nrows=1
            self.fig, ax = plt.subplots(nrows=grid[0],ncols=grid[1],sharex=sharex,sharey=sharey,**kwds)
            self.ax= [ax]
        else:
            self.fig,ax = plt.subplots(nrows=grid[0],ncols=grid[1],sharex=sharex,sharey=sharey)
            self.ax =  self.flatten_an_item(ax)      
        #plt.pause(0.001)
        self.curves=[[],]*grid[0]*grid[1]
        self.fig.canvas.set_window_title(title)
        return

    def set_axis_labels(self,xlabel="",ylabel="",viewport=0):
        self.ax[viewport].set_xlabel(xlabel)
        self.ax[viewport].set_ylabel(ylabel)
        return

    def flatten_an_item(self,item):
        flattened=[]
        for bit in item:
            if isinstance(bit,(list,tuple,set,numpy.ndarray)):
                flattened.extend(self.flatten_an_item(bit))
            else:
                flattened.append(bit)
        return flattened

    def add_curve(self,x,y,viewport=0,update=True,**kwds):
        if self.curves[viewport] == []:
            self.curves[viewport] = self.ax[viewport].plot(x,y,**kwds)
            if len(x)>0:
                self.ax[viewport].set_xlim(min(x),max(x))
                self.ax[viewport].set_ylim(min(y),max(y))
        else:
            self.curves[viewport].extend(self.ax[viewport].plot(x,y,**kwds))
            if len(x)>0:
                xmin,xmax = self.ax[viewport].get_xlim()
                ymin,ymax = self.ax[viewport].get_ylim()
                self.ax[viewport].set_xlim(min(min(x),xmin),max(xmax,max(x)))
                self.ax[viewport].set_ylim(min(min(y),ymin),max(ymax,max(y)))
        if update:
            plt.pause(0.01)
        #self.bg=self.fig.canvas.copy_from_bbox(self.fig.bbox)
        #self.ax[viewport].draw_artist(self.curves[viewport][-1])
        #self.fig.canvas.blit(self.fig.bbox)
        return

    def update_curve(self,x,y,viewport=0,curve=0,update=True):
        #self.fig.canvas.restore_region(self.bg)
        self.curves[viewport][curve].set(data=(x,y))
        xmin,xmax = self.ax[viewport].get_xlim()
        ymin,ymax = self.ax[viewport].get_ylim()
        self.ax[viewport].set_xlim(min(min(x),xmin),max(xmax,max(x)))
        self.ax[viewport].set_ylim(min(min(y),ymin),max(ymax,max(y)))
        #self.ax[viewport].draw_artist(self.curves[viewport][curve])
        #self.fig.canvas.blit(self.fig.bbox)
        #self.fig.canvas.flush_events()
        plt.pause(0.01)

    def plot(self,x,y,viewport=0,curve=0,update=True,**kwds):
        if len(self.curves[viewport]) < curve + 1:
            self.add_curve(x,y,viewport,update=update,**kwds)
        else:
            self.update_curve(x,y,viewport,curve,update=update)
        return

def test():
    def spiral(length,step,angle):
        p=arange(length)
        x = 0.5*step*p/pi*cos(0.5*p/pi+angle)
        y = 0.5*step*p/pi*sin(0.5*p/pi+angle)
        return x,y
    
    f=speck_figure(1,"TestPlot",(2,2),sharex=True,sharey=True,figsize=(12,8))
    f.set_axis_labels("X0","Y0",0)
    f.set_axis_labels("X1","Y1",1)
    f.set_axis_labels("X2","Y2",2)
    f.set_axis_labels("X3","Y3",3)
    for i in arange(0,2*pi,2*pi/10):
        x,y=spiral(50,2,i)
        f.plot(x,y,viewport=0,curve=0,update=False,marker="x",linestyle="--",linewidth=2,color="b")
        f.plot(-x,-y,viewport=0,curve=1,update=False,marker="x",linestyle="--",linewidth=2,color="b")
        f.plot(-x,y,viewport=1,update=False)
        f.plot(x,-y,viewport=2,update=False)
        f.plot(-x,-y,viewport=3,update=True)
    return f
