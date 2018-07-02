#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Class for telemetry parameter settings

TMParameter -- describes parameter callback progression

callback
m_initValue=ITM.AllValues(m_sampleTime=IBASE.Time(m_sec=1511367658, m_micro=916000, m_isDelta=False),
                          m_oolState='n', 
                          m_sccState='\x00', 
                          m_rawValue=ITM.ReducedValue(m_value=IBASE.Variant(m_doubleFormat = -0.37105342745780945), m_validity=24576), 
                          m_engValue=ITM.ReducedValue(m_value=IBASE.Variant(m_doubleFormat = -0.37105342745780945), m_validity=24576), 
                          m_synValue=ITM.ReducedValue(m_value=IBASE.Variant(m_nullFormat = False), m_validity=0), 
                          m_sourceValue=ITM.ReducedValue(m_value=IBASE.Variant(m_doubleFormat = -0.37105342745780945), m_validity=24576), 
                          m_defaultValue=ITM.ReducedValue(m_value=IBASE.Variant(m_doubleFormat = -0.37105342745780945), m_validity=24576)))

MIB data 
IMIB.ParamDef(m_name='PBTPWR00', 
              m_description='BAT_STR_POWER_0', 
              m_type='0', 
              m_width=32, 
              m_hasValPar=True, 
              m_valPar='PBVPWR00', 
              m_valChk=1, 
              m_valueFlags=4912, 
              m_rawValueUnit='RAW', 
              m_engValueUnit='W', 
              m_synValueUnit='', 
              m_sourceValueUnit='RAW', 
              m_defaultValueUnit='W', 
              m_calibration=IMIB.Calibration(m_pointCalibration = IMIB.PointCalibration(m_name='W', m_description='Display Unit W', m_interpretation=True, m_points=[IMIB.CalibrationPoint(m_sourceValue=-1000000.0, m_calibValue=-1000000.0), IMIB.CalibrationPoint(m_sourceValue=1000000.0, m_calibValue=1000000.0)])), 
              m_sourceValueDetails=IMIB.ValueDetailDef(m_hasValueRange=True, m_minValue=-1200000.0, m_maxValue=1200000.0, m_valueType='float1', m_decim=8, m_hasLimits=False), m_calibValueDetails=IMIB.ValueDetailDef(m_hasValueRange=True, m_minValue=-122.0, m_maxValue=142.0, m_valueType='float1', m_decim=3, m_hasLimits=True))

