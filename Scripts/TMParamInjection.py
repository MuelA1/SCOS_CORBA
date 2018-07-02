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

#==============================================================================
#                   Get Telemetry Parameter Injection Manager reference 
#==============================================================================

try:
    orb = CORBA.ORB_init()
    tmInjMngr = orb.string_to_object("corbaname::192.168.56.101:20001/NameService#TM_INJ_001")                            
    # in case tmInjMngr is a generic CORBA.Object, for safety purposes 
    tmInjMngr = tmInjMngr._narrow(ITM_INJ.ParamInjectMngr)

#==============================================================================    
#                          Definition of a single parameter 
#==============================================================================
    
    # parameter name (string) 
    # example: PSS - Battery Subsubsystem; _name = "PBTSCC03" or "YYTTLE01", "PBTSTC00", "XNTCAG00"
    # YM: System Manager, PSS Subsystem Mode 
    _name = "PBTPWR00"
    
    # switch wether the injected value is raw or engineering (boolean)
    # only raw values are currently supported
    _isEngValue = False
    
    # value (IBASE.Variant) (Syntax: IBASE.Variant('S',"Default")), IBASE.Variant('F',1.0)  
    _value = IBASE.Variant('D',-0.37105342745780945) 

    # create parameter structure  
    _singleParam = ITM.InjectParam(_name,_isEngValue,_value)

#==============================================================================    
#                                 Inject parameter 
#==============================================================================
    
    # inject single parameter with defaults
    # Error: IBASE.NotFound() - parameter name is not properly configured in the MIB
    print("Injecting TM parameter '" + _name + "'...")
    tmInjMngr.injectParameterWithDefaults(_singleParam,"MeinInjektor")

#==============================================================================
   
except Exception as e:
    print('\033[1;37;41m Exited with exception:', e, '\033[0m')
    sys.exit(1)
    
else:
    print('\033[1;37;42m Exited without exception \033[0m')
    sys.exit(0) 
