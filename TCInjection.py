#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Command Injection Services
Access to SCOS-2000 commanding system

"""

import sys
import CORBA, IBASE, ITC, ITC_INJ
import PortableServer
 
orb = CORBA.ORB_init()
# get Telecommand Parameter Injection server manager
tcInjServerMngr = orb.string_to_object("corbaname::192.168.56.101:20001/NameService#TC_INJ_002")
                       
if tcInjServerMngr is None:
    print("Failed to get tcInjServerMngr reference")
    sys.exit(1)

# in case tcInjServerMngr is a generic CORBA.Object, for safety purposes    
tcInjServerMngr = tcInjServerMngr._narrow(ITC_INJ.TCinjectServerMngr)

# TBD: implement client side view, destination for future server notifications
# Interface provided by external command source
# Error: CORBA.OBJECT_NOT_EXIST(omniORB.OBJECT_NOT_EXIST_NoMatch, CORBA.COMPLETED_NO)
# Object does not exist on server

# creates omniORB.PortableServer.POA object
poa = orb.resolve_initial_references("RootPOA")
# creates reference type <ITC_INJ._objref_CommandInjectMngrView object>
# string = Repository ID, identifies IDL Interface of the object
cmdInjMngrView = poa.create_reference("IDL:ITC_INJ/CommandInjectMngrView:1.0")
# object still has to be created

# get Command Injection Interface from server
# register Command Injection Manager View Interface here 
cmdInjMngr = tcInjServerMngr.getTCinjectMngr(cmdInjMngrView, "SourceName")

if cmdInjMngr is None:
    print("Failed to get reference to Command Injection Manager")
    sys.exit(1)

# ---------------------- Definition of Command Request Structure ------------

try:
	# empty time, command is not time tagged
    _emptyTime = IBASE.Time(0,0,True)
    
    _context = "context"
    _destination = "dest"
    _mapId = 0xFF
    _vcId = 0xFF
    _cmdName = "PING"
    _cmdParameters = []
    	#_cmdParameters = ITC.CommandParam("PING",False,"NoUnit",None,IBASE.Variant('I',"IS_LONG"))
    _paramSets = []
    _info = ITC_INJ.ReleaseInfo(_emptyTime,_emptyTime,_emptyTime,_emptyTime,ITC.CHECK_ENABLED,ITC.CHECK_ENABLED,False,0x80)
    _ilockType = ITC.IL_NONE
    _ilockStageType = ITC_INJ.IL_UV_GS_ACCEPT
    _additionalInfo = "addInfo"
    _tcRequestID =  0
    
    cmdRequest = ITC_INJ.CommandRequest(_context,_destination,_mapId,_vcId,_cmdName,_cmdParameters,_paramSets,_info,_ilockType,_ilockStageType,_additionalInfo,_tcRequestID)

# --------------------------- Inject Command --------------------------------

    injRequestID = cmdInjMngr.injectCmd(cmdRequest)
 
# ------------------------ get Command Callback -----------------------------
 
    _request_id = injRequestID
    _multiplexer_id = 0
    _stage = ITC.PTV_STATIC
    _stage_status = ITC.PASSED
    _completed_flag = True
    _updateTime = _emptyTime
    _tcRequestID = 0
    
    status = ITC_INJ.NotificationInfo(_request_id,_multiplexer_id,_stage,_stage_status,_completed_flag,_updateTime,_tcRequestID)
    
    cmdCallback = cmdInjMngrView.updateRequestStatus(status)    
    
except Exception as e:
    print ('\033[1;37;41m Exited with exception: ', e)
    # inform Command Inject Manager that Command Inject Manager View has finished with it
    # close connection 
    cmdInjMngr.deregister()
    sys.exit(1)
    
else:
    print ('\033[1;37;42m Exited without exception')
    cmdInjMngr.deregister()
    sys.exit(0)
    
