from __future__ import print_function
for i in ["mca1","mca2","mca3"]:
    try:
        print(mycurses.BOLD + i +mycurses.RESET, end=' ')
        StopServer(eval(i))
        print(mycurses.RED+" --> halted"+mycurses.RESET)
    except:
        print(" --> failed")
        pass
    sys.stdout.flush()

print(mycurses.UPNLINES%4)

for i in ["mca1","mca2","mca3"]:
    try:
        print(mycurses.BOLD + i +mycurses.RESET, end=' ')
        StartServer(eval(i))
        print(mycurses.GREEN+" --> started"+mycurses.RESET)
    except:
        print(" --> failed")
        pass
    sys.stdout.flush()
       
