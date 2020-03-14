#!/usr/bin/env python3
###
#   This module acquires driven vehicle path GPS/GNSS data
#   Ublox-EVKM8N GPS receiver is connected using USB to data acquisition system
#   Received NMEA sentence is parsed and required data elements are extracted
#
#   The Ublox receiver is connected on virtual serial port COM7 at
#   115200 baud rate.
#
#   Developed By J. Parikh(CAMP) / July, 2017
#   Initial Ver 1.0
#
###

###
#   Import python built-in functions.
###

import  time                                    #system time
import  datetime                                #current system date and time
import  serial                                  #serial communication
import  sys                                     #system functions
import  io                                      #serial i/o function
import  string                                  #string functions
import  msvcrt                                  #used for keyboard input in asynchronous mode
import  csv                                     #CSV file read/write

from    serial import SerialException           #serial port exception

###
#   Following are for parsing NMEA string
###

from parseNMEA      import parseGxGGA           #parse GGA for Time, Alt, #of Sats
from parseNMEA      import parseGxRMC           #parse RMC for Date, Lat, Lon, Speed, Heading
from parseNMEA      import parseGxGSA           #parse GSA for Hdop


###
#   Local variables...
###

GPSRate     = 10                                #GPS data rate in Hz
GPSDate     = ''                                #GPS Date
GPSTime     = ''                                #GPS Time
prevGPSTime = ''                                #previous GPS Time
GPSSats     = 0                                 #No. of Satellites
GPSLat      = 0.0                               #Latitude in degrees in decimal
GPSLon      = 0.0                               #Longitude in degrees in decimal
GPSAlt      = 0.0                               #Altitude in meters
GPSSpeed    = 0.0                               #Speed in m/s
GPSHeading  = 0.0                               #Heading in degrees
GPSHdop     = 0.0                               #Horizontal dilution of precision
GGAValid    = False                             #Init value
RMCValid    = False                             #Init value
GSAValid    = False                             #Init value



print ("\n\n *** CAMP V2I-SA Work Zone Mapping - Vehicle Path Data Acquisition v1.0 ***\n")

###
#
#   Open serial com port...U-Blox opens COM7 as virtual port on USB...
#
###


#ser             = serial.Serial()
#ser.baudrate    = 115200                        #baud rate
#ser.port        = 'COM7'                        #com port
#ser.timeout     = 1                             #required

try:
    portNum     = 'COM3'
    baudRate    = 4800
    timeOut     = 1
    ser         = serial.Serial(port=portNum, baudrate=baudRate, timeout=timeOut)       #open serial port

except SerialException:
    print("                 *** GPS Receiver NOT Connected ***\n")
    print(" *** Connect u_blox GPS receiver to the USB port as "+portNum+" and try again!!!\n")
    input('Enter a key...')
    sys.exit(0)

print("     *** Serial port configured as: \n")
print("     *** Serail Port: "+ser.port+", Baud: "+str(ser.baudrate)+"   ***\n")
print("     *** GPS Data Rate: "+str(GPSRate)+" Hz   ***\n\n")

###
#   EOL is not supported in PySerial for readline() in Python 3.6.
#   must use sio
###

sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))             


###
#   Get current date and time...
###

cDT = datetime.datetime.now().strftime("%Y%m%d_")+time.strftime("%H%M%S")

###
#   Open output file for data logging...
###

##outDir      = "C:\CAMP\V2I Projects\V2I - SA Extension 2\Task 14 - WZ Mapping\Test Data\Mar-2018"
##outDir      = "C:\CAMP\V2I Projects\V2I - SA Extension 2\Task 14 - WZ Mapping\Test Data\Apr-2018"
outDir      = "./WZ_VehPathData"
dataOutFile = outDir + "/WZ_Path_Data_"+cDT+".csv"

print("     *** Vehicle Path Data File: "+dataOutFile+"\n")

###
#   Open outFile for csv write...
#   make sure newline is set to null, otherwise will get extra cr.. 
###

