#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Implement client side views to get callbacks from server

"""

import ITC_INJ__POA
from colorama import Fore, Back, Style

class CommandInjectMngrView(ITC_INJ__POA.CommandInjectMngrView):
     
    def __init__(self):
        print('\nCreating client view...\n')
        
        self.__requestCounter = 0       
        self.__requestStatusList = []
        self.__systemStatusList = []
        
    def ping(self):
        print('Pong')
        
    def updateRequestStatus(self,status):
        print(Fore.BLUE + Style.BRIGHT + '\nRequest status update: {0}\n'.format(status), Style.RESET_ALL)
        self.__requestStatusList.append(status)
        
        if self.__requestStatusList[self.__requestCounter].m_stage == 's': 
            print('Current command stage is PTV_STATIC')
         
        if self.__requestStatusList[self.__requestCounter].m_stage_status == 128: 
            print(Fore.WHITE + Back.RED + Style.BRIGHT + 'CEV FAILED', Style.RESET_ALL)
        
        self.__requestCounter = self.__requestCounter + 1
       
    def updateSystemStatus(self,status):
        print('\nSystem status update: {0}'.format(status))
        self.__systemStatusList.append(status)
