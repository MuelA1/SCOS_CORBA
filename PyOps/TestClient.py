#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Client for test purposes -- here only pyops module (Facade) has to be used

@author: Axel Müller

#==============================================================================
#                          Command examples
#==============================================================================
        
# 'PING', 'YYC00000'
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

===============================================================================    
------------------------- command (single cmd or list) ------------------------
===============================================================================

cmd = op.createCommand(cmdName, 
                       numberOfCommands=, 
                       absReleaseTime=, 
                       relReleaseTime=, 
                       absExecutionTime=, 
                       staticPtv=, 
                       dynamicPtv=, 
                       cev=, 
                       timeout=, 
                       interlock=)     

All keyword arguments are optional, cmdName is required

Example:
     cmdName: 'YMC24101'
     numberOfCommands=5                        (default: 1 Command)
     absReleaseTime='2018.122.14.22.20.000'    (default: ASAP)
     relReleaseTime='00.00.05'                 (default: no relative time)
     absExecutionTime='2018.122.15.22.20.000'  (default: ASAP)
     staticPtv='E'                             (default: Disabled)
     dynamicPtv='D'                            (default: Disabled)
     cev=True                                  (default: CEV enabled (True))
     timeout=80                                (default: global TO)
     interlock=[]                              (default: no interlock)
     
     PTV checks: 'E': Enabled
                 'D': Disabled
                 'O': Override
                 'N': Enabled, but no notification
     CEV: True or False
                
     Interlock flags: ['FAILED', 'PASSED', 'TIMEOUT'] equals [] 
         List with arbitrary combinations of those values also works

===============================================================================
----------------------------- command parameter  ------------------------------
===============================================================================
   
cmd.setCommandParameter(paramName, isEng=, unit=, radix=, valueType=, value=) 

or

operator.setCommandParameter(cmd, paramName, isEng=, unit=, radix=, valueType=, value=)
(cmd can also be a list of commands here)

No keyword argument, then default value from MIB is used
Default parameters are used if method is not called

Example:
    paramName: 'DSP00000'
    isEng=False
    unit=
    radix='D' (only meaningful if value is integer)
    valueType='U'
    value=200
    
    isEng: True or False
    
    Radix: 'B': 'Binary'
           'O': 'Octal'
           'D': 'Decimal'
           'H': 'Hexa'
    
    Value types: '0': 'Null'
                 'i': 'Short'
                 'I': 'Long'
                 'u': 'Ushort'
                 'U': 'Ulong'
                 'F': 'Float'
                 'D': 'Double'
                 'C': 'Char'
                 'B': 'Boolean'
                 'O': 'Octet'
                 'S': 'String'
                 's': 'Bstring'
                 'T': 'Time'

Important: if value is set, then value type has also to be set    

===============================================================================
------------------------------- TM parameter  ---------------------------------
===============================================================================

param = op.registerTMParameter(paramName, notifyEveryUpdate=, notifySelectedValChange=, notifyOnlyOnce=)

All keyword arguments are optional, parameter name is required
Register parameter only once and use value updates from callback

Example:
    paramName: 'PBTPWR00'
    notifyEveryUpdate=False       (default: True)
    notifySelectedValChange='eng' (default: False)
    notifyOnlyOnce=False          (default: False)

    notifySelectedValChange - values:       'raw',
    (callback only if given value           'eng',
     changes)                               'syn',             
                                            'src',
                                            'def',
                                            'ool',
                                            'scc'

param.getLastValidValue(raw=) returns last raw or eng. value (default: raw=False), 'NOT_VALID' if no valid value for all callbacks
                              so far are received and 'None' if no callbacks at all are received
                                         
===============================================================================
-------------------------------- TM packets  ----------------------------------
===============================================================================

packet = op.registerTMPacket(filingKey, header=, body=, param=)

All keyword arguments optional, filing key has to be provided
Register packet (per filing key) only once and use reception updates from callback

Example:
    filingKey: 31900
    header=True (default: False, defines if packet header data is transmitted in callbacks)
    body=True   (default: False, defines if packet body data is transmitted in callbacks)
    param=True  (default: True, defines if packet parameters are transmitted in callbacks)
     
packet.verifyPacketReception(timeout=) returns 'TIMEOUT' or 'RECEIVED'
Example: timeout=10, default is global packet timeout (no timeout Kwarg)

