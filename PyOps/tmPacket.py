#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Class for telemetry packet settings

TMPacket -- describes packet filters and packet callback progression

[ITMP.TMpacketNotifyData(m_pktAttributes=ITMP.TMpacketAttributes(m_pktDetailsFlag=True, 
                         m_mnemo='AYHK1900safe', 
                         m_filingTime=IBASE.Time(m_sec=1511367728, m_micro=245000, m_isDelta=False), (generation time)
                         m_createTime=IBASE.Time(m_sec=1511367712, m_micro=27010, m_isDelta=False),  (reception time)
                         m_vcId=0, 
                         m_pusApId=53, 
                         m_pusSrcSeqCnt=10683, 
                         m_pusSrvcType=3, 
                         m_pusSrvcSubType=25, 
                         m_pi1Field=1900, 
                         m_pi2Field=0, 
                         m_streamId=65535, 
                         m_filingKey=31900, 
                         m_gsId=0, 
                         m_timeStampType='2', 
                         m_timeQualityFlag='G', 
                         m_filingFlag=True, 
                         m_distributionFlag=True, 
                         m_packetDescription='Srv (3,25) ACS Calculated Safe Mode Data', 
                         m_simulationFlag=True, 
                         m_spaceCraftId=605, 
                         m_sleID=0, 
                         m_occID=0, 
                         m_qualDataUnitType='G', 
                         m_tpsd=-1, 
                         m_seqCounter=1046, 
                         m_timeField=True, 
                         m_interval=10000, 
                         m_eventFlag='?', 
                         m_checkFlag=0), 
                         
                         m_pktHeaderRawData=b'', 
                         m_pktBodyRawData=b'', 
                         m_pktParams=[])]
