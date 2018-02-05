#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Access to static data for commands (MIB access)
Access to telemetry parameter data 

Sequence data, Alphanumeric Display data, Graphical Display data and Scrolling Display data also possible

"""

import sys
import CORBA, IMIB, IMIB_PRO

orb = CORBA.ORB_init()
# get MIB Manager reference
mibMngr = orb.string_to_object("corbaname::192.168.56.101:20001/NameService#MIB_PRO_001")
                             
if mibMngr is None:
	print("Failed to get mibMngr reference")
	sys.exit(1)

# in case mibMngr is a generic CORBA.Object, for safety purposes    
mibMngr = mibMngr._narrow(IMIB_PRO.MIBmngr)

# --------------------------- TC Data ---------------------------------------

try:
    print("\033[1;34;47m TC Data \n")

    # provides the iterator for Command data
    # access to static command data 
    commandDefIterator = mibMngr.getCommandDefIterator()
    
    # list with names of definition entries
    tcNamesList = commandDefIterator.getNames()
    print(tcNamesList)
    print('\n')
    
    # get definition of one command 
    commandDef = commandDefIterator.getDef("PING")
    print(commandDef)
    print('\n')
    
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
    print('\n')

# -------------------------- TM Data ----------------------------------------

    print("\033[1;32;47m TM Data \n")
    
    # provides the iterator for Telemetry Parameter data
    paramDefIterator = mibMngr.getParamDefIterator()
    
    # list with names of TM definition entries
    tmNamesList = paramDefIterator.getNames()
    print(tmNamesList)
    print('\n')
    
    # get Definition of one TM parameter 
    paramDef = paramDefIterator.getDef("YYTTLE01")
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
    print('\n')

except Exception as e:
    print ('\033[1;37;41m Exited with exception: ', e)
    sys.exit(1)
    
else:
    print ('\033[1;37;42m Exited without exception')
    sys.exit(0)