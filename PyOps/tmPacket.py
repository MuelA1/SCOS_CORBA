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

import ITMP
import sys
import os
import threading
import timeModule
import time
from tabulate import tabulate
from subprocess import Popen
from colorama import Fore, Style
import logging

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
    __tableLogHeaders = ['Generation Time', 'Reception Time']
    
    __packetCount = 0 
    __verbosityLevel = 2
    
    def __init__(self, filingKey, apIds=None, header=False, body=False, param=True):
        
        self.__globalPacketList.append(self)
        type(self).__packetCount += 1
        self.__instCount = self.__packetCount
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
         
        self.__packetTableRows = []
        self.__packetList = []
        self.__packetListLen = 0
        self.__packetThread = None
        self.__globalCallbackCounter = 0
        self.__localCallbackCounter = 0  
        
        self.__packetStatus = None

    def __str__(self):
        
        if self.__instCount > 999:
            disp = 83
        elif self.__instCount > 99:
            disp = 84
        elif self.__instCount > 9:
            disp = 85
        else:
            disp = 86
            
        string = '\n' + '*' * 95
        string += f'\nPacket {self.__instCount} {self.__filingKey[0]:=^{disp}}\n' 
        string += '*' * 95 + '\n\n' 
                
        if self.__packetTableRows != []:
            
            string += 'Mnemonic ' + '-' * 86 + '\n\n'
            string += f'{self.__packetList[0].m_pktAttributes.m_mnemo}\n\n'
            string += 'Description ' + '-' * 83 + '\n\n'
            string += f'{self.__packetList[0].m_pktAttributes.m_packetDescription}\n\n'   
            string += 'APID ' + '-' * 90 + '\n\n'
            string += f'{self.__packetList[self.__localCallbackCounter - 1].m_pktAttributes.m_pusApId}\n\n'
            string += 'Callback time ' + '-' * 81 + '\n\n'
            string += tabulate(self.__packetTableRows, headers=self.__tableLogHeaders) + '\n\n'
            string += '-' * 95 + '\n'
            string += f'Packet {self.__instCount} (SPID {self.__filingKey[0]}) received {len(self.__packetList)} callback(s)\n'
            string += '-' * 95 
        else:
            string += f'Packet {self.__filingKey[0]} received no callback\n\n'            
            string += '-' * 95                
        
        return string
                
    def setStreamIds(self, timeMngr):
        self.__streamIds = timeMngr.getDataStreams()
        
    def registerTMpackets(self):
        
        self.__tmPacketFilter = ITMP.TMpacketFilter(self.__streamIds, self.__apIds, self.__filingKey)
        self.__tmTransmissionFilter = ITMP.TransmissionFilter(self.__header, self.__body, self.__param)
        
        self.__viewKey = self.__tmPacketMngr.registerTMpackets(self.__packetView, self.__tmPacketFilter, self.__tmTransmissionFilter)
        print(f'Packet {self.__instCount} (' + Style.BRIGHT + f'SPID {self.__filingKey[0]}' + Style.RESET_ALL + ') is registered...')
        logging.debug(f'Packet {self.__instCount} (SPID {self.__filingKey[0]}) is registered...')
        
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
                        logging.debug(f'Packet {self.__instCount} (SPID {self.__filingKey[0]}) received callback...')
                        
                        self.__packetTableRows.append([timeModule.ibaseTime2SCOSdate(self.__packetList[self.__localCallbackCounter].m_pktAttributes.m_filingTime),
                                                       timeModule.ibaseTime2SCOSdate(self.__packetList[self.__localCallbackCounter].m_pktAttributes.m_createTime)])
                        
                        if self.__verbosityLevel == 2:                            
                            self.__packetLock.acquire()        
                            self.__rows[self.__filingKey[0]] = [self.__packetList[self.__localCallbackCounter].m_pktAttributes.m_mnemo,
                                                                Style.BRIGHT + f'{self.__packetList[self.__localCallbackCounter].m_pktAttributes.m_filingKey}' + Style.RESET_ALL,
                                                                self.__packetList[self.__localCallbackCounter].m_pktAttributes.m_packetDescription,
                                                                self.__packetList[self.__localCallbackCounter].m_pktAttributes.m_pusApId,
                                                                timeModule.ibaseTime2SCOSdate(self.__packetList[self.__localCallbackCounter].m_pktAttributes.m_filingTime),
                                                                timeModule.ibaseTime2SCOSdate(self.__packetList[self.__localCallbackCounter].m_pktAttributes.m_createTime)]     
                                                    
                            completeRows = []                    
                            for row in self.__rows.values():
                                completeRows.append(row)                        
    
                            with open(self.__PIPE_PATH_Packet, 'w') as packetTerminal:                                                                                                                                      
                                packetTerminal.write(self.__packetTerm.clear() + '\n' +  self.__packetTerm.bold('=' * 120 + '\nTM packets\n' + '=' * 120) +
                                                     self.__packetTerm.move(5, 0) + tabulate(completeRows, headers=self.__tableHeaders))                                                                                         
                                                                                                                     
                            self.__packetLock.release()
                    
                        self.__localCallbackCounter += 1    
                    self.__globalCallbackCounter += 1

                # call method every 0.5 sec    
                nextCall += 0.5
                time.sleep(nextCall - time.time())

        except Exception as exception:
            self.__packetThread.do_run = False
            print(Fore.RED + Style.BRIGHT + f'\nPacket {self.__filingKey[0]} - Exception during packet reception: ' + Style.RESET_ALL + f'{exception}')
            logging.exception(f'Packet {self.__filingKey[0]} - Exception during packet reception: {exception}', exc_info=False)
            
    def verifyPacketReception(self, timeout=None):
        
        if timeout is None:
            pktTimeout = self.__globalTimeout        
        else:
            pktTimeout = timeout
        
        currTime = time.time()
        timeoutTime = currTime +  pktTimeout
        
        print('Waiting ' + Style.BRIGHT + f'{pktTimeout} sec ' + Style.RESET_ALL + f'for packet {self.__instCount} (' + Style.BRIGHT + f'SPID {self.__filingKey[0]}' + Style.RESET_ALL + ')...',
              end='' if self.__verbosityLevel == 2 else '\n')
        logging.info(f'Waiting {pktTimeout} sec for packet {self.__instCount} (SPID {self.__filingKey[0]})...')
        self.__flush()
        
        while self.__packetListLen == len(self.__packetList):       
            if timeoutTime - time.time() < 0:          
                self.__packetStatus = 'TIMEOUT'           
                if self.__verbosityLevel == 2: 
                    print('<<' + Fore.YELLOW + self.__packetStatus + Style.RESET_ALL + '>>')                    
                elif self.__verbosityLevel == 1:   
                    print(f'Packet {self.__instCount} (' + Style.BRIGHT + f'SPID {self.__filingKey[0]}' + Style.RESET_ALL + ') ' + Fore.YELLOW + 'timed out' + Style.RESET_ALL + f' @ {timeModule.ibaseTime2SCOSdate(timeModule.stamp2ibaseTime(time.time()))}...')               
                logging.error(f'Packet {self.__instCount} (SPID {self.__filingKey[0]}) timed out...')
                self.__flush()
                return 'TIMEOUT'      
        self.__packetStatus = 'RECEIVED'
        self.__packetListLen = len(self.__packetList)
        if self.__verbosityLevel == 2:
            print('<<' + Fore.GREEN + self.__packetStatus + Style.RESET_ALL + '>>')
        elif self.__verbosityLevel == 1:   
            print(f'Packet {self.__instCount} (' + Style.BRIGHT + f'SPID {self.__filingKey[0]}' + Style.RESET_ALL + ') ' + Fore.GREEN + 'received' + Style.RESET_ALL + f' @ {timeModule.ibaseTime2SCOSdate(timeModule.stamp2ibaseTime(time.time()))}...')            
        logging.info(f'Packet {self.__instCount} (SPID {self.__filingKey[0]}) received...')
        logging.info('\n' + str(self) + '\n')
        self.__flush()
        return 'RECEIVED'
            
    def getViewKey(self):
        
        return self.__viewKey
    
    def unregisterTmPacket(self):  
        
        if self.__packetThread.isAlive():
            self.__packetThread.do_run = False
        self.__tmPacketMngr.unregisterTMpackets(self.__viewKey)
        self.__tmPacketMngr.unregisterView(self.__viewKey)                                         
        print(f'Unregistered packet {self.__instCount} (SPID {self.__filingKey[0]})...')
        logging.debug(f'Unregistered packet {self.__instCount} (SPID {self.__filingKey[0]})...')
        self.__flush()
                
    def __flush(self, sleep=0.02):
        
        sys.stdout.flush()
        time.sleep(sleep)

    @classmethod
    def getGlobalPacketList(cls):
        return cls.__globalPacketList
    
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
        cls.__notifyPacketListStatic.append(packet[0])      
       
    @classmethod    
    def setVerbosityLevel(cls, verbLevel):
        cls.__verbosityLevel = verbLevel

    @classmethod    
    def getVerbosityLevel(cls):
        return cls.__verbosityLevel 
    
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
            packetTerminal.write('\n' +  cls.__packetTerm.bold('=' * 120 + '\nTM packets\n' + '=' * 120) + '\n')    