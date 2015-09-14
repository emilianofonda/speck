import sys
sys.path.append("/home/fonda/python/spooky/modules/graphics")
import numpy as np
from GracePlotter import xplot

x=np.arange(10)
y=x*x
xplot(x,y)
