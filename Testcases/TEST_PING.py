#!/usr/bin/env python3
# -*- coding: utf-8 -*-
''' TEST_PING

This is a minimal example test script using pyops module to send ping command
'''
# Required for now
import sys
sys.path.append('AAIDL')

# This is the Operator Module
from pyops import Operator

with Operator() as op:
    
    # Set up operator
    #op.setVerbosity(2)
    op.setVerbosity(1)
    
    # Logging level 1 (critical info only) - 5 (detailed information)
    op.configLogging('pyops_logfile.txt', 5)

    op.setGlobalCommandTimeout(75) 
    op.setGlobalPacketTimeout(25)
    
    op.connect('192.168.197.23', 20000)
    op.initialize(terminal='xfce4-terminal')

    # This is the ping command
    PING = op.createCommand('PING')
    op.printCommandInformation(PING)
    
    # This is the packet we want to wait for
    PING_REPLY = op.registerTMPacket(7800)
    
    # Send command and verify reply reception
    op.injectCommand(PING)
    if PING_REPLY.verifyPacketReception(timeout=22) != 'RECEIVED':
        print('Ping test failed')   
        op.exitScr(1)
    else:
        print('Ping test success')   
            