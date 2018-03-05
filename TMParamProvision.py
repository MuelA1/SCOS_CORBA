#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Access to telemetry parameters

"""

import sys
import CORBA, ITM_PRO, ITM_PRO__POA, IMIB, ICLOCK, IBASE_IF__POA, IBASE
import TimeModule

#==============================================================================
#                           Implement client side view
#==============================================================================

try:     
    class View(IBASE_IF__POA.View):
        def __init__(self):
            pass
        def notifyOverflow(self):
            print("notifyOverflow: buffer overflow on the server side")            
        def owNotifyOverflow(self):    
            print("owNotifyOverflow: buffer overflow on the server side")

    class ParameterView(View,ITM_PRO__POA.ParameterView):
        def __init__(self):
            print('Creating View object...')
            
            self.paramCounter = 0           
            self.paramValuesList = []            
            
        def notifyParameter(self,key,value):
            print("\nView key is: " + str(key) + "\n")
            print('\033[1;34;48mParameter values: \033[0m' + str(value) + "\n")
    
            self.paramValuesList.append(value)
            TimeModule.timestamp2SCOSdate(self.paramValuesList[self.paramCounter].m_sampleTime.m_sec, self.paramValuesList[self.paramCounter].m_sampleTime.m_micro)
            TimeModule.timestamp2date(self.paramValuesList[self.paramCounter].m_sampleTime.m_sec, self.paramValuesList[self.paramCounter].m_sampleTime.m_micro)
            self.paramCounter =  self.paramCounter + 1
            print("Callback method call: " + str(self.paramCounter + 1) + "\n")
            
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
              
        scosDate = "2017.326.16.22.18.945000"
        
        timeMngr.setSampleTime(IBASE.Time(TimeModule.scosDate2timestamp(scosDate)[0],TimeModule.scosDate2timestamp(scosDate)[1],False))
        TimeModule.timestamp2SCOSdate(timeMngr.getSampleTime().m_sec,timeMngr.getSampleTime().m_micro)
      
        # timeMngr.setIntervalMode(IBASE.Time(0,100,False))        
        #timeMngr.step()
        #print('State after manipulating the time context: ' + str(timeMngr.step()) + "\n")

#==============================================================================
#                    get single TM Parameter Data Interface 
#==============================================================================
        
    # get single TM Parameter Data Provision Manager
    paramMngr = tmServer.m_parameterMngr
    
    paramIF = paramMngr.getParameter('PBTPWR00',paramView)

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
        while timeMngr.step():
            allValues = paramIF.getFullData(viewKey)
            print("\033[1;32;48mFull data: \033[0m" + str(allValues) + "\n")
            print("OOL state: " + str(paramIF.getOOLstate()) + "\n")
            print("Low Limit: " + str(paramIF.getActualLowLimit()) + "\n")
            print("High Limit: " + str(paramIF.getActualHighLimit()) + "\n")
       
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
      