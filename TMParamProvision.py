#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Access to telemetry parameters

"""

import sys
import CORBA, ITM_PRO, ITM_PRO__POA, IMIB, ICLOCK, IBASE_IF__POA, IBASE

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

    class ParameterView(View,ITM_PRO__POA.ParameterView):
        def __init__(self):
            print('Creating View object...')
        def notifyParameter(self,key,value):
            print("\nView key is: " + str(key))
            print('Parameter Values: ')
            print(value)
    
    paramViewObject = ParameterView()

#==============================================================================
#                         Get TM Server Manager reference 
#==============================================================================
    
    orb = CORBA.ORB_init()
    tmServerMngr = orb.string_to_object("corbaname::192.168.56.101:20001/NameService#TM_PRO_001")                                   
    # in case tmServerMngr is a generic CORBA.Object, for safety purposes    
    tmServerMngr = tmServerMngr._narrow(ITM_PRO.TMserverMngr)

#==============================================================================
#                              Activate View object 
#==============================================================================

    # creates omniORB.PortableServer.POA object with persistent object policies
    poa = orb.resolve_initial_references("omniINSPOA")
    poaId = "MyTMParamObjectId"
    poa.activate_object_with_id(poaId,paramViewObject)
    paramView = poa.servant_to_reference(paramViewObject)
    
    # activate the poa, that incoming requests are served
    poaManager = poa._get_the_POAManager()
    poaManager.activate()

#==============================================================================
#                        Get and initialize TM Timing Server 
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
    tmServer = tmServerMngr.getTMserver(serverType)
    
    if serverType == 0:
    
        # no access from other clients, then state modifying is possible
        tmServer.lock(paramView)
        
        # get TM Parameter Time Server Manager
        timeMngr = tmServer.m_timeMngr
        
        # retrieval backward mode (real time mode, history stop mode and retrieval forward mode also possible)
        timeMngr.setMode(ICLOCK.HISTORY_BACKWARD)
        print('Time mode is: ' + timeMngr.getMode())
        
        # clock of the server will be set to the largest packet time <= sampleTime
        """ 1511367738: 22.11.2017 16:22:18 (UTC0) """
        timeMngr.setSampleTime(IBASE.Time(1511367738,0,False))
        print('Sample time is: ' + str(timeMngr.getSampleTime()))
        
        #timeMngr.step()
        #print('State after manipulating the time context: ' + str(timeMngr.step()) + "\n")

#==============================================================================
#                    get single TM Parameter Data Interface 
#==============================================================================
        
    # get single TM Parameter Data Provision Manager
    paramMngr = tmServer.m_parameterMngr
    
    paramIF = paramMngr.getParameter('PBTSTC00',paramView)

#==============================================================================
#                             Register Parameter 
#==============================================================================
    
    viewKey = paramIF.registerParam(paramView,True,IMIB.PARAM_RAW_VALUE,False)

    if viewKey == 0:
        print("\033[1;31;48mRegistration not successful: Invalid view key... \033[0m")
        sys.exit(1)
        
    else:
         print("\033[1;32;48mRegistration successful: View key = " + str(viewKey) + "\033[0m")

#==============================================================================         
#                          Get retrieval data (private server)
#==============================================================================

    if serverType == 0:
        allValues = paramIF.getFullData(viewKey)
        print(allValues)
        print(paramIF.getOOLstate())
        print(paramIF.getActualLowLimit())
        print(paramIF.getActualHighLimit())
            
    if serverType == 1:
        orb.run()
        
#==============================================================================
    
except Exception as e:
    print('\033[1;37;41m Exited with exception:', e, '\033[0m')
    if serverType == 0:
        tmServer.unlock()
    paramIF.unregisterView(viewKey)
    sys.exit(1)
    
else:
    print('\033[1;37;42m Exited without exception \033[0m')
    if serverType == 0:
        tmServer.unlock()
    paramIF.unregisterView(viewKey)
    sys.exit(0)  
    