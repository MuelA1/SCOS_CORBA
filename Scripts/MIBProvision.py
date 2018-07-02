#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Access to static data for commands (MIB access)
Access to telemetry parameter data 

Sequence data, Alphanumeric Display data, Graphical Display data and Scrolling Display data also possible

"""

import sys
import CORBA, IMIB, IMIB_PRO
   
#==============================================================================
#                       Get MIB Manager reference from server 
#============================================================================== 

try:   
    orb = CORBA.ORB_init()
    mibMngr = orb.string_to_object("corbaname::192.168.56.101:20001/NameService#MIB_PRO_001")                             
    # in case mibMngr is a generic CORBA.Object, for safety purposes    
    mibMngr = mibMngr._narrow(IMIB_PRO.MIBmngr)

#==============================================================================
#                                    Get TC Data 
#==============================================================================
    
    print("\033[1;34;48mTC Data \n")

    # provides the iterator for Command data
    # access to static command data 
    commandDefIterator = mibMngr.getCommandDefIterator()
    
    # list with names of definition entries
    tcNamesList = commandDefIterator.getNames()
    #print(tcNamesList)
    #print('\n')
    
    # get definition of one command 
    commandDef = commandDefIterator.getDefsAsTable(tcNamesList,IMIB.PARAM_DESCRIPTION)
    for defs in commandDef[0].m_values:
       print(defs)
       #print('\n')
    
    # get total number of entries
    commandCount = commandDefIterator.getCount()
    print(commandCount)
    print('\n')
    
    # get last changes time
    lastTcChangesTime = commandDefIterator.getLastChanges()
    print(lastTcChangesTime)
    print('\n')
    
    # get TC definition entries as table
    # attributes: PARAM_NAME, PARAM_DESCRIPTION, PARAM_VALUE_FLAGS, PARAM_RAW_VALUE_UNIT,
    # PARAM_ENG_VALUE_UNIT, PARAM_SYN_VALUE_UNIT, PARAM_SOURCE_VALUE_UNIT, PARAM_DEFAULT_VALUE_UNIT
    tcDefinitionTable = commandDefIterator.getDefsAsTable(['PING'],IMIB.PARAM_DESCRIPTION)
    print(tcDefinitionTable)
    print('\n \033[0m')

#==============================================================================
#                                 Get TM Data 
#==============================================================================
    
    print("\033[1;32;48mTM Data \n")
    
    # provides the iterator for Telemetry Parameter data
    paramDefIterator = mibMngr.getParamDefIterator()
    
    # list with names of TM definition entries
    tmNamesList = paramDefIterator.getNames()
    print(tmNamesList)
    print('\n')
    
    # get Definition of one TM parameter 
    #paramDef = paramDefIterator.getDef("YYTTLE01")
    paramDef = paramDefIterator.getDef("PBTSTC00")
    print(paramDef)
    print('\n')
    
    # get total number of entries
    parameterCount = paramDefIterator.getCount()
    print(parameterCount)
    print('\n')
    
    # get last changes time
    lastTmChangesTime = paramDefIterator.getLastChanges()
    print(lastTmChangesTime)
    print('\n')
    
    # get TM definition entries as table
    # attributes: PARAM_NAME, PARAM_DESCRIPTION, PARAM_VALUE_FLAGS, PARAM_RAW_VALUE_UNIT,
    # PARAM_ENG_VALUE_UNIT, PARAM_SYN_VALUE_UNIT, PARAM_SOURCE_VALUE_UNIT, PARAM_DEFAULT_VALUE_UNIT
    paramDefinitionTable = paramDefIterator.getDefsAsTable(['YYTTLE01'],IMIB.PARAM_VALUE_FLAGS)
    print(paramDefinitionTable)
    print('\n \033[0m')

#==============================================================================

except Exception as e:
    print('\033[1;37;41m Exited with exception:', e, '\033[0m')
    sys.exit(1)
    
else:
    print('\033[1;37;42m Exited without exception \033[0m')
    sys.exit(0)
