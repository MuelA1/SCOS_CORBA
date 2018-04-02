#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Module contains functions for time convertion (SCOS date and timestamp convertion)

"""

import datetime
import IBASE
  
def timestamp2SCOSdate(sec, micro):
    
    #timestamp = (sec - 3600) + (micro/1e6)
    timestamp = sec + (micro/1e6)
    
    # create string out of timestamp
    dateString = datetime.datetime.fromtimestamp(timestamp).strftime('%Y.%j.%H.%M.%S.%f')
       
    return dateString
  
def timestamp2date(sec, micro):
    
    #timestamp = (sec - 3600) + (micro/1e6)      
    timestamp = sec + (micro/1e6) 
    
    # create string out of timestamp
    dateString = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S:%f')

    return dateString

# Example: dateString = "2017-11-22 16:00:00:928"
def date2timestamp(dateString):
    timeStruct = datetime.datetime.strptime(dateString, '%Y-%m-%d %H:%M:%S:%f')

    # timedelta object, UTC Convertion
    # utcDelta = datetime.timedelta(hours = 1)
    # get difference
    # timeStruct = timeStruct + utcDelta

    # get timestamp
    stamp = timeStruct.timestamp()
    
    second = int(stamp)
    micro = datetime.datetime.fromtimestamp(stamp).microsecond
     
    return IBASE.Time(second, micro, False)
    
# Example: dateString = "2017.326.16.00.00.928"
def scosDate2timestamp(dateString):    
    # datetime object
    timeStruct = datetime.datetime.strptime(dateString, '%Y.%j.%H.%M.%S.%f')   
    
    # timedelta object, UTC Convertion
    # utcDelta = datetime.timedelta(hours = 1)
    # get difference
    # timeStruct = timeStruct + utcDelta
    
    # get timestamp
    stamp = timeStruct.timestamp()
              
    second = int(stamp)
    micro = datetime.datetime.fromtimestamp(stamp).microsecond
          
    return IBASE.Time(second, micro, False)