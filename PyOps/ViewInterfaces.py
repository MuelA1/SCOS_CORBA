#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Client side views to get callbacks from server

CommandInjectMngrView -- describes a view object where callbacks from injection manager are sended
"""

import ITC_INJ__POA
from Command import Command

class CommandInjectMngrView(ITC_INJ__POA.CommandInjectMngrView):
           
    def __init__(self):
        print('\nCreating client view for command injection...\n')
                                                                              
    def ping(self):
        pass
    
    # command status    
    def updateRequestStatus(self,status):
        Command.getUpdateRequestStatus(status)
                            
    # global system status
    def updateSystemStatus(self,status):
        Command.getUpdateSystemStatus(status)
        

     

        
        