"""

import IMIB
import os
import sys
from subprocess import Popen
from tabulate import tabulate
import timeModule
from colorama import Fore, Style
import threading
import time
import logging

class TMParameter():
        
    __paramView = None
    __notifyParameterListStatic = []
    __PIPE_PATH_Param = None
    __paramTerm = None            
    __oolStateDict = {'n':Fore.GREEN + 'NOMINAL' + Style.RESET_ALL, 'v':Fore.RED + 'VIOLATION' + Style.RESET_ALL, 'u':'WARNING_UNKNOWN', 'l':'WARNING_LOW', 'h':'WARNING_HIGH', 'U':'ALARM_UNKNOWN', 'L':Fore.RED + 'ALARM_LOW' + Style.RESET_ALL, 'H':Fore.RED + 'ALARM_HIGH' + Style.RESET_ALL, 'S':'SCC'}
    __oolLogStateDict = {'n':'NOMINAL', 'v':'VIOLATION', 'u':'WARNING_UNKNOWN', 'l':'WARNING_LOW', 'h':'WARNING_HIGH', 'U':'ALARM_UNKNOWN', 'L':'ALARM_LOW', 'H':'ALARM_HIGH', 'S':'SCC'}
    __valueTypeDict = {'raw':IMIB.PARAM_RAW_VALUE, 'eng':IMIB.PARAM_ENG_VALUE, 'syn':IMIB.PARAM_SYN_VALUE, 'src':IMIB.PARAM_SOURCE_VALUE, 'def':IMIB.PARAM_DEFAULT_VALUE, 'ool':IMIB.PARAM_OOL, 'scc':IMIB.PARAM_SCC}

    __rows = {}
    __paramLock = threading.Lock()
    __globalParamList = []
    __tableHeaders = [Style.BRIGHT + 'Name', 'Description', 'Sample time', 'OOL state', 'Raw value', 'Eng value (Unit)', 'Vldity' + Style.RESET_ALL]
    __tableLogHeaders = ['Sample time', 'OOL state', 'Raw value', 'Eng value (Unit)', 'Vldity']
    __paramCount = 0       
    __verbosityLevel = 2
    
    def __init__(self, name, description, notifyEveryUpdate=True, notifySelectedValChange=False, notifyOnlyOnce=False):
        
        self.__globalParamList.append(self)
        type(self).__paramCount += 1
        self.__instCount = self.__paramCount
        self.__paramName = name
        self.__paramDescription = description
        self.__paramMIBDef = None
        self.__paramIF = None
        self.__viewKey = None
             
        self.__notifyEveryUpdate = notifyEveryUpdate
        if type(notifySelectedValChange) == str and notifySelectedValChange in self.__valueTypeDict.keys():
            self.__notifySelectedValChange = self.__valueTypeDict.get(notifySelectedValChange)
        else:    
            self.__notifySelectedValChange = notifySelectedValChange
        
        self.__notifyOnlyOnce = notifyOnlyOnce
        
        self.__paramList = []
        self.__paramTableRows = []
        
        self.__callbackThread = None
        self.__globalCallbackCounter = 0
        self.__localCallbackCounter = 0    
                     
    def __str__(self):
        
        if self.__instCount > 999:
            disp = 80
        elif self.__instCount > 99:
            disp = 81
        elif self.__instCount > 9:
            disp = 82
        else:
            disp = 83
            
        string = '\n' + '*' * 95
        string += f'\nParameter {self.__instCount} {self.__paramName:=^{disp}}\n' 
        string += '*' * 95 + '\n\n' 
                  
        string += 'Description ' + '-' * 83 + '\n\n'
        string += f'{self.__paramDescription}\n\n'
        
        string += 'Received values ' + '-' * 79 + '\n\n'
        
        if self.__paramTableRows != []:
            string += tabulate(self.__paramTableRows, headers=self.__tableLogHeaders) + '\n\n'
            string += '-' * 95 + '\n'
            string += f'Parameter {self.__instCount} ({self.__paramName}) received {len(self.__paramList)} callback(s)\n'
            string += '-' * 95 
        else:
            string += f'Parameter {self.__instCount} ({self.__paramName}) received no callback\n\n'        
            string += '-' * 95
                
        return string
        
    def setParameterDef(self, paramDef):
        self.__paramMIBDef = paramDef
               
    def getParameterFromServer(self, paramMngr):        
        # also provides MIB access
        self.__paramIF = paramMngr.getParameter(self.__paramName, self.__paramView)
    
    def registerParameter(self):
            
        # arg2: notify on every update
        # arg3: notify if selected value (raw, default,...) changes (IMIB.PARAM_OOL interesting), IMIB.PARAM_RAW_VALUE (IMIB.ParamValueType) 
        # arg4: notify only once            
        self.__viewKey = self.__paramIF.registerParam(self.__paramView, self.__notifyEveryUpdate, self.__notifySelectedValChange, self.__notifyOnlyOnce)
        print(f'Parameter {self.__instCount} (' + Style.BRIGHT + f'{self.__paramName}' + Style.RESET_ALL + ') is registered...')        
        logging.debug(f'Parameter {self.__instCount} ({self.__paramName}) is registered...')
        
        # Test
        # paramInit = self.__paramIF.registerParamInit(self.__paramView, self.__notifyEveryUpdate, self.__notifySelectedValChange, self.__notifyOnlyOnce)
        
        # start callback thread          
        self.__callbackThread = threading.Thread(target=self.printParameterValue)
        self.__callbackThread.start()
            
    def getViewKey(self):
        return self.__viewKey
                               
    def printParameterValue(self):

        try:
            nextCall = time.time()                        
            while getattr(self.__callbackThread, 'do_run', True):                              
                while self.__globalCallbackCounter < len(self.__notifyParameterListStatic): 
                    if self.__notifyParameterListStatic[self.__globalCallbackCounter][0] == self.__viewKey:                        
                        self.__paramList.append(self.__notifyParameterListStatic[self.__globalCallbackCounter][1])                       
                        logging.debug(f'Parameter {self.__instCount} ({self.__paramName}) received callback...')
                        
                        self.__paramTableRows.append([timeModule.ibaseTime2SCOSdate(self.__paramList[self.__localCallbackCounter].m_sampleTime),
                                                      self.__oolLogStateDict.get(self.__paramList[self.__localCallbackCounter].m_oolState),
                                                      f'{vars(self.__paramList[self.__localCallbackCounter].m_rawValue.m_value).get("_v")}',
                                                      f'{vars(self.__paramList[self.__localCallbackCounter].m_engValue.m_value).get("_v")} ({self.__paramMIBDef.m_engValueUnit})',
                                                      self.__paramIF.allValuesValid()])
                        
                        if self.__verbosityLevel == 2:                            
                            self.__paramLock.acquire()                                                        
                            self.__rows[self.__paramName] = [Style.BRIGHT + self.__paramName + Style.RESET_ALL,
                                                             self.__paramDescription,
                                                             timeModule.ibaseTime2SCOSdate(self.__paramList[self.__localCallbackCounter].m_sampleTime),
                                                             self.__oolStateDict.get(self.__paramList[self.__localCallbackCounter].m_oolState),
                                                             f'{vars(self.__paramList[self.__localCallbackCounter].m_rawValue.m_value).get("_v")}',
                                                             Style.BRIGHT + f'{vars(self.__paramList[self.__localCallbackCounter].m_engValue.m_value).get("_v")}' + Style.RESET_ALL + f' ({self.__paramMIBDef.m_engValueUnit})',
                                                             self.__paramIF.allValuesValid()]                                 
                            completeRows = []
                            for row in self.__rows.values():
                                completeRows.append(row) 
                                
                            with open(self.__PIPE_PATH_Param, 'w') as paramTerminal:                                                                   
                                paramTerminal.write(self.__paramTerm.clear() + '\n' +  self.__paramTerm.bold('=' * 120 + '\nTM parameters\n' + '=' * 120) +
                                                    self.__paramTerm.move(5, 0) + tabulate(completeRows, headers=self.__tableHeaders)) #floatfmt='.8f'        
                            self.__paramLock.release()
                        
                        self.__localCallbackCounter += 1    
                    self.__globalCallbackCounter += 1

                # call method every 0.5 sec    
                nextCall += 0.5
                time.sleep(nextCall - time.time())

        except Exception as exception:
            self.__callbackThread.do_run = False
            print(Fore.RED + Style.BRIGHT + f'\nParameter {self.__paramName} - Exception during value reception: ' + Style.RESET_ALL + f'{exception}')
            logging.exception(f'Parameter {self.__paramName} - Exception during value reception: {exception}', exc_info=False)
            
    def getLastValidValue(self, raw=False):
               
        print(f'Parameter {self.__instCount} (' + Style.BRIGHT + f'{self.__paramName}' + Style.RESET_ALL + ') is checking last valid value...',
              end='' if self.__verbosityLevel == 2 else '\n')
        logging.info(f'Parameter {self.__instCount} ({self.__paramName}) is checking last valid value...')
        self.__flush()
                
        reverseParamList = self.__paramList[::-1]
               
        if reverseParamList != []:                           

            if raw == False:            
                for param in reverseParamList:
                    if param.m_engValue.m_validity == 0:
                        if self.__verbosityLevel == 2:
                            print('got value <<' + Fore.GREEN + f'{vars(param.m_engValue.m_value).get("_v")}' + Style.RESET_ALL + '>>')                                                                             
                        elif self.__verbosityLevel == 1:
                            print(f'Parameter {self.__instCount} (' + Style.BRIGHT + f'{self.__paramName}' + Style.RESET_ALL + ') received value <<' + Fore.GREEN + f'{vars(param.m_engValue.m_value).get("_v")}' + Style.RESET_ALL + f'>> @ {timeModule.ibaseTime2SCOSdate(timeModule.stamp2ibaseTime(time.time()))}...')                                                                                                           
                        logging.info(f'Parameter {self.__instCount} ({self.__paramName}) received eng. value ({vars(param.m_engValue.m_value).get("_v")})...')
                        logging.info('\n' + str(self) + '\n')
                        self.__flush()  
                        return vars(param.m_engValue.m_value).get('_v')                        
                    elif param == reverseParamList[-1]:
                        if self.__verbosityLevel == 2:
                            print(Fore.RED + 'no valid eng. value received' + Style.RESET_ALL)              
                        elif self.__verbosityLevel == 1:
                            print(f'Parameter {self.__instCount} (' + Style.BRIGHT + f'{self.__paramName}' + Style.RESET_ALL + ') received ' + Fore.RED + 'no valid eng. value' + Style.RESET_ALL + f' @ {timeModule.ibaseTime2SCOSdate(timeModule.stamp2ibaseTime(time.time()))}...')                             
                        logging.warning(f'Parameter {self.__instCount} ({self.__paramName}) received no valid eng. value...')
                        logging.warning('\n' + str(self) + '\n')
                        self.__flush()
                        return 'NOT_VALID'
            elif raw == True:
                for param in reverseParamList:   
                    if param.m_rawValue.m_validity == 0:                                                                                                                                           
                        if self.__verbosityLevel == 2:
                            print('got value <<' + Fore.GREEN + f'{vars(param.m_rawValue.m_value).get("_v")}' + Style.RESET_ALL + '>>')                                                                                 
                        elif self.__verbosityLevel == 1:
                            print(f'Parameter {self.__instCount} (' + Style.BRIGHT + f'{self.__paramName}' + Style.RESET_ALL + ') received value <<' + Fore.GREEN + f'{vars(param.m_rawValue.m_value).get("_v")}' + Style.RESET_ALL + f'>> @ {timeModule.ibaseTime2SCOSdate(timeModule.stamp2ibaseTime(time.time()))}...')                                                                                                            
                        logging.info(f'Parameter {self.__instCount} ({self.__paramName}) received raw value ({vars(param.m_engValue.m_value).get("_v")})...')
                        logging.info('\n' + str(self) + '\n')
                        self.__flush() 
                        return vars(param.m_rawValue.m_value).get('_v')                         
                    elif param == reverseParamList[-1]:
                        if self.__verbosityLevel == 2:
                            print(Fore.RED + 'no valid raw value received' + Style.RESET_ALL)
                        elif self.__verbosityLevel == 1:
                            print(f'Parameter {self.__instCount} (' + Style.BRIGHT + f'{self.__paramName}' + Style.RESET_ALL + ') received ' + Fore.RED + 'no valid raw value' + Style.RESET_ALL + f' @ {timeModule.ibaseTime2SCOSdate(timeModule.stamp2ibaseTime(time.time()))}...')                            
                        logging.warning(f'Parameter {self.__instCount} ({self.__paramName}) received no valid raw value...')
                        logging.warning('\n' + str(self) + '\n')
                        self.__flush()
                        return 'NOT_VALID'                    
        else:
            if self.__verbosityLevel == 2:
                print(Fore.RED + 'no parameter callback received' + Style.RESET_ALL)                
            elif self.__verbosityLevel == 1:
                print(f'Parameter {self.__instCount} (' + Style.BRIGHT + f'{self.__paramName}' + Style.RESET_ALL + ') ' + Fore.RED + 'received no callback' + Style.RESET_ALL + f' @ {timeModule.ibaseTime2SCOSdate(timeModule.stamp2ibaseTime(time.time()))}...')                           
            logging.error(f'Parameter {self.__instCount} ({self.__paramName}) received no callback...')           
            self.__flush()
            return None
       
    def unregisterParamView(self):    
    
        if self.__callbackThread.isAlive():
            self.__callbackThread.do_run = False
        self.__paramIF.unregisterView(self.__viewKey)                                    
        print(f'Unregistered parameter {self.__instCount} ({self.__paramName})...')   
        logging.debug(f'Unregistered parameter {self.__instCount} ({self.__paramName})...')
        self.__flush()        
                
    def __flush(self, sleep=0.02):
        
        sys.stdout.flush()
        time.sleep(sleep)

    @classmethod
    def getGlobalParamList(cls):
        return cls.__globalParamList
    
    @classmethod
    def unregisterAllTmParameters(cls):
        
        for param in cls.__globalParamList:
            param.unregisterParamView()

    @classmethod    
    def setParamView(cls, paramView):
        cls.__paramView = paramView

    @classmethod        
    def getParameterNotification(cls, key, value):
        cls.__notifyParameterListStatic.append((key, value))        
               
    @classmethod    
    def setVerbosityLevel(cls, verbLevel):
        cls.__verbosityLevel = verbLevel

    @classmethod    
    def getVerbosityLevel(cls):
        return cls.__verbosityLevel 
    
    @classmethod
    def createParamNotificationTerminal(cls, term, terminalType):
        
        cls.__paramTerm = term
        cls.__PIPE_PATH_Param = '/tmp/paramNotifyPipe'  
        
        if os.path.exists(cls.__PIPE_PATH_Param):
            os.remove(cls.__PIPE_PATH_Param)
         
        # named pipe            
        os.mkfifo(cls.__PIPE_PATH_Param)
            
        # new terminal subprocess ('xterm' also possible) 
        Popen([terminalType, '-e', 'tail -f %s' % cls.__PIPE_PATH_Param])   
               
        with open(cls.__PIPE_PATH_Param, 'w') as paramTerminal:
            paramTerminal.write('\n' +  cls.__paramTerm.bold('=' * 120 + '\nTM parameters\n' + '=' * 120) + '\n')    
            