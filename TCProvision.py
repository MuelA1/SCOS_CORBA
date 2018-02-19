#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Command History Data Provision Services 

"""

import sys
import CORBA, ITC, ITC_PRO, ITC_PRO__POA, ICLOCK, IBASE, IBASE_IF__POA

#==============================================================================
#                           Implement client side view
#==============================================================================

try:
    class View(IBASE_IF__POA.View):
        def __init__(self):
            print("Init...")
        def notifyOverflow(self):
            print("notifyOverflow: buffer overflow on the server side")            
        def owNotifyOverflow(self):    
            print("owNotifyOverflow: buffer overflow on the server side")
            
    class CommandMngrView(View,ITC_PRO__POA.CommandMngrView):
        def __init__(self):
            print('Creating View object...')
        def notifyCommands(self,data):
            print('Command Values: ')
            print(data)
    
    mngrViewObject = CommandMngrView()
   
#==============================================================================
#                          Get TC Server Manager reference 
#==============================================================================
    
    orb = CORBA.ORB_init()
    tcServerMngr = orb.string_to_object("corbaname::192.168.56.101:20001/NameService#TC_PRO_002")                            
    # in case tcServerMngr is a generic CORBA.Object, for safety purposes    
    tcServerMngr = tcServerMngr._narrow(ITC_PRO.TCserverMngr)

#==============================================================================
#                               Activate View object 
#==============================================================================
   
    # creates omniORB.PortableServer.POA object with persistent object policies
    poa = orb.resolve_initial_references("omniINSPOA")
    poaId = "MyTCProObjectId"
    poa.activate_object_with_id(poaId,mngrViewObject)
    cmdMngrView = poa.servant_to_reference(mngrViewObject)
    
    # activate the poa, that incoming requests are served
    poaManager = poa._get_the_POAManager()
    poaManager.activate()

#==============================================================================
#                       Get and initialize TC Timing Server 
#==============================================================================

    # get user input
    serverTypeInput = input("Please type 'L' for Live data provision or 'H' for History data provision: ")
    if serverTypeInput in ['L','l']:
        serverType = 1
        print("Live data provision selected... \n")
    elif serverTypeInput in ['H','h']:
        serverType = 0
        print("History data provision selected... \n")
    else:
        print("\033[1;31;48mInvalid input \033[0m")
        sys.exit(1)
        
    # 1 --> shared realtime server, shared between clients 
    # 0 --> private retrieval server, for history data  
    tcServer = tcServerMngr.getTCserver(serverType)
    
    if serverType == 0:
    
        # no access from other clients, then state modifying is possible
        tcServer.lock(cmdMngrView)
        
        # get TC History Time Server Manager
        timeMngr = tcServer.m_timeMngr
        
        # retrieval backward mode (real time mode, history stop mode and retrieval forward mode also possible)
        timeMngr.setMode(ICLOCK.HISTORY_FORWARD)
        print('Time mode is: ' + timeMngr.getMode())
        
        # clock of the server will be set to the largest packet time <= sampleTime
        """ 08.02.2018 (039 Tage) 16:00 1518105600 --> (1518105690,384309,False): 16:01:30 (UTC0) """
        timeMngr.setSampleTime(IBASE.Time(1518105600,0,False))
        print('Sample time is: ' + str(timeMngr.getSampleTime()))
        
        # explicit stepping (forward/backward) in retrieval mode
        #timeMngr.step()
        #print('State after manipulating the time context: ' + str(timeMngr.step()))

#==============================================================================
#                          Definition of a Command Filter  
#==============================================================================       
    
    # only those commands, which match the filter, are sent to the client 
    _releaseTimeOrder = True
    _enableVerifyDetails = False     
    _enableParameters = True
    _enableRawData = False
    _name = "PING"
    _sourceName = "maestria-scos"
    _sourceType = ITC.EXT_SOURCE
    _subsystem = "DEFAULT"
    _sequenceName = ""
#    _verifyDetails = ITC.VerifyDetail('s',0x0002)
    _verifyDetails = []
    
    commandFilter = ITC.CommandFilter(_releaseTimeOrder,_enableVerifyDetails,_enableParameters,_enableRawData,_name,_sourceName,_sourceType,_subsystem,_sequenceName,_verifyDetails)

#==============================================================================
#                           Definition of a Transmission Filter 
#==============================================================================
    
    _transmitData = True
    _transmitPacketHeader = True
    _transmitPacketHeaderRawData = True
    _transmitPacketBodyRawData = True
    
    transmissionFilter = ITC.TransmissionFilter(_transmitData,_transmitPacketHeader,_transmitPacketHeaderRawData,_transmitPacketBodyRawData)

#==============================================================================
#                              Register at the CommandMngr 
#==============================================================================

    # server returns Interface CommandMngr, for command history data access
    cmdHistoryMngr = tcServer.m_commandMngr
       
    # register client for command history data 
    viewKey = cmdHistoryMngr.registerCommands(cmdMngrView,commandFilter,transmissionFilter)
 
    if viewKey == 0:
        print("\033[1;31;48mRegistration not successful: Invalid view key... \033[0m")
        sys.exit(1)
        
    else:
         print("\033[1;32;48mRegistration successful: View key = " + str(viewKey) + "\033[0m")

#==============================================================================         
#                           Get retrieval data (private server)
#==============================================================================

    if serverType == 0:
         
        fullData = cmdHistoryMngr.getFullData(viewKey)
        print("Get Full Data: " + str(fullData))
        
        nextData = cmdHistoryMngr.getNextData(viewKey)
        print("Get Next Data: " + str(nextData))
            
    if serverType == 1:
        orb.run()

#==============================================================================
    
except Exception as e:
    print('\033[1;37;41m Exited with exception:', e, '\033[0m')
    if serverType == 0:
        tcServer.unlock()
    cmdHistoryMngr.unregisterView(viewKey)
    sys.exit(1)
    
else:
    print('\033[1;37;42m Exited without exception \033[0m')
    if serverType == 0:
        tcServer.unlock()
    cmdHistoryMngr.unregisterView(viewKey)
    sys.exit(0)                        
