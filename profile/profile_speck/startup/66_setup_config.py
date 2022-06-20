from __future__ import print_function
import os
import mycurses

__setupDir = os.getenv("SPECK") + os.sep + "setup"

if os.getenv("SPECK_SETUP") != "":
    if  os.getenv("SPECK_SETUP")+".py" in os.listdir(__setupDir):
        __target = __setupDir + os.sep + os.getenv("SPECK_SETUP")+".py"
    elif os.getenv("SPECK_SETUP") in os.listdir(__setupDir):
        __target = __setupDir+ os.sep + os.getenv("SPECK_SETUP")
    else:
        print(mycurses.RED+"Cannot find setup %s in folder %s."%( os.getenv("SPECK_SETUP"),__setupDir) +mycurses.RESET)

    try:
        domacro(__target)
        ip = get_ipython()
        class MyPrompt(Prompts):
            def in_prompt_tokens(self,cli=None):
                return[(Token, os.getcwd()+"\n"+"%s"%os.getenv("SPECK_SETUP")),(Token.Prompt,' >')]

        ip=get_ipython()
        ip.prompts=MyPrompt(ip)

        #ip.prompt_manager.in_template = u'\w\n \T Speck[\#] %s >'%os.getenv("SPECK_SETUP")
        del ip
    except Exception as tmp:
        print(mycurses.RED+"Fault executing %s in folder %s."%( os.getenv("SPECK_SETUP"),__setupDir) +mycurses.RESET)
        raise tmp
    
    del __target,__setupDir


