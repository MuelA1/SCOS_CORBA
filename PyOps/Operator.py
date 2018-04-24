#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Facade, higher-level interface to use different agents and to perform specific tasks

Operator -- describes an interface where every object is created
"""

from MIBAgent import MIBAgent
from CommandAgent import CommandAgent
from Command import Command
from ViewInterfaces import CommandInjectMngrView
from colorama import Fore, Back, Style

class Operator():
    
    # create agent objects
    def __init__(self):
        self.__mibAgent = MIBAgent()
        self.__cmdAgent = CommandAgent()
                            
    # perform agent operations
    def connect(self, ip, port):
        mibMngr = self.__mibAgent.connect(ip, port, self.__mibAgent.getNamingService(), self.__mibAgent.getServerMngrType())
        cmdServerMngr = self.__cmdAgent.connect(ip, port, self.__cmdAgent.getNamingService(), self.__cmdAgent.getServerMngrType())
        
        return [mibMngr, cmdServerMngr]
    
    def initialize(self):
        cmdInjMngrView = self.createViewInterfaces()
        [commandDefIterator,cmdInjMngr] = self.getManagers()
    
        return cmdInjMngrView,commandDefIterator, cmdInjMngr
    
    def createViewInterfaces(self):       
        cmdInjMngrView = self.__cmdAgent.createCmdInjMngrView(CommandInjectMngrView(), 'MngrView')               
        
        return cmdInjMngrView
    
    def getManagers(self):
        commandDefIterator = self.__mibAgent.commandDefinitionIterator()
        cmdInjMngr = self.__cmdAgent.tcInjectMngr()
        
        return commandDefIterator,cmdInjMngr 
    
    def __createSingleCommand(self, cmdName, **cmdKwargs):
 
        # default MIB values
        cmdDef = self.__mibAgent.commandDefinition(cmdName)        
        # Test
        #print('Original command values from MIB: ' + str(cmdDef))
        
        command = Command(cmdDef.m_name, cmdDef.m_description, **cmdKwargs)              
        command.setCommandDef(cmdDef)
        command.setMIBCommandParameters() 
        command.setCommandInjMngr(self.__cmdAgent.getCmdInjMngr())
        command.setCommandServerMngr(self.__cmdAgent._serverMngr)
                             
        return command
           
    def createCommand(self, cmdName, numberOfCommands=0, **cmdKwargs):

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
            print(Fore.WHITE + Back.RED + Style.BRIGHT + '\nError: Please enter an integer number to create multiple commands.', Style.RESET_ALL)
     
    def __setSingleCommandParameter(self, cmdName, paramName, **paramKwargs):
        
        cmdName.setCommandParameter(paramName, **paramKwargs)
        
    def setCommandParameter(self, cmdName, paramName, **paramKwargs):    
    
        if type(cmdName) == Command:
            self.__setSingleCommandParameter(cmdName, paramName, **paramKwargs)
        
        elif type(cmdName) == list: 
            for cmd in cmdName:
                self.__setSingleCommandParameter(cmd, paramName, **paramKwargs)
            
    def printAndVerifyInj(self):
        
        for cmd in Command.getCommandList():
            # use __str__ method later
            cmd.printCommandInfo()
        
        print('\n' + '=' * 99)
        print('=' * 99 + '\n')
        inp = str(input('Do you want to continue with the command injection? (Y/N): ')).lower().strip()
                
        try:
            if inp[0] == 'y':
                self.__injectCommands()
                       
            elif inp[0] == 'n':
                self.deregister(1)    
                               
            else:
                print('Invalid input, please try again.')
                return self.printAndVerifyInj()
        
        except Exception as exception:  
            print(Fore.WHITE + Back.RED + Style.BRIGHT + '\nInput error: {}.'.format(exception), Style.RESET_ALL)
            return self.printAndVerifyInj()
        
    def __injectCommands(self):
        """ Method to inject all commands in global command list. """
        
        print('\n' + '*' * 99 + '\n' + Back.RED + Style.BRIGHT + f"{'Command injection':=^99}" + Style.RESET_ALL)
        print('*' * 99 + '\n')
        
        cmdList = Command.getCommandList()
        
        # check if there is a previous command with absolute release time to calculate relative release time
        absReleaseTime = False
        
        if len(cmdList) > 0:
            for cmd in cmdList:
                if cmd.relReleaseTime is None:                   
                    cmd.injectCommand()
                    if absReleaseTime == False:
                        absReleaseTime = True
                        
                elif absReleaseTime == True:
                    # start thread to get relative release time from previous command
                    cmd.startReleaseTimeThread(cmdList[cmd.getInstCount() - 2])
                    
                else:
                    print(Fore.WHITE + Back.RED + Style.BRIGHT + '\nError: Please create a command which defines the absolute release time.', Style.RESET_ALL)
                    self.deregister(1)
                    break
        else:
            print(Fore.WHITE + Back.RED + Style.BRIGHT + '\nError during command injection: Injection list is empty.', Style.RESET_ALL)
        
    def deregister(self, sec):
         
        self.__cmdAgent.deregister(sec)