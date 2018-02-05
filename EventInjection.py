#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Inject event messages into the SCOS-2000 system

"""

import sys
import CORBA, IEV, IEV_INJ

orb = CORBA.ORB_init()
# get Event Injection manager
evInj = orb.string_to_object("corbaname::192.168.56.101:20001/NameService#EV_INJ_001")
                             
if evInj is None:
	print("Failed to get evInj reference")
	sys.exit(1)
    
# in case evInj is a generic CORBA.Object, for safety purposes
evInj = evInj._narrow(IEV_INJ.EventInjectMngr)

# -------------------- Definition of Event injection data ------------------

try:  
    _id = "4908"
    _message = "My Test Event"
    _application = "Application"
    _workstation = "External Workstation"
    _scope = IEV.LOG
    _severity = IEV.WARNING  
    _dataStreamID = evInj.getDefaultDataStream()
    _spacecraft = evInj.getDefaultSpacecraftID()

    # only events with a configurable prefix will be processed (_id variable)        
    event = IEV.Event(_id,_message,_application,_workstation,_scope,_severity,_dataStreamID,_spacecraft)
  
# ---------------------------- Inject Event --------------------------------
    
    evInj.injectEvent(event)

except Exception as e:
    print ('\033[1;37;41m Exited with exception: ', e)
    sys.exit(1)
    
else:
    print ('\033[1;37;42m Exited without exception')
    sys.exit(0)