outFile     = open(dataOutFile,"w",newline='')
writeData   = csv.writer(outFile)

###
#   Write Title...
###

titleLine = "GPS Date/Time","# of Sats","HDOP","Latitude","Longitude","Altitude(m)","Speed(m/s)","Heading(Deg)","Marker","Value"
writeData.writerow(titleLine)

###
#   Few inits...
###

kt          = 0                                 #local count variable
dataLog     = False                             #data logging off
outStr      = ''                                #output string in "tuple"
marker      = ['',0]                            #marker from key press
appRunning  = True                              #set application running to TRUE
gotRefPt    = False                             #got Ref. Point
gotLCRP     = False                             #if no RP yet, set RP and LC the same data point
gotMarker   = False                             #marker key pressed
wpStat      = False                             #workers not present
laneStat    = [True,True,True,True,True,True,True,True,True,True] #all lanes are open (default)
                                                #pressing the same lane # key will toggle the from close to open

###
#   Print message for user for use of this application
###


print ( "\n   *** Use following keys to record following markers in the vehicle path data log file ***\n" \
        "         r         - to mark Reference Point (Start of WZ) \n" \
        "         1/2/3...  - to toggle lane closed/open marker (includes reference point if ref point is not marked before) \n" \
        "         w         - to toggle workers present/not present marker \n" \
        "         s         - to toggle start/stop data logging \n" \
        "         Esc       - End data logging and quit the application \n\n")

###
#   Do until ESC is pressed
###

while (appRunning):
    NMEAData = sio.readline()                   #Read NMEA string from serial port COM7
    #print (NMEAData)


###
#   for more detail on NMEA sentence visit: ---  http://www.gpsinformation.org/dale/nmea.htm  ---
###

###
#       --- Parse GGA String---
###
    
    if NMEAData[0:6] == '$GPGGA' or NMEAData[0:6] == "$GNGGA":
        GGA_out = parseGxGGA(NMEAData,GPSTime,GPSSats,GPSAlt,GGAValid)

        if GGA_out[3] == True:         
            GPSTime = GGA_out[0]
            GPSSats = GGA_out[1]
            GPSAlt  = GGA_out[2]
        pass
        print ("GGA: ", GPSTime, GPSSats,GPSAlt)
    pass

###
#       --- Parse RMC ---
###
  
    if NMEAData[0:6] == "$GPRMC":
        RMC_out = parseGxRMC(NMEAData,GPSDate,GPSLat,GPSLon,GPSSpeed,GPSHeading,RMCValid)

        if RMC_out[5] == True:
            GPSDate     = RMC_out[0]
            GPSLat      = RMC_out[1]
            GPSLon      = RMC_out[2]
            GPSSpeed    = RMC_out[3]*(1852.0/3600.0)        #Knot = 1.852 km/hr, Convert to m/s
            GPSHeading  = RMC_out[4]
        pass
        print ("RMC Output:", RMC_out)
    pass
        
###
#       --- Parse GSA ---
###
  
    if NMEAData[0:6] == "$GPGSA":
        GSA_out = parseGxGSA(NMEAData,GPSHdop,GSAValid)
        if GSA_out[1] == True:
            GPSHdop = GSA_out[0]
        pass
        print ("GSA Hdop:", GSA_out)
    pass