"""

import ITMP, IBASE
import sys
import os
import threading
import TimeModule
import time
from tabulate import tabulate
from terminaltables import AsciiTable
from subprocess import Popen
from colorama import Fore, Back, Style

class TMPacket():
    
    __packetView = None
    __notifyPacketListStatic = []
    __PIPE_PATH_Packet = None
    __packetTerm = None
    __tmPacketMngr = None
    __packetLock = threading.Lock()
    __rows = {}   
    __globalTimeout = 20
    __globalPacketList = []
    __tableHeaders = [Style.BRIGHT + 'Mnemonic', 'SPID', 'Description', 'APID', 'Generation Time', 'Reception Time' + Style.RESET_ALL]
    
    def __init__(self, filingKey, apIds=None, header=False, body=False, param=True):
        
        self.__globalPacketList.append(self)
        self.__streamIds = None
        self.__apIds = apIds if apIds is not None else []  
        self.__filingKey = []
        if type(filingKey) is not int:
            raise Exception(f'Please enter a valid filing key (SPID)')
        else:    
            self.__filingKey.append(filingKey)
            
        self.__header = header
        self.__body = body
        self.__param = param      
        self.__viewKey = None
        self.__tmPacketFilter = None
        self.__tmTransmissionFilter = None
         
        self.__packetList = []
        self.__packetListLen = 0
        self.__packetThread = None
        self.__globalCallbackCounter = 0
        self.__localCallbackCounter = 0  
        
        self.__packetStatus = None
                
    def setStreamIds(self, timeMngr):
        self.__streamIds = timeMngr.getDataStreams()
        
    def registerTMpackets(self):
        
        self.__tmPacketFilter = ITMP.TMpacketFilter(self.__streamIds, self.__apIds, self.__filingKey)
        self.__tmTransmissionFilter = ITMP.TransmissionFilter(self.__header, self.__body, self.__param)
        
        self.__viewKey = self.__tmPacketMngr.registerTMpackets(self.__packetView, self.__tmPacketFilter, self.__tmTransmissionFilter)

        # start callback thread          
        self.__packetThread = threading.Thread(target=self.printPacketValue)
        self.__packetThread.start()
    
    def printPacketValue(self):
        
        try:
            nextCall = time.time()                        
            while getattr(self.__packetThread, 'do_run', True):                              
                while self.__globalCallbackCounter < len(self.__notifyPacketListStatic):           
                    if self.__notifyPacketListStatic[self.__globalCallbackCounter].m_pktAttributes.m_filingKey == self.__filingKey[0]:                        
                        self.__packetList.append(self.__notifyPacketListStatic[self.__globalCallbackCounter])
                                                    
                        self.__packetLock.acquire()        
                        self.__rows[self.__filingKey[0]] = [self.__packetList[self.__localCallbackCounter].m_pktAttributes.m_mnemo,
                                                            Style.BRIGHT + f'{self.__packetList[self.__localCallbackCounter].m_pktAttributes.m_filingKey}' + Style.RESET_ALL,
                                                            self.__packetList[self.__localCallbackCounter].m_pktAttributes.m_packetDescription,
                                                            self.__packetList[self.__localCallbackCounter].m_pktAttributes.m_pusApId,
                                                            TimeModule.ibaseTime2SCOSdate(self.__packetList[self.__localCallbackCounter].m_pktAttributes.m_filingTime),
                                                            TimeModule.ibaseTime2SCOSdate(self.__packetList[self.__localCallbackCounter].m_pktAttributes.m_createTime)]     
                                                
                        completeRows = []                    
                        for row in self.__rows.values():
                            completeRows.append(row)                        

                        with open(self.__PIPE_PATH_Packet, 'w') as packetTerminal:
                          
                            #packetTerminal.write('\x1b[2J\x1b[H')
                            #packetTerminal.write(self.__packetTerm.move(0, 3) + '\n' * 10)

                            # Tabulate
                            packetTerminal.write(self.__packetTerm.move(0, 3) + tabulate(completeRows, 
                                                                                         headers=self.__tableHeaders,
                                                                                         tablefmt='fancy_grid') 
                                                                                         + '\n')
                            # Terminaltables
#                            completeRows.insert(0, self.__tableHeaders)
#                            table = AsciiTable(completeRows)
#                            table.outer_border = False
#                            packetTerminal.write(self.__packetTerm.move(0, 3) + '\n' + table.table + '\n')
                        
                        self.__packetLock.release()
                    
                        self.__localCallbackCounter += 1    
                    self.__globalCallbackCounter += 1

                # call method every 0.5 sec    
                nextCall += 0.5
                time.sleep(nextCall - time.time())

        except Exception as exception:
            self.__packetThread.do_run = False
            with open(self.__PIPE_PATH_Packet, 'w') as packetTerminal:                   
                with self.__packetTerm.location(0, self.__packetTerm.height - 1):
                    packetTerminal.write(self.__packetTerm.bold_red(f'\nPacket {self.__filingKey[0]} - Exception during packet reception: ') + f'{exception}')
    
    def verifyPacketReception(self, timeout=None):
        
        if timeout is None:
            pktTimeout = self.__globalTimeout        
        else:
            pktTimeout = timeout
        
        currTime = time.time()
        timeoutTime = currTime +  pktTimeout
        print(f'Waiting for packet (SPID {self.__filingKey[0]})...', end='')
                
        while self.__packetListLen == len(self.__packetList):       
            if timeoutTime - time.time() < 0:          
                self.__packetStatus = 'TIMEOUT'
#                with open(self.__PIPE_PATH_Packet, 'w') as packetTerminal:                   
#                    with self.__packetTerm.location(0, self.__packetTerm.height - 1):
#                        packetTerminal.write(self.__packetTerm.bold(f'\nPacket (SPID {self.__filingKey[0]})') + ' - ' + self.__packetTerm.yellow('TIMEOUT') + f' ({pktTimeout} sec)')             
                print(Fore.YELLOW + self.__packetStatus + Style.RESET_ALL)
                self.__flush()
                return 'TIMEOUT'      
        self.__packetStatus = 'RECEIVED'
        self.__packetListLen = len(self.__packetList)
        print(Fore.GREEN + self.__packetStatus + Style.RESET_ALL)
        self.__flush()
        return 'RECEIVED'
            
    def getViewKey(self):
        
        return self.__viewKey
    
    def unregisterTmPacket(self):  
        
        if self.__packetThread.isAlive():
            self.__packetThread.do_run = False
        self.__tmPacketMngr.unregisterTMpackets(self.__viewKey)
        self.__tmPacketMngr.unregisterView(self.__viewKey)                                         
        print(f'Unregistered packet {self.__filingKey[0]}...')
                        
    def __flush(self, sleep=0.02):
        
        sys.stdout.flush()
        time.sleep(sleep)

    @classmethod
    def unregisterAllTmPackets(cls):
        
        for packet in cls.__globalPacketList:
            packet.unregisterTmPacket()
    
    @classmethod
    def setGlobalPacketTimeout(cls, globalTimeout):
        cls.__globalTimeout = globalTimeout

    @classmethod
    def getGlobalPacketTimeout(cls):
        return cls.__globalTimeout 
    
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
            packetTerminal.write(str(packet) + '\n\n') 
        
    @classmethod
    def createPacketNotificationTerminal(cls, term, terminalType):
        
        cls.__packetTerm = term
        cls.__PIPE_PATH_Packet = '/tmp/packetNotifyPipe'  
        
        if os.path.exists(cls.__PIPE_PATH_Packet):
            os.remove(cls.__PIPE_PATH_Packet)
        
        # named pipe                      
        os.mkfifo(cls.__PIPE_PATH_Packet)
            
        # new terminal subprocess ('xterm' also possible)   
        Popen([terminalType, '-e', 'tail -f %s' % cls.__PIPE_PATH_Packet])   
               
        with open(cls.__PIPE_PATH_Packet, 'w') as packetTerminal:
            packetTerminal.write('\n' +  cls.__packetTerm.bold('Waiting for TM packets...') + '\n')    