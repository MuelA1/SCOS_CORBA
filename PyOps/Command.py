#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Class for command injection

Command -- describes command values, command injection and command status
"""

import IBASE, ITC, ITC_INJ
import TimeModule
import time, threading
from colorama import Fore, Back, Style
from operator import attrgetter
from tabulate import tabulate
import progressbar as pb
from subprocess import Popen
import os, sys
from blessings import Terminal
import logging

class Command():
       
    #__paramValueDict = {'0':'m_nullFormat','i':'m_shortFormat','I':'m_longFormat','u':'m_ushortFormat','U':'m_ulongFormat','F':'m_floatFormat','D':'m_doubleFormat','C':'m_charFormat','B':'m_booleanFormat','O':'m_octetFormat','S':'m_stringFormat','s':'m_bstringFormat','T':'m_timeFormat'}
    # cmdParameters[i].m_value._d_to_m
    #__stageList = ['s', 'D', 'R', 'G', 'T', 'O', 'A', 'S', '0', '1', '2', '3', '4', '5', 'C']
    
    __paramValueTypeDict = {'\x00':'Null', '0':'Null','i':'Short','I':'Long','u':'Ushort','U':'Ulong','F':'Float','D':'Double','C':'Char','B':'Boolean','O':'Octet','S':'String','s':'Bstring','T':'Time'}
    __paramRadixDict = {'B':'Binary','O':'Octal','D':'Decimal','H':'Hexa'}   
    __checkStateTypeDict = {'E':'Enabled', 'D':'Disabled', 'O':'Override', 'N':'No notification'}
    
    __stageDict = {'s':'PTV_STATIC','D':'PTV_DYNAMIC','R':'MCS_RELEASE','G':'UV_GS_RECEIVE','T':'UV_GS_UPLINK','O':'UV_ONB_ACCEPT','A':'EV_APP_ACCEPT',
                   'S':'EV_START_EXEC','0':'EV_PROGRESS_0','1':'EV_PROGRESS_1','2':'EV_PROGRESS_2','3':'EV_PROGRESS_3','4':'EV_PROGRESS_4','5':'EV_PROGRESS_5',
                   '6':'EV_PROGRESS_6','7':'EV_PROGRESS_7','8':'EV_PROGRESS_8','9':'EV_PROGRESS_9','C':'EV_END_EXEC'}
        
    __statusDict = {0x0001:'NOT_APPLICABLE',0x0002:'PASSED',0x0004:'UNCERTAIN_PASSED',0x0008:'UNVERIFIED',0x0010:'IDLE',0x0020:'PENDING',0x0040:'DISABLED',0x0080:'FAILED',
                    0x0100:'UNCERTAIN_FAILED',0x0200:'UNKNOWN',0x0400:'AFFECTED',0x0800:'SUPERSEDED',0x1000:'TIMEOUT',0x2000:'ASSUMED',0x4000:'SCC'}
     
    # global command status callback list
    __commandStatusListStatic = []
    
    # global system status callback list
    __systemStatusListStatic = []
    
    __cmdList = []
    __cmdCount = 0
    __globalTimeout = 60
    
    __lock = threading.Lock()
    __injectionLock = threading.Lock()
    
    __cmdTerm = Terminal()
    __cbTerm = None
    __PIPE_PATH_Callb = None
        
    __cmdInjMngr = None
    __commandServerMngr = None
    
    __pbMarker = ['Waiting for command callbacks... ', pb.AnimatedMarker()]
    __animMarker = pb.ProgressBar(widgets=__pbMarker)
    
    __callbackTableHeaders = ['Stage', 'Status', 'Time']
    __paramStyleHeaders = [Style.BRIGHT + 'Name', 'Description', 'Eng. Val', 'Unit', 'Radix', 'Value Type', 'Value' + Style.RESET_ALL]
    __paramLogHeaders = ['Name', 'Description', 'Eng. Val', 'Unit', 'Radix', 'Value Type', 'Value']
    
    __verbosityLevel = 2
    
    __passedCounter = 0
    __failedCounter = 0
    __timeoutCounter = 0
    
    def __init__(self, name, description, absReleaseTime=IBASE.Time(0,0,False), relReleaseTime=None, absExecutionTime=IBASE.Time(0,0,False), staticPtv='D', dynamicPtv='D', cev=True, timeout=None, interlock=None):
        
        self.__cmdList.append(self)
        type(self).__cmdCount += 1
        self.__instCount = self.__cmdCount
        
        self.__cmdDescription = description

        if timeout is None:
            self.__timeout = self.__globalTimeout        
        else:
            self.__timeout = timeout

        if type(absReleaseTime) == str:
            self.__absReleaseTime = TimeModule.scosDate2ibaseTime(absReleaseTime)
            if TimeModule.ibaseTime2stamp(self.__absReleaseTime) < time.time():
                raise Exception('Release time <<' + absReleaseTime + '>> from the past is used')                                   
            self.__timeoutTimestamp = TimeModule.ibaseTime2stamp(self.__absReleaseTime) + self.__timeout
            
        else:
            self.__absReleaseTime = absReleaseTime
            self.__timeoutTimestamp = None
               
        self.__relReleaseTime = relReleaseTime                    
               
        if type(absExecutionTime) == str:            
            self.__absExecutionTime = TimeModule.scosDate2ibaseTime(absExecutionTime)
            self.__timeoutTimestamp = TimeModule.ibaseTime2stamp(self.__absExecutionTime) + self.__timeout
            if TimeModule.ibaseTime2stamp(self.__absExecutionTime) < time.time():
                raise Exception('Execution time <<' + absExecutionTime + '>> from the past is used')        
        else:
            self.__absExecutionTime = absExecutionTime
            
        self.__staticPtv = staticPtv
        self.__dynamicPtv = dynamicPtv
        self.__cev = cev
         
        self.__injectionTime = IBASE.Time(0,0,False)
        
        self.__context = ''
        self.__destination = ''
        self.__mapId = ITC_INJ.MAPID_DEFAULT
        self.__vcId = ITC_INJ.VCID_DEFAULT
        self.__cmdName = name
        self.__cmdParameters = []
        self.__paramSets = []
        self.__info = None
        self.__ilockType = 'N'
        self.__ilockStageType = '0'
        self.__additionalInfo = ''
        self.__tcRequestID =  0
               
        self.__injRequestID = 0                    
        self.__cmdMIBDef = None
        self.__completeCmdParameters = []        
        self.__commandStatusList = []
        self.__paramIsModified = []
       
        self.__globalCallbackCounter = 0
        self.__localCallbackCounter = 0
        self.__callbackThread = None
        if self.__cmdCount > 1:
            self.__lastCommand = self.__cmdList[self.__instCount - 2]
        else:
            self.__lastCommand = None
                                
        self.__repeaterGroup = {}
        self.__repeaterGroupName = {}
        #self.__repeaterCountValues = {}
        #self.__repeaterCountIndex = 0
        
        self.__callbackCompletedStage = None
        self.__callbackCompletedStatus = None       
        self.__callbackCompletedTime = None
        
        self.__interlock = interlock       
        if self.__interlock == []:
            self.__interlock.append('PASSED')
            self.__interlock.append('FAILED')
            self.__interlock.append('TIMEOUT')
                                               
        self.__callbackTableRows = []
        self.__paramStyleTableRows = []
                    
        pbWidgets = [Fore.WHITE + Back.BLUE + Style.BRIGHT + self.__cmdName + Style.RESET_ALL + Style.BRIGHT, pb.Bar(fill='_'), ' ', pb.Percentage(), ' ', pb.ETA(), Style.RESET_ALL]
        self.__bar = pb.ProgressBar(widgets=pbWidgets, min_value=0, term_width=115)
        
        if self.__interlock is not None:
            ilockWidgets = ['Waiting for interlock status...', pb.BouncingBar(marker=pb.RotatingMarker())]
            self.__ilockBar = pb.ProgressBar(widgets=ilockWidgets, term_width=43)
        
        print(f'Command {self.__instCount} (' + Style.BRIGHT + f'{self.__cmdName}' + Style.RESET_ALL + f') is created @ {TimeModule.ibaseTime2SCOSdate(TimeModule.stamp2ibaseTime(time.time()))}...') 
        logging.debug(f'Command {self.__instCount} ({self.__cmdName}) is created...')
        self.__flush()
        
        #self.__call = 0
             
#    def __repr__(self):
#        
#        string = f'\nCommand status {self.__instCount} {self.__cmdName:=^89}\n\n'
#        string += 'name: {} \ndescription: {} \nparameters: {} \nrequestID: {} \n\ninjectionTime: {} \nreleaseTime: {} \nrelReleaseTime: {} \nexecutionTime: {} \ntimeout: {} sec \ntimeoutTime: {} \n\nstaticPtv: {} \ndynamicPtv: {} \ncev: {} \n{}'.format(self.__cmdName,
#                   self.__cmdDescription, self.__cmdParameters, self.__injRequestID, TimeModule.ibaseTime2SCOSdate(self.__injectionTime), TimeModule.ibaseTime2SCOSdate(self.__absReleaseTime), self.__relReleaseTime, TimeModule.ibaseTime2SCOSdate(self.__absExecutionTime), self.__timeout,
#                   TimeModule.ibaseTime2SCOSdate(TimeModule.stamp2ibaseTime(self.__timeoutTimestamp)), self.__staticPtv, self.__dynamicPtv, self.__cev, self)
#        
#        return string
    
    def __str__(self):
    
        if self.__instCount > 999:
            disp = 82
        elif self.__instCount > 99:
            disp = 83
        elif self.__instCount > 9:
            disp = 84
        else:
            disp = 85
            
        string = '\n' + '*' * 95
        string += f'\nCommand {self.__instCount} {self.__cmdName:=^{disp}}\n' 
        string += '*' * 95 + '\n\n' 
                  
        string += 'Description ' + '-' * 83 + '\n\n'
        string += f'{self.__cmdDescription}\n\n'
        
        string += 'Parameters ' + '-' * 84 + '\n\n'
        
        if self.__cmdParameters != []:
            
            i = 0
            paramLogTableRows = []
            while i < len(self.__cmdParameters):
                paramLogTableRows.append([self.__cmdParameters[i].m_name, self.__completeCmdParameters[i].m_description, self.__cmdParameters[i].m_isEngValue, 
                                                 self.__cmdParameters[i].m_unit, self.__paramRadixDict.get(self.__cmdParameters[i].m_radix), 
                                                 self.__paramValueTypeDict.get(vars(self.__cmdParameters[i].m_value).get('_d')), vars(self.__cmdParameters[i].m_value).get('_v')])            
                i += 1
                
            string += tabulate(paramLogTableRows, headers=self.__paramLogHeaders)
            string += '\n\n'
        else:
            string += f'Command {self.__cmdName} has no parameters\n\n'
                
        string += 'Time status ' + '-' * 83 + '\n\n'
        
        string += f'Injection time: {TimeModule.ibaseTime2SCOSdate(self.__injectionTime)}\n'        
        if self.__relReleaseTime is None:
            string += f'Release time:   {TimeModule.ibaseTime2SCOSdate(self.__absReleaseTime)} (Relative release time: -)\n'
        else:
            string += f'Release time:   {TimeModule.ibaseTime2SCOSdate(self.__absReleaseTime)} (Relative release time: {self.__relReleaseTime})\n'
        string += f'Execution time: {TimeModule.ibaseTime2SCOSdate(self.__absExecutionTime)}\n' 
        string += f'Timeout time:   {TimeModule.ibaseTime2SCOSdate(TimeModule.stamp2ibaseTime(self.__timeoutTimestamp))} ({self.__timeout} sec)\n\n'

        string += 'Interlock status ' + '-' * 78 + '\n\n'

        if self.__interlock is not None:
            string += '%s' % ', '.join(map(str, self.__interlock))
            string += '\n\n'
        else:
            string += ' -\n\n'
        
        string += 'Check status ' + '-' * 82 + '\n\n'
        
        string += f'Static PTV:  {self.__checkStateTypeDict.get(self.__staticPtv)}\n'
        string += f'Dynamic PTV: {self.__checkStateTypeDict.get(self.__dynamicPtv)}\n'
        string += f'CEV:\t     {self.__cev}\n\n'
        
        string += 'Callback status ' + '-' * 79 + '\n\n'
        
        if self.__callbackTableRows != []:
            string += tabulate(self.__callbackTableRows, headers=self.__callbackTableHeaders)
            string += f'\n\nCompleted stage:  {self.__callbackCompletedStage}\n'
            string += f'Completed status: {self.__callbackCompletedStatus}\n'
            string += f'Completed time:   {TimeModule.ibaseTime2SCOSdate(self.__callbackCompletedTime)}\n\n'            
        else:
            string += f'Command {self.__cmdName} received no callback\n\n'
            
        string += '-' * 95 + '\n'
        string += f'End of command {self.__instCount} ({self.__cmdName})\n'
        string += '-' * 95 
        
        return string    
                                     
    def printCommandInfo(self):
        """ Method for printing the command information before the injection """ 
        
        if self.__instCount > 999:
            disp = 82
        elif self.__instCount > 99:
            disp = 83
        elif self.__instCount > 9:
            disp = 84
        else:
            disp = 85
            
        print('\n' + self.__cmdTerm.bold('*') * 95 + '\n' + Back.BLUE + Style.BRIGHT + f'Command {self.__instCount} {self.__cmdName:=^{disp}}' + Style.RESET_ALL + '\n' + self.__cmdTerm.bold('*') * 95 + '\n')     
        self.__flush()
                             
        print(self.__cmdTerm.bold('Description ') + '-' * 83 + f'\n\n{self.__cmdDescription}\n\n' + self.__cmdTerm.bold('Parameters ') + '-' * 84 + '\n')
        
        if self.__cmdParameters != []:
            i = 0
            userInput = False
            isEditable = True
            isModified = False            
            while i < len(self.__cmdParameters):
                # user input
                if vars(self.__cmdParameters[i].m_value).get('_d') == '0' and vars(self.__cmdParameters[i].m_value).get('_v') == False:
                    userValName = Fore.RED + Style.BRIGHT + self.__cmdParameters[i].m_name + Style.RESET_ALL
                    # counter
                    if self.__completeCmdParameters[i].m_repeatSize > 0:
                        userValName = userValName + ' (Counter)'      
                    userValType = self.__paramValueTypeDict.get(vars(self.__cmdParameters[i].m_value).get('_d'))
                    if userValType == 'Null':
                        userValType = Fore.RED + Style.BRIGHT + userValType + Style.RESET_ALL
                    userVal = Fore.RED + Style.BRIGHT + f"{vars(self.__cmdParameters[i].m_value).get('_v')}" + Style.RESET_ALL
                    self.__paramStyleTableRows.append([userValName, self.__completeCmdParameters[i].m_description, self.__cmdParameters[i].m_isEngValue, self.__cmdParameters[i].m_unit, self.__paramRadixDict.get(self.__cmdParameters[i].m_radix), userValType, userVal])
                    userInput = True
                # editable   
                elif self.__completeCmdParameters[i].m_isEditable == False:
                    notEditName = Fore.YELLOW + Style.BRIGHT + self.__cmdParameters[i].m_name + Style.RESET_ALL                                                     
                    self.__paramStyleTableRows.append([notEditName, self.__completeCmdParameters[i].m_description, self.__cmdParameters[i].m_isEngValue, self.__cmdParameters[i].m_unit, self.__paramRadixDict.get(self.__cmdParameters[i].m_radix), self.__paramValueTypeDict.get(vars(self.__cmdParameters[i].m_value).get('_d')), vars(self.__cmdParameters[i].m_value).get('_v')])
                    isEditable = False
                # modified    
                elif self.__paramIsModified[i][4] == True:
                    modName = Fore.BLUE + Style.BRIGHT + f'{self.__cmdParameters[i].m_name}' + Style.RESET_ALL
                    # counter
                    if self.__completeCmdParameters[i].m_repeatSize > 0:
                        modName = modName + ' (Counter)'
                    if self.__paramIsModified[i][0] == True:
                        modEngVal = Fore.BLUE + Style.BRIGHT + f'{self.__cmdParameters[i].m_isEngValue}' + Style.RESET_ALL
                    else:
                        modEngVal = self.__cmdParameters[i].m_isEngValue
                    if self.__paramIsModified[i][1] == True:
                        modUnit = Fore.BLUE + Style.BRIGHT + f'{self.__cmdParameters[i].m_unit}' + Style.RESET_ALL
                    else:
                        modUnit = self.__cmdParameters[i].m_unit
                    if self.__paramIsModified[i][2] == True:       
                        modRadix = Fore.BLUE + Style.BRIGHT + f'{self.__paramRadixDict.get(self.__cmdParameters[i].m_radix)}' + Style.RESET_ALL 
                    else:    
                        modRadix = self.__paramRadixDict.get(self.__cmdParameters[i].m_radix)
                    if self.__paramIsModified[i][3] == True:             
                        modValueType = Fore.BLUE + Style.BRIGHT + self.__paramValueTypeDict.get(vars(self.__cmdParameters[i].m_value).get('_d')) + Style.RESET_ALL
                        modValue = Fore.BLUE + Style.BRIGHT + f"{vars(self.__cmdParameters[i].m_value).get('_v')}"  + Style.RESET_ALL
                    else: 
                        modValueType = self.__paramValueTypeDict.get(vars(self.__cmdParameters[i].m_value).get('_d'))    
                        modValue = vars(self.__cmdParameters[i].m_value).get('_v')   
                 
                    isModified = True                                                           
                    self.__paramStyleTableRows.append([modName, self.__completeCmdParameters[i].m_description, modEngVal, modUnit, modRadix, modValueType, modValue])
                else:                             
                    self.__paramStyleTableRows.append([self.__cmdParameters[i].m_name, self.__completeCmdParameters[i].m_description, self.__cmdParameters[i].m_isEngValue, self.__cmdParameters[i].m_unit, self.__paramRadixDict.get(self.__cmdParameters[i].m_radix), self.__paramValueTypeDict.get(vars(self.__cmdParameters[i].m_value).get('_d')), vars(self.__cmdParameters[i].m_value).get('_v')])
                                
                i += 1
                                
            print(tabulate(self.__paramStyleTableRows, headers=self.__paramStyleHeaders), end='\n\n')            
            self.__flush()
            
            if self.__repeaterGroupName != {}:           
                for rep in self.__repeaterGroupName.keys():                
                    print(f'Counter: {rep} - Group: ' + '%s' % ', '.join(map(str, self.__repeaterGroupName[rep])))
                                
            if userInput == True:
                print(Fore.RED + Style.BRIGHT + 'User input necessary' + Style.RESET_ALL)             
            if isEditable == False:
                print(Fore.YELLOW + Style.BRIGHT + 'Not editable' + Style.RESET_ALL)                                      
            if isModified == True:
                print(Fore.BLUE + Style.BRIGHT + 'Modified parameter(s)', Style.RESET_ALL)
                       
        else:
            print(f'Command {self.__cmdName} has no parameters')
        
        # time          
        print('\n' + self.__cmdTerm.bold('Time ') + '-' * 90 + '\n')        
        if self.__relReleaseTime == None:           
            print(f'Release time: {TimeModule.ibaseTime2SCOSdate(self.__absReleaseTime)} \nRelative release time: - \nExecution time: {TimeModule.ibaseTime2SCOSdate(self.__absExecutionTime)}')
            
        else:
            print(f'Release time: To be calculated \nRelative release time: {self.__relReleaseTime} \nExecution time: {TimeModule.ibaseTime2SCOSdate(self.__absExecutionTime)}')
                
        if self.__timeout == self.__globalTimeout:
            print(f'Timeout: {self.__timeout} sec (default)')
            
        else:
            print(Fore.BLUE + Style.BRIGHT + f'Timeout: {self.__timeout} sec (modified)' + Style.RESET_ALL)
        
        # interlock
        print('\n' + self.__cmdTerm.bold('Interlock ') + '-' * 85 + '\n')
        if self.__interlock is not None:
            print('%s' % ', '.join(map(str, self.__interlock)))
        else:
            print(' -')
         
        # checks     
        print('\n' + self.__cmdTerm.bold('Check status ') + '-' * 82 + '\n')          
        print(f'PTV static: {self.__checkStateTypeDict.get(self.__staticPtv)} \nPTV dynamic: {self.__checkStateTypeDict.get(self.__dynamicPtv)} \nCEV: {self.__cev}')      
        
        print('\n' + self.__cmdTerm.bold('-') * 95 + '\n')    
        
    def printCallback(self):
        """ Method for printing the full callback """   
               
        # lock thread while printing, for clean output print
        self.__lock.acquire()
        try: 
             
            compStatus = None
            if self.__callbackCompletedStatus == 'PASSED':   
                compStatus = Fore.GREEN + self.__callbackCompletedStatus + Style.RESET_ALL
                type(self).__passedCounter += 1
            elif self.__callbackCompletedStatus == 'FAILED':
                compStatus = Fore.RED + self.__callbackCompletedStatus + Style.RESET_ALL
                type(self).__failedCounter += 1
            elif self.__callbackCompletedStatus == 'TIMEOUT': 
                compStatus = Fore.YELLOW + self.__callbackCompletedStatus + Style.RESET_ALL
                type(self).__timeoutCounter += 1
                
            if self.__verbosityLevel == 2:
                
                if self.__instCount > 999:
                    disp = 55
                elif self.__instCount > 99:
                    disp = 56
                elif self.__instCount > 9:
                    disp = 57
                else:
                    disp = 58
                               
                with open(self.__PIPE_PATH_Callb, 'w') as cbTerminal:                                          
                    cbTerminal.write('\n' + self.__cbTerm.bold('*') * 75 + '\n' + Fore.WHITE + Back.BLACK + Style.BRIGHT + f'Command status {self.__instCount} {self.__cmdName:=^{disp}}' + Style.RESET_ALL + '\n' + self.__cbTerm.bold('*') * 75 + '\n')   
                                         
                    cbTerminal.write(f'\nDescription:    {self.__cmdDescription} \nRelease Time:   {TimeModule.ibaseTime2SCOSdate(self.__absReleaseTime)} \nExecution Time: {TimeModule.ibaseTime2SCOSdate(self.__absExecutionTime)}\n')
                                
                    # interlock
                    if self.__interlock is not None:
                        cbTerminal.write('Interlock:      ' + '%s' % ', '.join(map(str, self.__interlock)) + '\n\n')
                    else:
                        cbTerminal.write('Interlock:      -\n\n')
                                                      
                    if self.__callbackCompletedStatus == 'PASSED':                
                        cbTerminal.write(self.__cbTerm.green(tabulate(self.__callbackTableRows, headers=self.__callbackTableHeaders)))                        
                    elif self.__callbackCompletedStatus == 'FAILED':                     
                        cbTerminal.write(self.__cbTerm.red(tabulate(self.__callbackTableRows, headers=self.__callbackTableHeaders)))                        
                    elif self.__callbackCompletedStatus == 'TIMEOUT':                 
                        cbTerminal.write(self.__cbTerm.yellow(tabulate(self.__callbackTableRows, headers=self.__callbackTableHeaders)))
                                            
                    cbTerminal.write('\n\n')
                    
                    if self.__statusDict.get(self.__commandStatusList[-1].m_stage_status) == 'UNKNOWN':
                        cbTerminal.write(self.__cbTerm.bold + f'Command {self.__instCount}/{self.__cmdCount}: {self.__cmdName} exceeded SCOS Timeout\n' + self.__cbTerm.normal)
                        
                    cbTerminal.write(self.__cbTerm.bold + f'Command {self.__instCount}/{self.__cmdCount}: {self.__cmdName} completed with status ' + self.__cbTerm.normal + '<<' + compStatus + '>>\n')
                    
            elif self.__verbosityLevel == 1:  
                print(f'Command {self.__instCount} (' + Style.BRIGHT + f'{self.__cmdName}' + Style.RESET_ALL + ') completed with status <<' + compStatus + f'>> @ {TimeModule.ibaseTime2SCOSdate(self.__callbackCompletedTime)}...', end='\n')
                self.__flush()    
        finally:       
            self.__lock.release()
      
    def setCommandDef(self, cmdDef):
        self.__cmdMIBDef = cmdDef
         
    def getCallbackCompletedStatus(self):
        return self.__callbackCompletedStatus
    
#    def setCommandInterlock(self, ilockList):        
#        self.__interlock = ilockList
#                          
#    def getCommandInterlock(self):
#        return self.__interlock

    def getReleaseTime(self):
        return self.__absReleaseTime
    
    def setReleaseTime(self, absReleaseTime):
        self.__absReleaseTime = absReleaseTime
                                                                                          
    def getTimeoutStamp(self):
        return self.__timeoutTimestamp
    
    def getInjRequestID(self):
        return self.__injRequestID

    def getInstCount(self):
        return self.__instCount
            
    # set default MIB command parameters (different structure for injection)
    def setMIBCommandParameters(self, counter=None):

        repeater = False        
        repParams = []
        counterInRepGroup = []
        
        # get repeater group, if repeated parameters exist
        i = 0           
        while i < len(self.__cmdMIBDef.m_params):           
            if self.__cmdMIBDef.m_params[i].m_repeatSize > 0:
                startGroupIndex = i+1
                endGroupEndex = i + self.__cmdMIBDef.m_params[i].m_repeatSize
                tempRepeatGroupName = []
                tempRepeatGroup = []
                                
                while startGroupIndex <= endGroupEndex:
                    tempRepeatGroupName.append(self.__cmdMIBDef.m_params[startGroupIndex].m_name)
                    repParams.append(self.__cmdMIBDef.m_params[startGroupIndex].m_name)
                    tempRepeatGroup.append(self.__cmdMIBDef.m_params[startGroupIndex])
                    
                    if self.__cmdMIBDef.m_params[startGroupIndex].m_repeatSize is not 0:
                        counterInRepGroup.append(self.__cmdMIBDef.m_params[startGroupIndex].m_name)
                    
                    startGroupIndex += 1
                    
                self.__repeaterGroupName[self.__cmdMIBDef.m_params[i].m_name] = tempRepeatGroupName
                
                # key: counter, value: parameter to be repeated
                self.__repeaterGroup[self.__cmdMIBDef.m_params[i].m_name] = tempRepeatGroup
                                                
                repeater = True
         
            i += 1
         
        # set default parameters, no repeater    
        if repeater == False:                       
            for param in self.__cmdMIBDef.m_params:                 
                self.__setDefaultParam(param)
        
        # set default parameters, repeater exists                       
        else:                                
            if counter is None:     
                for rep in self.__repeaterGroupName.keys():                   
                    raise Exception(f'Please set counter value ({rep} - Group: ' + '%s' % ', '.join(map(str, self.__repeaterGroupName[rep])) + f') for command {self.__instCount} - {self.__cmdName}')             
                                                
            for param in self.__cmdMIBDef.m_params:  
                                               
                if param.m_repeatSize is not 0 and param.m_name not in counterInRepGroup: 
                    #logging.debug(f'Loop call with: {param.m_name}')
                    #self.__call += 1
                    self.__setCounterAndParameters(param, counter, 0)
                
                elif param.m_name not in repParams:
                    self.__setDefaultParam(param)
                    #logging.debug(f'NO Counter {self.__call} ' + param.m_name)
                     
    def __setCounterAndParameters(self, param, counter, j):

        self.__call += 1
        
        # ('DSP00006', 3, 3): counterParam
        for counterParam in counter:
            if counterParam[0] == param.m_name:    
                           
                # set counter    
                #logging.debug(f'Current parameter: {param.m_name}' + f' (Rec. call {self.__call})')                           
                paramStruct = ITC.CommandParam(param.m_name, param.m_engValueIsDefault, param.m_unit, param.m_defaultRadix, IBASE.Variant('U', counterParam[1]))    
                self.__cmdParameters.append(paramStruct)
                self.__completeCmdParameters.append(param)
                self.__paramIsModified.append([False, False, False, True, True]) 
                #logging.debug('Counter: ' + counterParam[0] + f' (Rec. call {self.__call})')
                
                #j = 0
                while j < counterParam[1]:
                    for repParam in self.__repeaterGroup[counterParam[0]]:
                                                   
                        # counter in repeated group
                        if repParam.m_repeatSize is not 0:
                            #logging.debug(f'Recursive call with: {repParam.m_name}')                           
                            #logging.debug(f'Counter parameter: {counterParam}')
#                            for counterParam in counter:
#                                if counterParam[0] == repParam.m_name and len(counterParam) > 2:
#                                   counterParam.remove(counterParam[1])                                    
                            self.__setCounterAndParameters(repParam, counter, 1)
                            
                        # set number of counter parameters 
                        else:
                            self.__setDefaultParam(repParam)
                            #logging.debug(f'Appended parameter: ' + repParam.m_name + f' (Rec. call {self.__call})')                        
                                                                        
                    j += 1

                    if j == counterParam[1]:
                        if len(counterParam) == 2:                               
                            if counter == []:
                                return 1
                            del counter[0]                               
                            #logging.debug('Return ' + str(counter) + f' (Rec. call {self.__call})')
                            return 1
                        else:
                            counterParam.remove(counterParam[1])
                            #logging.debug('Return ' + str(counter) + f' (Rec. call {self.__call})')
                            return 1

    def __setDefaultParam(self, param):
        
        paramStruct = ITC.CommandParam(param.m_name, param.m_engValueIsDefault, param.m_unit, param.m_defaultRadix, param.m_defaultValue)                
        self.__cmdParameters.append(paramStruct)                           
        self.__completeCmdParameters.append(param)
        # vector which describes if parameter is modified in method setCommandParameter 
        self.__paramIsModified.append([False, False, False, False, False])          
                                                                                        
    def setCommandParameter(self, name, isEng=None, unit=None, radix=None, valueType=None, value=None):
         
        logging.debug(f'Command {self.__instCount} ({self.__cmdName}) is setting command parameter {name}...')
        i = 0
        while i < len(self.__cmdParameters): 
            if self.__cmdParameters[i].m_name == name:               
                if self.__paramIsModified[i][4] == False:                   
                    if self.__completeCmdParameters[i].m_isEditable == True:  
                        if isEng is not None:
                            self.__cmdParameters[i].m_isEngValue = isEng
                            self.__paramIsModified[i][0] = True
                            self.__paramIsModified[i][4] = True                            
                        if unit is not None:
                            self.__cmdParameters[i].m_unit = unit
                            self.__paramIsModified[i][1] = True
                            self.__paramIsModified[i][4] = True  
                        if radix is not None:
                            self.__cmdParameters[i].m_radix = radix
                            self.__paramIsModified[i][2] = True
                            self.__paramIsModified[i][4] = True                         
                        if value is not None and valueType is not None:                                        
                            self.__cmdParameters[i].m_value = IBASE.Variant(valueType, value)
                            self.__paramIsModified[i][3] = True
                            self.__paramIsModified[i][4] = True                         
                        elif valueType is not None:
                            raise Exception(f'Please enter a corresponding value for value type {self.__paramValueTypeDict.get(valueType)}')
                        elif value is not None:
                            raise Exception(f'Please enter a corresponding value type for value {value}')                                                                                           
                    break                   
            if self.__cmdParameters[i] == self.__cmdParameters[-1]:
                raise Exception(f'Parameter does not exist in command {self.__cmdName}') 
            i += 1
                                                         
    def injectCommand(self):
                
        try: 
            self.__flush() 
            self.__injectionLock.acquire()
            
            # relative release time (timeout here?)
            if self.__lastCommand is not None and type(self.__relReleaseTime) == str:
                while(str(self.__lastCommand.getReleaseTime()) == str(IBASE.Time(0,0,False))):
                    pass

                self.__absReleaseTime = TimeModule.calcRelativeReleaseTime(self.__lastCommand.getReleaseTime(), self.__relReleaseTime)         
                #timeout    
                if self.__timeoutTimestamp is None:
                    self.__timeoutTimestamp = TimeModule.ibaseTime2stamp(self.__absReleaseTime)  + self.__timeout                
            
            elif self.__lastCommand is None and type(self.__relReleaseTime) == str:
                raise Exception('Relative release time - previous command does not exist')
                     
            self.__info = ITC_INJ.ReleaseInfo(self.__absReleaseTime, IBASE.Time(0,0,False), IBASE.Time(0,0,False), self.__absExecutionTime, self.__staticPtv, self.__dynamicPtv, self.__cev, ITC_INJ.ACK_MIB_DEFAULT)    
            cmdRequest = ITC_INJ.CommandRequest(self.__context, self.__destination, self.__mapId, self.__vcId, self.__cmdName, self.__cmdParameters, self.__paramSets, self.__info, self.__ilockType, self.__ilockStageType, self.__additionalInfo, self.__tcRequestID)
            
            # wait until previous command is injected (pay attention if previous commands are not injected!)
            while self.__lastCommand is not None and self.__lastCommand.getInjRequestID() is 0:
                pass  
                                    
            # interlock
            if self.__interlock is not None:
                
                if self.__verbosityLevel == 2:
                    self.__ilockBar.start()
                    self.__flushBar()
                 
                if self.__lastCommand is None:
                    raise Exception('Interlock - previous command does not exist')
                for ilockStatus in self.__interlock:
                    if ilockStatus not in ['PASSED', 'FAILED', 'TIMEOUT']:
                        raise Exception("Interlock - please choose between 'PASSED', 'FAILED' and 'TIMEOUT'")
                                                                                                              
                logging.debug(f'Command {self.__instCount} ({self.__cmdName}) is waiting for interlock status type <<' + '%s' % ', '.join(map(str, self.__interlock)) + '>>...') 
                
                if self.__verbosityLevel == 2:
                    while self.__lastCommand.getCallbackCompletedStatus() not in self.__interlock:   
                        for i in self.__ilockBar(iter(lambda:0,1)):                                              
                            time.sleep(0.02)                         
                            if self.__lastCommand.getCallbackCompletedStatus() in self.__interlock:
                                break     
                            elif self.__lastCommand.getCallbackCompletedStatus() is not None:                     
                                raise Exception(f'Interlock - got illegal status <<{self.__lastCommand.getCallbackCompletedStatus()}>>')             
                    print(f'...got status <<{self.__lastCommand.getCallbackCompletedStatus()}>>')  
                              
                elif self.__verbosityLevel == 1:
                    print(f'Command {self.__instCount} (' + Style.BRIGHT + f'{self.__cmdName}' + Style.RESET_ALL + ') is waiting for interlock status <<' + '%s' % ', '.join(map(str, self.__interlock)) + '>>...', end='\n')
                    self.__flush()
                    while self.__lastCommand.getCallbackCompletedStatus() not in self.__interlock:                                        
                        time.sleep(0.1)
                        if self.__lastCommand.getCallbackCompletedStatus() in self.__interlock:
                            break     
                        elif self.__lastCommand.getCallbackCompletedStatus() is not None:                     
                            raise Exception(f'Interlock - got illegal status <<{self.__lastCommand.getCallbackCompletedStatus()}>>')                                                                                    
                    print(f'Command {self.__instCount} (' + Style.BRIGHT + f'{self.__cmdName}' + Style.RESET_ALL + f') received interlock status <<{self.__lastCommand.getCallbackCompletedStatus()}>>...', end='\n')
                                                  
                logging.debug(f'Command {self.__instCount} ({self.__cmdName}) received interlock status type <<{self.__lastCommand.getCallbackCompletedStatus()}>>...')
                self.__flush()
            
            if self.__verbosityLevel == 2:                                       
                # Release ASAP, finish bar immediately
                if str(self.__absReleaseTime) == str(IBASE.Time(0,0,False)):                                   
                    self.__bar.max_value = 200                         
                    self.__bar.start()         
                    self.__bar.finish()
                    self.__flushBar()
                    
                # Release time tagged
                else:                                  
                    releaseStamp = TimeModule.ibaseTime2stamp(self.__absReleaseTime)
                     
                    if releaseStamp - time.time() < 0.5:
                        self.__bar.max_value = 200
                        self.__bar.start()           
                        self.__bar.finish()
                        self.__flushBar()
                        
                    else:    
                        self.__bar.max_value = int(TimeModule.ibaseTime2stamp(self.__absReleaseTime) - time.time())                         
                        logging.debug(f'Command {self.__instCount} ({self.__cmdName}) is waiting ' + str(self.__bar.max_value) + ' sec for command injection...')
                        self.__bar.start()
        
                        for i in range(self.__bar.max_value):
                            self.__bar.update(i)                      
                            if releaseStamp - time.time() < 1.5:
                                break
                            time.sleep(1)
                                                
                        self.__bar.finish()           
                        self.__flushBar()
            
            elif self.__verbosityLevel == 1:
                # Release time tagged
                if str(self.__absReleaseTime) != str(IBASE.Time(0,0,False)):
                    tempTime = int(TimeModule.ibaseTime2stamp(self.__absReleaseTime) - time.time())
                    print(f'Command {self.__instCount} (' + Style.BRIGHT + f'{self.__cmdName}' + Style.RESET_ALL + ') is waiting ' + self.__cmdTerm.bold(str(tempTime) + ' sec') + ' for command injection...', end='\n')    
                    logging.debug(f'Command {self.__instCount} ({self.__cmdName}) is waiting ' + str(tempTime) + ' sec for command injection...')
                    self.__flush()
                    while TimeModule.ibaseTime2stamp(self.__absReleaseTime) - time.time() > 0.5:
                        pass           
                    
            self.__injRequestID = self.__cmdInjMngr.injectCmd(cmdRequest)
            self.__injectionTime = self.__commandServerMngr.getUTC()         
            
            if self.__verbosityLevel == 2:
                print(self.__cmdTerm.bold('Injecting ') + f'command {self.__instCount}/{self.__cmdCount}: {self.__cmdName} - {self.__cmdDescription} @ {TimeModule.ibaseTime2SCOSdate(self.__injectionTime)}...\n')
                             
            elif self.__verbosityLevel == 1:
                print(f'Command {self.__instCount} (' + Style.BRIGHT + f'{self.__cmdName}' + Style.RESET_ALL + f') is injected @ {TimeModule.ibaseTime2SCOSdate(self.__injectionTime)}...')
                
            logging.info(f'Command {self.__instCount} ({self.__cmdName}) is injected...')
            self.__flush()    
            self.__injectionLock.release()
            
            # start callback thread          
            self.__callbackThread = threading.Thread(target=self.getCommandStatus)
            self.__callbackThread.start()
                             
        except Exception as exception:      
            print(self.__cmdTerm.bold_red(f'\nCommand {self.__instCount}: {self.__cmdName} - Exception during command injection: ') + f'{exception}')
            logging.exception(f'Command {self.__instCount}: {self.__cmdName} - Exception during command injection: {exception}', exc_info=False)
            self.deregister(error=True)
                                                              
    def getCommandStatus(self):      
        """ Get callback for individual instance """
        
        try:          
            nextCall = time.time()            
            while getattr(self.__callbackThread, 'do_run', True):                              
                while self.__globalCallbackCounter < len(self.__commandStatusListStatic): 
                    
                    if self.__commandStatusListStatic[self.__globalCallbackCounter].m_request_id == self.__injRequestID:                       
                        self.__commandStatusList.append(self.__commandStatusListStatic[self.__globalCallbackCounter])
                          
                        # get release time if neccessary                
                        if self.__commandStatusList[self.__localCallbackCounter].m_stage == 's':
                            if str(self.__absReleaseTime) == str(IBASE.Time(m_sec=0, m_micro=0, m_isDelta=False)):
                                self.__absReleaseTime = TimeModule.scosDate2ibaseTime(self.__commandStatusList[self.__localCallbackCounter].m_updateTime)
                                
                                # set timeout
                                if self.__timeoutTimestamp is None:
                                    self.__timeoutTimestamp = TimeModule.ibaseTime2stamp(self.__absReleaseTime)  + self.__timeout

                        # get execution time if neccessary
                        if self.__commandStatusList[self.__localCallbackCounter].m_stage == 'S':
                            if str(self.__absExecutionTime) == str(IBASE.Time(m_sec=0, m_micro=0, m_isDelta=False)):
                                self.__absExecutionTime = TimeModule.scosDate2ibaseTime(self.__commandStatusList[self.__localCallbackCounter].m_updateTime)
                                             
                        self.__callbackTableRows.append([self.__stageDict.get(self.__commandStatusList[self.__localCallbackCounter].m_stage) + ' (' + self.__commandStatusList[self.__localCallbackCounter].m_stage + ')',
                                                         self.__statusDict.get(self.__commandStatusList[self.__localCallbackCounter].m_stage_status),
                                                         self.__commandStatusList[self.__localCallbackCounter].m_updateTime])                                                                                                    
                        
                        logging.debug(f'Command {self.__instCount} ({self.__cmdName}) received callback ({self.__commandStatusList[self.__localCallbackCounter].m_stage} - {self.__statusDict.get(self.__commandStatusList[self.__localCallbackCounter].m_stage_status)})...')
                        # callback finished, finish thread and print full callback
                        if self.__commandStatusList[self.__localCallbackCounter].m_completed_flag == True: 
                               
                            self.__callbackThread.do_run = False  
                            
                            self.__callbackCompletedTime = TimeModule.scosDate2ibaseTime(self.__commandStatusList[self.__localCallbackCounter].m_updateTime)
                            self.__callbackCompletedStage = self.__stageDict.get(self.__commandStatusList[self.__localCallbackCounter].m_stage)
                            self.__callbackCompletedStatus = self.__statusDict.get(self.__commandStatusList[self.__localCallbackCounter].m_stage_status)
                            
                            if self.__callbackCompletedStatus == 'FAILED':
                                logging.error(f'Command {self.__instCount} ({self.__cmdName}) {self.__callbackCompletedStatus} at stage {self.__callbackCompletedStage}...') 
                            else:
                                logging.info(f'Command {self.__instCount} ({self.__cmdName}) {self.__callbackCompletedStatus} at stage {self.__callbackCompletedStage}...')                                                                          
                            logging.info('\n' + str(self) + '\n')
                            
                            self.printCallback()
                                                   
                        self.__localCallbackCounter += 1    
                    self.__globalCallbackCounter += 1
                
                # timeout if callback is not completed 
                if self.__timeoutTimestamp is not None:
                    if self.__timeoutTimestamp - time.time() <= 0:
                        if self.__localCallbackCounter > 0 and self.__commandStatusList[self.__localCallbackCounter - 1].m_completed_flag == False:  
                               
                            self.__callbackThread.do_run = False
                            
                            self.__callbackCompletedTime = TimeModule.stamp2ibaseTime(time.time())
                            self.__callbackCompletedStage = ''
                            self.__callbackCompletedStatus = 'TIMEOUT'                        
                                                                            
                            logging.warning(f'Command {self.__instCount} ({self.__cmdName}) - {self.__callbackCompletedStatus}...') 
                            logging.info('\n' + str(self) + '\n')
                            self.printCallback()
                                                     
                # call method every 0.3 sec    
                nextCall += 0.3
                time.sleep(nextCall - time.time())

        except Exception as exception:
            self.__callbackThread.do_run = False
            print(self.__cmdTerm.bold_red(f'\nCommand {self.__instCount}: {self.__cmdName} - Exception during callback reception: ') + f'{exception}')            
            logging.exception(f'Command {self.__instCount}: {self.__cmdName} - Exception during callback reception: {exception}', exc_info=False)
            self.printCallback()
                       
    def __flush(self, sleep=0.015):
        
        sys.stdout.flush()
        time.sleep(sleep)
     
    def __flushBar(self, sleep=0.02):

        pb.streams.flush()
        sys.stdout.flush()
        time.sleep(sleep)        

    @classmethod
    def setCommandInjMngr(cls, cmdInjMngr):
        cls.__cmdInjMngr = cmdInjMngr
    
    @classmethod
    def setCommandServerMngr(cls, serverMngr):
        cls.__commandServerMngr = serverMngr
            
    @classmethod    
    def getUpdateRequestStatus(cls, status):
        status.m_updateTime = TimeModule.ibaseTime2SCOSdate(status.m_updateTime)
        cls.__commandStatusListStatic.append(status)
                
        #sort by time
        #sorted(cb.m_updateTime for cb in list1)
        #sorted(list1, key=lambda cb: cb.m_updateTime)
        cls.__commandStatusListStatic.sort(key=attrgetter('m_updateTime'))

    @classmethod        
    def getUpdateSystemStatus(cls, status):
        cls.__systemStatusListStatic.append(status)
               
    @classmethod    
    def getCommandList(cls):
        return cls.__cmdList
    
    @classmethod
    def getCommandCount(cls):
        return cls.__cmdCount
    
    @classmethod
    def createCallbackTerminal(cls, term, terminalType):
        
        cls.__cbTerm = term
        cls.__PIPE_PATH_Callb = '/tmp/callbackPipe'  
        
        if os.path.exists(cls.__PIPE_PATH_Callb):
            os.remove(cls.__PIPE_PATH_Callb)
         
        # named pipe                     
        os.mkfifo(cls.__PIPE_PATH_Callb)
            
        # new terminal subprocess (Test with different emulators: 'gnome-terminal', 'xterm', 'konsole',...) 
        Popen([terminalType, '-e', 'tail -f %s' % cls.__PIPE_PATH_Callb])   
          
        #os.environ.get('TERM') 
        with open(cls.__PIPE_PATH_Callb, 'w') as cbTerminal:
            cbTerminal.write('\n' +  cls.__cbTerm.bold('Waiting for command callbacks...') + '\n')
        
    @classmethod    
    def getGlobalCommandTimeout(cls):
        return cls.__globalTimeout
    
    @classmethod
    def setGlobalCommandTimeout(cls, globalTimeout):
        cls.__globalTimeout = globalTimeout
    
    @classmethod    
    def setVerbosityLevel(cls, verbLevel):
        cls.__verbosityLevel = verbLevel

    @classmethod    
    def getVerbosityLevel(cls):
        return cls.__verbosityLevel 
    
    @classmethod    
    def deregister(cls, error=False):
        """ Deregister callback interface and clear internal buffer """
        
        if error == False:                           
            logging.debug('Waiting for callback completion...')
            
            if cls.__verbosityLevel == 2:
                cls.__animMarker.start()
                time.sleep(0.02) 
                
                for cmd in cls.__cmdList:           
                    while cmd.__callbackCompletedStatus not in ['PASSED', 'FAILED', 'TIMEOUT']:                              
                        for i in cls.__animMarker(iter(lambda:0,1)):
                            time.sleep(0.02)                             
                            if cmd.__callbackCompletedStatus in ['PASSED', 'FAILED', 'TIMEOUT']:
                                if cmd.__callbackThread.isAlive():
                                    cmd.__callbackThread.do_run = False
                                break                        
                    continue            

                time.sleep(0.5)
                print('\n')
                with open(cls.__PIPE_PATH_Callb, 'w') as cbTerminal: 
                    with cls.__cbTerm.location(0, cls.__cbTerm.height - 1):                                         
                        cbTerminal.write('\n' + cls.__cbTerm.bold('=') * 75 + '\nEnd of callback reception\n' + cls.__cbTerm.bold('=') * 75 + '\n')
             
            elif cls.__verbosityLevel == 1:
                print('Waiting for command callbacks...')
                for cmd in cls.__cmdList:           
                    while cmd.__callbackCompletedStatus not in ['PASSED', 'FAILED', 'TIMEOUT']:                                                     
                        time.sleep(0.05)                             
                        if cmd.__callbackCompletedStatus in ['PASSED', 'FAILED', 'TIMEOUT']:
                            if cmd.__callbackThread.isAlive():
                                cmd.__callbackThread.do_run = False
                            break                        
                    continue                 
                                                                         
            print(Fore.GREEN + 'All callbacks received...' + Style.RESET_ALL)  
            logging.debug('All callbacks received...')
            cls.__cmdInjMngr.deregister()
            print('Unregistered from external command server...')
            logging.info('Unregistered from external command server...\n' + '=' * 100)
                       
            print(Style.BRIGHT + '=' * 95 + f'\nSuccessfully processed {cls.__cmdCount} commands...' + Style.RESET_ALL + '\n' +
                  Fore.GREEN + f'{cls.__passedCounter} commands passed' + Style.RESET_ALL + '...' + '\n' +
                  Fore.RED + f'{cls.__failedCounter} commands failed' + Style.RESET_ALL + '...' + '\n' +
                  Fore.YELLOW + f'{cls.__timeoutCounter} commands timed out' + Style.RESET_ALL + '...\n' + 
                  Style.BRIGHT + '=' * 95 + Style.RESET_ALL)
            
            logging.info(f'Successfully processed {cls.__cmdCount} commands...\n{cls.__passedCounter} commands passed...\n{cls.__failedCounter} commands failed...\n{cls.__timeoutCounter} commands timed out...' + '\n' + '=' * 100)                  
        
        if error == True:            
            for cmd in cls.__cmdList:  
                if cmd.__callbackThread.isAlive():
                    cmd.__callbackThread.do_run = False
                    
            cls.__cmdInjMngr.deregister()
            print('Unregistered from external command server...')
            logging.debug('Unregistered from external command server...')           
            sys.exit(1)
            
    absReleaseTime = property(getReleaseTime, setReleaseTime)
           