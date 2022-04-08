from matplotlib import pyplot as plt
import numpy

class speck_figure:
    def __init__(self,fign=1, title="speck", grid=(1,1),sharex=True,sharey=False,**kwds):
        """Create a figure via a simplified interface:
        fign is the figure number, it may enable overwriting a defined figure instead of spawning a number of them around. 
        The title appears on the window bar itself, it is not part of the graph.
        grid is the layout as a matrix of graphs called viewports (rows, cols)
        if sharex or sharey these axis scales are shared between the graphs/viewports"""
        if grid[0]<=1 and grid[1]<=1:
            ncols=1
            nrows=1
            self.fig, ax = plt.subplots(num=fign,nrows=grid[0],ncols=grid[1],sharex=sharex,sharey=sharey,**kwds)
            self.ax= [ax]
        else:
            self.fig,ax = plt.subplots(num=fign,nrows=grid[0],ncols=grid[1],sharex=sharex,sharey=sharey)
            self.ax =  self.flatten_an_item(ax)      
        #plt.pause(0.001)
        self.curves=[[],]*grid[0]*grid[1]
        self.fig.canvas.set_window_title(title)
        return

    def set_axis_labels(self,xlabel="",ylabel="",viewport=0):
        """Use set_axis_labels to add labels to you axis, if no viewport is specified, the first is modified.
        xlabel and ylabel are exactly what they look like.
        It can be used once, after declaring the speck_figure"""
        self.ax[viewport].set_xlabel(xlabel)
        self.ax[viewport].set_ylabel(ylabel)
        return

    def flatten_an_item(self,item):
        """Internal function, to flatten the list of axis from the nested format returned by matplotlib.pyplot.subplots."""
        flattened=[]
        for bit in item:
            if isinstance(bit,(list,tuple,set,numpy.ndarray)):
                flattened.extend(self.flatten_an_item(bit))
            else:
                flattened.append(bit)
        return flattened

    def add_curve(self,x,y,viewport=0,update=True,**kwds):
        """Advanced.The function is used by the plot command to a new curve. 
        The parameters are the same as for plot.
        Except for curve, since the curve is a new one and will be numbered as the last one on the graph
        The curve number is returned."""
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
        return len(self.curves[viewport])-1

    def update_curve(self,x,y,viewport=0,curve=0,update=True):
        """Advanced.The function is used by the plot command to avoid replotting or plotting a new 
        line instead of updating an existing one.
        The parameters are the same as for plot except legend, since legend is called only at creation time"""
        self.curves[viewport][curve].set(data=(x,y))
        xmin,xmax = self.ax[viewport].get_xlim()
        ymin,ymax = self.ax[viewport].get_ylim()
        self.ax[viewport].set_xlim(min(min(x),xmin),max(xmax,max(x)))
        self.ax[viewport].set_ylim(min(min(y),ymin),max(ymax,max(y)))
        plt.pause(0.01)
        return curve

    def plot(self,x,y,viewport=0,curve=0,update=True,legend=False,**kwds):
        """Straightforward way of plotting in one of the viewports opened:
        
        viewport starts from 0 and numbers the viewports from top left to bottom right
        0  1   
        2  3
        for instance.
            
        curve is the number of the curve to trace or update
        update: if several curves have to be drawn one after the other, you can set this to False to avoid 
        redrawing too often, the last command with update=True will refresh the entire figure.
        
        legend= name of the curve for instance 'data01'
        **kwds are all keywords that can be passed to the matplotlib.pyplot.plot command
        at first drawing call and at FIRST call only.

        For later reuse the number of the curve is returned, useful for new curves in a viewport.
        
        """
        
        
        if len(self.curves[viewport]) < curve + 1:
            crv = self.add_curve(x,y,viewport,update=update,**kwds)
            if legend:
                self.ax[viewport].legend()
        else:
            crv = self.update_curve(x,y,viewport,curve,update=update)
        return crv

    def close(self):
        """Close the plotting window, you may then del the object and free space (maybe)."""
        plt.close(self.fig.number)
        return

def test():
    from numpy import arange, linspace,pi,cos,sin
    from numpy.random import randn
    from time import sleep
    def spiral(length,step,angle):
        p=arange(length)
        x = 0.5*step*p/pi*cos(0.5*p/pi+angle)
        y = 0.5*step*p/pi*sin(0.5*p/pi+angle)
        return x,y
    
    f=speck_figure(grid=(2,2),sharex=False,sharey=False,figsize=(12,8))
    f.set_axis_labels("X0","Y0",0)
    f.set_axis_labels("X1","Y1",1)
    f.set_axis_labels("X2","Y2",2)
    f.set_axis_labels("X3","Y3",3)
    for i in arange(0,2*pi,2*pi/10):
        x,y=spiral(25,1,i)
        f.plot(x,y,viewport=0,curve=0,update=False,legend=False,marker="x",linestyle="--",linewidth=2,color="b",label="L-")
        f.plot(-x,-y,viewport=0,curve=1,update=False,legend=True,marker="x",linestyle="--",linewidth=2,color="b",label="R+")
        #f.plot(range(len(y)),y,viewport=1,update=False)
        #f.plot(range(len(x)),x,viewport=2,update=False)
        f.plot(y,range(len(y)),viewport=3,update=True)
    return f 
