#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Access to SCOS-2000 TM Packet Data 

TMPacketAgent -- describes access to telemetry packet services
"""

from BaseAgent import BaseAgent
import ITMP_PRO

class TMPacketAgent(BaseAgent):
       
    def __init__(self):
        super().__init__()
        self.__namingService = 'TMP_PRO_001'
        self.__serverMngrType = ITMP_PRO.TMPserverMngr
        self.__packetView = None
        self.__tmPServerType = None
        self.__packetMngr = None 
        self.__timeMngr = None 
        
    def getNamingService(self):
        return self.__namingService   
     
    def getServerMngrType(self):
        return self.__serverMngrType
    
    def createPacketView(self, packetView):
        self.__packetView = self.createCorbaObject(packetView)
        return self.__packetView
        
    def getPacketView(self):
        return self.__packetView
    
    def tmPServerType(self):
        self.__tmPServerType = self._serverMngr.getTMPserver(1)
           
    def getTmPServerType(self):
        return self.__tmPServerType
    
    def packetMngr(self):
        self.__packetMngr = self.__tmPServerType.m_packetMngr
        
    def getPacketMngr(self):
        return self.__packetMngr
    
    def timeMngr(self):
        self.__timeMngr = self.__tmPServerType.m_timeMngr
              
    def getTimeMngr(self):
        return self.__timeMngr
    
