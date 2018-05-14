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
import os
from blessings import Terminal

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
    
    __lock = threading.Lock()
    __injLock = threading.Lock()
    
    __PIPE_PATH_Callb = None
    __cbTerm = Terminal()
    
    __cmdInjMngr = None
    __commandServerMngr = None
         
    def __init__(self, name, description, absReleaseTime=IBASE.Time(0,0,False), relReleaseTime=None, absExecutionTime=IBASE.Time(0,0,False), staticPtv='D', dynamicPtv='D', cev=False, timeout=None):
        
        self.__cmdList.append(self)
        type(self).__cmdCount += 1
        self.__instCount = self.__cmdCount
        
        self.__cmdDescription = description

        if type(absReleaseTime) == str:
            self.__absReleaseTime = TimeModule.scosDate2timestamp(absReleaseTime)
            if TimeModule.ibaseTime2stamp(self.__absReleaseTime) < time.time():
                raise Exception(' Release time ' + absReleaseTime + ' from the past is used')                
            if timeout != None:
                self.__timeoutTimestamp = TimeModule.ibaseTime2stamp(self.__absReleaseTime) + timeout
            else:
                self.__timeoutTimestamp = None
        else:
            self.__absReleaseTime = absReleaseTime
            self.__timeoutTimestamp = None
            
        if type(relReleaseTime) == str:
            self.__relReleaseTime = relReleaseTime
            
        else:
            self.__relReleaseTime = relReleaseTime
        self.__releaseTimeThread = None
        
        if type(absExecutionTime) == str:            
            self.__absExecutionTime = TimeModule.scosDate2timestamp(absExecutionTime)
            if TimeModule.ibaseTime2stamp(self.__absExecutionTime) < time.time():
                raise Exception(' Execution time ' + absExecutionTime + ' from the past is used')        
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
        self.__exception = None
        self.__timeout = timeout
        
        self.__repeaterGroup = {}
        
        self.__callbackCompletedStage = None
        self.__callbackCompletedStatus = None       
        self.__callbackCompletedTime = None
        
        self.__interlock = [False, False, False]
        
        self.__callbackTable = PrettyTable(['Stage', 'Status', 'Time'])        
        self.__paramTable = PrettyTable(['Name', 'Description', 'Eng. Val', 'Unit', 'Radix', 'Value Type', 'Value'])
          
        pbWidgets = [Fore.WHITE + Back.BLUE + Style.BRIGHT + 'Next inj: ' + self.__cmdName + Style.RESET_ALL, ' ', pb.Percentage(), pb.Bar(), pb.Timer(), ' ', pb.ETA()]
        self.__bar = pb.ProgressBar(widgets=pbWidgets, min_value=0)
        
    def __repr__(self):
        
        string = f'\nCommand status {self.__instCount} {self.__cmdName:=^89}\n\n'
        string += 'name: {} \ndescription: {} \nparameters: {} \nrequestID: {} \n\ninjectionTime: {} \nreleaseTime: {} \nrelReleaseTime: {} \nexecutionTime: {} \ntimeout: {} sec \ntimeoutTime: {} \n\nstaticPtv: {} \ndynamicPtv: {} \ncev: {} \n{}'.format(self.__cmdName,
                   self.__cmdDescription, self.__cmdParameters, self.__injRequestID, TimeModule.timestamp2SCOSdate(self.__injectionTime), TimeModule.timestamp2SCOSdate(self.__absReleaseTime), self.__relReleaseTime, TimeModule.timestamp2SCOSdate(self.__absExecutionTime), self.__timeout,
                   TimeModule.timestamp2SCOSdate(TimeModule.stamp2ibaseTime(self.__timeoutTimestamp)), self.__staticPtv, self.__dynamicPtv, self.__cev, self)
        
        return string
    
    def __str__(self):

        string = '\nCommand status of command {}: {} - {}\n\n'.format(self.__instCount, self.__cmdName, self.__cmdDescription)      
        for status in self.__commandStatusList:
            string += '\t{}: ({} - {}) at {} \trequestID: {}\n'.format(self.__instCount, status.m_stage, self.__statusDict.get(status.m_stage_status), status.m_updateTime, status.m_request_id)
                   
        return string    
         
    def printCallback(self, timeout=False):
        """ Method for printing the full callback. """   
               
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
                cbTerminal.write('\n' + '*' * 75 + '\n' + Fore.WHITE + Back.BLACK + Style.BRIGHT + f'Command status {self.__instCount} {self.__cmdName:=^{disp}}' + Style.RESET_ALL)   
                cbTerminal.write('\n' + '*' * 75 + '\n')
            
    #            for status in self.__commandStatusList:
    #                if status.m_stage_status == 0x0002:
    #                    print(f'{self.__instCount}: ' + Fore.WHITE + Back.GREEN + Style.BRIGHT + f'({status.m_stage} - {self.__statusDict.get(status.m_stage_status)})' + Style.RESET_ALL + f' at {status.m_updateTime}')     
    #                elif status.m_stage_status == 0x0080:  
    #                    print(f'{self.__instCount}: ' + Fore.WHITE + Back.RED + Style.BRIGHT + f'({status.m_stage} - {self.__statusDict.get(status.m_stage_status)})' + Style.RESET_ALL + f' at {status.m_updateTime}')  
    #                else:
    #                    print('{}: ({} - {}) at {}'.format(self.__instCount, status.m_stage, self.__statusDict.get(status.m_stage_status), status.m_updateTime)) 
            
    #            for status in self.__commandStatusList:            
    #                self.__callbackTable.add_row([status.m_stage, self.__statusDict.get(status.m_stage_status), status.m_updateTime])
            
                cbTerminal.write('\nName: {} \nDescription: {} \nRelease Time: {} \nExecution Time: {} \n\n'.format(self.__cmdName, self.__cmdDescription, TimeModule.timestamp2SCOSdate(self.__absReleaseTime), TimeModule.timestamp2SCOSdate(self.__absExecutionTime)))
                # interlock
                if self.__interlock[0] == True:
                    cbTerminal.write('Interlock: last command succeeded\n\n')
                if self.__interlock[1] == True:
                    cbTerminal.write('Interlock: last command failed\n\n')  
                if self.__interlock[2] == True:
                    cbTerminal.write('Interlock: last command timed out\n\n') 
            
                if self.__callbackCompletedStatus == 'PASSED':
                    cbTerminal.write(Fore.GREEN + Style.BRIGHT + str(self.__callbackTable) + Style.RESET_ALL)
                elif self.__callbackCompletedStatus == 'FAILED':
                    cbTerminal.write(self.__cbTerm.bold_red(str(self.__callbackTable)))
                elif self.__callbackCompletedStatus == 'TIMEOUT':
                    cbTerminal.write(Fore.YELLOW + Style.BRIGHT + str(self.__callbackTable) + Style.RESET_ALL)
                else:
                    cbTerminal.write(self.__callbackTable)
                               
                if timeout == True:
                    if self.__commandStatusList[-1].m_completed_flag == True:
                        cbTerminal.write('\n' + Fore.RED + Style.BRIGHT + 'Command {}: {} - Timeout: Command completion exceeded timeout setting'.format(self.__instCount, self.__cmdName), Style.RESET_ALL)
                    else :
                        cbTerminal.write('\n' + Fore.RED + Style.BRIGHT + 'Command {}: {} - Timeout: Command is not completed'.format(self.__instCount, self.__cmdName), Style.RESET_ALL)
                 
                cbTerminal.write('\n')    
      
        finally:
            self.__lock.release()
            self.__callbackThread.do_run = False

    def initTables(self):
           
        self.__paramTable.title = 'Parameters'
        self.__paramTable.horizontal_char = '='               
        self.__paramTable.align['Name'] = 'l'
        self.__paramTable.align['Description'] = 'l'   
                      
        self.__callbackTable.horizontal_char = '='
        #self.__callbackTable.sortby = 'Time'
        
    @classmethod
    def setCommandInjMngr(cls, cmdInjMngr):
        cls.__cmdInjMngr = cmdInjMngr
    
    @classmethod
    def setCommandServerMngr(cls, serverMngr):
        cls.__commandServerMngr = serverMngr
    
    def setCommandDef(self, cmdDef):
        self.__cmdMIBDef = cmdDef
     
