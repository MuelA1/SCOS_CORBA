#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Time module

"""

import datetime

# UTC+0  
def timestamp2SCOSdate(sec, micro):
    
    #timestamp = (sec - 3600) + (micro/1e6)

    timestamp = sec + (micro/1e6)
    dateString = datetime.datetime.fromtimestamp(timestamp).strftime('%Y.%j.%H.%M.%S.%f %ZUTC+0')
       
    #print('\033[1;34;48mSCOS date: ' + dateString + '\033[0m')
    return dateString

# UTC+0   
def timestamp2date(sec, micro):
    
    timestamp = (sec - 3600) + (micro/1e6)     
    # create string out of timestamp
    dateString = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S:%f %ZUTC+0')

    #print('\033[1;34;48mDate: ' + dateString + '\033[0m')
    return dateString

# UTC+0, for SCOS; 
# Example: dateString = "2017-11-22 16:00:00:928"
def date2timestamp(dateString):
    timeStruct = datetime.datetime.strptime(dateString, '%Y-%m-%d %H:%M:%S:%f')

    # timedelta object, UTC + 1 to UTC + 0
    utcDelta = datetime.timedelta(hours = 1)
    # get difference
    timeStruct = timeStruct + utcDelta

    stamp = timeStruct.timestamp()
    
    second = int(stamp)
    micro = datetime.datetime.fromtimestamp(stamp).microsecond
     
    print('Timestamp: {0}; second: {1}; microsecond: {2}'.format(stamp,second,micro))
    return second, micro, stamp
   
# UTC+0, for SCOS; 
# Example: dateString = "2017.326.16.00.00.928"
def scosDate2timestamp(dateString):
    
    # datetime object
    timeStruct = datetime.datetime.strptime(dateString, '%Y.%j.%H.%M.%S.%f')   
    
    # timedelta object UTC + 0 in SCOS
    utcDelta = datetime.timedelta(hours = 1)
    timeStruct = timeStruct + utcDelta
    
    # get timestamp
    stamp = timeStruct.timestamp()
              
    second = int(stamp)
    micro = datetime.datetime.fromtimestamp(stamp).microsecond
 
    print('SCOS timestamp: {0}; second: {1}; microsecond: {2}'.format(stamp,second,micro))
    
    timestamp2date(second, micro)
       
    return second, micro, stamp
