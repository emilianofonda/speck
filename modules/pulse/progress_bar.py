import mycurses
import sys
from time import time as now
from time import sleep

def progress_bar(fraction,width=40):
    p=int(fraction*width)
    print("["+"#"*p+" "*(width-p)+"]")
    print(mycurses.UPNLINES%2)

def test_progress_bar(duration=60,interval=1,width=40):
    t0=now()
    while (now()-t0 <= duration):
        progress_bar((now()-t0)/duration,width=width)
        sys.stdout.flush()
        sleep(interval)   
    return


