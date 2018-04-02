#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Class for command injection

Command -- describes command values, command injection and command status print
"""

import IBASE, ITC, ITC_INJ
import TimeModule
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
         
    def __init__(self,name = '',description = '',releaseTime = IBASE.Time(0,0,False),executionTime = IBASE.Time(0,0,False),staticPtv = 'D',dynamicPtv = 'D',cev = False,ilockType = ITC.IL_NONE,ilockStageType = '0'):
        
        self.__commandDescription = description

        self.__releaseTime = releaseTime            
        self.__executionTime = executionTime
        self.__staticPtv = staticPtv
        self.__dynamicPtv = dynamicPtv
        self.__cev = cev
         
        self.__context = ''
        self.__destination = ''
        self.__mapId = ITC_INJ.MAPID_DEFAULT
        self.__vcId = ITC_INJ.VCID_DEFAULT
        self.__cmdName = name
        self.__cmdParameters = []
        self.__paramSets = []
        self.__info = ITC_INJ.ReleaseInfo(self.__releaseTime,IBASE.Time(0,0,False),IBASE.Time(0,0,False),self.__executionTime,self.__staticPtv,self.__dynamicPtv,self.__cev,ITC_INJ.ACK_MIB_DEFAULT)
        self.__ilockType = ilockType
        self.__ilockStageType = ilockStageType
        self.__additionalInfo = ''
        self.__tcRequestID =  0
               
        self.__injRequestID = 0      
        self.__cmdInjMngr = None       
        self.__cmdMIBDef = None        
        self.__commandStatusList = []
        
    def __repr__(self):
        return 'name: {} \ndescription: {} \nparameters: {} \nrequestID: {} \nreleaseTime: {} \nexecutionTime: {} \nstaticPtv: {} \ndynamicPtv: {} \ncev: {} \nilockType: {} \nilockStageType: {} \nstatusList: {} \n'.format(self.__cmdName,
                self.__commandDescription,self.__cmdParameters,self.__injRequestID,self.__releaseTime,self.__executionTime,self.__staticPtv,self.__dynamicPtv,self.__cev,self.__ilockType,self.__ilockStageType,self.__commandStatusList)
    
    def __str__(self):
        cmdList = []
        i = 0
            
        while i < len(self.__commandStatusList):
            cmdList.append((self.__commandStatusList[i].m_stage,self.__statusDict.get(self.__commandStatusList[i].m_stage_status),TimeModule.timestamp2SCOSdate(self.__commandStatusList[i].m_updateTime.m_sec,self.__commandStatusList[i].m_updateTime.m_micro)))          
            i = i + 1
        
        return '{0} {1}'.format(self.__cmdName,cmdList)
        
    def setCommandInjMngr(self,cmdInjMngr):
        self.__cmdInjMngr = cmdInjMngr
    
    def setCommandDef(self,cmdDef):
        self.__cmdMIBDef = cmdDef
           
    # set default MIB command parameters (different structure for injection)
    def setMIBCommandParameters(self):
        
        i = 0
        while i < len(self.__cmdMIBDef.m_params):                   
            paramStruct = ITC.CommandParam(self.__cmdMIBDef.m_params[i].m_name,self.__cmdMIBDef.m_params[i].m_engValueIsDefault,self.__cmdMIBDef.m_params[i].m_unit,self.__cmdMIBDef.m_params[i].m_defaultRadix,self.__cmdMIBDef.m_params[i].m_defaultValue)
            self.__cmdParameters.append(paramStruct)
            
            if str(self.__cmdParameters[i].m_value) in  ['IBASE.Variant(m_nullFormat = False)']:
                print(Fore.WHITE + Back.RED + Style.BRIGHT + "User input for parameter '{}' necessary".format(self.__cmdParameters[i].m_name), Style.RESET_ALL)
            i = i + 1  
   
        print(Fore.GREEN + Style.BRIGHT + 'Default Command Parameters from MIB:', Style.RESET_ALL)
        for p in self.__cmdParameters:
            print(p)
                    
    def setCommandParameter(self,paramName,paramValue):

        i = 0
        while i < len(self.__cmdParameters): 
            if self.__cmdParameters[i].m_name in [paramName]:
                # override only default value, not previously set value (if default value = current value)
                if str(self.__cmdMIBDef.m_params[i].m_defaultValue) == str(self.__cmdParameters[i].m_value):               
                    if self.__cmdMIBDef.m_params[i].m_isEditable == True:
                        self.__cmdParameters[i].m_value = IBASE.Variant(paramValue[0],paramValue[1])
                        break
                    else:
                        print(Fore.WHITE + Back.RED + Style.BRIGHT + "Error: Parameter '{}' is not editable".format(self.__cmdParameters[i].m_name), Style.RESET_ALL)
                        break
            i = i+1               
        
    def injectCommand(self):
        print(Fore.BLUE + Style.BRIGHT + '\nCommand Parameters for Injection:', Style.RESET_ALL)
        for p in self.__cmdParameters:
            print(p)
            
        cmdRequest = ITC_INJ.CommandRequest(self.__context,self.__destination,self.__mapId,self.__vcId,self.__cmdName,self.__cmdParameters,self.__paramSets,self.__info,self.__ilockType,self.__ilockStageType,self.__additionalInfo,self.__tcRequestID)
        print(Fore.WHITE + Back.BLACK + Style.BRIGHT + "\nInjecting command '{0}': {1}".format(self.__cmdName,self.__commandDescription),Style.RESET_ALL)
        self.__injRequestID = self.__cmdInjMngr.injectCmd(cmdRequest)
                                 
    @classmethod    
    def getUpdateRequestStatus(cls,status):
        cls.__commandStatusListStatic.append(status)

    @classmethod        
    def getUpdateSystemStatus(cls,status):
        cls.__systemStatusListStatic.append(status)
        print(status)
        
    def getCommandStatus(self):
        # get callback for individual instance
        i = 0
        while i < len(self.__commandStatusListStatic): 
            if self.__commandStatusListStatic[i].m_request_id == self.__injRequestID:
                self.__commandStatusList.append(self.__commandStatusListStatic[i])

            i = i + 1
 
#    def printCommandCallback(self):
#        i = 0
#        while i < len(self.__commandStatusList):
#            print('Command ID: ' + Fore.BLUE + Style.BRIGHT + '{0}'.format(self.__commandStatusList[i].m_request_id), Style.RESET_ALL)
#            print('SCOS multiplexer ID (ticket): ' + Fore.BLUE + Style.BRIGHT + '({0},{1})'.format(self.__commandStatusList[i].m_multiplexer_id.m_id,self.__commandStatusList[i].m_multiplexer_id.m_elemIndex), Style.RESET_ALL)
#            print('Command progression stage: ' + Fore.BLUE + Style.BRIGHT + '{0}'.format(self.__stageDict.get(self.__commandStatusList[i].m_stage)), Style.RESET_ALL)
#            print('Stage success status: ' + Fore.BLUE + Style.BRIGHT + '{0}'.format(self.__statusDict.get(self.__commandStatusList[i].m_stage_status)), Style.RESET_ALL)
#            #print('Update time: ' + Fore.BLUE + Style.BRIGHT + '{0}'.format(TimeModule.timestamp2SCOSdate(self.__commandStatusList[i].m_updateTime.m_sec,self.__commandStatusList[i].m_updateTime.m_micro)), Style.RESET_ALL)
#            print('Completed: ' + Fore.BLUE + Style.BRIGHT + '{0}\n'.format(self.__commandStatusList[i].m_completed_flag), Style.RESET_ALL)     
#            
#            i = i + 1
          