#    def getLastCommand(self):
#        return self.__lastCommand
    
    def getCallbackCompletedStatus(self):
        return self.__callbackCompletedStatus
    
    def setCommandInterlock(self, lastCmdCompleted=None, lastCmdFailed=None, lastCmdTimeout=None):
        
        if lastCmdCompleted == True:
            if self.__lastCommand is None:
                raise Exception('Error: last command does not exist')
            else:
                self.__interlock[0] = True
                              
        if lastCmdFailed == True:
            if self.__lastCommand is None:
                raise Exception('Error: last command does not exist')
            else:
                self.__interlock[1] = True
                    
        if lastCmdTimeout == True:
            if self.__lastCommand is None:
                raise Exception('Error: last command does not exist')
            else:
                self.__interlock[2] = True
                  
    def getCommandInterlock(self):
        return self.__interlock
    
    def printCommandInfo(self):
        """ Method for printing the command information before injection. """ 

        if len(self.__cmdParameters) > 0:
            userInput = False
            isEditable = True
            isModified = False
        
        if self.__instCount > 999:
            disp = 82
        elif self.__instCount > 99:
            disp = 83
        elif self.__instCount > 9:
            disp = 84
        else:
            disp = 85
            
        print('\n' + '*' * 95 + '\n' + Back.BLUE + Style.BRIGHT + f'Command {self.__instCount} {self.__cmdName:=^{disp}}' + Style.RESET_ALL)     
        print('*' * 95 + '\n')
        
        print('Description: {}\n'.format(self.__cmdDescription))
        
        if len(self.__cmdParameters) > 0:
            i = 0
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
                    modName =  Fore.BLUE + Style.BRIGHT + f'{self.__cmdParameters[i].m_name}' + Style.RESET_ALL
                    # counter
                    if self.__cmdMIBDef.m_params[i].m_repeatSize > 0:
                        modName = modName + ' (Counter)'
                    if self.__paramIsModified[i][0] == True:
                        modEngVal = Fore.BLUE + Style.BRIGHT + f'{self.__cmdParameters[i].m_isEngValue}' + Style.RESET_ALL
                    else:
                        modEngVal = f'{self.__cmdParameters[i].m_isEngValue}'
                    if self.__paramIsModified[i][1] == True:
                        modUnit = Fore.BLUE + Style.BRIGHT + f'{self.__cmdParameters[i].m_unit}' + Style.RESET_ALL
                    else:
                        modUnit = f'{self.__cmdParameters[i].m_unit}'
                    if self.__paramIsModified[i][2] == True:       
                        modRadix = Fore.BLUE + Style.BRIGHT + f'{self.__paramRadixDict.get(self.__cmdParameters[i].m_radix)}' + Style.RESET_ALL 
                    else:    
                        modRadix = f'{self.__paramRadixDict.get(self.__cmdParameters[i].m_radix)}'
                    if self.__paramIsModified[i][3] == True:             
                        modValueType = Fore.BLUE + Style.BRIGHT + self.__paramValueTypeDict.get(vars(self.__cmdParameters[i].m_value).get('_d')) + Style.RESET_ALL
                        modValue = Fore.BLUE + Style.BRIGHT + f"{vars(self.__cmdParameters[i].m_value).get('_v')}"  + Style.RESET_ALL
                    else: 
                        modValueType = self.__paramValueTypeDict.get(vars(self.__cmdParameters[i].m_value).get('_d'))    
                        modValue = f"{vars(self.__cmdParameters[i].m_value).get('_v')}"   
                 
                    isModified = True       
                    self.__paramTable.add_row([modName, self.__cmdMIBDef.m_params[i].m_description, modEngVal, modUnit, modRadix, modValueType, modValue])
                else:                 
                    self.__paramTable.add_row([self.__cmdParameters[i].m_name, self.__cmdMIBDef.m_params[i].m_description, self.__cmdParameters[i].m_isEngValue, self.__cmdParameters[i].m_unit, self.__paramRadixDict.get(self.__cmdParameters[i].m_radix), self.__paramValueTypeDict.get(vars(self.__cmdParameters[i].m_value).get('_d')), vars(self.__cmdParameters[i].m_value).get('_v')])
                            
                i += 1
                    
            print(self.__paramTable)
            print('\n')
            
            if len(self.__repeaterGroup) > 0:
                for rep in self.__repeaterGroup.keys():
                    print(f'Counter: {rep} - Group: {self.__repeaterGroup[rep]}')
                print('\n')    
                
            if userInput == True:
                print(Fore.WHITE + Back.RED + Style.BRIGHT + '---: User input necessary' + Style.RESET_ALL)             
            if isEditable == False:
                print(Fore.WHITE + Back.BLACK + Style.BRIGHT + '---: Not editable' + Style.RESET_ALL)                    
            print('---: Default parameter(s)')           
            if isModified == True:
                print(Fore.BLUE + Style.BRIGHT + '---: Modified parameter(s)', Style.RESET_ALL)
                       
        else:
            print('Parameters: command {} has no parameters\n'.format(self.__cmdName))
        
        # time         
        if self.__relReleaseTime == None:           
            print('\nRelease time: {} \nRelative release time: {} \nExecution time: {}'.format(TimeModule.timestamp2SCOSdate(self.__absReleaseTime), self.__relReleaseTime, TimeModule.timestamp2SCOSdate(self.__absExecutionTime)))
            
        else:
            print('\nRelease time: To be calculated \nRelative release time: {} \nExecution time: {}'.format(self.__relReleaseTime, TimeModule.timestamp2SCOSdate(self.__absExecutionTime)))
                
        if self.__timeout == None:
            print('Timeout: {}'.format(self.__timeout))
            
        else:
            print('Timeout: {} sec'.format(self.__timeout))
        
        # interlock
        if self.__interlock[0] == True:
            print('\nInterlock: Inject command if last command succeeded')
        if self.__interlock[1] == True:
            print('\nInterlock: Inject command if last command failed')  
        if self.__interlock[2] == True:
            print('\nInterlock: Inject command if last command timed out')    
         
        # checks    
        print('\nPTV static: {} \nPTV dynamic: {} \nCEV: {}'.format(self.__checkStateTypeDict.get(self.__staticPtv), self.__checkStateTypeDict.get(self.__dynamicPtv), self.__cev))      
                  
    def getReleaseTime(self):
        return self.__absReleaseTime
    
    def setReleaseTime(self, absReleaseTime):
        self.__absReleaseTime = absReleaseTime
    
    def setRelReleaseTime(self):
        """ Method to get release time from previous command and calculate new release time. """
           
        # TODO: Set timeout for finishing thread
        try:
            nextCall = time.time()
            
            while getattr(self.__releaseTimeThread, 'do_run', True):
                prevReleaseTime = self.__lastCommand.getReleaseTime()
               
                if str(prevReleaseTime) != str(IBASE.Time(0,0,False)):               
                    # succesfull injection of previous command
                    if self.__lastCommand.getInjRequestID() != 0:
                        self.__releaseTimeThread.do_run = False
                    # exception during previous command injection, continue with current command injection
                    if self.__lastCommand.getException() != None:
                        self.__releaseTimeThread.do_run = False
                # call method every 0.2 sec    
                nextCall += 0.2
                time.sleep(nextCall - time.time())
                    
            self.__absReleaseTime = TimeModule.relativeReleaseTime(prevReleaseTime, self.__relReleaseTime)
          
            #timeout
            if self.__timeout != None:
                self.__timeoutTimestamp = TimeModule.ibaseTime2stamp(self.__absReleaseTime)  + self.__timeout
       
            self.injectCommand()

        except Exception as exception:
            print(Fore.RED + Style.BRIGHT + '\nException during release time setting:', exception, Style.RESET_ALL)
            self.__releaseTimeThread.do_run = False
     
    def getRelativeReleaseTime(self):
        return self.__relReleaseTime
        
    def startReleaseTimeThread(self):

        self.__releaseTimeThread = threading.Thread(target=self.setRelReleaseTime)
        self.__releaseTimeThread.start()        
        
    def getInjRequestID(self):
        return self.__injRequestID
    
    # set default MIB command parameters (different structure for injection)
    def setMIBCommandParameters(self, counter=None):
        
        if counter is not None:
            repeatGroup = []
        
        i = 0            
        while i < len(self.__cmdMIBDef.m_params):
            # repeater
            if self.__cmdMIBDef.m_params[i].m_repeatSize > 0:
                
                #if 'repeatGroup' is not locals():
                #raise Exception(' Please set counter value for command {} - {}'.format(self.__instCount, self.__cmdName)) 
                
                startGroupIndex = i+1
                endGroupEndex = i + self.__cmdMIBDef.m_params[i].m_repeatSize
                tempRepeatGroupName = []
                tempRepeatGroup = []
                
                while startGroupIndex <= endGroupEndex:
                    tempRepeatGroupName.append(self.__cmdMIBDef.m_params[startGroupIndex].m_name) 
                    tempRepeatGroup.append(self.__cmdMIBDef.m_params[startGroupIndex])
                    startGroupIndex += 1
                    
                repeatGroup.append(tempRepeatGroupName)
                self.__repeaterGroup[self.__cmdMIBDef.m_params[i].m_name] = tempRepeatGroupName
                            
                for param in counter:
                    if param[0] == self.__cmdMIBDef.m_params[i].m_name:
                        # counter
                        paramStruct = ITC.CommandParam(self.__cmdMIBDef.m_params[i].m_name, self.__cmdMIBDef.m_params[i].m_engValueIsDefault, self.__cmdMIBDef.m_params[i].m_unit, self.__cmdMIBDef.m_params[i].m_defaultRadix, IBASE.Variant('U', param[1]))    
                        self.__cmdParameters.append(paramStruct)
                                             
