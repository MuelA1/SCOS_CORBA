#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Facade, higher-level interface to use different agents and to perform specific tasks

Operator -- describes an interface (>>Facade<<) where every object is created

@author: Axel Müller
"""

import sys
import time
import logging
from time import sleep
from mibAgent import MIBAgent
from commandAgent import CommandAgent
from tmParamAgent import TMParamAgent
from tmPacketAgent import TMPacketAgent
from command import Command
from tmParameter import TMParameter
from tmPacket import TMPacket
from viewInterfaces import CommandInjectMngrView, ParameterView, PacketView
from colorama import Fore, Back, Style
from blessings import Terminal

class Operator():
    
    def __init__(self):
        
        self.__verbLevel = 1
               
        self.__mibAgent = MIBAgent()
        self.__cmdAgent = CommandAgent()
        self.__tmParamAgent = TMParamAgent() 
        self.__tmPacketAgent = TMPacketAgent()

    def __enter__(self):
        
        # change terminal window size (especially for verbLevel 2), works on gnome terminal but not for every terminal emulator
        print('\x1b[8;{rows};{cols}t'.format(rows=30, cols=120))          
        print('\n' + Style.BRIGHT + '=' * 95 + '\nStarting PyOps...\n' + '=' * 95 + Style.RESET_ALL + '\n')             
        
        return self
                
    def __exit__(self, type, value, traceback):
                             
        if type == KeyboardInterrupt:
            self.exitScr(1, keybInterrupt=True)
        elif Command.getExecutionError() == False and TMParameter.getExecutionError() == False and TMPacket.getExecutionError() == False:
            self.exitScr(0)
                    
    def configLogging(self, fileName, lvl):
        
        if lvl == 1:
            logLvl = logging.CRITICAL
        elif lvl == 2:     
            logLvl = logging.ERROR
        elif lvl == 3:     
            logLvl = logging.WARNING
        elif lvl == 4:     
            logLvl = logging.INFO
        elif lvl == 5:     
            logLvl = logging.DEBUG
        elif lvl not in [1, 2, 3, 4, 5]:
            print(Fore.RED + Style.BRIGHT + '\nError: ' + Style.RESET_ALL + 'Please enter a logging level between 1 and 5')           
            sys.exit(1)
            
        logging.basicConfig(filename=fileName, format='%(asctime)s (%(module)s): %(message)s', level=logLvl, filemode='w')
        logging.critical('Starting log...\n' + '=' * 100)    
      
    def connect(self, ip, port, mib=True, command=True, parameter=True, packet=True):
        
        try:
            if mib == True:                
                self.__mibAgent.connect(ip, port, self.__mibAgent.getNamingService(), self.__mibAgent.getServerMngrType())
                logging.debug('Successfully connected to external MIB server...')                
            if command == True:
                self.__cmdAgent.connect(ip, port, self.__cmdAgent.getNamingService(), self.__cmdAgent.getServerMngrType())
                logging.debug('Successfully connected to external command server...')
            if parameter == True:
                self.__tmParamAgent.connect(ip, port, self.__tmParamAgent.getNamingService(), self.__tmParamAgent.getServerMngrType())
                logging.debug('Successfully connected to external parameter server...')
            if packet == True:
                self.__tmPacketAgent.connect(ip, port, self.__tmPacketAgent.getNamingService(), self.__tmPacketAgent.getServerMngrType())
                logging.debug('Successfully connected to external packet server...')
                
        except Exception as exception: 
            print(Fore.RED + Style.BRIGHT + '\nException during server connection: ' + Style.RESET_ALL + f'{exception}') 
            logging.exception(f'Exception during server connection: {exception}', exc_info=False)
            sys.exit(1)
        
        self.initialize()
        
    def initialize(self):
         
        try:
            self.__createViewInterfaces()       
            self.__getManagers()
            
            if self.__verbLevel == 2:
                self.__setTerminals()

        except Exception as exception: 
            print(Fore.RED + Style.BRIGHT + '\nException during initialisation: ' + Style.RESET_ALL + f'{exception}')
            logging.exception(f'Exception during initialisation: {exception}', exc_info=False)
            if self.__cmdAgent.getCmdInjMngr() is not None:
                self.deregisterCommandMngr(error=True)
            sys.exit(1)
            
    def __createViewInterfaces(self):      
        
        if self.__cmdAgent.commandServiceIsConnected() == True: 
            self.__cmdAgent.createCmdInjMngrView(CommandInjectMngrView())  
            logging.debug('Successfully created command view interface...')
            
        if self.__tmParamAgent.paramServiceIsConnected() == True:
            tmParamView = self.__tmParamAgent.createParamView(ParameterView())
            TMParameter.setParamView(tmParamView)
            logging.debug('Successfully created parameter view interface...')
            
        if self.__tmPacketAgent.packetServiceIsConnected() == True:
            tmPacketView = self.__tmPacketAgent.createPacketView(PacketView())
            TMPacket.setPacketView(tmPacketView)
            logging.debug('Successfully created packet view interface...')      
            
    def __getManagers(self):
        
        if self.__mibAgent.mibServiceIsConnected() == True:
            self.__mibAgent.commandDefinitionIterator()
            self.__mibAgent.parameterDefinitionIterator()
            logging.debug('Getting MIB managers from server...') 
            
        if self.__cmdAgent.commandServiceIsConnected() == True:
            self.__cmdAgent.tcInjectMngr()        
            Command.setCommandInjMngr(self.__cmdAgent.getCmdInjMngr())
            Command.setCommandServerMngr(self.__cmdAgent._serverMngr)
            logging.debug('Getting command manager from server...')
            
        if self.__tmParamAgent.paramServiceIsConnected() == True:
            self.__tmParamAgent.tmServerType()
            self.__tmParamAgent.singleTMParamMngr()
            logging.debug('Getting parameter managers from server...')
            
        if self.__tmPacketAgent.packetServiceIsConnected() == True:
            self.__tmPacketAgent.tmPServerType()
            self.__tmPacketAgent.packetMngr()
            self.__tmPacketAgent.timeMngr()
            TMPacket.setTmPacketMngr(self.__tmPacketAgent.getPacketMngr())
            logging.debug('Getting packet managers from server...')
            
    def __setTerminals(self):
              
        if self.__cmdAgent.commandServiceIsConnected() == True:                                 
            Command.createCallbackTerminal(Terminal())
            logging.debug('Creating terminal for command callbacks...')
            
        if self.__tmParamAgent.paramServiceIsConnected() == True:
            TMParameter.createParamNotificationTerminal(Terminal())
            logging.debug('Creating terminal for parameter callbacks...')
            
        if self.__tmPacketAgent.packetServiceIsConnected() == True:
            TMPacket.createPacketNotificationTerminal(Terminal())
            logging.debug('Creating terminal for packet callbacks...')
            
    def __createSingleCommand(self, cmdName, counter=None, **cmdKwargs):
 
        # default MIB values
        cmdDef = self.__mibAgent.commandMIBDefinition(cmdName)        
        
        command = Command(cmdDef.m_name, cmdDef.m_description, **cmdKwargs)              
        command.setCommandDef(cmdDef)
        command.setMIBCommandParameters(counter) 
                                      
        return command
           
    def createCommand(self, cmdName, numberOfCommands=1, **cmdKwargs):
        
        try:
            if numberOfCommands == 1:
                command = self.__createSingleCommand(cmdName, **cmdKwargs)
                return command
            
            elif type(numberOfCommands) == int and numberOfCommands != 0:           
                cmdList = []
                for cmdNum in range(numberOfCommands):
                    command = self.__createSingleCommand(cmdName, **cmdKwargs)
                    cmdList.append(command)           
                return cmdList
            
            else:
                print(Fore.RED + Style.BRIGHT + '\nError: ' + Style.RESET_ALL + 'Please enter an integer number to create multiple commands')
                logging.error('Error: Please enter an integer number to create multiple commands', exc_info=False)  
                self.deregisterCommandMngr(error=True)
                sys.exit(1)
                
        except Exception as exception: 
            print(Fore.RED + Style.BRIGHT + f'\nException during command creation of command {cmdName}: ' + Style.RESET_ALL  + f'{exception}')    
            logging.exception(f'Exception during command creation of command {cmdName}: {exception}', exc_info=False)
            self.deregisterCommandMngr(error=True)   
            sys.exit(1)
            
    def setCommandParameter(self, command, paramName, **paramKwargs):    

        try:    
            if type(command) == Command:          
                command.setCommandParameter(paramName, **paramKwargs)
                
            elif type(command) == list: 
                for cmd in command:
                    cmd.setCommandParameter(paramName, **paramKwargs)

        except Exception as exception: 
            print(Fore.RED + Style.BRIGHT + f'\nException during setting of parameter {paramName}: ' + Style.RESET_ALL  + f'{exception}')    
            logging.exception(f'Exception during setting of parameter {paramName}: {exception}', exc_info=False)
            self.deregisterCommandMngr(error=True)   
            sys.exit(1)
                
    def printCommandInformation(self, *cmds):
       
        # print information of all commands
        if len(cmds) == 0:
            if Command.getCommandList() != []:
                for cmd in Command.getCommandList():
                    cmd.printCommandInfo()        
                    
                    if cmd == Command.getCommandList()[-1]:
                        print('\n' + Style.BRIGHT + '=' * 95 + Style.RESET_ALL + '\nEnd of command definition\n' + Style.BRIGHT + '=' * 95 + Style.RESET_ALL + '\n')
                        sys.stdout.flush()
                        sleep(0.005)                     
            else:
                print(Fore.RED + Style.BRIGHT + '\nError: ' + Style.RESET_ALL + 'Command list is empty, please create commands')
                logging.error('Error: Command list is empty, please create commands', exc_info=False)   
        
        # print information of *cmds argument
        else:
            for cmd in cmds:
                if type(cmd) == Command:
                    cmd.printCommandInfo() 
                elif type(cmd) == list:
                    for singleCmd in cmd:
                        singleCmd.printCommandInfo()
                                 
    def injectCommand(self, *cmds):
        """ Method to inject all commands in the global command list """
        
        if self.__verbLevel == 2:        
            print('\n' + Style.BRIGHT + '*' * 95 + '\n' + Back.RED + f"{'Command injection':=^95}"  + Style.RESET_ALL + '\n' + Style.BRIGHT + '*' * 95 + Style.RESET_ALL + '\n')      
            sys.stdout.flush()
            sleep(0.005)        
        
        # inject all commands 
        if len(cmds) == 0:       
            cmdList = Command.getCommandList()
            
        # inject selected commands (from *cmds argument)
        else:
            cmdList = []
            for cmd in cmds:
                if type(cmd) == Command:
                    cmdList.append(cmd)
                elif type(cmd) == list:
                    cmdList.extend(cmd)
                       
        if cmdList != []:
            for cmd in cmdList:                                           
                cmd.injectCommand()

        else:
            print(Fore.RED + Style.BRIGHT + '\nError during command injection: ' + Style.RESET_ALL + 'Injection list is empty')
            logging.error('Error during command injection: Injection list is empty', exc_info=False)
            self.deregisterCommandMngr(error=True)            
                                 
    def setGlobalCommandTimeout(self, timeout):
        
        Command.setGlobalCommandTimeout(timeout)

    def getGlobalCommandTimeout(self):
        
        return Command.getGlobalCommandTimeout()
        
    def setGlobalPacketTimeout(self, timeout):
        
        TMPacket.setGlobalPacketTimeout(timeout)

    def getGlobalPacketTimeout(self):
        
        return TMPacket.getGlobalPacketTimeout()
    
    def setVerbosity(self, verbLevel, terminal=None):
        
        if verbLevel in [2, 1]:
            self.__verbLevel = verbLevel
            
            if verbLevel == 2 and terminal == None:
                print(Fore.RED + Style.BRIGHT + '\nError: ' + Style.RESET_ALL + f'Please set terminal type for verbosity level 2')
                logging.error(f'Error: Terminal type for verbosity level 2 is not set', exc_info=False)
                sys.exit(1)                
            elif verbLevel == 2:
                Command.setTerminalType(terminal)
                TMParameter.setTerminalType(terminal)
                TMPacket.setTerminalType(terminal)
            
            Command.setVerbosityLevel(verbLevel)
            TMParameter.setVerbosityLevel(verbLevel)
            TMPacket.setVerbosityLevel(verbLevel)
                                    
        else:
            print(Fore.RED + Style.BRIGHT + '\nError: ' + Style.RESET_ALL + f'Verbosity level must be 1 or 2, not {verbLevel}')
            logging.error(f'Error: Verbosity level must be 1 or 2, not {verbLevel}', exc_info=False)
            sys.exit(1)
            
    def registerTMParameter(self, paramName, **paramKwargs):

        try:        
            paramDef = self.__mibAgent.parameterMIBDefinition(paramName)
            
            parameter = TMParameter(paramDef.m_name, paramDef.m_description, **paramKwargs)
            parameter.setParameterDef(paramDef)
            parameter.getParameterFromServer(self.__tmParamAgent.getSingleTMParamMngr())
            parameter.registerParameter()
                                                   
            return parameter

        except Exception as exception: 
            print(Fore.RED + Style.BRIGHT + '\nException during parameter reception: ' + Style.RESET_ALL + f'{exception}')            
            logging.exception(f'Exception during parameter reception: {exception}', exc_info=False)
            if 'parameter' is locals() and parameter.getViewKey() != 0:
                parameter.unregisterParamView()
            
    def registerTMPacket(self, filingKey, **packetKwargs):

        try:        
            packet = TMPacket(filingKey, **packetKwargs)
            packet.setStreamIds(self.__tmPacketAgent.getTimeMngr())
            packet.registerTMpackets()
        
            return packet

        except Exception as exception: 
            print(Fore.RED + Style.BRIGHT + '\nException during packet reception: ' + Style.RESET_ALL + f'{exception}')           
            logging.exception(f'Exception during packet reception: {exception}', exc_info=False)
            if 'packet' is locals() and packet.getViewKey() != 0:
                packet.unregisterTmPacket()
    
    def unregisterAllTmParameters(self):
        
        TMParameter.unregisterAllTmParameters()

    def unregisterAllTmPackets(self):
        
        TMPacket.unregisterAllTmPackets()
    
    def writeCommandLog(self, path):
        
        print('Writing command log...', 
              end='' if self.__verbLevel == 2 else '\n')
        logging.debug('Writing command log...')
        
        with open(path, 'w') as log:
            for cmd in Command.getCommandList():
                log.write(str(cmd) + '\n')
                
                if cmd == Command.getCommandList()[-1]:
                    log.write('\n' + '=' * 95 + '\nEnd of log\n' + '=' * 95 + '\n')

        if self.__verbLevel == 2:            
            print('done') 
        elif self.__verbLevel == 1:
            print('Finished writing command log...')          
        
        logging.debug('Finished writing command log...')
        self.__flush()

    def writeParameterLog(self, path):
        
        print('Writing parameter log...', 
              end='' if self.__verbLevel == 2 else '\n')
        logging.debug('Writing parameter log...')
        
        with open(path, 'w') as log:
            for param in TMParameter.getGlobalParamList():
                log.write(str(param) + '\n')
                
                if param == TMParameter.getGlobalParamList()[-1]:
                    log.write('\n' + '=' * 95 + '\nEnd of log\n' + '=' * 95 + '\n')

        if self.__verbLevel == 2:            
            print('done') 
        elif self.__verbLevel == 1:
            print('Finished writing parameter log...')          
        
        logging.debug('Finished writing parameter log...')
        self.__flush()    

    def writePacketLog(self, path):
        
        print('Writing packet log...', 
              end='' if self.__verbLevel == 2 else '\n')
        logging.debug('Writing packet log...')
        
        with open(path, 'w') as log:
            for packet in TMPacket.getGlobalPacketList():
                log.write(str(packet) + '\n')
                
                if packet == TMPacket.getGlobalPacketList()[-1]:
                    log.write('\n' + '=' * 95 + '\nEnd of log\n' + '=' * 95 + '\n')

        if self.__verbLevel == 2:            
            print('done') 
        elif self.__verbLevel == 1:
            print('Finished writing packet log...')          
        
        logging.debug('Finished writing packet log...')
        self.__flush() 
    
    def pauseForExecution(self, sec):
        
        print(f'Waiting {sec} sec for commands to be executed...',
              end='' if self.__verbLevel == 2 else '\n')
        logging.debug(f'Waiting {sec} sec for commands to be executed...')
        self.__flush()
     
        currTime = time.time()
        while time.time() - currTime < sec:
            pass
        if self.__verbLevel == 2:            
            print('continuing') 
        elif self.__verbLevel == 1:
            print('Continuing...')          
        
        logging.debug('Continuing program execution...')
        self.__flush()
        
    def __flush(self, sleep=0.015):
        
        sys.stdout.flush()
        time.sleep(sleep)

    def deregisterCommandMngr(self, **error):
         
        Command.deregister(**error)
        
    def exitScr(self, exitFlag, keybInterrupt=False):    

        if exitFlag == 1 and keybInterrupt == False:
            print('\n' + Style.BRIGHT + '=' * 95 + Style.RESET_ALL + '\n' + Fore.RED + 'Test procedure error, preparing to exit PyOps' + Style.RESET_ALL + '...')
            logging.critical('Test procedure error, preparing to exit PyOps...' + '\n' + '=' * 100)         
        elif exitFlag == 1 and keybInterrupt == True:
            print('\n' + Style.BRIGHT + '=' * 95 + Style.RESET_ALL + '\n' + Fore.RED + 'Test canceled by user, preparing to exit PyOps' + Style.RESET_ALL + '...')
            logging.critical('Test canceled by user, preparing to exit PyOps...' + '\n' + '=' * 100) 
        elif exitFlag == 0:
            print('\n' + Style.BRIGHT + '=' * 95 + Style.RESET_ALL + '\nSuccessfully finished script, preparing to exit PyOps...')
            logging.critical('Successfully finished script, preparing to exit PyOps...' + '\n' + '=' * 100)
        elif exitFlag not in [0, 1]:
            print(Fore.RED + Style.BRIGHT + '\nError: ' + Style.RESET_ALL + 'Method exitScr - please enter 0 (success) or 1 (failure)')           
            sys.exit(1) 
            
        if TMParameter.getGlobalParamList != []:
            self.unregisterAllTmParameters()
        if TMPacket.getGlobalPacketList != []:
            self.unregisterAllTmPackets()
        
        if exitFlag == 1:
            if self.__cmdAgent.getCmdInjMngr() is not None:
                self.deregisterCommandMngr(error=True)                              
        elif exitFlag == 0:
            if self.__cmdAgent.getCmdInjMngr() is not None:
                self.deregisterCommandMngr()                
                sys.exit(exitFlag)               
                                     