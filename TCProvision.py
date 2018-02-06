#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Command History Data Provision Services 

"""

import sys
import CORBA, IBASE_IF, ITC, ITC_PRO, ITC_PRO__POA
import omniORB

orb = CORBA.ORB_init()
# get TCserverMngr reference
tcServerMngr = orb.string_to_object("corbaname::192.168.56.101:20001/NameService#TC_PRO_002")
                             
if tcServerMngr is None:
	print("Failed to get tcServerMngr reference")
	sys.exit(1)

# in case tcServerMngr is a generic CORBA.Object, for safety purposes    
tcServerMngr = tcServerMngr._narrow(ITC_PRO.TCserverMngr)

# shared realtime server or private retrieval server, depending on boolean p_shared
# 1 --> shared realtime server (?)    
tcServer = tcServerMngr.getTCserver(1)

# server returns Interface CommandMngr, for command history access
cmdHistory = tcServer.m_commandMngr

# client side view, destination for future server notifications 
poa = orb.resolve_initial_references("RootPOA")
# string = Repository ID, identifies IDL Interface of the object
cmdMngrView = poa.create_reference("IDL:ITC_PRO/CommandMngrView:1.0")

class testView5(ITC_PRO__POA.CommandMngrView):
    def __init__(self):
        print('')
    def notifyCommands(self,data):
        print('Hat geklappt')

# ------------------------ Definition of a Command Filter ------------------
# only those commands, which match the filter, are sent to the client    

try:
    _releaseTimeOrder = False
    _enableVerifyDetails = False     
    _enableParameters = False
    _enableRawData = True
    _name = "PING"
    _sourceName = "source"
    _sourceType = ITC.EXT_SOURCE
    _subsystem = ""
    _sequenceName = ""
#    _verifyDetails = ITC.VerifyDetail('s',0x0002)
    _verifyDetails = []
    
    commandFilter = ITC.CommandFilter(_releaseTimeOrder,_enableVerifyDetails,_enableParameters,_enableRawData,_name,_sourceName,_sourceType,_subsystem,_sequenceName,_verifyDetails)

# ------------------- Definition of a Transmission Filter ------------------

    _transmitData = False
    _transmitPacketHeader = False
    _transmitPacketHeaderRawData = False
    _transmitPacketBodyRawData = False
    
    transmissionFilter = ITC.TransmissionFilter(_transmitData,_transmitPacketHeader,_transmitPacketHeaderRawData,_transmitPacketBodyRawData)

# --------------------- Register at the CommandMngr -------------------------
    
    # register client for command history data 
    viewKey = cmdHistory.registerCommands(cmdMngrView,commandFilter,transmissionFilter)
    
    if viewKey == 0:
        print("\033[1;31;47m Registration not successful: view key = 0")

# ----------------------------- get Data ------------------------------------
 
    data = cmdHistory.getFullData(viewKey)

    test5 = testView5()
    poa.activate_object(test5)
    reff = poa.servant_to_reference(test5)
    cmdHistory.registerCommands(reff,commandFilter,transmissionFilter)
    
except Exception as e:
    print ('\033[1;37;41m Exited with exception: ', e)
    sys.exit(1)
    
else:
    print ('\033[1;37;42m Exited without exception')
    sys.exit(0)                        
