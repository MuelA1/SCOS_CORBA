#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Client side views to get callbacks from server

CommandInjectMngrView -- describes a view object where callbacks from injection manager are sended
View                  -- Base class of ParameterView and PacketView class, gives information about overflows on server side
ParameterView         -- describes a view object where callbacks from telemetry parameter manager are sended
PacketView            -- describes a view object where callbacks from telemetry packet manager are sended
"""

import ITC_INJ__POA, IBASE_IF__POA, ITM_PRO__POA, ITMP_PRO__POA
from Command import Command
from tmParameter import TMParameter
from tmPacket import TMPacket
#from colorama import Fore, Back, Style
#import time

class CommandInjectMngrView(ITC_INJ__POA.CommandInjectMngrView):
           
    def __init__(self):
        pass
                                                                              
    def ping(self):
        pass
    
    # command status    
    def updateRequestStatus(self, status):
        #print(status)
        #print(Fore.RED + Back.BLUE + Style.BRIGHT + 'Time: {}'.format(time.time()), Style.RESET_ALL)
        Command.getUpdateRequestStatus(status)
                            
    # global system status
    def updateSystemStatus(self, status):
        Command.getUpdateSystemStatus(status)
        
class View(IBASE_IF__POA.View):
    
    def __init__(self):
        pass
    
    def notifyOverflow(self):
        print("notifyOverflow: buffer overflow on the server side") 
           
    def owNotifyOverflow(self):    
        print("owNotifyOverflow: buffer overflow on the server side")

class ParameterView(View, ITM_PRO__POA.ParameterView):
   
    def __init__(self):
        pass
           
    def notifyParameter(self, key, value):
        #print("\nView key is: " + str(key) + "\n")
        #print('Parameter values: ' + str(value))
        TMParameter.getParameterNotification(key, value)

class PacketView(View, ITMP_PRO__POA.TMpacketMngrView):
    
    def __init__(self):
        pass
    
    def notifyTMpackets(self, packet):         
        TMPacket.getPacketNotification(packet) 
         
         