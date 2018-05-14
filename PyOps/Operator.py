#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Facade, higher-level interface to use different agents and to perform specific tasks

Operator -- describes an interface where every object is created
"""

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
            print(Fore.RED + Style.BRIGHT + '\nException during server connection:{}'.format(exception), Style.RESET_ALL) 
            
    def initialize(self, **initKwargs):
         
        try:
            self.__createViewInterfaces(**initKwargs)       
            self.__getManagers(**initKwargs)
            self.__setTerminals(**initKwargs)

        except Exception as exception: 
            print(Fore.RED + Style.BRIGHT + '\nException during initialisation:{}'.format(exception), Style.RESET_ALL)
        
    def __createViewInterfaces(self, mib=True, command=True, parameter=True, packet=True):      
        
        if command == True: 
            self.__cmdAgent.createCmdInjMngrView(CommandInjectMngrView(), 'MngrView')  
             
        if parameter == True:
            tmParamView = self.__tmParamAgent.createParamView(ParameterView(), 'ParamView')
            TMParameter.setParamView(tmParamView)
            
        if packet == True:
            tmPacketView = self.__tmPacketAgent.createPacketView(PacketView(), 'PacketView')
            TMPacket.setPacketView(tmPacketView)
                   
    def __getManagers(self, mib=True, command=True, parameter=True, packet=True):
        
        if mib == True:
            self.__mibAgent.commandDefinitionIterator()
        
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
                   
    def __setTerminals(self, mib=True, command=True, parameter=True, packet=True):
    
        if command == True:
            term = Terminal()
            # change window size
            print('\x1b[8;{rows};{cols}t'.format(rows=30, cols=100))
            print('\n' + term.bold('Commands to be injected...'))             
            
            Command.createCallbackTerminal()
        
        if parameter == True:
            TMParameter.createParamNotificationTerminal()
            
        if packet == True:
            TMPacket.createPacketNotificationTerminal()
               
    def __createSingleCommand(self, cmdName, counter=None, **cmdKwargs):
 
        # default MIB values
        cmdDef = self.__mibAgent.commandDefinition(cmdName)        
        # Test
        #print('Original command values from MIB: ' + str(cmdDef))
        
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
                print(Fore.RED + Style.BRIGHT + '\nError: Please enter an integer number to create multiple commands.', Style.RESET_ALL)
     
        except Exception as exception: 
            print(Fore.RED + Style.BRIGHT + '\nException during command creation:{}'.format(exception), Style.RESET_ALL)    
                    
    def setCommandParameter(self, command, paramName, **paramKwargs):    
    
        if type(command) == Command:          
            command.setCommandParameter(paramName, **paramKwargs)
            
        elif type(command) == list: 
            for cmd in command:
                cmd.setCommandParameter(paramName, **paramKwargs)
                
    def printCommandInformation(self, *cmds):
       
        # print information of all commands
        if len(cmds) == 0:
            for cmd in Command.getCommandList():
                cmd.printCommandInfo()        

        # print information of command arguments
        else:
            for cmd in cmds:
                if type(cmd) == Command:
                    cmd.printCommandInfo() 
                elif type(cmd) == list:
                    for singleCmd in cmd:
                        singleCmd.printCommandInfo()
                    
    def injectCommands(self, *cmds):
        
        print('\n' + '=' * 95)
        print('=' * 95 + '\n')
        inp = str(input('Do you want to continue with the command injection? (Y/N): ')).lower().strip()
                
        try:
            if inp[0] == 'y':
                self.__inject(*cmds)
                       
            elif inp[0] == 'n':
                self.deregister(1)    
                               
            else:
                print('Invalid input, please try again.')
                return self.injectCommands()
        
        except Exception as exception:  
            print(Fore.RED + Style.BRIGHT + '\nInput error:{}.'.format(exception), Style.RESET_ALL)
            return self.injectCommands()       
    
      
    def __inject(self, *cmds):
        """ Method to inject all commands in global command list. """
        
        print('\n' + '*' * 95 + '\n' + Back.RED + Style.BRIGHT + f"{'Command injection':=^95}" + Style.RESET_ALL)
        print('*' * 95 + '\n')
           
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
                    print(Fore.RED + Style.BRIGHT + '\nError: Please create a command which defines the absolute release time.', Style.RESET_ALL)
                    self.deregister(1)
                    break
        else:
            print(Fore.RED + Style.BRIGHT + '\nError during command injection: Injection list is empty.', Style.RESET_ALL)
                                  
    def setCommandInterlock(self, command, **iLockKwargs):
        
        if type(command) == Command:
            command.setCommandInterlock(**iLockKwargs)
            
        elif type(command) == list:    
            for cmd in command:
                cmd.setCommandInterlock(**iLockKwargs)
        
    def getTMParameter(self, paramName):
        
        parameter = TMParameter(paramName)
        parameter.getParameterFromServer(self.__tmParamAgent.getSingleTMParamMngr())
        parameter.registerParameter()
    
        return parameter
    
    def getTMPacket(self, **packetKwargs):
        
        packet = TMPacket(**packetKwargs)
        packet.setStreamIds(self.__tmPacketAgent.getTimeMngr())
        packet.registerTMpackets()
    
        return packet
    
    def deregister(self, sec):
         
        self.__cmdAgent.deregister(sec)
        
        
        
        