#                        i = 1
#                        while i < param[1]:
#                            for repParam in tempRepeatGroup:
#                                # counter parameter (number)
#                                paramStruct = ITC.CommandParam(repParam.m_name, repParam.m_engValueIsDefault, repParam.m_unit, repParam.m_defaultRadix, repParam.m_defaultValue) 
#                                self.__cmdParameters.append(paramStruct)                                                     
#                            i += 1
            # no repeater
            else:
                paramStruct = ITC.CommandParam(self.__cmdMIBDef.m_params[i].m_name, self.__cmdMIBDef.m_params[i].m_engValueIsDefault, self.__cmdMIBDef.m_params[i].m_unit, self.__cmdMIBDef.m_params[i].m_defaultRadix, self.__cmdMIBDef.m_params[i].m_defaultValue)                
                self.__cmdParameters.append(paramStruct)
                
            paramIsModifiedList = [False, False, False, False, False]
            # vector which describes if parameter is modified in method setCommandParameter 
            self.__paramIsModified.append(paramIsModifiedList)             
            
            if self.__cmdMIBDef.m_params[i].m_repeatSize > 0:
                self.__paramIsModified[i][3] = True
                self.__paramIsModified[i][4] = True  
                
            i += 1
                          
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
                    break                   
            i += 1
                                                         
    def injectCommand(self):
        
        try:                                    
            self.__info = ITC_INJ.ReleaseInfo(self.__absReleaseTime, IBASE.Time(0,0,False), IBASE.Time(0,0,False), self.__absExecutionTime, self.__staticPtv, self.__dynamicPtv, self.__cev, ITC_INJ.ACK_MIB_DEFAULT)    
            cmdRequest = ITC_INJ.CommandRequest(self.__context, self.__destination, self.__mapId, self.__vcId, self.__cmdName, self.__cmdParameters, self.__paramSets, self.__info, self.__ilockType, self.__ilockStageType, self.__additionalInfo, self.__tcRequestID)
            
            # wait until previous command is injected (pay attention if previous commands are not injected!)
            while self.__lastCommand is not None and self.__lastCommand.getInjRequestID() is 0:
                pass  

            # interlock
            if self.__interlock[0] == True:
                while self.__lastCommand.getCallbackCompletedStatus() is not 'PASSED':
                    pass
            if self.__interlock[1] == True:
                while self.__lastCommand.getCallbackCompletedStatus() is not 'FAILED':
                    pass
            if self.__interlock[2] == True:
                while self.__lastCommand.getCallbackCompletedStatus() is not 'TIMEOUT':
                    pass   
                
            self.__injLock.acquire()
            
            # Release ASAP, finish bar immediately
            if str(self.__absReleaseTime) == str(IBASE.Time(0,0,False)):                
                                            
                self.__bar.start()
                self.__bar.finish()

            # Release time tagged
            else:                   
