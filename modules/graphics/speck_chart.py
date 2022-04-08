"""
============
Modified from Oscilloscope
============

Modified from the 'Emulates an oscilloscope.' code found in matplotlib.org documentation
"""

import numpy as np
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
import matplotlib.animation as animation


class speck_chart:
    def __init__(self, title="speck_chart"):
        self.fig, self.ax = plt.subplots()
        self.fig.title(title)
        self.xdata = []
        self.ydata = []
        self.line = Line2D(self.xdata, self.ydata)
        self.ax.add_line(self.line)

    def update(self, x,y):
        self.xdata = x
        self.ydata = y
        self.ax.set_xlim(min(x),max(x))
        self.ax.set_ylim(min(y),max(y))
        self.ax.figure.canvas.draw()
        self.line.set_data(self.xdata, self.ydata)
        return self.line,

#scope = Scope(ax)

# pass a generator in "emitter" to produce data for the update func
#ani = animation.FuncAnimation(fig, scope.update, emitter, interval=50,
#                              blit=True)

#plt.show()
