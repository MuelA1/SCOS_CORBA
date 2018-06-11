#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Class for command injection

Command -- describes command values, command injection and command status
"""

import IBASE, ITC, ITC_INJ
import TimeModule
import time, threading
from colorama import Fore, Back, Style
from prettytable import PrettyTable
from operator import attrgetter
import progressbar as pb
from subprocess import Popen
import os, sys
#import logging

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
    
    __cmdTerm = None
    __cbTerm = None
    __PIPE_PATH_Callb = None
        
    __cmdInjMngr = None
    __commandServerMngr = None
    
    __pbMarker = ['Waiting for command callbacks... ', pb.AnimatedMarker()]
    __animMarker = pb.ProgressBar(widgets=__pbMarker)
         
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
                raise Exception('Release time << ' + absReleaseTime + ' >> from the past is used')                                   
            self.__timeoutTimestamp = TimeModule.ibaseTime2stamp(self.__absReleaseTime) + self.__timeout
            
        else:
            self.__absReleaseTime = absReleaseTime
            self.__timeoutTimestamp = None
               
        self.__relReleaseTime = relReleaseTime                    
               
        if type(absExecutionTime) == str:            
            self.__absExecutionTime = TimeModule.scosDate2ibaseTime(absExecutionTime)
            self.__timeoutTimestamp = TimeModule.ibaseTime2stamp(self.__absExecutionTime) + self.__timeout
            if TimeModule.ibaseTime2stamp(self.__absExecutionTime) < time.time():
                raise Exception('Execution time << ' + absExecutionTime + ' >> from the past is used')        
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
        
        self.__callbackCompletedStage = None
        self.__callbackCompletedStatus = None       
        self.__callbackCompletedTime = None
        
        self.__interlock = interlock       
        if self.__interlock == []:
            self.__interlock.append('PASSED')
            self.__interlock.append('FAILED')
            self.__interlock.append('TIMEOUT')
                           
        self.__callbackTable = PrettyTable(['Stage', 'Status', 'Time'])        
        self.__paramTable = PrettyTable([Style.BRIGHT + 'Name', 'Description', 'Eng. Val', 'Unit', 'Radix', 'Value Type', 'Value'+ Style.RESET_ALL])
        self.__paramTableLog = PrettyTable(['Name', 'Description', 'Eng. Val', 'Unit', 'Radix', 'Value Type', 'Value'])
              
        pbWidgets = [Fore.WHITE + Back.BLUE + Style.BRIGHT + self.__cmdName + Style.RESET_ALL + Style.BRIGHT, pb.Bar(fill='_'), ' ', pb.Percentage(), ' ', pb.ETA(), Style.RESET_ALL]
        self.__bar = pb.ProgressBar(widgets=pbWidgets, min_value=0, term_width=115)
        
        if self.__interlock is not None:
            ilockWidgets = ['Waiting for interlock status...', pb.BouncingBar(marker=pb.RotatingMarker())]
            self.__ilockBar = pb.ProgressBar(widgets=ilockWidgets, term_width=43)
        
        #logging.basicConfig(level=logging.DEBUG)
        
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
            string += self.__paramTableLog.get_string() 
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
        
        string += self.__callbackTable.get_string()
        string += f'\n\nCompleted stage:  {self.__callbackCompletedStage}\n'
        string += f'Completed status: {self.__callbackCompletedStatus}\n'
        string += f'Completed time:   {TimeModule.ibaseTime2SCOSdate(self.__callbackCompletedTime)}\n'
        
        return string    
                     
    def initTables(self):
           
        self.__paramTable.horizontal_char = '='               
        self.__paramTable.align['Name'] = 'l'
        self.__paramTable.align['Description'] = 'l'   
   
        self.__paramTableLog.horizontal_char = '='               
        self.__paramTableLog.align['Name'] = 'l'
        self.__paramTableLog.align['Description'] = 'l' 
                      
        self.__callbackTable.horizontal_char = '='
        #self.__callbackTable.sortby = 'Time'
                
    def printCommandInfo(self):
        """ Method for printing the command information before injection. """ 
        
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
                if str(self.__cmdParameters[i].m_value) == 'IBASE.Variant(m_nullFormat = False)':
                    userValName = Fore.WHITE + Back.RED + Style.BRIGHT + self.__cmdParameters[i].m_name + Style.RESET_ALL
                    # counter
                    if self.__cmdMIBDef.m_params[i].m_repeatSize > 0:
                        userValName = userValName + ' (Counter)'
                    #userValType = Fore.WHITE + Back.RED + Style.BRIGHT + self.__paramValueTypeDict.get(vars(self.__cmdParameters[i].m_value).get('_d')) + Style.RESET_ALL       
                    userValType = self.__paramValueTypeDict.get(self.__cmdMIBDef.m_params[i].m_valueType)
                    if userValType == 'Null':
                        userValType = Fore.WHITE + Back.RED + Style.BRIGHT + userValType + Style.RESET_ALL
                    userVal = Fore.WHITE + Back.RED + Style.BRIGHT + f"{vars(self.__cmdParameters[i].m_value).get('_v')}" + Style.RESET_ALL
                    self.__paramTable.add_row([userValName, self.__cmdMIBDef.m_params[i].m_description, self.__cmdParameters[i].m_isEngValue, self.__cmdParameters[i].m_unit, self.__paramRadixDict.get(self.__cmdParameters[i].m_radix), userValType, userVal])
                    userInput = True
                # editable   
                elif self.__cmdMIBDef.m_params[i].m_isEditable == False:
                    notEditName = Fore.WHITE + Back.BLACK + Style.BRIGHT + self.__cmdParameters[i].m_name + Style.RESET_ALL
                    self.__paramTable.add_row([notEditName, self.__cmdMIBDef.m_params[i].m_description, self.__cmdParameters[i].m_isEngValue, self.__cmdParameters[i].m_unit, self.__paramRadixDict.get(self.__cmdParameters[i].m_radix), self.__paramValueTypeDict.get(vars(self.__cmdParameters[i].m_value).get('_d')), vars(self.__cmdParameters[i].m_value).get('_v')])
                    isEditable = False
                # modified    
                elif self.__paramIsModified[i][4] == True:
                    modName = Fore.BLUE + Style.BRIGHT + f'{self.__cmdParameters[i].m_name}' + Style.RESET_ALL
                    # counter
                    if self.__cmdMIBDef.m_params[i].m_repeatSize > 0:
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
                    self.__paramTable.add_row([modName, self.__cmdMIBDef.m_params[i].m_description, modEngVal, modUnit, modRadix, modValueType, modValue])
                else:                 
                    self.__paramTable.add_row([self.__cmdParameters[i].m_name, self.__cmdMIBDef.m_params[i].m_description, self.__cmdParameters[i].m_isEngValue, self.__cmdParameters[i].m_unit, self.__paramRadixDict.get(self.__cmdParameters[i].m_radix), self.__paramValueTypeDict.get(vars(self.__cmdParameters[i].m_value).get('_d')), vars(self.__cmdParameters[i].m_value).get('_v')])
                
                self.__paramTableLog.add_row([self.__cmdParameters[i].m_name, self.__cmdMIBDef.m_params[i].m_description, self.__cmdParameters[i].m_isEngValue, self.__cmdParameters[i].m_unit, self.__paramRadixDict.get(self.__cmdParameters[i].m_radix), self.__paramValueTypeDict.get(vars(self.__cmdParameters[i].m_value).get('_d')), vars(self.__cmdParameters[i].m_value).get('_v')])
                i += 1
                    
            print(self.__paramTable.get_string())
            self.__flush()
            
            if self.__repeaterGroupName != {}:           
                for rep in self.__repeaterGroupName.keys():
                    #print(f'\nCounter: {rep} - Group: {self.__repeaterGroupName[rep]}')
                    print(f'Counter: {rep} - Group: ' + '%s' % ', '.join(map(str, self.__repeaterGroupName[rep])))
                print('\n')
                    
            if userInput == True:
                print('\n' + Fore.WHITE + Back.RED + Style.BRIGHT + 'User input necessary' + Style.RESET_ALL)             
            if isEditable == False:
                print('\n' + Fore.WHITE + Back.BLACK + Style.BRIGHT + 'Not editable' + Style.RESET_ALL)                                      
            if isModified == True:
                print('\n' + Fore.BLUE + Style.BRIGHT + 'Modified parameter(s)', Style.RESET_ALL)
                       
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
                  
    def printCallback(self):
        """ Method for printing the full callback """   
               
        # lock thread while printing, for clean output print
        self.__lock.acquire()
        try: 
            
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
                 
                compStage = None                
                if self.__callbackCompletedStatus == 'PASSED':
                    cbTerminal.write(self.__cbTerm.green(self.__callbackTable.get_string()))
                    compStage = self.__cbTerm.green(self.__callbackCompletedStatus)
                elif self.__callbackCompletedStatus == 'FAILED':
                    cbTerminal.write(self.__cbTerm.red(self.__callbackTable.get_string()))
                    compStage = self.__cbTerm.red(self.__callbackCompletedStatus)
                elif self.__callbackCompletedStatus == 'TIMEOUT':
                    cbTerminal.write(self.__cbTerm.yellow(self.__callbackTable.get_string()))
                    compStage = self.__cbTerm.yellow(self.__callbackCompletedStatus)
                
                cbTerminal.write('\n\n')
                
                if self.__statusDict.get(self.__commandStatusList[-1].m_stage_status) == 'UNKNOWN':
                    cbTerminal.write(self.__cbTerm.bold + f'Command {self.__instCount}/{self.__cmdCount}: {self.__cmdName} exceeded SCOS Timeout\n' + self.__cbTerm.normal)
                    
                cbTerminal.write(self.__cbTerm.bold + f'Command {self.__instCount}/{self.__cmdCount}: {self.__cmdName} completed with status: ' + self.__cbTerm.normal + compStage + '\n')
                                
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
                    tempRepeatGroup.append(self.__cmdMIBDef.m_params[startGroupIndex])
                    startGroupIndex += 1
                    
                self.__repeaterGroupName[self.__cmdMIBDef.m_params[i].m_name] = tempRepeatGroupName
                
                # key: counter, value: parameter to be repeated
                self.__repeaterGroup[self.__cmdMIBDef.m_params[i].m_name] = tempRepeatGroup
                
                repeater = True
                #repeaterList = []
            i += 1
            
        if repeater == False:          
             i = 0    
             while i < len(self.__cmdMIBDef.m_params):                 
                paramStruct = ITC.CommandParam(self.__cmdMIBDef.m_params[i].m_name, self.__cmdMIBDef.m_params[i].m_engValueIsDefault, self.__cmdMIBDef.m_params[i].m_unit, self.__cmdMIBDef.m_params[i].m_defaultRadix, self.__cmdMIBDef.m_params[i].m_defaultValue)                
                self.__cmdParameters.append(paramStruct)                           
                # vector which describes if parameter is modified in method setCommandParameter 
                self.__paramIsModified.append([False, False, False, False, False])               
             
                i += 1
         
        else:
            if counter is None:     
                for rep in self.__repeaterGroupName.keys():                   
                    raise Exception(f'Please set counter value ({rep} - Group: ' + '%s' % ', '.join(map(str, self.__repeaterGroupName[rep])) + f') for command {self.__instCount} - {self.__cmdName}')             
            
            while i < len(self.__cmdMIBDef.m_params):
                if self.__cmdMIBDef.m_params[i].m_repeatSize > 0: 
                    for param in counter:
                        if param[0] == self.__cmdMIBDef.m_params[i].m_name:
                            # set counter
                            paramStruct = ITC.CommandParam(self.__cmdMIBDef.m_params[i].m_name, self.__cmdMIBDef.m_params[i].m_engValueIsDefault, self.__cmdMIBDef.m_params[i].m_unit, self.__cmdMIBDef.m_params[i].m_defaultRadix, IBASE.Variant('U', param[1]))    
                            self.__cmdParameters.append(paramStruct)
                            self.__paramIsModified.append([False, False, False, True, True])                  

                            j = 1
                            while j < param[1]:
                                for repParam in self.__repeaterGroup[param[0]]:
                                    # set counter parameter (number)
                                    paramStruct = ITC.CommandParam(repParam.m_name, repParam.m_engValueIsDefault, repParam.m_unit, repParam.m_defaultRadix, repParam.m_defaultValue) 
                                    self.__cmdParameters.append(paramStruct)
                                    self.__cmdMIBDef.m_params.insert(i+j, repParam)
                                    self.__paramIsModified.append([False, False, False, False, False])      
                                    
                                    if repParam.m_repeatSize > 0:
                                        paramStruct = ITC.CommandParam(repParam.m_name, repParam.m_engValueIsDefault, repParam.m_unit, repParam.m_defaultRadix, repParam.m_defaultValue) 
                                        self.__cmdParameters.append(paramStruct) 
                                        self.__paramIsModified.append([False, False, False, False, False]) 
                                    i += 1                                                     
                                j += 1

                    
                else:
                    paramStruct = ITC.CommandParam(self.__cmdMIBDef.m_params[i].m_name, self.__cmdMIBDef.m_params[i].m_engValueIsDefault, self.__cmdMIBDef.m_params[i].m_unit, self.__cmdMIBDef.m_params[i].m_defaultRadix, self.__cmdMIBDef.m_params[i].m_defaultValue)                
                    self.__cmdParameters.append(paramStruct)                           
                    # vector which describes if parameter is modified in method setCommandParameter 
                    self.__paramIsModified.append([False, False, False, False, False])               
                 
                i += 1                    
                          
    # TODO
    def __createCounterParameters(self, index, counter):
        
        for param in counter:
            if param[0] == self.__cmdMIBDef.m_params[index].m_name:
                # set counter
                paramStruct = ITC.CommandParam(self.__cmdMIBDef.m_params[index].m_name, self.__cmdMIBDef.m_params[index].m_engValueIsDefault, self.__cmdMIBDef.m_params[index].m_unit, self.__cmdMIBDef.m_params[index].m_defaultRadix, IBASE.Variant('U', param[1]))    
                self.__cmdParameters.append(paramStruct)
                self.__paramIsModified.append([False, False, False, True, True])          

                j = 1
                counterIndex = []
                while j < param[1]:
                    for repParam in self.__repeaterGroup[param[0]]:

                        # counter, recursive calls
                        if repParam.m_repeatSize > 0:
                            counterIndex.append(index)
                        # set counter parameter (number)
                        paramStruct = ITC.CommandParam(repParam.m_name, repParam.m_engValueIsDefault, repParam.m_unit, repParam.m_defaultRadix, repParam.m_defaultValue) 
                        self.__cmdParameters.append(paramStruct)
                        self.__cmdMIBDef.m_params.insert(index+j, repParam)
                        self.__paramIsModified.append([False, False, False, False, False])      
                        index += 1                                                     
                    
                    if j == param[1] and counterIndex != []:
                        self.__createCounterParameters()
                    j += 1                        
    
    def setCommandParameter(self, name, isEng=None, unit=None, radix=None, valueType=None, value=None):
             
        i = 0
        while i < len(self.__cmdParameters): 
            if self.__cmdParameters[i].m_name == name:               
                if self.__paramIsModified[i][4] == False:                   
                    if self.__cmdMIBDef.m_params[i].m_isEditable == True:  
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
                
                self.__ilockBar.start()
                self.__flushBar()
                 
                if self.__lastCommand is None:
                    raise Exception('Interlock - previous command does not exist')
                for ilockStatus in self.__interlock:
                    if ilockStatus not in ['PASSED', 'FAILED', 'TIMEOUT']:
                        raise Exception("Interlock - please choose between 'PASSED', 'FAILED' and 'TIMEOUT'")
                        
                #print('Waiting for interlock status <<' + '%s' % ', '.join(map(str, self.__interlock)) + '>>...')                       
                while self.__lastCommand.getCallbackCompletedStatus() not in self.__interlock:               
                    for i in self.__ilockBar(iter(lambda:0,1)):                                              
                        time.sleep(0.02)                         
                        if self.__lastCommand.getCallbackCompletedStatus() in self.__interlock:
                            break     
                        elif self.__lastCommand.getCallbackCompletedStatus() is not None:                     
                            raise Exception(f'Interlock - got illegal status <<{self.__lastCommand.getCallbackCompletedStatus()}>>')
                #self.__flushBar() 
                print(f'...got status: <<{self.__lastCommand.getCallbackCompletedStatus()}>>')                     
                self.__flush()
                                                   
            # Release ASAP, finish bar immediately
            if str(self.__absReleaseTime) == str(IBASE.Time(0,0,False)):                                   
                self.__bar.max_value = 200                         
                self.__bar.start()         
                self.__bar.finish()
                self.__flushBar()
                
            # Release time tagged
            else:                   
#                while TimeModule.ibaseTime2stamp(self.__absReleaseTime) - time.time() > 0.5:
#                    pass                 
                releaseStamp = TimeModule.ibaseTime2stamp(self.__absReleaseTime)
                 
                if releaseStamp - time.time() < 0.5:
                    self.__bar.max_value = 200
                    self.__bar.start()           
                    self.__bar.finish()
                    self.__flushBar()
                    
                else:    
                    self.__bar.max_value = int(TimeModule.ibaseTime2stamp(self.__absReleaseTime) - time.time())                         
                    self.__bar.start()
    
                    for i in range(self.__bar.max_value):
                        self.__bar.update(i)                      
                        if releaseStamp - time.time() < 1.5:
                            break
                        time.sleep(1)
                                            
                    self.__bar.finish()           
                    self.__flushBar()
                                        
            self.__injRequestID = self.__cmdInjMngr.injectCmd(cmdRequest)
            self.__injectionTime = self.__commandServerMngr.getUTC()         
            print(self.__cmdTerm.bold('Injecting ') + f'command {self.__instCount}/{self.__cmdCount}: {self.__cmdName} - {self.__cmdDescription} @ {TimeModule.ibaseTime2SCOSdate(self.__injectionTime)}...\n')
            self.__flush() 
            
            self.__injectionLock.release()
            
            # start callback thread          
            self.__callbackThread = threading.Thread(target=self.getCommandStatus)
            self.__callbackThread.start()
                             
        except Exception as exception:
            #self.__exception = exception
            print(self.__cmdTerm.bold_red(f'\nCommand {self.__instCount}: {self.__cmdName} - Exception during command injection: ') + f'{exception}')
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
                                    
                        self.__callbackTable.add_row([self.__commandStatusList[self.__localCallbackCounter].m_stage, self.__statusDict.get(self.__commandStatusList[self.__localCallbackCounter].m_stage_status), self.__commandStatusList[self.__localCallbackCounter].m_updateTime])
                                                                                                                            
                        # callback finished, finish thread and print full callback
                        if self.__commandStatusList[self.__localCallbackCounter].m_completed_flag == True: 
                            
                            self.__callbackThread.do_run = False
                            
                            self.__callbackCompletedTime = TimeModule.scosDate2ibaseTime(self.__commandStatusList[self.__localCallbackCounter].m_updateTime)
                            self.__callbackCompletedStage = self.__stageDict.get(self.__commandStatusList[self.__localCallbackCounter].m_stage)
                            self.__callbackCompletedStatus = self.__statusDict.get(self.__commandStatusList[self.__localCallbackCounter].m_stage_status)
                                                                           
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
                                                                            
                            self.printCallback()
                                                     
                # call method every 0.2 sec    
                nextCall += 0.2
                time.sleep(nextCall - time.time())

        except Exception as exception:
            self.__callbackThread.do_run = False
            print(self.__cmdTerm.bold_red(f'\nCommand {self.__instCount}: {self.__cmdName} - Exception during callback reception: ') + f'{exception}')            
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
    def setTerminal(cls, term):
    
        cls.__cmdTerm = term    

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
    def deregister(cls, error=False):
        """ Deregister callback interface and clear internal buffer """
        
        if error == False:                    
            #print('\nWaiting for callback completion...', end='')
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
            with open(cls.__PIPE_PATH_Callb, 'w') as cbTerminal: 
                with cls.__cbTerm.location(0, cls.__cbTerm.height - 1):                                         
                    cbTerminal.write('\n' + cls.__cbTerm.bold('=') * 75 + '\nEnd of callback reception\n' + cls.__cbTerm.bold('=') * 75 + '\n')
            print(Fore.GREEN + '\nAll callbacks received...' + Style.RESET_ALL)  
            
        cls.__cmdInjMngr.deregister()
        print('Unregistered from external command server...')
        #sys.stdout.write('/033[FWaiting for command callbacks...done\nDeregistered from external command server')
        
        if error==True:
            sys.exit(1)
            
    absReleaseTime = property(getReleaseTime, setReleaseTime)
           