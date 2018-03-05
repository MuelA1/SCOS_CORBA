#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Base class of agent classes

"""

import CORBA

class BaseAgent():
   
    def __init__(self):      
        self.__ip = '192.168.56.101'
        self.__port = '20001'
        self.__poaType = 'omniINSPOA'       
        self._serverMngr = None
        
        self.__orb = CORBA.ORB_init()
        
    # call: str, ModuleType
    def connect(self,namingService,serverMngrType):
        self._serverMngr = self.__orb.string_to_object('corbaname::{0}:{1}/NameService#{2}'.format(self.__ip,self.__port,namingService))   
        self._serverMngr = self._serverMngr._narrow(serverMngrType)       
        return self._serverMngr

    def createCorbaObject(self,mngrViewObject,poaIdStr):
        
        poa = self.__orb.resolve_initial_references(self.__poaType)
        poaId = poaIdStr
        poa.activate_object_with_id(poaId,mngrViewObject)
        mngrView = poa.servant_to_reference(mngrViewObject)
           
        # activate the poa, that incoming requests are served
        poaManager = poa._get_the_POAManager()
        poaManager.activate()
        return mngrView
    
    def getIp(self):
        return self.__ip    
    def setIp(self,ip):
        self.__ip = ip
        
    def getPort(self):
        return self.__port
    def setPort(self,port):
        self.__port = port
        
    def getPOAType(self):
        return self.__poaType
    def setPOAType(self,poaType):
        self.__poaType = poaType
        
    def getServerMngr(self):
        print('Server manager is: {0}'.format(self._serverMngr))
        return self._serverMngr
            
        

