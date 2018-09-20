#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Base class of agent classes

BaseAgent -- describes basic CORBA operations used by other agent classes

@author: Axel Müller
"""

import CORBA

class BaseAgent():
   
    def __init__(self):      
        self.__ip = ''
        self.__port = ''
        self._serverMngr = None               
        self.__orb = CORBA.ORB_init()
        self._isConnected = False
        
    def connect(self, ip, port, namingService, serverMngrType):
        self.__ip = ip
        self.__port = port
        self._serverMngr = self.__orb.string_to_object(f'corbaname::{self.__ip}:{self.__port}/NameService#{namingService}')   
        self._serverMngr = self._serverMngr._narrow(serverMngrType)       
        self._isConnected = True
       
    def createCorbaObject(self, mngrViewObject):
                
        poa = self.__orb.resolve_initial_references('RootPOA')
        poa.activate_object(mngrViewObject)
        mngrView = poa.servant_to_reference(mngrViewObject)
           
        # activate the poa, that incoming requests are served
        poaManager = poa._get_the_POAManager()
        poaManager.activate()
               
        return mngrView
    
    def getIp(self):
        return self.__ip    
    def setIp(self, ip):
        self.__ip = ip
        
    def getPort(self):
        return self.__port
    def setPort(self, port):
        self.__port = port
        
    def getPOAType(self):
        return self.__poaType
    def setPOAType(self, poaType):
        self.__poaType = poaType
        
    def getServerMngr(self):
        return self._serverMngr
            