#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Inject event messages into the SCOS-2000 system

"""

import sys
import CORBA, IEV, IEV_INJ
   
#==============================================================================    
#                    Get Event Injection Manager from server 
#==============================================================================

try:    
    orb = CORBA.ORB_init()
    evInj = orb.string_to_object("corbaname::192.168.56.101:20001/NameService#EV_INJ_001")                                
    # in case evInj is a generic CORBA.Object, for safety purposes
    evInj = evInj._narrow(IEV_INJ.EventInjectMngr)

#==============================================================================
#                       Definition of Event injection data 
#============================================================================== 
    
    #_id = "ECH_SERVER::" or "CMDHmplx::" or "EVLlog::" (Application + ::)
    _id = 'ECH_SERVER::'
    _message = ''
    _application = ''
    _workstation = ''
    _scope = IEV.LOG 
    _severity = IEV.INFORMATION
    _dataStreamID = evInj.getDefaultDataStream()
    _spacecraft = evInj.getDefaultSpacecraftID()

    # only events with a configurable prefix will be processed (_id variable)        
    event = IEV.Event(_id,_message,_application,_workstation,_scope,_severity,_dataStreamID,_spacecraft)
 
#==============================================================================    
#                                Inject Event 
#==============================================================================
    
    print("Injecting Event '" + _id + "'...")
    evInj.injectEvent(event)

#==============================================================================

except Exception as e:
    print('\033[1;37;41m Exited with exception:', e, '\033[0m')
    sys.exit(1)
    
else:
    print('\033[1;37;42m Exited without exception \033[0m')
    sys.exit(0)
