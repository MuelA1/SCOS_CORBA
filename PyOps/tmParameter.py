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
from terminaltables import AsciiTable 
import TimeModule
from colorama import Fore, Style
import threading
import time

class TMParameter():
        
    __paramView = None
    __notifyParameterListStatic = []
    __PIPE_PATH_Param = None
    __paramTerm = None            
    __oolStateDict = {'n':Fore.GREEN + 'NOMINAL' + Style.RESET_ALL, 'v':Fore.RED + 'VIOLATION' + Style.RESET_ALL, 'u':'WARNING_UNKNOWN', 'l':'WARNING_LOW', 'h':'WARNING_HIGH', 'U':'ALARM_UNKNOWN', 'L':Fore.RED + 'ALARM_LOW' + Style.RESET_ALL, 'H':Fore.RED + 'ALARM_HIGH' + Style.RESET_ALL, 'S':'SCC'}
    __valueTypeDict = {'raw':IMIB.PARAM_RAW_VALUE, 'eng':IMIB.PARAM_ENG_VALUE, 'syn':IMIB.PARAM_SYN_VALUE, 'src':IMIB.PARAM_SOURCE_VALUE, 'def':IMIB.PARAM_DEFAULT_VALUE, 'ool':IMIB.PARAM_OOL, 'scc':IMIB.PARAM_SCC}

    __rows = {}
    __paramLock = threading.Lock()
    __globalParamList = []
    __tableHeaders = [Style.BRIGHT + 'Name', 'Description', 'Sample time', 'OOL state', 'Raw value', 'Eng value (Unit)', 'Vldity' + Style.RESET_ALL]
    
    def __init__(self, name, description, notifyEveryUpdate=True, notifySelectedValChange=False, notifyOnlyOnce=False):
        
        self.__globalParamList.append(self)
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
        self.__callbackThread = None
        self.__globalCallbackCounter = 0
        self.__localCallbackCounter = 0    
        
        self.__TESTThread = None
        
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
        
        # Test
        #paramInit = self.__paramIF.registerParamInit(self.__paramView, self.__notifyEveryUpdate, self.__notifySelectedValChange, self.__notifyOnlyOnce)
           
        # start callback thread          
        self.__callbackThread = threading.Thread(target=self.printParameterValue)
        self.__callbackThread.start()
            
    def getViewKey(self):
        return self.__viewKey

    def getLastValidValue(self, raw=False):
                
        print(f'Checking last valid parameter value ({self.__paramName})...', end='')
        reverseParamList = self.__paramList[::-1]
               
        if reverseParamList != []:                           

            if raw == False:            
                for param in reverseParamList:
                    if param.m_engValue.m_validity == 0:                       
                        print(Fore.GREEN + f'got value << {vars(param.m_engValue.m_value).get("_v")} >>' + Style.RESET_ALL)                                                     
                        return vars(param.m_engValue.m_value).get('_v')                        
                    elif param == reverseParamList[-1]:
                        print(Fore.RED + 'no valid eng. value received' + Style.RESET_ALL)
                        self.__flush()
                        return 'NOT_VALID'
            elif raw == True:
                for param in reverseParamList:   
                    if param.m_rawValue.m_validity == 0:                                       
                        print(Fore.GREEN + f'got value << {vars(param.m_rawValue.m_value).get("_v")} >>' + Style.RESET_ALL)                                                          
                        return vars(param.m_rawValue.m_value).get('_v')                                               
                    elif param == reverseParamList[-1]:
                        print(Fore.RED + 'no valid raw value received' + Style.RESET_ALL)
                        self.__flush()
                        return 'NOT_VALID'
                    
        else:
            print(Fore.RED + 'no parameter received' + Style.RESET_ALL)
            return None
                               
    def printParameterValue(self):

        try:
            nextCall = time.time()                        
            while getattr(self.__callbackThread, 'do_run', True):                              
                while self.__globalCallbackCounter < len(self.__notifyParameterListStatic): 
                    if self.__notifyParameterListStatic[self.__globalCallbackCounter][0] == self.__viewKey:                        
                        self.__paramList.append(self.__notifyParameterListStatic[self.__globalCallbackCounter][1])
                        
                        self.__paramLock.acquire()
                        self.__rows[self.__paramName] = [Style.BRIGHT + self.__paramName + Style.RESET_ALL,
                                                         self.__paramDescription,
                                                         TimeModule.ibaseTime2SCOSdate(self.__paramList[self.__localCallbackCounter].m_sampleTime),
                                                         self.__oolStateDict.get(self.__paramList[self.__localCallbackCounter].m_oolState),
                                                         f'{vars(self.__paramList[self.__localCallbackCounter].m_rawValue.m_value).get("_v")}',
                                                         Style.BRIGHT + f'{vars(self.__paramList[self.__localCallbackCounter].m_engValue.m_value).get("_v")}' + Style.RESET_ALL + f' ({self.__paramMIBDef.m_engValueUnit})',
                                                         self.__paramIF.allValuesValid()]     
                        
                        completeRows = []
                        for row in self.__rows.values():
                            completeRows.append(row) 
                            
                        with open(self.__PIPE_PATH_Param, 'w') as paramTerminal:                   
#                            paramTerminal.write(self.__paramTerm.move(3, 0) + self.__callbackTable.get_string() + '\n')                        
                            paramTerminal.write(self.__paramTerm.move(3, 0) + tabulate(completeRows, 
                                                                                       headers=self.__tableHeaders) 
                                                                                       + '\n') #floatfmt='.8f', tablefmt='fancy_grid'

                            # Terminaltables
#                            completeRows.insert(0, self.__tableHeaders)
#                            table = AsciiTable(completeRows)
#                            table.outer_border = False
#                            paramTerminal.write(self.__paramTerm.move(0, 3) + '\n' + table.table + '\n')  
    
                        self.__paramLock.release()
                        
                        self.__localCallbackCounter += 1    
                    self.__globalCallbackCounter += 1

                # call method every 0.5 sec    
                nextCall += 0.5
                time.sleep(nextCall - time.time())

        except Exception as exception:
            self.__callbackThread.do_run = False
            with open(self.__PIPE_PATH_Param, 'w') as paramTerminal:                   
                with self.__paramTerm.location(0, self.__paramTerm.height - 1):
                    paramTerminal.write(self.__paramTerm.bold_red(f'\nParameter {self.__paramName} - Exception during value reception: ') + f'{exception}')
       
    def unregisterParamView(self):    
    
        if self.__callbackThread.isAlive():
            self.__callbackThread.do_run = False
        self.__paramIF.unregisterView(self.__viewKey)                                    
        print(f'Unregistered parameter {self.__paramName}...')   
                        
    def __flush(self, sleep=0.02):
        
        sys.stdout.flush()
        time.sleep(sleep)

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
            paramTerminal.write('\n' +  cls.__paramTerm.bold('Waiting for TM parameter...') + '\n')    
            