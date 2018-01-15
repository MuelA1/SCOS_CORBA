#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Inject telemetry parameter values into SCOS-2000
Allows TM parameter injection of these categories:
    UDC - Data (User Defined Constants)
    MISCdynamic variable (Miscellaneous subsystem)

"""

import sys
import CORBA, IBASE, ITM, ITM_INJ

orb = CORBA.ORB_init()
# get Telemetry parameter injection manager
tmInjMngr = orb.string_to_object("corbaname::192.168.56.101:20001/NameService#TM_INJ_001")
                             
if tmInjMngr is None:
    print("Failed to get tmInjMngr reference")
    sys.exit(1)    

# in case tmInjMngr is a generic CORBA.Object, for safety purposes 
tmInjMngr = tmInjMngr._narrow(ITM_INJ.ParamInjectMngr)
    
# ------------------ Definition of a single parameter ---------------------

# parameter name (string) 
# example: PSS - Battery Subsubsystem _name = "PBTSCC03"
# YM: System Manager, PSS Subsystem Mode 
_name = "YMTMD107"

# switch wether the injected value is raw or engineering (boolean)
# only raw values are currently supported
_isEngValue = False

# value (IBASE.Variant) (Syntax: IBASE.Variant('S',"Default"))  
_value = IBASE.Variant('S',"Off")

# create parameter structure  
_singleParam = ITM.InjectParam(_name,_isEngValue,_value)

# ---------------------- Inject parameter ---------------------------------

# inject single parameter with defaults
# Error: IBASE.NotFound() - parameter name is not properly configured in the MIB
tmInjMngr.injectParameterWithDefaults(_singleParam,"sourceID")
   
sys.exit(0)   