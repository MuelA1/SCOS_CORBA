#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Server for retrieving all TM packet data of a single TM packet (SPID)

"""

import sys
import CORBA, ITMP_PRO, IBASE

#==============================================================================
#                   Get TMP History Query Server Manager reference
#==============================================================================

try:
    orb = CORBA.ORB_init()
    tmpHistoryQueryMngr = orb.string_to_object("corbaname::192.168.56.101:20001/NameService#TMPQ_PRO_001")                          
    # in case tmpHistoryQueryMngr is a generic CORBA.Object, for safety purposes    
    tmpHistoryQueryMngr = tmpHistoryQueryMngr._narrow(ITMP_PRO.TMPhistoryQueryMngr)   

#==============================================================================
#                               Get single TM packet data
#==============================================================================

    # SCOS-2000 packet ID (SPID)
    # e.g. 34210, 36910
    _filingKey = 36910
    # data stream
    _streamId = 65535         
    # (UNIX timestamp; sec, micro, delta: UTC + 4) 
    """ 1511367738: 22.11.2017 16:22:18 (UTC0) """
    """ 1511367641: 22.11.2017 16:20:41 (UTC0) """
    # SCOS-2000 packet creation time (reception time)
    _createTime = IBASE.Time(1511367621,0,False)
    # onboard time (generation time, filing time)
    _filingTime = IBASE.Time(1511367641,0,False)

    # get packet from TM Packet History     
    tmPacketNotifyData = tmpHistoryQueryMngr.getHistoryData(_filingKey,_streamId,_createTime,_filingTime) 
    print(tmPacketNotifyData)

#==============================================================================
     
except Exception as e:
    print('\033[1;37;41m Exited with exception:', e, '\033[0m')
    sys.exit(1)
    
else:
    print('\033[1;37;42m Exited without exception \033[0m')
    sys.exit(0)    