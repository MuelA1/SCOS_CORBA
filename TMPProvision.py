#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Access to TM Packet Data History (all packets filtered by DS and APID)

"""

import sys
import CORBA, ITMP, ITMP_PRO, ITMP_PRO__POA, ICLOCK, IBASE, IBASE_IF__POA
import TimeModule

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
            
            self.packetCounter = 0           
            self.packetsList = []             
            
        def notifyTMpackets(self,data):
            
            self.packetsList.append(data)
            print('\033[1;34;48mTM packet values: \033[0m ' + str(data))
            TimeModule.timestamp2SCOSdate(self.packetsList[self.packetCounter].m_pktAttributes.m_filingTime.m_sec, self.packetsList[self.packetCounter].m_pktAttributes.m_filingTime.m_micro)
            TimeModule.timestamp2date(self.packetsList[self.packetCounter].m_pktAttributes.m_filingTime.m_sec, self.packetsList[self.packetCounter].m_pktAttributes.m_filingTime.m_micro)
            print('\n')
            
            self.packetCounter = self.packetCounter + 1

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
        timeMngr.setMode(ICLOCK.HISTORY_BACKWARD)
        print('Time mode is: ' + timeMngr.getMode())
               
        scosDate = "2017.326.16.22.20.945000"
        
        timeMngr.setSampleTime(IBASE.Time(TimeModule.scosDate2timestamp(scosDate)[0],TimeModule.scosDate2timestamp(scosDate)[1],False))
        TimeModule.timestamp2SCOSdate(timeMngr.getSampleTime().m_sec,timeMngr.getSampleTime().m_micro)
        
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
    _apIds = []
    _filingKeys = []
    
    tmPacketFilter = ITMP.TMpacketFilter(_streamIds,_apIds,_filingKeys)
    
#==============================================================================
#                        Definition of a Transmission Filter 
#==============================================================================

    _transmitPacketHeaderRawData = False
    _transmitPacketBodyRawData = False
    _transmitParameters = True
    
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
    
#==============================================================================         
#                        Get retrieval data (private server)
#==============================================================================

    # get every packet
    if serverType == 0:      
        
        historyDataCounter = 0
        historyDataList = []
        
        while timeMngr.step():
            fullData = tmpHistoryMngr.getFullData(viewKey)
            
            historyDataList.append(fullData)
            print("\033[1;32;48mGet Full Data: \033[0m" + str(fullData))
            TimeModule.timestamp2SCOSdate(historyDataList[historyDataCounter][0].m_pktAttributes.m_filingTime.m_sec, historyDataList[historyDataCounter][0].m_pktAttributes.m_filingTime.m_micro)
            print('\n')
            
            historyDataCounter = historyDataCounter + 1
            
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
