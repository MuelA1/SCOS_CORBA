#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Class for telemetry parameter settings

TMParameter -- describes parameter callback progression
"""

import IMIB
import os
from subprocess import Popen
from prettytable import PrettyTable 
import TimeModule
from colorama import Fore, Style
import threading
import time

class TMParameter():
        
    __paramView = None
    __notifyParameterListStatic = []
    __PIPE_PATH_Param = None
    __paramTerm = None
    __callbackTable = PrettyTable([Style.BRIGHT + 'Name', 'Description', 'Sample time', 'OOL state', 'Raw value [Vldity]', 'Eng. value [Vldity]', 'Vldity' + Style.RESET_ALL])
    __callbackTable.horizontal_char = '='  
    __callbackTable.align['Raw value [Vldity]'] = 'r'
    __callbackTable.align['Eng value [Vldity]'] = 'r'              
    __oolStateDict = {'n':Fore.GREEN + 'NOMINAL' + Style.RESET_ALL, 'v':Fore.RED + 'VIOLATION' + Style.RESET_ALL, 'u':'WARNING_UNKNOWN', 'l':'WARNING_LOW', 'h':'WARNING_HIGH', 'U':'ALARM_UNKNOWN', 'L':Fore.RED + 'ALARM_LOW' + Style.RESET_ALL, 'H':Fore.RED + 'ALARM_HIGH' + Style.RESET_ALL, 'S':'SCC'}
    __validityDict = {'0x00000001':'STATE_OFF', '0x00000002':'POWER_OFF', '0x00000004':'ROUTE_OFF', '0x00000008':'MISC',  # INVALID - 4 bits
                      '0x00000010':'TRANSIENT',  # TRANSIENT - 1 bit
                      '0x00002000':'EXPIRED',  #EXPIRED - 1 bit
                      '0x00004000':'UNKNOWN_STATE', '0x00008000':'UNKNOWN_COMMAND', '0x00010000':'UNKNOWN_CRITERIA', '0x00020000':'CALIBRATION', '0x00040000':'TOO_EARLY', '0x00080000':'UNKNOWN_PKT',  # INDETERMINABLE - 6 bits
                      '0x00100000':'UNINIT', '0x00200000':'PKT_RETRV', '0x00400000':'MIB_ERROR', '0x00800000':'SYSTEM_ERROR', '0x01000000':'FIELD_UNKNOWN', '0x02000000':'FIELD_ABSENT', '0x04000000':'UNKNOWN_TYPE', '0x08000000':'UNKNOWN_OP', '0x10000000':'VAL_UNKNOWN_CONV', '0x20000000':'OVERFLOW', '0x40000000':'DIVIDE_BY_ZERO', '0x80000000':'OL_PARSE'}  # GENERAL SYSTEM ERROR - 12 bits  
    #__tableRows = []
    #__paramNamesList = []
    
    def __init__(self, name, description):
        
        self.__paramName = name
        self.__paramDescription = description
        self.__paramMIBDef = None
        self.__paramIF = None
        self.__viewKey = None
        
        self.__paramList = []
        self.__callbackThread = None
        self.__globalCallbackCounter = 0
        self.__localCallbackCounter = 0    
        
    def setParameterDef(self, paramDef):
        self.__paramMIBDef = paramDef
               
    def getParameterFromServer(self, paramMngr):        
        # also provides MIB access
        self.__paramIF = paramMngr.getParameter(self.__paramName, self.__paramView)
    
    def registerParameter(self):
    
        #self.__paramNamesList.append(Style.BRIGHT + self.__paramName)
        
        # arg2: notify on every update, arg3: notify if selected value (raw, default,...) changes (IMIB.PARAM_OOL interesting), arg4: notify only once 
        # arg3: IMIB.PARAM_RAW_VALUE (IMIB.ParamValueType)       
        self.__viewKey = self.__paramIF.registerParam(self.__paramView, True, False, False)
        
        # Test
        paramInit = self.__paramIF.registerParamInit(self.__paramView, True, False, False)
        self.__notifyParameterListStatic.append((self.__viewKey, paramInit.m_initValue)) 
        
        # start callback thread          
        self.__callbackThread = threading.Thread(target=self.printParameterValue)
        self.__callbackThread.start()
    
    def unregisterParamView(self):       
        self.__paramIF.unregisterView(self.__viewKey)
        print('Unregistered parameter view...')

    def getViewKey(self):
        return self.__viewKey

    def printParameterValue(self):

        try:
            nextCall = time.time()
            
            while getattr(self.__callbackThread, 'do_run', True):                              
                while self.__globalCallbackCounter < len(self.__notifyParameterListStatic): 
                    if self.__notifyParameterListStatic[self.__globalCallbackCounter][0] == self.__viewKey:                        
                        self.__paramList.append(self.__notifyParameterListStatic[self.__globalCallbackCounter][1])
            
                        self.__callbackTable.add_row([Style.BRIGHT + self.__paramName + Style.RESET_ALL,
                                                      self.__paramDescription,
                                                      TimeModule.ibaseTime2SCOSdate(self.__paramList[self.__localCallbackCounter].m_sampleTime),
                                                      self.__oolStateDict.get(self.__paramList[self.__localCallbackCounter].m_oolState),
                                                      f'{vars(self.__paramList[self.__localCallbackCounter].m_rawValue.m_value).get("_v"):.3f} [{self.__validityDict.get(self.__paramList[self.__localCallbackCounter].m_rawValue.m_validity)}]',
                                                      Style.BRIGHT + f'{vars(self.__paramList[self.__localCallbackCounter].m_engValue.m_value).get("_v"):.3f}' + Style.RESET_ALL + f' ({self.__paramMIBDef.m_engValueUnit}) [{self.__validityDict.get(self.__paramList[self.__localCallbackCounter].m_engValue.m_validity)}]',
                                                      self.__paramIF.allValuesValid()])

                        with open(self.__PIPE_PATH_Param, 'w') as paramTerminal:                   
                            with self.__paramTerm.location():
                                paramTerminal.write(self.__paramTerm.move(3, 0) + self.__callbackTable.get_string())

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

# callback
# m_initValue=ITM.AllValues(m_sampleTime=IBASE.Time(m_sec=1511367658, m_micro=916000, m_isDelta=False),
#                           m_oolState='n', 
#                           m_sccState='\x00', 
#                           m_rawValue=ITM.ReducedValue(m_value=IBASE.Variant(m_doubleFormat = -0.37105342745780945), m_validity=24576), 
#                           m_engValue=ITM.ReducedValue(m_value=IBASE.Variant(m_doubleFormat = -0.37105342745780945), m_validity=24576), 
#                           m_synValue=ITM.ReducedValue(m_value=IBASE.Variant(m_nullFormat = False), m_validity=0), 
#                           m_sourceValue=ITM.ReducedValue(m_value=IBASE.Variant(m_doubleFormat = -0.37105342745780945), m_validity=24576), 
#                           m_defaultValue=ITM.ReducedValue(m_value=IBASE.Variant(m_doubleFormat = -0.37105342745780945), m_validity=24576)))

# MIB data 
#IMIB.ParamDef(m_name='PBTPWR00', 
#              m_description='BAT_STR_POWER_0', 
#              m_type='0', 
#              m_width=32, 
#              m_hasValPar=True, 
#              m_valPar='PBVPWR00', 
#              m_valChk=1, 
#              m_valueFlags=4912, 
#              m_rawValueUnit='RAW', 
#              m_engValueUnit='W', 
#              m_synValueUnit='', 
#              m_sourceValueUnit='RAW', 
#              m_defaultValueUnit='W', 
#              m_calibration=IMIB.Calibration(m_pointCalibration = IMIB.PointCalibration(m_name='W', m_description='Display Unit W', m_interpretation=True, m_points=[IMIB.CalibrationPoint(m_sourceValue=-1000000.0, m_calibValue=-1000000.0), IMIB.CalibrationPoint(m_sourceValue=1000000.0, m_calibValue=1000000.0)])), 
#              m_sourceValueDetails=IMIB.ValueDetailDef(m_hasValueRange=True, m_minValue=-1200000.0, m_maxValue=1200000.0, m_valueType='float1', m_decim=8, m_hasLimits=False), m_calibValueDetails=IMIB.ValueDetailDef(m_hasValueRange=True, m_minValue=-122.0, m_maxValue=142.0, m_valueType='float1', m_decim=3, m_hasLimits=True))
        
    @classmethod    
    def setParamView(cls, paramView):
        cls.__paramView = paramView

    @classmethod        
    def getParameterNotification(cls, key, value):
        cls.__notifyParameterListStatic.append((key, value))        
        #with open(cls.__PIPE_PATH_Param, 'w') as paramTerminal:
            #paramTerminal.write(str(key) + ': ' + str(value) + '\n\n') 
        
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
            