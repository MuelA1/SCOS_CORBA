#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Client for test purposes

"""

import sys
sys.path.append('AAIDL')

#import profile

# here only Operator (Facade) has to be used
from Operator import Operator
from colorama import Fore, Back, Style

try:    
    operator = Operator()
    
    # '192.168.56.101','20001'
    [mibMngr,serverMngr] = operator.connect('192.168.197.50','20001')  
    [view,commandDefIterator,cmdInjMngr] = operator.initialize()
    
#==============================================================================
#                          Command examples
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
    # 'PPC00600'
        #PCDU Subsystem
        #(2,130)SetEndChar Vol S0   
    # 'AGC0DW02'
        #GPS Subsystem
        #(2,130) GPS2 SetDoppWin
        #cmd.setCommandParameter('AGP00000', valueType='U', value=50)  
    # 'DSC00001'
        #Repeater    
    # 'DSC32000'
        #OBSW Subsystem 
        #Srv(3,1) DefineHK 32000
    # 'GRC10002'
        #SimulatorConstSensFailur
        #Exited with exception: ITC_INJ.CommandInjectMngr.InjectionFailed(reason='Unmatched parameter, expected (COMMAN16),
        #received (COMMAN09) in command GRC10002') 
        #operator.setCommandParameter(cmd1, 'COMMAN16', radix='C', valueType='S', value='TEST2')
        #operator.setCommandParameter(cmd1, 'COMMAN16', isEng=True, valueType='S', value='TEST')
        #operator.setCommandParameter(cmd1, 'COMMAN16', radix='C', valueType='S', value='TEST4')
        #operator.setCommandParameter(cmd1, 'COMMAN05', radix='C', valueType='S', value='TEST3')
        
    # optional command arguments: absReleaseTime, relReleaseTime, absExecutionTime, staticPtv, dynamicPtv, cev, timeout
    # ITC.CheckStateType (E,D,O,N) (N: Enabled, but no notification) for PTV checks   

    # optional parameter arguments: isEng, unit, radix, valueType, value
        

#==============================================================================
#                                   Test 1
#==============================================================================
    def test1(): 
        
        global cmdList    
        cmdList = operator.createCommand('YYC00000', numberOfCommands=1)

    # Check:
        # Callback?
        # Release time ASAP?
        # works with multiple commands?

#==============================================================================
#                                   Test 2
#==============================================================================
    def test2(): 
        
        global cmd1, cmd2_16    
        cmd2_16Kwargs = {'relReleaseTime':'00.00.05'}
        
        cmd1 = operator.createCommand('YYC00000')
        cmd2_16 = operator.createCommand('YYC00000', **cmd2_16Kwargs, numberOfCommands=15)

    # Check:
        # relative release time all 5 sec?
        
#==============================================================================
#                                   Test 3
#==============================================================================
    def test3():
        
        global cmd1_5
        cmdKwargs = {'absReleaseTime':'2018.115.12.00.55.928234'}
        cmd1_5 = operator.createCommand('YYC00000', **cmdKwargs, numberOfCommands=5)

    # Check:
        # absolute release time in UTC 0? 

#==============================================================================
#                                   Test 4
#==============================================================================
    def test4():
        
        global cmd1, cmd2_6     
        cmd1Kwargs = {'absReleaseTime':'2018.115.12.10.50.928234'}
        cmd2_6Kwargs = {'relReleaseTime':'00.00.05'}
        
        cmd1 = operator.createCommand('YYC00000', **cmd1Kwargs)
        cmd2_6 = operator.createCommand('YYC00000', **cmd2_6Kwargs, numberOfCommands=5)

    # Check:
        # absolute release time in UTC 0? 
        # relative release time all 5 sec?

#==============================================================================
#                                   Test 5
#==============================================================================
    def test5():
        
        global cmd1   
        cmdKwargs = {'absExecutionTime':'2018.115.12.30.10.928234'}
        cmd1 = operator.createCommand('YYC00000', **cmdKwargs, numberOfCommands=1)

    # Check:
        # absolute execution time in UTC 0? 
        # what happens in SCOS?
      
#==============================================================================
#                                   Test 6
#==============================================================================
    def test6():
        
        global cmd1  
        cmdKwargs = {'timeout':20}
        cmd1 = operator.createCommand('YYC00000', **cmdKwargs, numberOfCommands=1)

    # Check:
        # Release ASAP, timeout in 100s? 
        # Does programm work correctly?
        
#==============================================================================
#                                   Test 7
#==============================================================================
    def test7():
        
        global cmd1
        cmdKwargs = {'absReleaseTime':'2018.115.12.44.25.928234',
                     'timeout':100}
        cmd1 = operator.createCommand('YYC00000', **cmdKwargs, numberOfCommands=1)

    # Check:
        # Release time correct? Timeout 100s later? 
        # Does programm work correctly?        

#==============================================================================
#                                   Test 8
#==============================================================================
    def test8():
        
        global cmd1, cmd2_6, cmd7
        cmd1Kwargs = {'absReleaseTime':'2018.115.13.00.40.928234',
                      'timeout':100}
        cmd2_6Kwargs = {'relReleaseTime':'00.00.05',
                        'timeout':100}
        cmd7Kwargs = {'absExecutionTime':'2018.115.13.02.55.928234'}
        
        cmd1 = operator.createCommand('YYC00000', **cmd1Kwargs)
        cmd2_6 = operator.createCommand('YYC00000', **cmd2_6Kwargs, numberOfCommands=5)
        cmd7 = operator.createCommand('YYC00000', **cmd7Kwargs)
    
    # Check:
        # multiple time settings, program works correctly?

#==============================================================================
#                                   Test 9
#==============================================================================
    def test9(): 
        
        global cmd1, cmd2_6 
        cmd1Kwargs = {'absReleaseTime':'2018.115.13.30.05.928234',
                      'timeout':100}
        cmd2_6Kwargs = {'relReleaseTime':'00.00.05',
                        'timeout':100}
    
        cmd1 = operator.createCommand('PPC02001', **cmd1Kwargs)
        cmd2_6 = operator.createCommand('PPC02001', **cmd2_6Kwargs, numberOfCommands=5)

        operator.setCommandParameter(cmd2_6, 'YMP00000', valueType='U', value=200000)
        
    # Check:
        # multiple time settings, program works correctly?
        # parameter correct?

#==============================================================================
#                                   Test 10
#==============================================================================
    def test10():  
        
        global cmd1, cmd2_6
        cmd1Kwargs = {'absReleaseTime':'2018.115.13.50.35.928234',
                      'timeout':100}
        cmd2_6Kwargs = {'relReleaseTime':'00.00.05',
                        'timeout':100}
    
        cmd1 = operator.createCommand('PPC00600', **cmd1Kwargs)
        cmd2_6 = operator.createCommand('PPC00600', **cmd2_6Kwargs, numberOfCommands=5)
    
        operator.setCommandParameter(cmd1, 'PBP00002', valueType='U', value=342)
        operator.setCommandParameter(cmd2_6, 'DSP00011', valueType='U', value=100)
        operator.setCommandParameter(cmd2_6, 'PBP00002', valueType='U', value=124)
     
    # Check:
        # multiple time settings, program works correctly?
        # parameter setting works correctly?
    
#==============================================================================
#                                   Test 11
#==============================================================================
    def test11():
             
        global cmd1, cmd2_6, cmd7, cmd8_10
                
        cmd1Kwargs = {'absReleaseTime':'2018.115.14.00.00.928234'}           
        cmd2_6Kwargs = {'relReleaseTime':'00.00.05'}
        cmd7Kwargs = {'absReleaseTime':'2018.115.14.05.30.928234'}
        cmd8_10Kwargs = {'relReleaseTime':'00.00.05'}
        
        cmd1 = operator.createCommand('DSC32000', **cmd1Kwargs)
        cmd2_6 = operator.createCommand('YYC00000', **cmd2_6Kwargs, numberOfCommands=5)
        cmd7 = operator.createCommand('PPC00201', **cmd7Kwargs)
        cmd8_10 = operator.createCommand('PPC01900', **cmd8_10Kwargs, numberOfCommands=3)

        operator.setCommandParameter(cmd1, 'DSP00000', valueType='U', value=3000)
        operator.setCommandParameter(cmd1, 'DSP00003', isEng=False, unit='', radix = 'D', valueType='U', value=100000)
        operator.setCommandParameter(cmd1, 'DSP00003', valueType='U', value=200000)

       
        # Problem: When all cmds are in buffer: First, all cmds with absolute release time are processed, then cmds with relative release time
        #          cmds 7, 8-10 work correctly 
        # Solution: Maybe inject cmds shortly before release time, thread for injection method 
        
#==============================================================================
#                          Start tests
#==============================================================================    
 
    test1() 
       
#==============================================================================
#                          Inject command(s)
#==============================================================================
        
    operator.printAndVerifyInj()
   
#==============================================================================      
             
except Exception as e:
    print(Fore.WHITE + Back.RED + Style.BRIGHT + '\nExited with exception:', e, Style.RESET_ALL)
    operator.deregister(1)           
      
else:               
    #print(Fore.WHITE + Back.GREEN + Style.BRIGHT + '\nExited script without exception, waiting for callback...', Style.RESET_ALL)
    operator.deregister(20)
   
    
    
    
