#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Client for test purposes -- here only Operator (Facade) has to be used

"""

import sys
sys.path.append('AAIDL')
#import profile
from Operator import Operator

operator = Operator()

# mib=True, command=True, parameter=True, packet=True
# '192.168.56.101' '20001'
operator.connect('192.168.197.50','20001', parameter=False, packet=False)

# terminal='konsole' or 'gnome-terminal' or 'xterm'...
operator.initialize(terminal='konsole', parameter=False, packet=False)
    
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
    #GRC10002 = operator.createCommand('GRC10002')    
    #operator.setCommandParameter(GRC10002, 'COMMAN16', isEng=True, valueType='S', value='FOG2')
    #operator.setCommandParameter(GRC10002, 'COMMAN16', isEng=True, valueType='S', value='FOG3')
    #operator.setCommandParameter(GRC10002, 'COMMAN05', valueType='S', value='CONST')         
# 'YMC25104'
    # YMP00015(eng, BATT_STR_0) 
# 'DSC00005'   

#==============================================================================
#                                   Syntax
#==============================================================================

# ------------------- command (single cmd or list) ------------------------
# cmd = operator.createCommand(cmdName, numberOfCommands=, absReleaseTime=, relReleaseTime=, absExecutionTime=, staticPtv=, dynamicPtv=, cev=, timeout=, interlock=)     

    # absolute time: '2018.122.14.22.20.000'
    # relative time: '00.00.05'
    # PTV: (E,D,O,N) (N: Enabled, but no notification) (ITC.CheckStateType)        
    # interlock=['FAILED', 'PASSED', 'TIMEOUT']
    
# ------------------- parameter (for single cmd or cmd list) --------------
# operator.setCommandParameter(cmd, paramName, isEng=, unit=, radix=, valueType=, value=)

# ---------------------------- interlock ----------------------------------
# operator.setCommandInterlock(['FAILED', 'PASSED', 'TIMEOUT'])

#==============================================================================
#                              Test 0 (single command)
#==============================================================================

def test_singleCmd(cmd):
    
    global command
    
    command = operator.createCommand(cmd)

#==============================================================================
#                                 Test 1 (Ping)
#==============================================================================
def test_ping(number): 
    
    global PING    
    
    PING = operator.createCommand('PING', numberOfCommands=number)
     
# Check:
    # Callback? Sorted list?        
  
#==============================================================================
#                              Test 2 (Interlock)
#==============================================================================
def test_interlock(): 
    
    global YMC25104, PING_2_11    
         
    YMC25104 = operator.createCommand('YMC25104')  
    operator.setCommandParameter(YMC25104, 'YMP00015', isEng=True, valueType='S', value='BATT_STR_0')
    
    PING_2_11 = operator.createCommand('YYC00000', numberOfCommands=10, interlock=['PASSED', 'FAILED'])               
                
# Check:
    # Full callback?
    # Interlock works? Also for list?
              
#==============================================================================
#                         Test 3 (absolute release time)
#==============================================================================
def test_absReleaseTime():
    
    global PPC00201, PING_2_6 
 
    PPC00201 = operator.createCommand('PPC00201', absReleaseTime='2018.149.12.48.30.000')
    PING_2_6 = operator.createCommand('YYC00000', absReleaseTime='2018.149.12.49.20.000', numberOfCommands=5)
 
# Check:
    # absolute release time for multiple commands? 

#==============================================================================
#                          Test 4 (relative release time)
#==============================================================================
def test_relReleaseTime():
    
    global PPC00A00, YMC22003_2_6            
          
    #PPC00A00 = operator.createCommand('PPC00A00', absReleaseTime='2018.149.12.13.25.928234')
    PPC00A00 = operator.createCommand('PPC00A00')
    YMC22003_2_6 = operator.createCommand('YMC22003', numberOfCommands=5, relReleaseTime='00.00.10')
            
# Check:
    # absolute release time in UTC 0? 
    # relative release time all 10 sec?
    # precision?

#==============================================================================
#                          Test 5 (absolute execution time)
#==============================================================================
def test_absExecutionTime():
    
    global PPC00A00   
    PPC00A00 = operator.createCommand('PPC00A00', absExecutionTime='2018.149.12.50.10.928234')

# Check:
    # absolute execution time in UTC 0? 
    # what happens in SCOS?
    # callback?
      
#==============================================================================
#                                 Test 6 (timeout)
#==============================================================================
def test_timeout():
    
    global YMC25101       
    YMC25101 = operator.createCommand('YMC25101', timeout=60)
    operator.setCommandParameter(YMC25101, 'YMP00015', isEng=True, valueType='S', value='SUS_F_N')
    operator.setCommandParameter(YMC25101, 'YMP00003', valueType='U', value=8)
    
# Check:
    # Timeout if completed_flag = True?
    # Release ASAP, timeout in 60s? 
    # Does programm work correctly?
        
#==============================================================================
#                                 Test 7 (timeout)
#==============================================================================
def test_timeout2():
    
    global PPC00A00
    PPC00A00Kwargs = {'absReleaseTime':'2018.149.12.52.25.928234',
                      'timeout':100}
    PPC00A00 = operator.createCommand('PPC00A00', **PPC00A00Kwargs, numberOfCommands=1)

# Check:
    # Release time correct? Timeout 100s later? 
    # Does programm work correctly?        

#==============================================================================
#                           Test 8 (multiple time settings)
#==============================================================================
def test_multipleTimeSettings():
    
    global YMC22003, PING_2_6, PPC00400_7
    
    YMC22003Kwargs = {'absReleaseTime':'2018.149.12.50.40.928234',
                      'timeout':100}
    PING_2_6Kwargs = {'relReleaseTime':'00.00.05',
                      'timeout':100}
    PPC00400_7Kwargs = {'absExecutionTime':'2018.149.12.51.20.928234'}
    
    YMC22003 = operator.createCommand('YMC22003', **YMC22003Kwargs)
         
    PING_2_6 = operator.createCommand('YYC00000', **PING_2_6Kwargs, numberOfCommands=5)
    
    PPC00400_7 = operator.createCommand('PPC00400', **PPC00400_7Kwargs)
    operator.setCommandParameter(PPC00400_7, 'PPP00004', valueType='D', value=5)
    
# Check:
    # multiple time settings, program works correctly?

#==============================================================================
#                             Test 9 (multiple commands)
#==============================================================================
def test_multipleCommands():  
    
    global PPC02001, PPC00600_2_6
    
    PPC02001Kwargs = {'absReleaseTime':'2018.149.12.50.40.928234',
                      'timeout':100}
    PPC00600_2_6Kwargs = {'relReleaseTime':'00.00.05',
                      'timeout':100}

    PPC02001 = operator.createCommand('PPC02001', **PPC02001Kwargs)
    PPC00600_2_6 = operator.createCommand('PPC00600', **PPC00600_2_6Kwargs, numberOfCommands=5)

    operator.setCommandParameter(PPC02001, 'YMP00000', valueType='U', value=200000)
    operator.setCommandParameter(PPC00600_2_6, 'PBP00002', valueType='U', value=342)
    operator.setCommandParameter(PPC00600_2_6, 'DSP00011', valueType='U', value=100)
        
# Check:
    # multiple time settings, program works correctly?
    # parameter setting works correctly?
    
#==============================================================================
#                           Test 10 (multiple commands)
#==============================================================================
def test_multipleCommands2():
         
    global DSC32000_1, YYC00000_2_6, PPC00201_7, PPC01900_8_10
            
    DSC32000_1Kwargs = {'absReleaseTime':'2018.149.12.15.20.928234'}           
    YYC00000_2_6Kwargs = {'relReleaseTime':'00.00.04'}
    PPC00201_7Kwargs = {'absReleaseTime':'2018.149.12.16.50.928234'}
    PPC01900_8_10Kwargs = {'relReleaseTime':'00.00.05'}

    DSC32000_1 = operator.createCommand('DSC32000', **DSC32000_1Kwargs)
    YYC00000_2_6 = operator.createCommand('YYC00000', **YYC00000_2_6Kwargs, numberOfCommands=5)
    PPC00201_7 = operator.createCommand('PPC00201', **PPC00201_7Kwargs)
    PPC01900_8_10 = operator.createCommand('PPC01900', **PPC01900_8_10Kwargs, numberOfCommands=3)

    operator.setCommandParameter(DSC32000_1, 'DSP00000', valueType='U', value=3000)
    operator.setCommandParameter(DSC32000_1, 'DSP00003', isEng=False, unit='', radix = 'D', valueType='U', value=100000)
    operator.setCommandParameter(DSC32000_1, 'DSP00003', valueType='U', value=200000)
       
# Check:
    # parameters, time and interlock settings work correctly?   

#==============================================================================
#                           Test 11 (repeater (TODO))
#==============================================================================
 
def test_repeater():
        
    global DSC00001
    
    DSC00001 = operator.createCommand('DSC00001', counter=[('DSP00002', 2), ('DSP00004', 2), ('DSP00006', 3, 3)])
        
# -------------- 1 Counter ------------------        
#    DSC00003 = operator.createCommand('DSC00003', counter=[('DSP00007', 2)])
#    operator.setCommandParameter(DSC00003, 'DSP00000', isEng=True, valueType='S', value='ACS Safe Data')  
#    operator.setCommandParameter(DSC00003, 'DSP00000', isEng=True, valueType='S', value='DDS Data') 
 
# -------------- 2 Counter ------------------------         
    #DSC00051 = operator.createCommand('DSC00051', counter=[('DSP00050', 2)])
    #operator.setCommandParameter(DSC00051, 'DSP00051', isEng=True, valueType='S', value='SUS_MON_HIGH')
    #operator.setCommandParameter(DSC00051, 'DSP00052', isEng=True, valueType='S', value='FUSE_0')
    #operator.setCommandParameter(DSC00051, 'DSP00051', isEng=True, valueType='S', value='TARGET_REACHED')
    #operator.setCommandParameter(DSC00051, 'DSP00052', isEng=True, valueType='S', value='FUSE_1')
        
#==============================================================================
#                          Start tests
#==============================================================================    
 
#test_singleCmd('FEINISVR')
test_ping(5)
#test_interlock()
#test_absReleaseTime()
#test_relReleaseTime()
#test_absExecutionTime()
#test_timeout()
#test_timeout2()
#test_multipleTimeSettings()
#test_multipleCommands()
#test_multipleCommands2()
#test_repeater()
           
#==============================================================================
#                          Inject command(s)
#==============================================================================
        
# no arguments --> all cmds are printed and injected
operator.printCommandInformation()
operator.injectCommands()

# Check:
    # test with all commands, single commands and command list

#==============================================================================
#                          TM parameter(s)
#==============================================================================    

#param = operator.getTMParameter('PBTPWR00')
#param2 = operator.getTMParameter('PBTPWR01')
#param3 = operator.getTMParameter('PBTCAP03')
#param4 = operator.getTMParameter('AYTM0M00')

#==============================================================================
#                          TM packet(s)
#============================================================================== 

#packet = operator.getTMPacket()
#packet2 = operator.getTMPacket(header=True)
    
#==============================================================================
#                          Logging
#==============================================================================     
 
#log file will be overwritten for each test
#operator.printLogfile('pyops_logfile.txt')  
    
#==============================================================================      
