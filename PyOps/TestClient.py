#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Client for test purposes

"""

# import as class, not module
# here only Operator (Facade) has to be used
from Operator import Operator

import sys
from colorama import Fore, Back, Style
from datetime import datetime

try:    
    operator = Operator()
 
    [mibMngr,serverMngr] = operator.connect()
    operator.createViewInterfaces()
    [commandDefIterator,cmdInjMngr] = operator.getManagers()
    
    # Test: PING, PPC00201, AGC0DW02,'DSC32000','GRC10002'
    operator.setDefaultCommandValues('AGC0DW02')
    operator.setRequiredParameterValues('AGP00000',['U',50])
    #operator.setDefaultCommandValues('GRC10002')
    #operator.setRequiredParameterValues('COMMAN16',['S','TEST1'])
    #operator.setRequiredParameterValues('COMMAN16',['S','TEST2'])
    #operator.setRequiredParameterValues('COMMAN05',['S','TEST3'])
    operator.injectCommand()
   
except Exception as e:
    print(Fore.WHITE + Back.RED + Style.BRIGHT + '\nExited with exception:',e, Style.RESET_ALL)
    cmdInjMngr.deregister()
    sys.exit(1)   
    
else:      
    # Wait 20 seconds for callback, then deregister and exit
    time1 = datetime.now()
    while(datetime.now() - time1).seconds <= 20:
        pass
        
    cmdInjMngr.deregister()
    print(Fore.WHITE + Back.GREEN + Style.BRIGHT + '\nExited without exception', Style.RESET_ALL)
    sys.exit(0)    
    