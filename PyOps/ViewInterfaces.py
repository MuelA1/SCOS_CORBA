#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Implement client side views to get callbacks from server

"""

import ITC_INJ__POA, TimeModule
from colorama import Fore, Back, Style

class CommandInjectMngrView(ITC_INJ__POA.CommandInjectMngrView):
    
    def __init__(self):
        print('\nCreating client view...\n')
        
        self.__commandCounter = 0       
        self.__commandStatusList = []
        self.__systemStatusList = []
        self.__stageDict = {'D':'PTV_DYNAMIC','s':'PTV_STATIC','R':'MCS_RELEASE','G':'UV_GS_RECEIVE','T':'UV_GS_UPLINK','O':'UV_ONB_ACCEPT','A':'EV_APP_ACCEPT',
                            'S':'EV_START_EXEC','0':'EV_PROGRESS_0','1':'EV_PROGRESS_1','2':'EV_PROGRESS_2','3':'EV_PROGRESS_3','4':'EV_PROGRESS_4','5':'EV_PROGRESS_5',
                            '6':'EV_PROGRESS_6','7':'EV_PROGRESS_7','8':'EV_PROGRESS_8','9':'EV_PROGRESS_9','C':'EV_END_EXEC'}
        
        self.__statusDict = {0x0001:'NOT_APPLICABLE',0x0002:'PASSED',0x0004:'UNCERTAIN_PASSED',0x0008:'UNVERIFIED',0x0010:'IDLE',0x0020:'PENDING',0x0040:'DISABLED',0x0080:'FAILED',
                             0x0100:'UNCERTAIN_FAILED',0x0200:'UNKNOWN',0x0400:'AFFECTED',0x0800:'SUPERSEDED',0x1000:'TIMEOUT',0x2000:'ASSUMED',0x4000:'SCC'}
                                                                 
    def ping(self):
        print('Pong')
    
    # command status    
    def updateRequestStatus(self,status):
        print(Fore.BLUE + Style.BRIGHT + '\nCommand status update {0}:'.format(self.__commandCounter), Style.RESET_ALL)
        self.__commandStatusList.append(status)
        
        print('Command ID: ' + Fore.BLUE + Style.BRIGHT + '{0}'.format(self.__commandStatusList[self.__commandCounter].m_request_id), Style.RESET_ALL)
        print('SCOS multiplexer ID (ticket): ' + Fore.BLUE + Style.BRIGHT + '({0},{1})'.format(self.__commandStatusList[self.__commandCounter].m_multiplexer_id.m_id,self.__commandStatusList[self.__commandCounter].m_multiplexer_id.m_elemIndex), Style.RESET_ALL)
        print('Command progression stage: ' + Fore.BLUE + Style.BRIGHT + '{0}'.format(self.__stageDict.get(self.__commandStatusList[self.__commandCounter].m_stage)), Style.RESET_ALL)
        print('Stage success status: ' + Fore.BLUE + Style.BRIGHT + '{0}'.format(self.__statusDict.get(self.__commandStatusList[self.__commandCounter].m_stage_status)), Style.RESET_ALL)
        print('Update time: ' + Fore.BLUE + Style.BRIGHT + '{0}'.format(TimeModule.timestamp2SCOSdate(self.__commandStatusList[self.__commandCounter].m_updateTime.m_sec,self.__commandStatusList[self.__commandCounter].m_updateTime.m_micro)), Style.RESET_ALL)
        print('Completed: ' + Fore.BLUE + Style.BRIGHT + '{0}\n'.format(self.__commandStatusList[self.__commandCounter].m_completed_flag), Style.RESET_ALL) 
                
        self.__commandCounter = self.__commandCounter + 1
       
    # global system status
    def updateSystemStatus(self,status):
        print('\nSystem status update: {0}'.format(status))
        self.__systemStatusList.append(status)
