#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Command Injection Services
Access to SCOS-2000 commanding system

"""

import sys
import CORBA, IBASE, ITC, ITC_INJ, ITC_INJ__POA

#==============================================================================
#                           Implement client side view
#==============================================================================

try:
    class CommandInjectMngrView(ITC_INJ__POA.CommandInjectMngrView):
         
        def __init__(self):
            print('Creating View object...')
            
            self.requestCounter = 0
            
            self.requestStatusList = []
            self.systemStatusList = []
        def ping(self):
            print('Pong')
            
        def updateRequestStatus(self,status):
            print('Request Status Update: ')
            print(status)
            self.requestStatusList.append(status)
            
            if self.requestStatusList[self.requestCounter].m_stage == 's': 
                print("Current command stage is PTV_STATIC")
             
            if self.requestStatusList[self.requestCounter].m_stage_status == 128: 
                print("\033[1;37;41m CEV FAILED \033[0m")
            
            self.requestCounter = self.requestCounter + 1
            #return self.requestStatusList
        
        def updateSystemStatus(self,status):
            print('System Status Update: ')
            print(status)
            self.systemStatusList.append(status)
            #return self.systemStatusList
    
    injMngrViewObject = CommandInjectMngrView()

#==============================================================================
#               Get Telecommand Parameter Injection server manager
#==============================================================================

    orb = CORBA.ORB_init()
    tcInjServerMngr = orb.string_to_object("corbaname::192.168.56.101:20001/NameService#TC_INJ_002")
    # in case tcInjServerMngr is a generic CORBA.Object, for safety purposes    
    tcInjServerMngr = tcInjServerMngr._narrow(ITC_INJ.TCinjectServerMngr)

#==============================================================================
#                           Activate View object 
#==============================================================================

    # creates omniORB.PortableServer.POA object with persistent object policies
#    poa = orb.resolve_initial_references("omniINSPOA")
#    poaId = "MyObjectId"
#    poa.activate_object_with_id(poaId,injMngrViewObject)

    poa = orb.resolve_initial_references("RootPOA")
    poa.activate_object(injMngrViewObject)
    cmdInjMngrView = poa.servant_to_reference(injMngrViewObject)

    # activate the poa, that incoming requests are served
    poaManager = poa._get_the_POAManager()
    poaManager.activate()

#==============================================================================
#                    Get Command Injection Interface from server 
#==============================================================================    
    
    cmdInjMngr = tcInjServerMngr.getTCinjectMngr(cmdInjMngrView, "Client")

#==============================================================================
#                    Definition of a Command Request Structure
#==============================================================================

	# empty time, command is not time tagged
    _emptyTime = IBASE.Time(0,0,True)
    
    _context = "context"
    _destination = "dest"
    _mapId = 0xFF
    _vcId = 0xFF
    _cmdName = "PPC00201"
    _cmdParameters = [ITC.CommandParam(m_name='DSP00010', m_isEngValue=False, m_unit='', m_radix='H', m_value=IBASE.Variant(m_ulongFormat = 1140863488)),
                      ITC.CommandParam(m_name='DSP00011', m_isEngValue=False, m_unit='', m_radix='H', m_value=IBASE.Variant(m_ulongFormat = 2)),
                      ITC.CommandParam(m_name='PPP00003', m_isEngValue=False, m_unit='', m_radix='H', m_value=IBASE.Variant(m_ulongFormat = 0)),
                      ITC.CommandParam(m_name='PPP00003', m_isEngValue=False, m_unit='', m_radix='H', m_value=IBASE.Variant(m_ulongFormat = 1))]
    _paramSets = []
    _info = ITC_INJ.ReleaseInfo(_emptyTime,_emptyTime,_emptyTime,_emptyTime,ITC.CHECK_ENABLED,ITC.CHECK_ENABLED,False,0x80)
    _ilockType = ITC.IL_NONE
    _ilockStageType = ITC_INJ.IL_UV_GS_ACCEPT
    _additionalInfo = "addInfo"
    _tcRequestID =  0
    
    cmdRequest = ITC_INJ.CommandRequest(_context,_destination,_mapId,_vcId,_cmdName,_cmdParameters,_paramSets,_info,_ilockType,_ilockStageType,_additionalInfo,_tcRequestID)

#==============================================================================
#                               Inject Command
#==============================================================================
    
    print("Injecting command '" + _cmdName + "'...")
    injRequestID = cmdInjMngr.injectCmd(cmdRequest)
    
    # default is BD, AD also possible (Command Frame Type)
    print("Command frame type is: " + str(cmdInjMngr.getTransferMode()))
    
    #orb.run()

#==============================================================================
   
except Exception as e:
    print('\033[1;37;41m Exited with exception:', e, '\033[0m')
    # inform Command Inject Manager that Command Inject Manager View has finished with it
    # close connection, no further callbacks 
    cmdInjMngr.deregister()
    sys.exit(1)
    
else:
    print('\033[1;37;42m Exited without exception \033[0m')
    cmdInjMngr.deregister()
    sys.exit(0)
    