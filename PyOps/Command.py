#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Class for command injection

Command -- describes command values, command injection and command status
"""

import IBASE, ITC, ITC_INJ
import TimeModule
import time, threading
from colorama import Fore, Back, Style

class Command():

    # static members   
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
         
    def __init__(self, name, description, absReleaseTime=IBASE.Time(0,0,False), relReleaseTime=None, absExecutionTime=IBASE.Time(0,0,False), staticPtv='D', dynamicPtv='D', cev=False, timeout=None):
        
        self.__cmdList.append(self)
        type(self).__cmdCount += 1
        self.__instCount = self.__cmdCount
        
        self.__cmdDescription = description

        if type(absReleaseTime) == str:
            self.__absReleaseTime = TimeModule.scosDate2timestamp(absReleaseTime)
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
        self.__cmdInjMngr = None 
        self.__commandServerMngr = None
        self.__cmdMIBDef = None        
        self.__commandStatusList = []
        self.__paramIsModified = []
        
        self.__i = 0
        self.__j = 0
        self.__callbackThread = None
        self.__lastCommand = None
        self.__exception = None
        self.__timeout = timeout
           
        self.__callbackCompletedTime = None
        
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
            print('\n' + '*' * 99 + '\n' + Fore.WHITE + Back.BLACK + Style.BRIGHT + f'Command status {self.__instCount} {self.__cmdName:=^82}' + Style.RESET_ALL)   
            print('*' * 99 + '\n')
            
            for status in self.__commandStatusList:
                if status.m_stage_status == 0x0002:
                    print(f'{self.__instCount}: ' + Fore.WHITE + Back.GREEN + Style.BRIGHT + f'({status.m_stage} - {self.__statusDict.get(status.m_stage_status)})' + Style.RESET_ALL + f' at {status.m_updateTime}')     
                elif status.m_stage_status == 0x0080:  
                    print(f'{self.__instCount}: ' + Fore.WHITE + Back.RED + Style.BRIGHT + f'({status.m_stage} - {self.__statusDict.get(status.m_stage_status)})' + Style.RESET_ALL + f' at {status.m_updateTime}')  
                else:
                    print('{}: ({} - {}) at {}'.format(self.__instCount, status.m_stage, self.__statusDict.get(status.m_stage_status), status.m_updateTime)) 
                    
            if self.__commandStatusList[-1].m_stage != 'C':
                print(Fore.RED + Style.BRIGHT + '\nCommand {}: {} - Not completed'.format(self.__instCount, self.__cmdName), Style.RESET_ALL)
            
            if timeout == True:
                if self.__commandStatusList[-1].m_stage == 'C' and self.__statusDict.get(self.__commandStatusList[-1].m_stage_status) != 'PASSED':
                    print(Fore.RED + Style.BRIGHT + 'Command {}: {} - Timeout: Stage C did not pass.'.format(self.__instCount, self.__cmdName), Style.RESET_ALL)
                else:
                    print(Fore.RED + Style.BRIGHT + 'Command {}: {} - Timeout: No callback for stage C received.'.format(self.__instCount, self.__cmdName), Style.RESET_ALL)
                    
            print('\n' + '*' * 99 + '\nCommand {}: {} - Callback finished\n'.format(self.__instCount, self.__cmdName) + '*' * 99 + '\n')
           
        finally:
            self.__lock.release()
            self.__callbackThread.do_run = False

    def setCommandInjMngr(self, cmdInjMngr):
        self.__cmdInjMngr = cmdInjMngr
    
    def setCommandServerMngr(self, serverMngr):
        self.__commandServerMngr = serverMngr
    
    def setCommandDef(self, cmdDef):
        self.__cmdMIBDef = cmdDef
     
    def printCommandInfo(self):
        """ Method for printing the command information before injection. """ 

        if len(self.__cmdParameters) > 0:
            userInput = False
            isEditable = True
            isModified = False
                  
        print('\n' + '*' * 99 + '\n' + Back.BLUE + Style.BRIGHT + f'Command {self.__instCount} {self.__cmdName:=^89}' + Style.RESET_ALL)     
        print('*' * 99 + '\n')
        
        print('Name: {} \nDescription: {} \nParameter(s):'.format(self.__cmdName, self.__cmdDescription))
        
        i = 0
        while i < len(self.__cmdParameters):
            # user input
            if str(self.__cmdParameters[i].m_value) == 'IBASE.Variant(m_nullFormat = False)':
                param = '\t' + Fore.WHITE + Back.RED + Style.BRIGHT + f'{self.__cmdParameters[i].m_name}' + Style.RESET_ALL + f' (engVal={self.__cmdParameters[i].m_isEngValue}, unit={self.__cmdParameters[i].m_unit}, radix={self.__cmdParameters[i].m_radix}, ' + Fore.WHITE + Back.RED + Style.BRIGHT + f'value={self.__cmdParameters[i].m_value}' + Style.RESET_ALL + ')'
                #param += f'{self.__cmdMIBDef.m_params[i].m_description:>20}'
                print(param)
                userInput = True
            # editable   
            elif self.__cmdMIBDef.m_params[i].m_isEditable == False:
                print('\t' + Fore.WHITE + Back.BLACK + Style.BRIGHT + f'{self.__cmdParameters[i].m_name}' + Style.RESET_ALL + f' (engVal={self.__cmdParameters[i].m_isEngValue}, unit={self.__cmdParameters[i].m_unit}, radix={self.__cmdParameters[i].m_radix}, value={self.__cmdParameters[i].m_value}' + ')')
                isEditable = False
            # modified    
            elif self.__paramIsModified[i][4] == True:
                modifiedParam = '\t' + Fore.BLUE + Style.BRIGHT + f'{self.__cmdParameters[i].m_name} ' + Style.RESET_ALL
                if self.__paramIsModified[i][0] == True:
                    modifiedParam += '(' + Fore.BLUE + Style.BRIGHT + f'engVal={self.__cmdParameters[i].m_isEngValue}' + Style.RESET_ALL + ', '
                else:
                    modifiedParam += f'(engVal={self.__cmdParameters[i].m_isEngValue}, ' 
                if self.__paramIsModified[i][1] == True:
                    modifiedParam += Fore.BLUE + Style.BRIGHT + f'unit={self.__cmdParameters[i].m_unit}' + Style.RESET_ALL + ', '
                else:
                    modifiedParam += f'unit={self.__cmdParameters[i].m_unit}, '
                if self.__paramIsModified[i][2] == True:
                    modifiedParam += Fore.BLUE + Style.BRIGHT + f'radix={self.__cmdParameters[i].m_radix}' + Style.RESET_ALL + ', '
                else:
                    modifiedParam += f'radix={self.__cmdParameters[i].m_radix}, ' 
                if self.__paramIsModified[i][3] == True:  
                    modifiedParam += Fore.BLUE + Style.BRIGHT + f'value={self.__cmdParameters[i].m_value}' + Style.RESET_ALL + ')'
                else:
                    modifiedParam += f'value={self.__cmdParameters[i].m_value})' 
                 
                #modifiedParam += f'\t{self.__cmdMIBDef.m_params[i].m_description}'    
                isModified = True
                print(modifiedParam)
            else:    
                print('\t{} (engVal={}, unit={}, radix={}, value={})'.format(self.__cmdParameters[i].m_name, self.__cmdParameters[i].m_isEngValue, self.__cmdParameters[i].m_unit, self.__cmdParameters[i].m_radix, self.__cmdParameters[i].m_value))
        
            i += 1
        
        if len(self.__cmdParameters) > 0:
        
            print('\n')           
         
            if userInput == True:
                print('\t' + Fore.WHITE + Back.RED + Style.BRIGHT + '---: User input necessary', Style.RESET_ALL)             
            if isEditable == False:
                print('\t' + Fore.WHITE + Back.BLACK + Style.BRIGHT + '---: Not editable', Style.RESET_ALL)                    
            print('\t---: Default parameter(s)')           
            if isModified == True:
                print('\t' + Fore.BLUE + Style.BRIGHT + '---: Modified parameter(s)', Style.RESET_ALL)
            
        if self.__relReleaseTime == None:           
            print('\nRelease time: {} \nRelative release time: {} \nExecution time: {}'.format(TimeModule.timestamp2SCOSdate(self.__absReleaseTime), self.__relReleaseTime, TimeModule.timestamp2SCOSdate(self.__absExecutionTime)))
        
        else:
            print('\nRelease time: To be calculated \nRelative release time: {} \nExecution time: {}'.format(self.__relReleaseTime, TimeModule.timestamp2SCOSdate(self.__absExecutionTime)))
        
        if self.__timeout == None:
            print('Timeout: {}'.format(self.__timeout))
            
        else:
            print('Timeout: {} sec'.format(self.__timeout))
        
        print('\nPTV static: {} \nPTV dynamic: {} \nCEV: {}'.format(self.__staticPtv, self.__dynamicPtv, self.__cev))            
        
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
            print(Fore.WHITE + Back.RED + Style.BRIGHT + '\nException during release time setting: ', exception, Style.RESET_ALL)
            self.__releaseTimeThread.do_run = False
     
    def getRelativeReleaseTime(self):
        return self.__relReleaseTime
        
    def startReleaseTimeThread(self, lastCommand):

        self.__lastCommand = lastCommand
        self.__releaseTimeThread = threading.Thread(target=self.setRelReleaseTime)
        self.__releaseTimeThread.start()        
        
    def getInjRequestID(self):
        return self.__injRequestID
    
    # set default MIB command parameters (different structure for injection)
    def setMIBCommandParameters(self):
                   
        for param in self.__cmdMIBDef.m_params:
            paramStruct = ITC.CommandParam(param.m_name, param.m_engValueIsDefault, param.m_unit, param.m_defaultRadix, param.m_defaultValue)
            self.__cmdParameters.append(paramStruct)
            paramIsModifiedList = [False, False, False, False, False]
            # vector which describes if parameter is modified in method setCommandParameter 
            self.__paramIsModified.append(paramIsModifiedList)             
            
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
            
            self.__injRequestID = self.__cmdInjMngr.injectCmd(cmdRequest)
            self.__injectionTime = self.__commandServerMngr.getUTC()
            
            print('Injecting command {}: {} - {} at {}...'.format(self.__instCount, self.__cmdName, self.__cmdDescription, TimeModule.timestamp2SCOSdate(self.__injectionTime)))
                  
            # set release time to current UTC time if release time is empty
            # backup, changed to update time of stage R 
    #        if str(self.__absReleaseTime) == str(IBASE.Time(m_sec=0, m_micro=0, m_isDelta=False)):
    #            self.__absReleaseTime = self.__commandServerMngr.getUTC()        
    #        print(Fore.WHITE + Back.BLACK + Style.BRIGHT + "Release time: {}".format(TimeModule.timestamp2SCOSdate(self.__absReleaseTime)),Style.RESET_ALL + '\n')  
    
            # start callback thread
            self.__callbackThread = threading.Thread(target=self.getCommandStatus)
            self.__callbackThread.start()
               
        except Exception as exception:
            self.__exception = exception
            print(Fore.WHITE + Back.RED + Style.BRIGHT + '\nException during command injection: ', exception, Style.RESET_ALL)
            
    @classmethod    
    def getUpdateRequestStatus(cls, status):
        cls.__commandStatusListStatic.append(status)

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
     
    def getInstCount(self):
        return self.__instCount
    
    def getException(self):
        return self.__exception
    
    def getCommandStatus(self):      
        """ Get callback for individual instance. """
        
        try:          
            nextCall = time.time()
            
            while getattr(self.__callbackThread, 'do_run', True):
                              
                while self.__i < len(self.__commandStatusListStatic): 
                    if self.__commandStatusListStatic[self.__i].m_request_id == self.__injRequestID:
                        self.__commandStatusList.append(self.__commandStatusListStatic[self.__i])
                          
                        # get release time if neccesary                
                        if self.__commandStatusList[self.__j].m_stage == 'R':
                            if str(self.__absReleaseTime) == str(IBASE.Time(m_sec=0, m_micro=0, m_isDelta=False)):
                                self.__absReleaseTime = self.__commandStatusList[self.__j].m_updateTime
                                
                                # set timeout
                                if self.__timeout != None:
                                    self.__timeoutTimestamp = TimeModule.ibaseTime2stamp(self.__absReleaseTime)  + self.__timeout

                        # change callback timestamp to SCOS date and print callback                
                        self.__commandStatusList[self.__j].m_updateTime = TimeModule.timestamp2SCOSdate(self.__commandStatusList[self.__j].m_updateTime)                           
                        #print('Callback for command {}: {} ({} - {}) {}'.format(self.__instCount, self.__cmdName, self.__commandStatusList[self.__j].m_stage, self.__statusDict.get(self.__commandStatusList[self.__j].m_stage_status), self.__commandStatusList[self.__j].m_updateTime))
                                                                                                                   
                        # callback finished, finish thread and print full callback
                        if self.__commandStatusList[self.__j].m_completed_flag == True:                           
                            self.__callbackCompletedTime = TimeModule.scosDate2timestamp(self.__commandStatusList[self.__j].m_updateTime)
                            
                            # timeout
                            if self.__timeoutTimestamp is not None:
                                if self.__timeoutTimestamp - TimeModule.ibaseTime2stamp(self.__callbackCompletedTime) <= 0:
                                    self.printCallback(timeout=True)
                                else:
                                    self.printCallback(timeout=False)
                            else:     
                                self.printCallback()
                                                       
                        self.__j += 1    
                    self.__i += 1
                
                # timeout if callback is not completed                
                if self.__timeoutTimestamp != None:
                    if self.__j > 0 and self.__commandStatusList[self.__j - 1].m_completed_flag == False:
                        if self.__timeoutTimestamp - time.time() <= 0:
                            self.printCallback(timeout=True)
                            
                # call method every 0.5 sec    
                nextCall += 0.5
                time.sleep(nextCall - time.time())

        except Exception as exception:
            print(Fore.WHITE + Back.RED + Style.BRIGHT + '\nCommand {}: {} - Exception during callback reception: {}.'.format(self.__instCount, self.__cmdName, exception), Style.RESET_ALL)
            self.__callbackThread.do_run = False
            self.printCallback()
            
    absReleaseTime = property(getReleaseTime, setReleaseTime)
    relReleaseTime = property(getRelativeReleaseTime)
       