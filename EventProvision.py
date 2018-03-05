#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Access to Event Data 

"""

import sys
import CORBA, IEV, IEV_PRO, IEV_PRO__POA, ICLOCK, IBASE, IBASE_IF__POA
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
            
    class EventMngrView(View,IEV_PRO__POA.EventMngrView):
        def __init__(self):
            print('Creating View object...')

            self.eventCounter = 0           
            self.eventsList = []            
            
        def notifyEvents(self,data):
            
            self.eventsList.append(data)
                       
            print('\033[0;34;48mEvent notification:\033[0m ' + str(data))
            TimeModule.timestamp2SCOSdate(self.eventsList[self.eventCounter].m_evPktTime.m_sec,self.eventsList[self.eventCounter].m_evPktTime.m_micro)
            TimeModule.timestamp2date(self.eventsList[self.eventCounter].m_evPktTime.m_sec,self.eventsList[self.eventCounter].m_evPktTime.m_micro)
            print('\n')
            
            self.eventCounter = self.eventCounter + 1
            
    eventMngrViewObject = EventMngrView()

#==============================================================================
#                       Get Event Server Manager reference 
#==============================================================================
   
    orb = CORBA.ORB_init()
    evServerMngr = orb.string_to_object("corbaname::192.168.56.101:20001/NameService#EV_PRO_001")                                
    # in case evServerMngr is a generic CORBA.Object, for safety purposes    
    evServerMngr = evServerMngr._narrow(IEV_PRO.EVserverMngr)

#==============================================================================
#                             Activate View object 
#==============================================================================
    
    # creates omniORB.PortableServer.POA object with persistent object policies
    poa = orb.resolve_initial_references("omniINSPOA")
    poaId = "MyEventViewObjectId"
    poa.activate_object_with_id(poaId,eventMngrViewObject)
    evMngrView = poa.servant_to_reference(eventMngrViewObject)
    
    # activate the poa, that incoming requests are served
    poaManager = poa._get_the_POAManager()
    poaManager.activate()

#==============================================================================    
#                   Get and initialize Event Timing Server 
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
    evServer = evServerMngr.getEVserver(serverType)

    if serverType == 0:
        
        # no access from other clients, then state modifying is possible
        evServer.lock(evMngrView)
        
        # get Event History Time Server Manager
        timeMngr = evServer.m_timeMngr
        
        # retrieval backward mode, real time mode, history stop mode and retrieval forward mode possible
        timeMngr.setMode(ICLOCK.HISTORY_BACKWARD)
        print('Time mode is: ' + timeMngr.getMode())
    
        #scosDate = "2018.054.16.48.33.999000"
        scosDate = "2017.326.16.11.40.999000"

        # set specific time in Event History   
        # sample time: release time 
        timeMngr.setSampleTime(IBASE.Time(TimeModule.scosDate2timestamp(scosDate)[0],TimeModule.scosDate2timestamp(scosDate)[1],False))
        TimeModule.timestamp2SCOSdate(timeMngr.getSampleTime().m_sec,timeMngr.getSampleTime().m_micro)
        
        # explicit stepping (forward/backward) in retrieval mode
        #timeMngr.step()
        #print('State after manipulating the time context: ' + str(timeMngr.step()))

    if serverType == 1:
        # get Event History Time Server Manager
        timeMngr = evServer.m_timeMngr
        
#==============================================================================              
#                     Definition of an Event Transmission Filter 
#==============================================================================
        
    _transmitData = True
    _transmitPacketHeader = True
    _transmitPacketHeaderRawData = True
    _transmitPacketBodyRawData = True
    
    evTransmissionFilter = IEV.TransmissionFilter(_transmitData,_transmitPacketHeader,_transmitPacketHeaderRawData,_transmitPacketBodyRawData)

#============================================================================== 
#                        Register Event View at the Event Manager
#==============================================================================
    
    # server returns Interface EventMngr, for Event history data access
    evHistoryMngr = evServer.m_eventMngr
   
    viewKey = evHistoryMngr.registerEventView(evMngrView,evTransmissionFilter)

    if viewKey == 0:
        print("\033[1;31;48mRegistration not successful: Invalid view key... \033[0m")
        sys.exit(1)
        
    else:
         print("\033[1;32;48mRegistration successful: View key = " + str(viewKey) + "\033[0m")

#==============================================================================
#                           Definition of an Event Filter 
#==============================================================================
    
    #_id = "ECH_SERVER::" or "CMDHmplx::" or "EVLlog::" or...
    _id = ""
    _message = ""
    _application = ""
    _workstation = ""
    _scope = IEV.SYSTEM | IEV.SOFTWARE| IEV.MIB | IEV.LOG
    _severity = IEV.WARNING | IEV.ERROR | IEV.FATAL | IEV.INFORMATION 
    _dataStreamIDs = timeMngr.getDataStreams()
    _spacecraft = ""

    # only events with a configurable prefix will be processed (_id variable)        
    eventFilter = IEV.EventFilter(_id,_message,_application,_workstation,_scope,_severity,_dataStreamIDs,_spacecraft)

#============================================================================== 
#                        Register Event at the Event Manager
#==============================================================================
 
    registeredEvent = evHistoryMngr.registerEvents(viewKey,eventFilter) 
    
    if registeredEvent == 1:
        print("\033[1;32;48mEvent registration successful\033[0m \n")
    else:
        print("\033[1;31;48mEvent registration not successful\033[0m")  
        
#==============================================================================         
#                           Get retrieval data (private server)
#==============================================================================
    
    # get every packet, check sample Time!
    if serverType == 0:
        while timeMngr.step():
            fullData = evHistoryMngr.getFullData(viewKey)
            print("Get Full Data: " + str(fullData))
            TimeModule.timestamp2SCOSdate(timeMngr.getSampleTime().m_sec,timeMngr.getSampleTime().m_micro)
            print("Sample time is: " + str(timeMngr.getSampleTime()) + "\n")

    if serverType == 1:
        orb.run()

#==============================================================================
    
except Exception as e:
    print('\033[1;37;41m Exited with exception:', e, '\033[0m')
    if serverType == 0:
        evServer.unlock()
    # no more callbacks (even if unregisterEventView(viewKey) is not set)    
    evHistoryMngr.unregisterEvents(viewKey)
    # unregistration of a notification information view (Live-Mode)
    evHistoryMngr.unregisterEventView(viewKey)
    sys.exit(1)
    
else:
    print('\033[1;37;42m Exited without exception \033[0m')
    if serverType == 0:
        evServer.unlock()
    evHistoryMngr.unregisterEvents(viewKey)
    evHistoryMngr.unregisterEventView(viewKey)
    sys.exit(0) 