###                        
#       Check for key pressed...
#
#       s - Start/stop data logging
#       r - Ref Point   OR   1/2/3 (lane number) to mark ref point at the same location as start of lane closure
#       w - Toggle workers are present/not present marker
#       1/2/3... - Togle selected lane close/open marker,
#       Esc - End data logging and stop prog
#
#           .....
#
###

    if msvcrt.kbhit():                                  #see if key pressed
        key = bytes.decode(msvcrt.getch())              #get key pressed
        ##print ("key pressed: ", key)
  
        if key == 's' or key == 'S':                    #start/stop data logging
            dataLog = not dataLog                       #toggle logging
            markerStr = "*** Marker - Data Log:"+str(dataLog)
            print (markerStr)
            marker[0] = "Data Log"
            marker[1] = dataLog
            gotMarker = True
            ##writeData.writerow (markerStr)            #write complete outStr with marker at the end of kbhit check
        pass                                            #end of data log start/stop
            
        if (key == 'r' or key == 'R') and gotRefPt == False: #Mark reference point
            markerStr = "*** Marker - Reference Point @ "+str(GPSLat)+", "+str(GPSLon)+","+str(GPSAlt)
            print (markerStr)
            marker[0] = "RP"                            #reference point
            marker[1] = ''
            gotRefPt = True                             #got the reference point
            gotMarker = True                            #got the marker
            ##writeData.writerow (markerStr)            #write complete outStr with marker at the end of kbhit check
        pass                                            #end of ref point


        if key == 'w' or key == 'W':                    #workers present/not present
            wpStat = not wpStat                         #Toggle wp/np
            markerStr = "*** Marker - Workers Present: "+str(wpStat)
            print (markerStr)
            marker[0] = "WP"                            #WP marker
            if gotRefPt == False:
                marker[0]="WP+RP"                       #WP+ref pt
                gotRefPt = True                         #gotRefPT True    
            marker[1] = wpStat
            ###marker[1] = int(wpStat)                  #convert boolean WP marker to 0/1 ... NOT NOW...

            gotMarker = True
            ##writeData.writerow (markerStr)            #write complete outStr with marker at the end of kbhit check
        pass                                            #end of data log start/stop

    
        if key > '0' and key <= '9':                    #Mark lane# closed point
            ##print ("Key Pressed: ", key)
            lane = int(key)                             #lane number
            laneStat[lane] = not laneStat[lane]         #Lane open status (T or F)
            lc = "LC"                                   #set lc to "LC" - Lane Closed
            if laneStat[lane] == True:
                lc = "LO"                               #toggle lane status to Lane Open
            if gotRefPt == False:                       #if ref pt has not been marked yet
                lc = lc + "+RP"                         #lc + ref. pt
                gotRefPt = True                         #set to true
            pass
        
            markerStr = "*** Marker - Lane: "+str(key)+" "+str(lc)+" @ "+str(GPSLat)+", "+str(GPSLon)+","+str(GPSAlt)
            print (markerStr)
            marker[0] = lc 
            marker[1] = key                
            gotMarker = True
            ##writeData.writerow (markerStr)            #write complete outStr with marker at the end of kbhit check
        pass                                            #end of LC marker

        if key == '\x1b':                               #Esc key pressed... Quit the logging routine...
            markerStr = "*** Marker - Application Stopped"
            print (markerStr)
            marker[0] = "App Ended"
            marker[1] = ""
            gotMarker = True
            appRunning = not appRunning
        pass                                            #end of Esc key

        if gotMarker == True:
            time_date = GPSDate+":"+GPSTime
            outStr = time_date,GPSSats,GPSHdop,GPSLat,GPSLon,GPSAlt,GPSSpeed,GPSHeading,marker[0],marker[1]       #added marker
            writeData.writerow(outStr)                  #write to file
            gotMarker = not gotMarker
            marker = ['','']                            #reset marker
        pass                                            #end of marker tag
    pass                                                #end of key pressed         
###
#       Construct output string including marker based on key hit and write to file..    
#       Log data to csv file...
###

    if GPSTime != prevGPSTime and GPSDate != '':        #log data only if next sentence(GPSTime) is different from the previous
        
        time_date = GPSDate+":"+GPSTime
        outStr  = time_date,GPSSats,GPSHdop,GPSLat,GPSLon,GPSAlt,GPSSpeed,GPSHeading,marker[0],marker[1]            #added marker
        ##print (outStr)
        
        if dataLog == True:
            writeData.writerow(outStr)                  #write to file
            marker = ['','']                            #reset marker
        pass
                       
        prevGPSTime = GPSTime                           #save current GPSTime
    pass                                                #end of writing outStr

          
ser.close()                                             #end of data acquisition and logging
outFile.close()

input("Press Enter to continue...")




 
