#!/usr/bin/env python3
###
#   Python functions do the following:
#
#   A. Parse following NMEA strings for GPS Data
#
#       1. parseGxGGA: to parse GGA (x = P for GPS, N for GNSS) sentence for:
#           - Time, Altitude (m), # of Satellites
#
#       2. parseGxRMC: to parse RMC (x = P for GPS, N for GNSS) sentence for:
#           - Date, Latitude, Longitude, Speed and Heading
#       
#       3. parseGxGSA: tp parse GSA (x = P for GPS, N for GNSS) sentence for:
#           - Horizontal Dilution of Precision (HDOP)
#
#   By J. Parikh (CAMP) / July, 2017
#   Initial Ver 1.0
###

import string

###
#   parse $GxGGA sentence... x = P GPS, N = GNSS
###

def parseGxGGA(NMEAData,GPSTime,GPSSats,GPSAlt,GGAValid):   

###
#       Input:  NMEAData
#       Output: GPSTime, GPSSats, GPSAlt, GGAValid
###
    
##### -------------
#
#       Here's the $GxGGA sentence decoding logic.
#
#       If there was a checksum problem (missing or mismatch), NMEAData is cleared.
#       That will cause all processing to be skipped because there will be no match
#       in the first 5 columns.
#
#       GPGGA,010049.000,3805.0524,N,12212.4962,W,2,18,0.7,75.3,M,-24.5,M,0000,0000*47
#         0         1        2     3      4     5 6  7  8    9  10  11  12 13   14 
#       GxGGA        Global Positioning System Fix Data
#       1   - 123519.000    Fix taken at 12:35:19 UTC
#       2,3 - 4807.038,N    Latitude 48 deg 07.038' N
#       4,5 - 01131.000,E   Longitude 11 deg 31.000' E
#       6   - Fix quality:  0 = invalid
#                           1 = GPS fix (SPS)
#                           2 = DGPS fix
#                           3 = PPS fix
#                           4 = Real Time Kinematic
#			    5 = Float RTK
#                           6 = estimated (dead reckoning) (2.3 feature)
#	        	    7 = Manual input mode
#			    8 = Simulation mode
#       7     - 18          Number of satellites being tracked
#       8     - 0.7         Horizontal dilution of position
#       9,10  - 75.3,M      Altitude, Meters, above mean sea level
#       11,12 - -24.5,M     Height of geoid (mean sea level) above WGS84 ellipsoid
#       13    -             (empty field)   time in seconds since last DGPS update
#       14    -             (empty field) DGPS station ID number
#       *47   -             the checksum data, always begins with *
#
##### -----------------

###
#       Constants...$GxGGA (GPGGA or GNGGA)
###
 
    GGAGMT      =  1            # Time in GMT in GGA
    GGAFIXQUAL  =  6            # Fix Quality
    GGASATS     =  7            # # of satellites
    GGAALT      =  9            # Altitude
    GGAALTUN    = 10            # Altitude Units
    GGAValid    = False         # Set init value

###
#       Break up the input sentenceGPSTime,GPSLat,GPSLon,GPSFixQual,GPSSats,GPSHDOP,GPSAlt
###
    s = NMEAData.split(',')
    
###
#       Get time in GMT
###


    if int(s[GGAFIXQUAL]) > 0:  #Valid GPS data
        GGAValid = True         #Set valid flag

        GPSTime = s[GGAGMT][0:2]+":"+s[GGAGMT][2:4]+":"+s[GGAGMT][4:6]+":"+s[GGAGMT][7:9]    
###
#       Get # of satellites        
### 
        GPSSats = int(s[GGASATS])

###        
#       Get altitude in meters
###
        GPSAlt      = float(s[GGAALT])
        
    return GPSTime,GPSSats,GPSAlt,GGAValid


### ------ END of GxGGA --------

###
#   parse $GxRMC sentence...
###

def parseGxRMC(NMEAData,GPSDate,GPSLat,GPSLon,GPSSpeed,GPSHeading,RMCValid):    

###
#       Input:  NMEAData
#       Output: GPSDate, GPSLat, GPSLon, GPSSpeed (ground speed in knots), GPSHeading (Angle)
####
       
