#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Client for test purposes

"""

# here only Operator (Facade) has to be used
from Operator import Operator
import TimeModule

import sys
#sys.path.append('AAIDL')

from colorama import Fore, Back, Style
from datetime import datetime

try:    
    operator = Operator()
 
    # '192.168.197.50','20001'
    [mibMngr,serverMngr] = operator.connect('192.168.56.101','20001')    
    [view,commandDefIterator,cmdInjMngr] = operator.initialize()
    
#==============================================================================
#                          Command settings
#==============================================================================
        
    #  Test: PING, 'YYC00000'
    # 'PPC00201'
        #PCDU Subsystem
        #Srv(2,130) CheckBattCap1      
    # 'PPC02001'
        #PCDU Subsystem
        #(2,130)ReadMaxCompCurr
    # 'PPC01900'  
        #PCDU Subsystem
        #(2,130)ReadCPUToggleTime
    # 'AGC0DW02'
        #GPS Subsystem
        #(2,130) GPS2 SetDoppWin
        #commandList[i].setCommandParameter('AGP00000',['U',50])   
    # 'DSC32000'
        #OBSW Subsystem 
        #Srv(3,1) DefineHK 32000
    # 'GRC10002'
        #SimulatorConstSensFailur
        #Exited with exception: ITC_INJ.CommandInjectMngr.InjectionFailed(reason='Unmatched parameter, expected (COMMAN16),
        #received (COMMAN09) in command GRC10002') 
    
    commandList = []
    commandName = 'PPC01900'
    
    # optional values (release time, execution time, static PTV, dynamic PTV, cev, interlockType, interlockStageType)

    ''' ITC.CheckStateType (E,D,O,N) (N: Enabled, but no notification) for PTV checks
        ITC.InterlockType (N,L,G,l,g,F,f)
        ITC_INJ.InterlockStageType (G,U,O,E,C) '''
    
#    cmdKwargs = {'staticPtv' : 'D',
#                 'cev' : 'True',
#                 'dynamicPtv' : 'D',
#                 'executionTime' : TimeModule.scosDate2timestamp("2018.093.16.00.00.928"),
#                 'ilockType' : 'N',
#                 'ilockStageType' : '0'}
       
    numberOfCommands = 3
      
#==============================================================================
#                          Inject command(s)
#==============================================================================
    
    i = 0
    while len(commandList) < numberOfCommands:
 
        print(f'\nCommand injection {(len(commandList) + 1)} {commandName:=^110} \n')

        commandList.append(operator.createCommand(commandName))
        #commandList.append(operator.createCommand(commandName,**cmdKwargs))
        commandList[i].injectCommand()
        i = i + 1

    print('\n \n')

#==============================================================================
#                          Get command status
#==============================================================================

    # Wait 2 seconds for callback
    time1 = datetime.now()
    while(datetime.now() - time1).seconds <= 2:
        pass

    i = 0
    while i < len(commandList):       
        
        print(f'\nCommand status {(i + 1)} {commandName:=^110} \n')
        
        commandList[i].getCommandStatus()
        print(repr(commandList[i]))
        print(Fore.WHITE + Back.BLUE + Style.BRIGHT + str(commandList[i]), Style.RESET_ALL)
        i = i + 1
      
    print('\n' + '=' * 130 + '\n')
            
except Exception as e:
    print(Fore.WHITE + Back.RED + Style.BRIGHT + '\nExited with exception:',e, Style.RESET_ALL)
    cmdInjMngr.deregister()           
    sys.exit(1)   
    
else:               
    print(Fore.WHITE + Back.GREEN + Style.BRIGHT + '\nExited without exception', Style.RESET_ALL)
    cmdInjMngr.deregister() 
    sys.exit(0)    
    
