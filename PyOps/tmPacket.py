#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Class for telemetry packet settings

TMPacket -- describes packet filters and packet callback progression
"""

import ITMP
import os
from subprocess import Popen
from blessings import Terminal

class TMPacket():
    
    __packetView = None
    __notifyPacketListStatic = []
    __PIPE_PATH_Packet = None
    __packetTerm = Terminal()
    __tmPacketMngr = None
    
    def __init__(self, apIds=None, filingKeys=None, header=False, body=False, param=True):
        
        self.__streamIds = None
        self.__apIds = apIds if apIds is not None else []
        self.__filingKeys = filingKeys if filingKeys is not None else []
        self.__header = header
        self.__body = body
        self.__param = param      
        self.__viewKey = None
        self.__tmPacketFilter = None
        self.__tmTransmissionFilter = None
            
    def setStreamIds(self, timeMngr):
        self.__streamIds = timeMngr.getDataStreams()
        
    def registerTMpackets(self):
         
        self.__tmPacketFilter = ITMP.TMpacketFilter(self.__streamIds, self.__apIds, self.__filingKeys)
        self.__tmTransmissionFilter = ITMP.TransmissionFilter(self.__header, self.__body, self.__param)
        
        self.__viewKey = self.__tmPacketMngr.registerTMpackets(self.__packetView, self.__tmPacketFilter, self.__tmTransmissionFilter)
    
    def unregisterTmPacket(self):       
        self.__tmPacketMngr.unregisterTMpackets(self.__viewKey)
    
    @classmethod       
    def setTmPacketMngr(cls, packetMngr):
        cls.__tmPacketMngr = packetMngr
    
    @classmethod    
    def setPacketView(cls, packetView):
        cls.__packetView = packetView

    @classmethod        
    def getPacketNotification(cls, packet):
        cls.__notifyPacketListStatic.append(packet)      

        with open(cls.__PIPE_PATH_Packet, 'w') as packetTerminal:
            packetTerminal.write(packet) 
        
    @classmethod
    def createPacketNotificationTerminal(cls):
        
        cls.__PIPE_PATH_Packet = '/tmp/packetNotifyPipe'  
        
        if os.path.exists(cls.__PIPE_PATH_Packet):
            os.remove(cls.__PIPE_PATH_Packet)
        
        # named pipe                      
        os.mkfifo(cls.__PIPE_PATH_Packet)
            
        # new terminal subprocess ('xterm' also possible)   
        Popen(['gnome-terminal', '-e', 'tail -f %s' % cls.__PIPE_PATH_Packet])   
               
        with open(cls.__PIPE_PATH_Packet, 'w') as packetTerminal:
            packetTerminal.write('\n' +  cls.__packetTerm.bold('Waiting for TM packets...') + '\n')    