"""

#import sys
#sys.path.append('AAIDL')

from pyops import Operator

with Operator() as operator:

    
    # 1 - command information, injection and success are printed in 1 console
    # 2 - Progressbar and spinners, printed in multiple consoles
    # terminal='konsole', 'gnome-terminal', 'xterm', 'xfce4-terminal' works
    
    #operator.setVerbosity(2, terminal='xfce4-terminal')
    operator.setVerbosity(1)

    # Logging level 1 (critical info only) - 5 (detailed information)
    operator.configLogging('pyops_logfile.txt', 5)
    
    operator.setGlobalCommandTimeout(80) 
    operator.setGlobalPacketTimeout(20)
           
    commandFlag=True
    parameterFlag=True
    packetFlag=True
     
    # '192.168.197.50', '20001'
    operator.connect('192.168.197.23', '20000', command=commandFlag, parameter=parameterFlag, packet=packetFlag)
                         
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
                  
#==============================================================================
#                              Test 2 (Interlock)
#==============================================================================
    def test_interlock(): 
        
        global YMC25104, PING_2_6, PING_7_11   
             
        YMC25104 = operator.createCommand('YMC25104')  
        operator.setCommandParameter(YMC25104, 'YMP00015', isEng=True, valueType='S', value='BATT_STR_0')
        
        PING_2_6 = operator.createCommand('YYC00000', numberOfCommands=5, interlock=['FAILED'])               
        PING_7_11 = operator.createCommand('YYC00000', numberOfCommands=5, interlock=[])             
                     
#==============================================================================
#                         Test 3 (absolute release time)
#==============================================================================
    def test_absReleaseTime():
        
        global PPC00201, PING_2_6 
     
        PPC00201 = operator.createCommand('PPC00201', absReleaseTime='2018.242.11.50.30.000')
        PING_2_6 = operator.createCommand('YYC00000', absReleaseTime='2018.242.11.55.20.000', numberOfCommands=5)
        
#==============================================================================
#                          Test 4 (relative release time)
#==============================================================================
    def test_relReleaseTime():
        
        global PPC00A00, YMC22003_2_6            
                  
        PPC00A00 = operator.createCommand('PPC00A00')
        YMC22003_2_6 = operator.createCommand('YMC22003', numberOfCommands=5, relReleaseTime='00.00.03')
                   
#==============================================================================
#                          Test 5 (absolute execution time)
#==============================================================================
    def test_absExecutionTime():
        
        global PPC00A00, PING   
        
        PPC00A00 = operator.createCommand('PPC00A00', absExecutionTime='2018.242.13.26.40.928234')
                 
#==============================================================================
#                                 Test 6 (timeout)
#==============================================================================
    def test_timeout():
        
        global YMC25101       
        YMC25101 = operator.createCommand('YMC25101', timeout=60)
        operator.setCommandParameter(YMC25101, 'YMP00015', isEng=True, valueType='S', value='SUS_F_N')
        operator.setCommandParameter(YMC25101, 'YMP00003', valueType='U', value=8)
                
#==============================================================================
#                                 Test 7 (timeout)
#==============================================================================
    def test_timeout2():
        
        global PPC00A00
        PPC00A00Kwargs = {'absReleaseTime':'2018.177.13.00.25.928234',
                          'timeout':100}
        PPC00A00 = operator.createCommand('PPC00A00', **PPC00A00Kwargs)
           
#==============================================================================
#                           Test 8 (multiple time settings)
#==============================================================================
    def test_multipleTimeSettings():
        
        global YMC22003, PING_2_6, PPC00400_7
        
        YMC22003Kwargs = {'absReleaseTime':'2018.177.14.00.40.928234',
                          'timeout':100}
        PING_2_6Kwargs = {'relReleaseTime':'00.00.05',
                          'timeout':100}
        PPC00400_7Kwargs = {'absExecutionTime':'2018.177.14.02.20.928234'}
        
        YMC22003 = operator.createCommand('YMC22003', **YMC22003Kwargs)         
        PING_2_6 = operator.createCommand('YYC00000', **PING_2_6Kwargs, numberOfCommands=5)    
        
        PPC00400_7 = operator.createCommand('PPC00400', **PPC00400_7Kwargs)
        operator.setCommandParameter(PPC00400_7, 'PPP00004', valueType='D', value=5)
           
#==============================================================================
#                             Test 9 (multiple commands)
#==============================================================================
    def test_multipleCommands():  
        
        global PPC02001, PPC00600_2_6
        
        PPC02001Kwargs = {'absReleaseTime':'2018.177.14.30.40.928234',
                          'timeout':100}
        PPC00600_2_6Kwargs = {'relReleaseTime':'00.00.05',
                          'timeout':100}
    
        PPC02001 = operator.createCommand('PPC02001', **PPC02001Kwargs)
        PPC00600_2_6 = operator.createCommand('PPC00600', **PPC00600_2_6Kwargs, numberOfCommands=5)
    
        operator.setCommandParameter(PPC02001, 'YMP00000', valueType='U', value=200000)
        operator.setCommandParameter(PPC00600_2_6, 'PBP00002', valueType='U', value=342)
        operator.setCommandParameter(PPC00600_2_6, 'DSP00011', valueType='U', value=100)
                    
#==============================================================================
#                           Test 10 (multiple commands)
#==============================================================================
    def test_multipleCommands2():
             
        global DSC32000_1, YYC00000_2_6, PPC00201_7, PPC01900_8_10
                
        DSC32000_1Kwargs = {'absReleaseTime':'2018.177.15.21.20.928234'}           
        YYC00000_2_6Kwargs = {'relReleaseTime':'00.00.04'}
        PPC00201_7Kwargs = {'absReleaseTime':'2018.177.15.22.50.928234'}
        PPC01900_8_10Kwargs = {'relReleaseTime':'00.00.05'}
    
        DSC32000_1 = operator.createCommand('DSC32000', **DSC32000_1Kwargs)
        YYC00000_2_6 = operator.createCommand('YYC00000', **YYC00000_2_6Kwargs, numberOfCommands=5)
        PPC00201_7 = operator.createCommand('PPC00201', **PPC00201_7Kwargs)
        PPC01900_8_10 = operator.createCommand('PPC01900', **PPC01900_8_10Kwargs, numberOfCommands=3)
    
        operator.setCommandParameter(DSC32000_1, 'DSP00000', valueType='U', value=3000)
        operator.setCommandParameter(DSC32000_1, 'DSP00003', isEng=False, unit='', radix = 'D', valueType='U', value=100000)
        operator.setCommandParameter(DSC32000_1, 'DSP00003', valueType='U', value=200000)
              
#==============================================================================
#                           Test 11 (repeater)
#==============================================================================
     
    def test_repeater():
            
        global DSC00001, DSC00003, DSC00051
          
        #DSC00001 = operator.createCommand('DSC00001', counter={'DSP00002':[4], 'DSP00004':[6], 'DSP00006':[1, 4, 1, 4, 5, 10]})

        DSC00001 = operator.createCommand('DSC00001', counter={'DSP00002':[3], 'DSP00004':[2], 'DSP00006':[2, 1]})        
                    
        DSC00003 = operator.createCommand('DSC00003', counter={'DSP00007':[7]})
        operator.setCommandParameter(DSC00003, 'DSP00000', isEng=True, valueType='S', value='ACS Safe Data')  
        operator.setCommandParameter(DSC00003, 'DSP00000', isEng=True, valueType='S', value='DDS Data') 
           
        DSC00051 = operator.createCommand('DSC00051', counter={'DSP00050':[4]})
        operator.setCommandParameter(DSC00051, 'DSP00051', isEng=True, valueType='S', value='SUS_MON_HIGH')
        operator.setCommandParameter(DSC00051, 'DSP00052', isEng=True, valueType='S', value='FUSE_0')
        operator.setCommandParameter(DSC00051, 'DSP00051', isEng=True, valueType='S', value='TARGET_REACHED')
        operator.setCommandParameter(DSC00051, 'DSP00052', isEng=True, valueType='S', value='FUSE_1')
            
#==============================================================================
#                          Start tests
#==============================================================================    
    
    if commandFlag == True: 
        
        test_singleCmd('FEINISVR')
        test_ping(5)
        test_interlock()
        #test_absReleaseTime()
        test_relReleaseTime()
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
            
        # no arguments --> all cmds created so far are printed and injected
        operator.printCommandInformation()
        operator.injectCommand()
        
#==============================================================================
#                          TM parameter(s)
#==============================================================================    
    
    if parameterFlag == True:
        
        param1 = operator.registerTMParameter('PBTPWR00', notifyEveryUpdate=False, notifySelectedValChange='eng', notifyOnlyOnce=False)
        param2 = operator.registerTMParameter('PBTPWR01')
        param3 = operator.registerTMParameter('PBTCAP03')
        param4 = operator.registerTMParameter('AYTM0M00')
        param5 = operator.registerTMParameter('DSTFEF00')
        param6 = operator.registerTMParameter('DSTFEF01')
        param7 = operator.registerTMParameter('DCTCDR00')
        param8 = operator.registerTMParameter('DCTCDR01')
        
# ------------------------------- get values ----------------------------------
 
        operator.pauseForExecution(10)
       
        lastVal1 = param1.getLastValidValue()        
        lastVal2 = param2.getLastValidValue(raw=True)
        lastVal3 = param3.getLastValidValue()
        lastVal4 = param4.getLastValidValue()
            
    #    lastVal1 = param1.getLastValidValue()
    #    print(lastVal1)
    #    operator.pauseForExecution(30)
    #    lastVal2 = param1.getLastValidValue()
    #    print(lastVal2)
    #    operator.pauseForExecution(30)
    #    lastVal3 = param1.getLastValidValue()
    #    print(lastVal3)
    #    operator.pauseForExecution(30)
    #    lastVal4 = param1.getLastValidValue()
    #    print(lastVal4)
    #    operator.pauseForExecution(30)
                    
#==============================================================================
#                          TM packet(s)
#============================================================================== 
        
    if packetFlag == True:
        
        packet1 = operator.registerTMPacket(31900)
        packet2 = operator.registerTMPacket(35800)
         
# ----------------------------- wait for packets ------------------------------
    
        if packet2.verifyPacketReception(timeout=5) == 'RECEIVED':
            pass
        elif packet2.verifyPacketReception(timeout=3) == 'TIMEOUT':            
            operator.exitScr(1)
            
#==============================================================================
#                        Write separate logfiles (if needed)
#==============================================================================   
        
    #log files will be overwritten for each test
    operator.writeCommandLog('pyops_cmdLogfile.txt')
    operator.writePacketLog('pyops_packetLogfile.txt')
    operator.writeParameterLog('pyops_paramLogfile.txt')
    
#==============================================================================
       