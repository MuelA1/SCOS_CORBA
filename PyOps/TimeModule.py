#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Module contains functions for time convertion (SCOS date and timestamp convertion)

"""

import time
import sys
import datetime
import IBASE
#import threading

def ibaseTime2stamp(ibaseTime):
    
    timestamp = ibaseTime.m_sec + (ibaseTime.m_micro/1e6)
    return timestamp

def stamp2ibaseTime(stamp):
    
    if stamp is not None:
        second = int(stamp)
        micro = datetime.datetime.fromtimestamp(stamp).microsecond  
        
        return IBASE.Time(second, micro, False)
    
def timestamp2SCOSdate(ibaseTime):
    
    if str(ibaseTime) == str(IBASE.Time(0,0,False)):
        return 'ASAP'
    
    elif ibaseTime is not None:
               
        timestamp = ibaseTime2stamp(ibaseTime)
        # create string out of timestamp
        dateString = datetime.datetime.fromtimestamp(timestamp).strftime('%Y.%j.%H.%M.%S.%f')
           
        return dateString
  
def timestamp2date(ibaseTime):
       
    timestamp = ibaseTime2stamp(ibaseTime)
    # create string out of timestamp
    dateString = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S:%f')

    return dateString

# Example: dateString = "2017-11-22 16:00:00:928"
def date2timestamp(dateString):
    
    timeStruct = datetime.datetime.strptime(dateString, '%Y-%m-%d %H:%M:%S:%f')

    # get timestamp
    stamp = timeStruct.timestamp()    
    ibaseTime = stamp2ibaseTime(stamp)
    
    return ibaseTime
    
# Example: dateString = "2017.326.16.00.00.928"
def scosDate2timestamp(dateString):    
    
    # datetime object
    timeStruct = datetime.datetime.strptime(dateString, '%Y.%j.%H.%M.%S.%f')   
        
    # get timestamp
    stamp = timeStruct.timestamp()
    ibaseTime = stamp2ibaseTime(stamp)       

    return ibaseTime

def relativeReleaseTime(releaseTime, relativeTime):
    
    # release time is IBASE.Time 
    if type(releaseTime) == IBASE.Time:
        
        releaseTimestamp = releaseTime.m_sec + (releaseTime.m_micro/1e6)
        releaseTimeString = datetime.datetime.fromtimestamp(releaseTimestamp).strftime('%Y.%j.%H.%M.%S.%f')
        releaseTimeStruct = datetime.datetime.strptime(releaseTimeString, '%Y.%j.%H.%M.%S.%f')
     
    # release time is time string    
    else:    
        releaseTimeStruct = datetime.datetime.strptime(releaseTime, '%Y.%j.%H.%M.%S.%f')
  
    # relative time
    relativeTimeStruct = datetime.datetime.strptime(relativeTime, '%H.%M.%S')   
    timeDelta = datetime.timedelta(hours=relativeTimeStruct.hour, minutes=relativeTimeStruct.minute, seconds=relativeTimeStruct.second)
 
    # new release time
    newReleaseTimeStruct = releaseTimeStruct + timeDelta
    newReleaseTimestamp = newReleaseTimeStruct.timestamp()
      
    ibaseTime = stamp2ibaseTime(newReleaseTimestamp) 
    #timeThread = threading.Thread(target=timeCounter, args=(relativeTimeStruct.second,))
    #timeThread.start()   
    
    #timeCounter(relativeTimeStruct.second)
    
    return ibaseTime
       
def timeCounter(sec):
    
    print('\nNext injection in: ')
    while sec:
        mins, secs = divmod(sec, 59)
        timeformat = '{:02d}:{:02d}'.format(mins, secs)
        sys.stdout.write('\r' + timeformat + '\r')
        time.sleep(1)
        sec -= 1
    sys.stdout.write('\r00:00 \r \n')
    #currThread = threading.currentThread()
    #currThread.do_run = False
    #currThread.do_run = False
    