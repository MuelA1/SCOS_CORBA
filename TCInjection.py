#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Command Injection Services
Access to SCOS-2000 commanding system

"""

import sys
import CORBA, IBASE, ITC, ITC_INJ
  
orb = CORBA.ORB_init()
# get Telecommand parameter injection server manager
tcInjServerMngr = orb.string_to_object("corbaname::192.168.56.101:20001/NameService#TC_INJ_002")
                       
if tcInjServerMngr is None:
    print("Failed to get tcInjServerMngr reference")
    sys.exit(1)

# in case tcInjServerMngr is a generic CORBA.Object, for safety purposes    
tcInjServerMngr = tcInjServerMngr._narrow(ITC_INJ.TCinjectServerMngr)

""" TBD, narrow does not work like this
    narrow(dest) only works for destination in which "ServiceName" is defined, see IDL file """
# cmndInjMngrView = tcInjServerMngr._narrow(ITC_INJ.CommandInjectMngrView)

""" TBD, client side view, destination for future server notifications, registration fails
    Interface provided by external command source
    "Expecting object reference, got <class 'ITC_INJ._objref_CommandInjectMngrView'>" Error during registration """
# cmdInjMngrView = ITC_INJ._objref_CommandInjectMngrView(orb)

# get Command Injection Interface from server
# register Command Injection Manager View Interface here 
cmdInjMngr = tcInjServerMngr.getTCinjectMngr(None, "source")

if cmdInjMngr is None:
    print("Failed to get reference to Command Injection Manager")
    sys.exit(1)

# ---------------------- Definition of Command Request Structure ------------

# empty time, command is not time tagged
_emptyTime = IBASE.Time(0,0,True)

_context = "context"
_destination = "dest"
_mapId = 0xFF
_vcId = 0xFF
_cmdName = "PING"
_cmdParameters = ITC.CommandParam("PING",False,"NoUnit",None,IBASE.Variant('I',"IS_LONG"))
_paramSets = None
_info = ITC_INJ.ReleaseInfo(_emptyTime,_emptyTime,_emptyTime,_emptyTime,None,None,False,0x80)
# RuntimeError: Cannot construct objects of this type.
#_ilockType = ITC.InterlockType('N')
_ilockType = None
_ilockStageType = 0
_additionalInfo = "addInfo"
_tcRequestID =  0

cmdRequest = (_context,_destination,_mapId,_vcId,_cmdName,_cmdParameters,_paramSets,_info,_ilockType,_ilockStageType,_additionalInfo,_tcRequestID)

# -------------------------------- Inject Command ---------------------------

injRequestID = cmdInjMngr.injectCmd(cmdRequest)

# inform Command Inject Manager that Command Inject Manager View has finished with it
# close connection    
cmdInjMngr.deregister()

sys.exit(0)
