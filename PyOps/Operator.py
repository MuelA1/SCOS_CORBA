#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Facade, higher-level interface to use different agents and to perform specific tasks

Operator -- describes an interface where every object is created
"""

import sys
from time import sleep
from MIBAgent import MIBAgent
from CommandAgent import CommandAgent
from tmParamAgent import TMParamAgent
from tmPacketAgent import TMPacketAgent
from Command import Command
from tmParameter import TMParameter
from tmPacket import TMPacket
from ViewInterfaces import CommandInjectMngrView, ParameterView, PacketView
from colorama import Fore, Back, Style
from blessings import Terminal

class Operator():
    
    def __init__(self):
        
        self.__mibAgent = MIBAgent()
        self.__cmdAgent = CommandAgent()
        self.__tmParamAgent = TMParamAgent() 
        self.__tmPacketAgent = TMPacketAgent()
                
    def connect(self, ip, port, mib=True, command=True, parameter=True, packet=True):
        
        try:
            if mib == True:
                self.__mibAgent.connect(ip, port, self.__mibAgent.getNamingService(), self.__mibAgent.getServerMngrType())
            if command == True:
                self.__cmdAgent.connect(ip, port, self.__cmdAgent.getNamingService(), self.__cmdAgent.getServerMngrType())
            if parameter == True:
                self.__tmParamAgent.connect(ip, port, self.__tmParamAgent.getNamingService(), self.__tmParamAgent.getServerMngrType())
            if packet == True:
                self.__tmPacketAgent.connect(ip, port, self.__tmPacketAgent.getNamingService(), self.__tmPacketAgent.getServerMngrType())

        except Exception as exception: 
            print(Fore.RED + Style.BRIGHT + '\nException during server connection: ' + Style.RESET_ALL + f'{exception}') 
            sys.exit(1)
            
    def initialize(self, **initKwargs):
         
        try:
            self.__createViewInterfaces(**initKwargs)       
            self.__getManagers(**initKwargs)
            self.__setTerminals(**initKwargs)

        except Exception as exception: 
            print(Fore.RED + Style.BRIGHT + '\nException during initialisation: ' + Style.RESET_ALL + f'{exception}')
            if self.__cmdAgent.getCmdInjMngr() is not None:
                self.deregister()
            sys.exit(1)
            
    def __createViewInterfaces(self, terminal=None, mib=True, command=True, parameter=True, packet=True):      
        
        if command == True: 
            self.__cmdAgent.createCmdInjMngrView(CommandInjectMngrView(), 'MngrView')  
             
        if parameter == True:
            tmParamView = self.__tmParamAgent.createParamView(ParameterView(), 'ParamView')
            TMParameter.setParamView(tmParamView)
            
        if packet == True:
            tmPacketView = self.__tmPacketAgent.createPacketView(PacketView(), 'PacketView')
            TMPacket.setPacketView(tmPacketView)
                   
    def __getManagers(self, terminal=None, mib=True, command=True, parameter=True, packet=True):
        
        if mib == True:
            self.__mibAgent.commandDefinitionIterator()
            self.__mibAgent.parameterDefinitionIterator()
            
        if command == True:
            self.__cmdAgent.tcInjectMngr()        
            Command.setCommandInjMngr(self.__cmdAgent.getCmdInjMngr())
            Command.setCommandServerMngr(self.__cmdAgent._serverMngr)
        
        if parameter == True:
            self.__tmParamAgent.tmServerType()
            self.__tmParamAgent.singleTMParamMngr()
        
        if packet == True:
            self.__tmPacketAgent.tmPServerType()
            self.__tmPacketAgent.packetMngr()
            self.__tmPacketAgent.timeMngr()
            TMPacket.setTmPacketMngr(self.__tmPacketAgent.getPacketMngr())
                   
    def __setTerminals(self, terminal='konsole', mib=True, command=True, parameter=True, packet=True):
    
        if command == True:
            term = Terminal()        
            # change window size, works on gnome terminal
            print('\x1b[8;{rows};{cols}t'.format(rows=30, cols=120))          
            print('\n' + term.bold('Commands to be injected...'))             
            
            Command.setTerminal(term)
            Command.createCallbackTerminal(Terminal(), terminalType=terminal)
        
        if parameter == True:
            TMParameter.createParamNotificationTerminal(Terminal(), terminalType=terminal)
            
        if packet == True:
            TMPacket.createPacketNotificationTerminal(Terminal(), terminalType=terminal)
               
    def __createSingleCommand(self, cmdName, counter=None, **cmdKwargs):
 
        # default MIB values
        cmdDef = self.__mibAgent.commandMIBDefinition(cmdName)        
        
        command = Command(cmdDef.m_name, cmdDef.m_description, **cmdKwargs)              
        command.setCommandDef(cmdDef)
        command.setMIBCommandParameters(counter) 
        command.initTables()        
                     
        return command
           
    def createCommand(self, cmdName, numberOfCommands=0, **cmdKwargs):
        
        try:
            if numberOfCommands == 0:
                command = self.__createSingleCommand(cmdName, **cmdKwargs)
                return command
            
            elif type(numberOfCommands) == int:           
                cmdList = []
                for cmdNum in range(numberOfCommands):
                    command = self.__createSingleCommand(cmdName, **cmdKwargs)
                    cmdList.append(command)           
                return cmdList
            
            else:
                print(Fore.RED + Style.BRIGHT + '\nError: ' + Style.RESET_ALL + 'Please enter an integer number to create multiple commands')
                self.deregister()
                sys.exit(1)
                
        except Exception as exception: 
            print(Fore.RED + Style.BRIGHT + f'\nException during command creation of command {cmdName}: ' + Style.RESET_ALL  + f'{exception}')    
            self.deregister()   
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
            self.deregister()   
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
                   
        # print information of command arguments
        else:
            for cmd in cmds:
                if type(cmd) == Command:
                    cmd.printCommandInfo() 
                elif type(cmd) == list:
                    for singleCmd in cmd:
                        singleCmd.printCommandInfo()
                    
    def injectCommands(self, *cmds):
        
        inp = str(input('Do you want to continue with the command injection? ' + Style.BRIGHT + '(Y/N)' + Style.RESET_ALL + ': ')).lower().strip()
                
        try:
            if inp[0] == 'y':
                self.__inject(*cmds)
                       
            elif inp[0] == 'n':
                self.deregister()    
                               
            else:
                print(Fore.RED + Style.BRIGHT +'Invalid input, please try again...' + Style.RESET_ALL)
                return self.injectCommands()
        
        except Exception as exception:  
            print(Fore.RED + Style.BRIGHT + '\nInput error: ' + Style.RESET_ALL + f'{exception}')
            return self.injectCommands()       
          
    def __inject(self, *cmds):
        """ Method to inject all commands in the global command list """
                
        print('\n' + Style.BRIGHT + '*' * 95 + '\n' + Back.RED + f"{'Command injection':=^95}"  + Style.RESET_ALL + '\n' + Style.BRIGHT + '*' * 95 + Style.RESET_ALL + '\n')      
        sys.stdout.flush()
        sleep(0.005)        
        
        # inject all commands 
        if len(cmds) == 0:       
            cmdList = Command.getCommandList()
            
        # inject selected commands (from argument)
        else:
            cmdList = []
            for cmd in cmds:
                if type(cmd) == Command:
                    cmdList.append(cmd)
                elif type(cmd) == list:
                    cmdList.extend(cmd)

        # check if there is a previous command with absolute release time to calculate relative release time
        absReleaseTime = False
                       
        if len(cmdList) > 0:
            for cmd in cmdList:                
                if cmd.relReleaseTime is None:                   
                    cmd.injectCommand()
                    if absReleaseTime == False:
                        absReleaseTime = True
                        
                elif absReleaseTime == True:
                    # start thread to get relative release time from previous command and inject cmd 
                    cmd.startReleaseTimeThread()
                    
                else:
                    print(Fore.RED + Style.BRIGHT + '\nError: ' + Style.RESET_ALL + 'Please create a command which defines the absolute release time')
                    self.deregister()
                    break
        else:
            print(Fore.RED + Style.BRIGHT + '\nError during command injection: ' + Style.RESET_ALL + 'Injection list is empty')
            self.deregister()            
                                 
    def setCommandInterlock(self, command, ilockList):
        
        if type(command) == Command:
            command.setCommandInterlock(ilockList)
            
        elif type(command) == list:    
            for cmd in command:
                cmd.setCommandInterlock(ilockList)

    def setGlobalTimeout(self, timeout):
        
        Command.setGlobalTimeout(timeout)

    def getGlobalTimeout(self):
        
        return Command.getGlobalTimeout()
        
    def getTMParameter(self, paramName):

        try:        
            paramDef = self.__mibAgent.parameterMIBDefinition(paramName)
            
            parameter = TMParameter(paramDef.m_name, paramDef.m_description)
            parameter.setParameterDef(paramDef)
            parameter.getParameterFromServer(self.__tmParamAgent.getSingleTMParamMngr())
            parameter.registerParameter()
                                                   
            return parameter

        except Exception as exception: 
            print(Fore.RED + Style.BRIGHT + '\nException during parameter reception: ' + Style.RESET_ALL + f'{exception}')            
            if parameter.getViewKey() != 0:
                parameter.unregisterParamView()
            
    def getTMPacket(self, **packetKwargs):

        try:        
            packet = TMPacket(**packetKwargs)
            packet.setStreamIds(self.__tmPacketAgent.getTimeMngr())
            packet.registerTMpackets()
        
            return packet

        except Exception as exception: 
            print(Fore.RED + Style.BRIGHT + '\nException during packet reception: ' + Style.RESET_ALL + f'{exception}')
    
    def printLogfile(self, path):
        
        with open(path, 'w') as log:
            for cmd in Command.getCommandList():
                log.write(str(cmd) + '\n')

    def deregister(self):
         
        self.__cmdAgent.deregister()
        