##### ----------
#       GNRMC,222218.000,A,3805.047687,N,12212.496518,W,0.02,224.41,201116,,,D
#         0     1        2     3       4      5       6   7    8       9
#       GPRMC,010046.000,A,3805.052482,N,12212.496245,W,0.00,354.54,061116,,
#       Where:
#       0     RMC           Recommended Minimum sentence C
#       1     123519        Fix taken at 12:35:19 UTC
#       2     A             Status A=active or V=Void. (Valid or Invalid)
#       3,4   4807.038,N    Latitude 48 deg 07.038' N
#       5,6   01131.000,E   Longitude 11 deg 31.000' E
#       7     022.4         Speed over the ground in knots
#       8     084.4         Track angle in degrees True
#       9     230394        Date - 23rd of March 1994
#       10,11 003.1,W       Magnetic Variation, Direction
#       12    *6A           The checksum data, always begins with *
#       Unhandled
###### ----------

###
#       Constants...$GxRMC
###
    RMCSTAT     = 2         # Status A=Valid, V=Invalid
    RMCLAT      = 3         # Latitude in GGA
    RMCLATNS    = 4         # Either N(+) or S(-)
    RMCLON      = 5         # Longitude in GGA
    RMCLONEW    = 6         # Either E(+) or W(-)
#
    RMCKNOTS    = 7         #Speed in Knots
    RMCANGLE    = 8         #Direction angle
    RMCDATE     = 9         #Date from GPRMC
    RMCValid    = False     #Init flag

###        
#       Break up the input sentence
#       Check for RMCDATE
#       Check for RMCSTAT, process the following only if Valid...
###
    s = NMEAData.split(',')
    if len(s) >= RMCDATE and s[RMCSTAT] == "A":     # Be sure it is there before using it
        RMCValid = True                             #Set valid flag
        GPSDate = '20' + s[RMCDATE][4:6]  + '/' + s[RMCDATE][2:4]  + '/' + s[RMCDATE][0:2]         
                                        

###
#       Get Latitude and convert to decimal degrees
###
        lats = float(s[RMCLAT])
        p1  = int(lats/100.)
        lat = (p1+(lats-p1*100)/60.0)
        if s[RMCLATNS] == "S":
            lat = -lat
        pass                                #null stmt end of if        
        GPSLat = lat   
###
#       Get longitude and convert to decimal degrees        
###       
        lng = float(s[RMCLON])
        p1  = int(lng/100.)
        lon = (p1+(lng-p1*100)/60.0)
        if s[RMCLONEW] == "W":
            lon = -lon
        pass                                #null stmt, end of if              
        GPSLon = lon        

###
#       Get speed and heading...
###

        GPSSpeed = float(s[RMCKNOTS])       # Speed in Knots
        if s[RMCANGLE] != '':
            GPSHeading  = float(s[RMCANGLE])# Direction angle
        pass

###
#   Return to caller with value...

    return GPSDate,GPSLat,GPSLon,GPSSpeed,GPSHeading,RMCValid    #end of GxRMC (GPRMC or GNRMC)

### ------ END of GxRMC --------

###
#   parse $GxGSA sentence...
###

def parseGxGSA(NMEAData,GPSHdop,GSAValid):    

###
#       Input:  NMEAData
#       Output: GPSHDOP,GSAStat
####
       
##### ----------
#       GPGSA,A,3,17,28,19,06,01,03,22,24,51,30,11,,1.79,0.98,1.50*09
#          0  1 2  3  4  5  6  7  8  9 10 11 12 13   15   16   17 
#       GNGSA,A,3,67,66,76,82,77,83,68,,,,,,1.2,0.7,1.0
#       GSA     Satellite status
#       1 -     A       Auto selection of 2D or 3D fix (M = manual) 
#       2 -     3       3D fix - values include: 1 = no fix
#                       2 = 2D fix
#                       3 = 3D fix
#       4-5...  PRNs of satellites used for fix (space for 12) 
#       15 -    1.79    PDOP (dilution of precision) 
#       16 -    0.98    Horizontal dilution of precision (HDOP) 
#       17 -    1.50    Vertical dilution of precision (VDOP)
#       *39     the checksum data, always begins with *
###### ----------

###
#       Constants...$GxGSA
###
    GSAStat     = 2         # Fix value, 1 = Nofix (invalid)
    GSAHDOP     = 16        # HDOP
    GSAValid    = False     # Init value
    
###        
#       Break up the input sentence
###
    s = NMEAData.split(',')

    if int(s[GSAStat]) > 1: # Valid data
        GSAValid = True     # Set valid flag
        GPSHdop = float(s[GSAHDOP])
    pass                    # end of if

    return GPSHdop,GSAValid #end of GxGSA (GPGSA or GNGSA)



