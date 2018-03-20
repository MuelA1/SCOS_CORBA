#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Class command

"""

import IBASE, ITC, ITC_INJ
from CommandAgent import CommandAgent
from colorama import Fore, Back, Style

class Command(CommandAgent):
    
    def __init__(self):
        
        # empty time, command is not time tagged
        self.__emptyTime = IBASE.Time(0,0,False)
        self.__commandDescription = ''
        
        self.__context = ''
        self.__destination = ''
        self.__mapId = ITC_INJ.MAPID_DEFAULT
        self.__vcId = ITC_INJ.VCID_DEFAULT
        self.__cmdName = ''
        self.__cmdParameters = []
        self.__paramSets = []
        self.__info = ITC_INJ.ReleaseInfo(self.__emptyTime,self.__emptyTime,self.__emptyTime,self.__emptyTime,ITC.CHECK_OVERRIDE,ITC.CHECK_OVERRIDE,True,ITC_INJ.ACK_MIB_DEFAULT)
        self.__ilockType = ITC.IL_NONE
        self.__ilockStageType = ITC_INJ.IL_UV_GS_ACCEPT
        self.__additionalInfo = ''
        self.__tcRequestID =  0
        
        self.__injRequestID = 0
        
        #CommandAgent.__init__(self)
        
    def setCommandName(self,commandName):
        self.__cmdName = commandName

    def setCommandDescription(self,description):
        self.__commandDescription = description

    # set default MIB command parameters (different structure for injection)
    def setCommandParameters(self,commandParameters):
        
        i = 0
        while i < len(commandParameters):                   
            paramStruct = ITC.CommandParam(commandParameters[i].m_name,commandParameters[i].m_engValueIsDefault,commandParameters[i].m_unit,commandParameters[i].m_defaultRadix,commandParameters[i].m_defaultValue)
            self.__cmdParameters.append(paramStruct)
            
            if str(self.__cmdParameters[i].m_value) in  ['IBASE.Variant(m_nullFormat = False)']:
                print(Fore.WHITE + Back.RED + Style.BRIGHT + "User input for parameter '{}' necessary. Value with unit '{}' has to be defined...".format(self.__cmdParameters[i].m_name,self.__cmdParameters[i].m_unit), Style.RESET_ALL)
            i = i + 1  
   
        print(Fore.GREEN + Style.BRIGHT + '\nDefault Command Parameters from MIB:', Style.RESET_ALL)
        for p in self.__cmdParameters:
            print(p)
        
    def setRequiredParameterValues(self,paramName,paramValue):

        i = 0
        while i < len(self.__cmdParameters): 
            if self.__cmdParameters[i].m_name in [paramName]:
                if str(self.__cmdParameters[i].m_value) in  ['IBASE.Variant(m_nullFormat = False)']:
                    self.__cmdParameters[i].m_value = IBASE.Variant(paramValue[0],paramValue[1])
                    break
            i = i+1        
        
    def injectCommand(self,cmdInjMngr):
        print(Fore.BLUE + Style.BRIGHT + '\nCommand Parameters for Injection:', Style.RESET_ALL)
        for p in self.__cmdParameters:
            print(p)
            
        cmdRequest = ITC_INJ.CommandRequest(self.__context,self.__destination,self.__mapId,self.__vcId,self.__cmdName,self.__cmdParameters,self.__paramSets,self.__info,self.__ilockType,self.__ilockStageType,self.__additionalInfo,self.__tcRequestID)
        print(Fore.WHITE + Back.BLACK + Style.BRIGHT + "\nInjecting command '{0}': {1}".format(self.__cmdName,self.__commandDescription),Style.RESET_ALL)
        #print(self._cmdInjMngr)
        self.__injRequestID = cmdInjMngr.injectCmd(cmdRequest)

