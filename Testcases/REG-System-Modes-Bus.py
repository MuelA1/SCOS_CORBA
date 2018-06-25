#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" REG-System-Modes-Bus

Syntax:

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

All keyword arguments optional, cmdName is required

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

op.setCommandParameter(cmd, paramName, isEng=, unit=, radix=, valueType=, value=)
(cmd can also be a list of commands here)

No keyword argument, then default values from MIB are used
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

All keyword arguments optional, parameter name is required
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

packet = op.registerTMPacket(filingKey, apIds=, header=, body=, param=)

All keyword arguments optional, filing key has to be provided
Register packet (per filing key) only once and use reception updates from callback

Example:
    filingKey: 31900
    apIds=[53]  (default: all apIds ([]))
    header=True (default: False, defines if packet header data is transmitted in callbacks)
    body=True   (default: False, defines if packet body data is transmitted in callbacks)
    param=True  (default: True, defines if packet parameters are transmitted in callbacks)
     
packet.verifyPacketReception(timeout=) returns 'TIMEOUT' or 'RECEIVED'
Example: timeout=10, default is global packet timeout (no timeout Kwarg)
    
"""
#==============================================================================
# Imports                          
#==============================================================================
import sys
sys.path.append('AAIDL')
from Operator import Operator

op = Operator()

#==============================================================================
# Set output verbosity and logging level                        
#==============================================================================

# 1 - command information, injection and success are printed in 1 console
# 2 - Progressbar and spinners, printed in multiple consoles   
op.setVerbosity(1)

# Logging level 1 (critical info only) - 5 (detailed information)
op.configLogging('pyops_logfile.txt', 5)

#==============================================================================
# Set global timeout                          
#==============================================================================
op.setGlobalCommandTimeout(60) 
op.setGlobalPacketTimeout(180)  

#==============================================================================
# Connect and initialize                          
#==============================================================================
op.connect('192.168.197.50','20001')
op.initialize(terminal='konsole')

# register required TM packets and parameters (global usage)
YMEV1604mode = op.registerTMPacket(61604)
YMEV1572mode = op.registerTMPacket(61572)
YMTMD104 = op.registerTMParameter('YMTMD104')
YMTMD072 = op.registerTMParameter('YMTMD072')
YMTMD073 = op.registerTMParameter('YMTMD073')
YMTMD074 = op.registerTMParameter('YMTMD074')
YMTMD105 = op.registerTMParameter('YMTMD105')
YMTMD107 = op.registerTMParameter('YMTMD107')

# write test functions
def systemModesTest(ymp00120, ymtmd072, ymtmd073, ymtmd074, ymtmd105, ymtmd107, pktTimeout=None, pause=None):
    
    YMC22001 = op.createCommand('YMC22001')
    YMC22001.setCommandParameter('YMP00120', isEng=True, valueType='S', value=ymp00120)    
    op.printCommandInformation(YMC22001)   
    op.injectCommand(YMC22001)
           
    if YMEV1572mode.verifyPacketReception(timeout=pktTimeout) == 'TIMEOUT':
        # do something here 
        pass        
    
    if type(pause) == int:        
        op.pauseForExecution(pause)
        
    if YMTMD072.getLastValidValue() != ymtmd072:
        # do something here 
        pass        
    if YMTMD073.getLastValidValue() != ymtmd073:
        # do something here 
        pass       
    if YMTMD074.getLastValidValue() != ymtmd074:
        # do something here 
        pass        
    if YMTMD105.getLastValidValue() != ymtmd105:
        # do something here 
        pass        
    if YMTMD107.getLastValidValue() != ymtmd107:
        # do something here 
        pass

def fallbackSystemModesTest(*cmdArgs, fallbackOnly=False, pktTimeout=None):
    
    if fallbackOnly == False:
        YMC22001 = op.createCommand('YMC22001')
        YMC22001.setCommandParameter('YMP00120', isEng=True, valueType='S', value=cmdArgs[10])    
        op.printCommandInformation(YMC22001)   
        op.injectCommand(YMC22001)
               
        if YMEV1572mode.verifyPacketReception(timeout=pktTimeout) == 'TIMEOUT':
            # do something here 
            pass        
            
        if YMTMD072.getLastValidValue() != cmdArgs[11]:
            # do something here 
            pass        

    cmd = op.createCommand(cmdArgs[0])
    cmd.setCommandParameter(cmdArgs[1], isEng=True, valueType='S', value=cmdArgs[2])    
    op.printCommandInformation(cmd)   
    op.injectCommand(cmd)
        
    if YMEV1572mode.verifyPacketReception(timeout=pktTimeout) == 'TIMEOUT':
        # do something here 
        pass      

    if YMTMD072.getLastValidValue() != cmdArgs[3]:
        # do something here 
        pass 
    
    if YMTMD073.getLastValidValue() != cmdArgs[4]:
        # do something here 
        pass       
    if YMTMD074.getLastValidValue() != cmdArgs[5]:
        # do something here 
        pass        
    if YMTMD105.getLastValidValue() != cmdArgs[6]:
        # do something here 
        pass        
    if YMTMD107.getLastValidValue() != cmdArgs[7]:
        # do something here 
        pass

    YMC24101 = op.createCommand('YMC24101')
    YMC24101.setCommandParameter('YMP00013', isEng=True, valueType='S', value=cmdArgs[8])    
    YMC24101.setCommandParameter('YMP00003', isEng=True, valueType='S', value=cmdArgs[9])   
    op.printCommandInformation(YMC24101)   
    op.injectCommand(YMC24101)

    if YMEV1572mode.verifyPacketReception(timeout=pktTimeout) == 'TIMEOUT':
        # do something here 
        pass  

"""
###############################################################################
Start
###############################################################################
"""    

#==============================================================================
#Set all Subsystems (but TTC) to healthy
#==============================================================================

YMC24101_list = op.createCommand('YMC24101', numberOfCommands=5)

YMC24101_list[0].setCommandParameter('YMP00013', isEng=True, valueType='S', value='ACS Subsystem')
YMC24101_list[0].setCommandParameter('YMP00003', isEng=True, valueType='S', value='Healthy')
YMC24101_list[1].setCommandParameter('YMP00013', isEng=True, valueType='S', value='CDH Subsystem')
YMC24101_list[1].setCommandParameter('YMP00003', isEng=True, valueType='S', value='Healthy')
YMC24101_list[2].setCommandParameter('YMP00013', isEng=True, valueType='S', value='Payload Subsyste')
YMC24101_list[2].setCommandParameter('YMP00003', isEng=True, valueType='S', value='Healthy')
YMC24101_list[3].setCommandParameter('YMP00013', isEng=True, valueType='S', value='PSS Subsystem')
YMC24101_list[3].setCommandParameter('YMP00003', isEng=True, valueType='S', value='Healthy')
YMC24101_list[4].setCommandParameter('YMP00013', isEng=True, valueType='S', value='TCS Subsystem')
YMC24101_list[4].setCommandParameter('YMP00003', isEng=True, valueType='S', value='Healthy')

#==============================================================================
#Command TTC Subsytem to Comm mode
#==============================================================================
YMC24306 = op.createCommand('YMC24306')
YMC24306.setCommandParameter('YMP00106', isEng=True, valueType='S', value='Comm')

#Print command info (optional) and inject commands
op.printCommandInformation(YMC24101_list, YMC24306)
op.injectCommand(YMC24101_list, YMC24306)

#Check packet 
if YMEV1604mode.verifyPacketReception(timeout=20) == 'TIMEOUT':
    # make decision here
    #sys.exit(1)
    pass

#Check parameter
if YMTMD104.getLastValidValue() != 'Comm':
    # make decision here
    #sys.exit(1)
    pass

#==============================================================================
#Set system to safe mode and check
#==============================================================================
systemModesTest('Safe', 'Safe', 'Safe', 'Default', 'Default', 'Off', pktTimeout=20, pause=60)

#==============================================================================
#get all modes and health states to initialise the TM parameters, check system mode
#==============================================================================
YMC22102 = op.createCommand('YMC22102')
YMC22003 = op.createCommand('YMC22003')

op.printCommandInformation(YMC22102, YMC22003)
op.injectCommand(YMC22102, YMC22003)

op.pauseForExecution(5)

"""  
###############################################################################
Nominal System mode transitions part I 
###############################################################################
"""

#==============================================================================
# Set system to none mode and check
#==============================================================================
systemModesTest('None', 'None', 'Off', 'Off', 'Off', 'Off', pktTimeout=30)

#==============================================================================
#Set system to coarse nadir mode and check
#==============================================================================
systemModesTest('CoarseNadir', 'CoarseNadir', 'CoarseNadir', 'Default', 'Default', 'Off')

#============================================================================== 
#Set system to safe mode and check
#==============================================================================
systemModesTest('Safe', 'Safe', 'Safe', 'Default', 'Default', 'Off')

#==============================================================================
#Set system to coarse nadir mode and check
#==============================================================================
systemModesTest('CoarseNadir', 'CoarseNadir', 'CoarseNadir', 'Default', 'Default', 'Off')

#==============================================================================
#Set system to none mode and check
#==============================================================================
systemModesTest('None', 'None', 'Off', 'Off', 'Off', 'Off')

#============================================================================== 
#Set system to safe mode and check
#==============================================================================
systemModesTest('Safe', 'Safe', 'Safe', 'Default', 'Default', 'Off')

#==============================================================================  
#Set system to idle mode and check
#============================================================================== 
systemModesTest('Idle', 'Idle', 'Idle', 'Default', 'Default', 'Off')

#==============================================================================
#Set system to none mode and check
#==============================================================================
systemModesTest('None', 'None', 'Off', 'Off', 'Off', 'Off')

#==============================================================================  
#Set system to idle mode and check
#============================================================================== 
systemModesTest('Idle', 'Idle', 'Idle', 'Default', 'Default', 'Off')

#==============================================================================
#Set system to coarse nadir mode and check
#==============================================================================
systemModesTest('CoarseNadir', 'CoarseNadir', 'CoarseNadir', 'Default', 'Default', 'Off')

#==============================================================================  
#Set system to idle mode and check
#============================================================================== 
systemModesTest('Idle', 'Idle', 'Idle', 'Default', 'Default', 'Off')

#============================================================================== 
#Set system to safe mode and check
#==============================================================================
systemModesTest('Safe', 'Safe', 'Safe', 'Default', 'Default', 'Off')

""" 
###############################################################################
Nominal System mode transitions part II
###############################################################################
"""

#============================================================================== 
#Set system to boot mode and check
#============================================================================== 

YMC22001 = op.createCommand('YMC22001')
YMC22001.setCommandParameter('YMP00120', isEng=True, valueType='S', value='Boot')
op.printCommandInformation(YMC22001)
op.injectCommand(YMC22001)

op.pauseForExecution(60)

YMC22003 = op.createCommand('YMC22003')
op.printCommandInformation(YMC22003)
op.injectCommand(YMC22003)

op.pauseForExecution(10)

if YMTMD072.getLastValidValue() != 'Boot':
    # do something here 
    pass        
if YMTMD073.getLastValidValue() != 'Off':
    # do something here 
    pass       
if YMTMD074.getLastValidValue() != 'Boot':
    # do something here 
    pass        
if YMTMD105.getLastValidValue() != 'Off':
    # do something here 
    pass        
if YMTMD107.getLastValidValue() != 'Off':
    # do something here 
    pass

#============================================================================== 
#Set system to safe mode and check
#==============================================================================
systemModesTest('Safe', 'Safe', 'Safe', 'Default', 'Default', 'Off')

#==============================================================================  
#Set system to idle mode and check
#============================================================================== 
systemModesTest('Idle', 'Idle', 'Idle', 'Default', 'Default', 'Off')

#============================================================================== 
#Set system to rotation mode and check
#============================================================================== 
systemModesTest('Rotation', 'Rotation', 'Rotation', 'Default', 'Default', 'Off')

#==============================================================================  
#Set system to idle mode and check
#============================================================================== 
systemModesTest('Idle', 'Idle', 'Idle', 'Default', 'Default', 'Off')

#==============================================================================
#Set system to inertial pointing mode and check
#==============================================================================
systemModesTest('Inertial Pointin', 'Inertial Point', 'InertialPt', 'Default', 'Default', 'Off')

#==============================================================================  
#Set system to idle mode and check
#============================================================================== 
systemModesTest('Idle', 'Idle', 'Idle', 'Default', 'Default', 'Off')
 
#==============================================================================
#Set system to TargetPt_GS mode and check
#==============================================================================
systemModesTest('TargetPt_GScont', 'TargetPt_GS', 'TargetPt', 'Default', 'Default', 'Off')
 
#==============================================================================  
#Set system to idle mode and check
#============================================================================== 
systemModesTest('Idle', 'Idle', 'Idle', 'Default', 'Default', 'Off')

#==============================================================================
#Set system to nadir pointing mode and check
#==============================================================================
systemModesTest('Nadir Pointing', 'Nadir Pointing', 'NadirPt', 'Default', 'Default', 'Off')

#==============================================================================  
#Set system to idle mode and check
#============================================================================== 
systemModesTest('Idle', 'Idle', 'Idle', 'Default', 'Default', 'Off')

#============================================================================== 
#Set system to GENIUS mode and check
#============================================================================== 
systemModesTest('GENIUS', 'GENIUS', 'GENIUS', 'Default', 'Default', 'Off')
 
#==============================================================================  
#Set system to idle mode and check
#============================================================================== 
systemModesTest('Idle', 'Idle', 'Idle', 'Default', 'Default', 'Off')
systemModesTest('Idle', 'Idle', 'Idle', 'Default', 'Default', 'Off')
systemModesTest('Idle', 'Idle', 'Idle', 'Default', 'Default', 'Off')

#============================================================================== 
#Set system to safe mode and check
#==============================================================================
systemModesTest('Safe', 'Safe', 'Safe', 'Default', 'Default', 'Off')

#==============================================================================
#Set system to ACS_Test mode and check
#==============================================================================
systemModesTest('ACS_Test', 'ACS_Test', 'Safe', 'Default', 'Default', 'Off')

#============================================================================== 
#Set system to safe mode and check
#==============================================================================
systemModesTest('Safe', 'Safe', 'Safe', 'Default', 'Default', 'Off')
 
"""
###############################################################################
Fallback System mode transitions
###############################################################################
"""

#==============================================================================
#Set system to coarse nadir mode and trigger fallback to Safe
#==============================================================================
fallbackSystemModesTest('YMC24304', 'YMP00104', 'Off',
                        'Safe', 'Safe', 'Default', 'Default', 'Off', 
                        'PSS Subsystem', 'Healthy', 
                        'CoarseNadir', 'CoarseNadir')

#==============================================================================
#Set system to GENIUS mode and trigger fallback to Idle
#==============================================================================
fallbackSystemModesTest('YMC24305', 'YMP00105', 'Survival',
                        'Idle', 'Idle', 'Default', 'Default', 'Off', 
                        'TCS Subsystem', 'Healthy',
                        'GENIUS', 'GENIUS')

#==============================================================================
#Set system to Rotation mode and trigger fallback to Idle
#==============================================================================
fallbackSystemModesTest('YMC24305', 'YMP00105', 'Survival',
                        'Idle', 'Idle', 'Default', 'Default', 'Off', 
                        'TCS Subsystem', 'Healthy',
                        'Rotation', 'Rotation')

#==============================================================================
#Set system to Inertial Pointing mode and trigger fallback to Idle
#==============================================================================
fallbackSystemModesTest('YMC24301', 'YMP00101', 'GENIUS', 
                        'Idle', 'Idle', 'Default', 'Default', 'Off', 
                        'ACS Subsystem', 'Healthy',
                        'Inertial Pointin', 'Inertial Point')

#==============================================================================
#Set system to target pointing mode and trigger fallback to Idle
#==============================================================================
fallbackSystemModesTest('YMC24304', 'YMP00104', 'Off',
                        'Idle', 'Idle', 'Default', 'Default', 'Off', 
                        'PSS Subsystem', 'Healthy',
                        'TargetPt_GScont', 'TargetPt_GS')

#==============================================================================
#Set system to Nadir pointing mode and trigger fallback to Idle
#==============================================================================
fallbackSystemModesTest('YMC24305', 'YMP00105', 'Survival',
                        'Idle', 'Idle', 'Default', 'Default', 'Off', 
                        'TCS Subsystem', 'Healthy',
                        'Nadir Pointing', 'Nadir Pointing')

#==============================================================================
#trigger fallback from Idle to safe 
#==============================================================================
fallbackSystemModesTest('YMC24301', 'YMP00101', 'GENIUS', 
                        'Safe', 'Safe', 'Default', 'Default', 'Off', 
                        'ACS Subsystem', 'Healthy', fallbackOnly=True)

#==============================================================================
#trigger fallback from safe to safe
#==============================================================================
fallbackSystemModesTest('YMC24304', 'YMP00104', 'Off', 
                        'Safe', 'Safe', 'Default', 'Default', 'Off', 
                        'PSS Subsystem', 'Healthy', fallbackOnly=True)

#==============================================================================
#Set system to ACS_Test mode and trigger fallback to Idle
#==============================================================================
fallbackSystemModesTest('YMC24305', 'YMP00105', 'Survival',
                        # idle?
                        'Safe', 'Safe', 'Default', 'Default', 'Off', 
                        'TCS Subsystem', 'Healthy',
                        'ACS_Test', 'ACS_Test')

""" 
###############################################################################
End of test
###############################################################################
"""

#==============================================================================
#                 Unregister command manager, parameters and packets
#============================================================================== 
op.deregisterCommandMngr()
op.unregisterAllTmPackets()
op.unregisterAllTmParameters()   

#==============================================================================
#                       Write separate logfiles (if needed)
#==============================================================================   
    
#log files will be overwritten for each test
op.writeCommandLog('pyops_cmdLogfile.txt')
op.writePacketLog('pyops_packetLogfile.txt')
op.writeParameterLog('pyops_paramLogfile.txt')  
