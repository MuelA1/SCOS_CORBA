#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Access to TM Packet Data History (all packets filtered by DS and APID)

"""

import sys
import CORBA, ITMP, ITMP_PRO, ITMP_PRO__POA, ICLOCK, IBASE, IBASE_IF__POA

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
       
    class TMpacketMngrView(View,ITMP_PRO__POA.TMpacketMngrView):
        def __init__(self):
            print('Creating View object...')
        def notifyTMpackets(self,data):
            print('TM packet values: ')
            print(data)

    mngrViewObject = TMpacketMngrView()

#==============================================================================
#                        Get TMP Server Manager reference
#==============================================================================
    
    orb = CORBA.ORB_init()
    tmpServerMngr = orb.string_to_object("corbaname::192.168.56.101:20001/NameService#TMP_PRO_001")                                 
    # in case tmpServerMngr is a generic CORBA.Object, for safety purposes    
    tmpServerMngr = tmpServerMngr._narrow(ITMP_PRO.TMPserverMngr)

#==============================================================================
#                               Activate View object 
#==============================================================================

    # creates omniORB.PortableServer.POA object with persistent object policies
    poa = orb.resolve_initial_references("omniINSPOA")
    poaId = "MyTMPViewObjectId"
    poa.activate_object_with_id(poaId,mngrViewObject)
    tmpMngrView = poa.servant_to_reference(mngrViewObject)
    
    # activate the poa, that incoming requests are served
    poaManager = poa._get_the_POAManager()
    poaManager.activate()

#==============================================================================
#                       Get and initialize TMP Timing Server 
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
    tmpServer = tmpServerMngr.getTMPserver(serverType)

    if serverType == 0:
       
        # no access from other clients, then state modifying is possible
        tmpServer.lock(tmpMngrView)
        
        # get TM Packet History Time Server Manager
        timeMngr = tmpServer.m_timeMngr
        
        # retrieval backward mode, real time mode, history stop mode and retrieval forward mode possible
        timeMngr.setMode(ICLOCK.HISTORY_FORWARD)
        print('Time mode is: ' + timeMngr.getMode())
        
        # clock of the server will be set to the largest packet time <= sampleTime
        """ 23.11.2017 (327 Tage) 16:00 1511452800 (UTC 0) --> 1511367738: 22.11.2017 16:22:18 (UTC0)"""
    
        """ 1511367738: 22.11.2017 16:22:18 (UTC0) """
        """ 1511367708: 22.11.2017 16:21:48 (UTC0) """    
        timeMngr.setSampleTime(IBASE.Time(1511367708,0,False))
        print('Sample time is: ' + str(timeMngr.getSampleTime()))
        
        # step to next history entry (forward/backward) in retrieval mode
        #timeMngr.step()
        #print('State after manipulating the time context: ' + str(timeMngr.step()))
        
        print('Packet Mode: ' + str(timeMngr.isPacketMode()))

    if serverType == 1:
        # get TM Packet History Time Server Manager
        timeMngr = tmpServer.m_timeMngr
        
#==============================================================================
#                         Definition of a TM Packet Filter  
#============================================================================== 

    # only those TM Packets, which match the filter, are sent to the client     
    _streamIds = timeMngr.getDataStreams()
    _apIds = [53]
    
    tmPacketFilter = ITMP.TMpacketFilter(_streamIds,_apIds)
    
#==============================================================================
#                        Definition of a Transmission Filter 
#==============================================================================

    _transmitPacketHeaderRawData = True
    _transmitPacketBodyRawData = True
    _transmitParameters = False
    
    tmTransmissionFilter = ITMP.TransmissionFilter(_transmitPacketHeaderRawData,_transmitPacketBodyRawData,_transmitParameters)

#==============================================================================
#                  Register client and filters at the TM Packet manager  
#==============================================================================

    # server returns Interface TMpacketMngr, for TM Packet history data access
    tmpHistoryMngr = tmpServer.m_packetMngr

    viewKey = tmpHistoryMngr.registerTMpackets(tmpMngrView,tmPacketFilter,tmTransmissionFilter)

    if viewKey == 0:
        print("\033[1;31;48mRegistration not successful: Invalid view key... \033[0m")
        sys.exit(1)
        
    else:
         print("\033[1;32;48mRegistration successful: View key = " + str(viewKey) + "\033[0m")

    # Error: Exited with exception: CORBA.MARSHAL(omniORB.MARSHAL_PassEndOfMessage, CORBA.COMPLETED_NO) 
    # CORBA.MARSHAL: Mismatch between the IDL definition seen by client and server?
    # Requested stream in TMP Server 2 Log, compare with history
    
#==============================================================================         
#                        Get retrieval data (private server)
#==============================================================================

    if serverType == 0:
        fullData = tmpHistoryMngr.getFullData(viewKey)
        print("Get Full Data: " + str(fullData))
        
        nextData = tmpHistoryMngr.getNextData(viewKey)
        print("Get Next Data: " + str(nextData))

    if serverType == 1:
        orb.run()

#==============================================================================

except Exception as e:
    print('\033[1;37;41m Exited with exception:', e, '\033[0m')    
    if serverType == 0:
        tmpServer.unlock()
    tmpHistoryMngr.unregisterTMpackets(viewKey)
    sys.exit(1)
    
else:
    print('\033[1;37;42m Exited without exception \033[0m')
    if serverType == 0:
        tmpServer.unlock()
    tmpHistoryMngr.unregisterTMpackets(viewKey)
    sys.exit(0) 