#                while TimeModule.ibaseTime2stamp(self.__absReleaseTime) - time.time() > 0.5:
#                    pass 
                
                releaseStamp = TimeModule.ibaseTime2stamp(self.__absReleaseTime)
                 
                if releaseStamp - time.time() < 0.5:
                    self.__bar.start()
                    self.__bar.finish()
                    
                else:    
                    self.__bar.max_value = int(TimeModule.ibaseTime2stamp(self.__absReleaseTime) - time.time())                    
                    self.__bar.start()
    
                    for i in range(self.__bar.max_value):
                        self.__bar.update(i)                    
                        if releaseStamp - time.time() < 1.5:
                            break
                        time.sleep(1)
                       
                    self.__bar.finish()
 
            self.__injRequestID = self.__cmdInjMngr.injectCmd(cmdRequest)
            self.__injectionTime = self.__commandServerMngr.getUTC()           
            print('Injecting command {}: {} - {} at {}...\n'.format(self.__instCount, self.__cmdName, self.__cmdDescription, TimeModule.timestamp2SCOSdate(self.__injectionTime)))
            
            self.__injLock.release()
            # set release time to current UTC time if release time is empty
            # backup, changed to update time of stage R 
    #        if str(self.__absReleaseTime) == str(IBASE.Time(m_sec=0, m_micro=0, m_isDelta=False)):
    #            self.__absReleaseTime = self.__commandServerMngr.getUTC()        
    #        print(Fore.WHITE + Back.BLACK + Style.BRIGHT + "Release time: {}".format(TimeModule.timestamp2SCOSdate(self.__absReleaseTime)),Style.RESET_ALL + '\n')  
    
            if self == self.__cmdList[-1]:
                print(Fore.GREEN + Style.BRIGHT + 'Done' + Style.RESET_ALL)
    
            # start callback thread          
            self.__callbackThread = threading.Thread(target=self.getCommandStatus)
            self.__callbackThread.start()
                 
        except Exception as exception:
            self.__exception = exception
            print(Fore.RED + Style.BRIGHT + '\nException during command injection:', exception, Style.RESET_ALL)
            
    @classmethod    
    def getUpdateRequestStatus(cls, status):
        status.m_updateTime = TimeModule.timestamp2SCOSdate(status.m_updateTime)
        cls.__commandStatusListStatic.append(status)
                
        #sort by time
        #sorted(cb.m_updateTime for cb in list1)
        #sorted(list1, key=lambda cb: cb.m_updateTime)
        cls.__commandStatusListStatic.sort(key=attrgetter('m_updateTime'))

    @classmethod        
    def getUpdateSystemStatus(cls, status):
        cls.__systemStatusListStatic.append(status)
        print(status)
        
    @classmethod    
    def getCommandList(cls):
        return cls.__cmdList
    
    @classmethod
    def getCommandCount(cls):
        return cls.__cmdCount

    @classmethod
    def createCallbackTerminal(cls):
        
        cls.__PIPE_PATH_Callb = '/tmp/callbackPipe'  
        
        if os.path.exists(cls.__PIPE_PATH_Callb):
            os.remove(cls.__PIPE_PATH_Callb)
         
        # named pipe                     
        os.mkfifo(cls.__PIPE_PATH_Callb)
            
        # new terminal subprocess (Test with different emulators: 'gnome-terminal', 'xterm', 'konsole',...) 
        Popen(['gnome-terminal', '-e', 'tail -f %s' % cls.__PIPE_PATH_Callb])   
               
        with open(cls.__PIPE_PATH_Callb, 'w') as cbTerminal:
            cbTerminal.write('\n' +  cls.__cbTerm.bold('Waiting for command callbacks...') + '\n')
 
        
    def getInstCount(self):
        return self.__instCount
    
    def getException(self):
        return self.__exception
    
    def getCommandStatus(self):      
        """ Get callback for individual instance. """
        
        try:          
            nextCall = time.time()
            
            while getattr(self.__callbackThread, 'do_run', True):
                              
                while self.__globalCallbackCounter < len(self.__commandStatusListStatic): 
                    if self.__commandStatusListStatic[self.__globalCallbackCounter].m_request_id == self.__injRequestID:
                        
                        self.__commandStatusList.append(self.__commandStatusListStatic[self.__globalCallbackCounter])
                          
                        # get release time if neccesary                
                        if self.__commandStatusList[self.__localCallbackCounter].m_stage == 's':
                            if str(self.__absReleaseTime) == str(IBASE.Time(m_sec=0, m_micro=0, m_isDelta=False)):
                                self.__absReleaseTime = TimeModule.scosDate2timestamp(self.__commandStatusList[self.__localCallbackCounter].m_updateTime)
                                
                                # set timeout
                                if self.__timeout != None:
                                    self.__timeoutTimestamp = TimeModule.ibaseTime2stamp(self.__absReleaseTime)  + self.__timeout
                        
                        #print('Callback for command {}: {} ({} - {}) {}'.format(self.__instCount, self.__cmdName, self.__commandStatusList[self.__localCallbackCounter].m_stage, self.__statusDict.get(self.__commandStatusList[self.__localCallbackCounter].m_stage_status), self.__commandStatusList[self.__localCallbackCounter].m_updateTime))   
                        self.__callbackTable.add_row([self.__commandStatusList[self.__localCallbackCounter].m_stage, self.__statusDict.get(self.__commandStatusList[self.__localCallbackCounter].m_stage_status), self.__commandStatusList[self.__localCallbackCounter].m_updateTime])
                                                                                                                            
                        # callback finished, finish thread and print full callback
                        if self.__commandStatusList[self.__localCallbackCounter].m_completed_flag == True:                           
                            self.__callbackCompletedTime = TimeModule.scosDate2timestamp(self.__commandStatusList[self.__localCallbackCounter].m_updateTime)
                            self.__callbackCompletedStage = self.__stageDict.get(self.__commandStatusList[self.__localCallbackCounter].m_stage)
                            self.__callbackCompletedStatus = self.__statusDict.get(self.__commandStatusList[self.__localCallbackCounter].m_stage_status)
                            
                            # timeout
                            if self.__timeoutTimestamp is not None:
                                if self.__timeoutTimestamp - TimeModule.ibaseTime2stamp(self.__callbackCompletedTime) <= 0:
                                    self.printCallback(timeout=True)
                                else:
                                    self.printCallback(timeout=False)
                            else:     
                                self.printCallback()
                                                       
                        self.__localCallbackCounter += 1    
                    self.__globalCallbackCounter += 1
                
                # timeout if callback is not completed                
                if self.__timeoutTimestamp != None:
                    if self.__localCallbackCounter > 0 and self.__commandStatusList[self.__localCallbackCounter - 1].m_completed_flag == False:
                        if self.__timeoutTimestamp - time.time() <= 0:
                            self.printCallback(timeout=True)
                            
                # call method every 0.5 sec    
                nextCall += 0.5
                time.sleep(nextCall - time.time())

        except Exception as exception:
            print(Fore.RED + Style.BRIGHT + '\nCommand {}: {} - Exception during callback reception:{}.'.format(self.__instCount, self.__cmdName, exception), Style.RESET_ALL)
            self.__callbackThread.do_run = False
            self.printCallback()
            
    absReleaseTime = property(getReleaseTime, setReleaseTime)
    relReleaseTime = property(getRelativeReleaseTime)
    interlock = property(getCommandInterlock)
       