#!/usr/bin/env python3
###
#   This module acquires driven vehicle path GPS/GNSS data
#   Ublox-EVKM8N GPS receiver is connected using USB to data acquisition system
#   Received NMEA sentence is parsed and required data elements are extracted
#
#   The Ublox receiver is connected on virtual serial port COM7 at
#   115200 baud rate.
#
#   Supports uo to 8 lanes for marking Lane closures and lane open markers...
#
#   Developed By J. Parikh(CAMP) / July, 2017
#   Initial Ver 1.0
#
###

###
#   Import python built-in functions.
###

import      time                                    #system time
import      datetime                                #current system date and time
import      serial                                  #serial communication
import      sys                                     #system functions
import      subprocess
import      io                                      #serial i/o function
import      string                                  #string functions
import      csv                                     #CSV file read/write
import      os.path
import      math
import      json
import      serial.tools.list_ports                      #used to enumerate COMM ports

from        serial import SerialException           #serial port exception

###
#   thread for tkinter for text window...
###

from    tkinter     import *
from    tkinter     import      messagebox

from PIL import ImageTk, Image

###
#   Following are for parsing NMEA string
###

from parseNMEA      import parseGxGGA           #parse GGA for Time, Alt, #of Satellites
from parseNMEA      import parseGxRMC           #parse RMC for Date, Lat, Lon, Speed, Heading
from parseNMEA      import parseGxGSA           #parse GSA for Hdop

###
#
#   ------------------  Start the Main Func... ----------------------
#
###

def startMainFunc():
    global  appRunning                          #boolean
    if (appRunning):
        logMsg('App running, starting getNMEA_String loop')
        getNMEA_String()                        #Get NMEA String and process it until 'appRunning is True...'
    else:
        logMsg('App not running, exiting')
    

###
#
#   ------------------  END of the Main Func... --------------------------------------
#

def configRead():
    global wzConfig
    file = local_config_path
    if os.path.exists(file):
        cfg = open(file, 'r+')
        wzConfig = json.loads(cfg.read())
        getConfigVars()
        update_config(cfg)
        cfg.close()

###
# ----------------- End of config_read --------------------
###
#
#   Following user specified values are read from the WZ config file specified by user in WZ_Config_UI.pyw...
#
#   WZ Configuration file is parsed here to get the user input values for used by different modules/functions...
#
#   Added: Aug. 2018
#
### -------------------------------------------------------------------------------------------------------

def getConfigVars():

###
#   Following are global variables are later used by other functions/methods...
###

    global  vehPathDataFile                                 #collected vehicle path data file
    global  sampleFreq                                      #GPS sampling freq.

    global  roadName

    global  totalLanes                                      #total number of lanes in wz
    global  laneWidth                                       #average lane width in meters
    global  lanePadApp                                      #approach lane padding in meters
    global  lanePadWZ                                       #WZ lane padding in meters
    global  dataLane                                        #lane used for collecting veh path data
    global  wzDesc                                          #WZ Description

    global  speedList                                       #speed limits
    global  c_sc_codes                                      #cause/subcause code

##
#   WZ schedule
##

    global  wzStartDate                                     #wz start date
    global  wzStartTime                                     #wz start time    
    global  wzEndDate                                       #wz end date
    global  wzEndTime                                       #wz end time
    global  wzDaysOfWeek                                    #wz active days of week

    global  wzStartLat                                     #wz start date
    global  wzStartLon                                     #wz start time    
    global  wzEndLat                                       #wz end date
    global  wzEndLon                                       #wz end time


###
#   Get collected vehicle path data point .csv file name from user input saved in wz config
###

###
#   Convert str from the config file to proper data types... VERY Important...
###

###
#   Get sampling frequency...
###

    sampleFreq      = int(wzConfig['SERIALPORT']['DataRate'])           #data sampling freq

###
#   Get INFO...
###

    roadName        = wzConfig['INFO']['RoadName']

###
#   Get LANE relevant information...
###

    totalLanes      = int(wzConfig['LANES']['NumberOfLanes'])           #total number of lanes in wz
    laneWidth       = float(wzConfig['LANES']['AverageLaneWidth'])      #average lane width in meters
    lanePadApp      = float(wzConfig['LANES']['ApproachLanePadding'])   #approach lane padding in meters
    lanePadWZ       = float(wzConfig['LANES']['WorkzoneLanePadding'])   #WZ lane padding in meters
    dataLane        = int(wzConfig['LANES']['VehiclePathDataLane'])     #lane used for collecting veh path data
    wzDesc          = wzConfig['LANES']['Description']                  #WZ Description

###
#   Get SPEED information...
###

    speedList       = wzConfig['SPEED']['NormalSpeed'], wzConfig['SPEED']['ReferencePointSpeed'], \
                      wzConfig['SPEED']['WorkersPresentSpeed']              
###
#   Get WZ CAUSE/SUBCAUSE Codes... Entered by the User
#
#   Cause code - 3 = Roadworks, Subcause code - (1=..., 2=..., 4=Short term stationary, 5= ... upto 255)
###

    c_sc_codes      = [int(wzConfig['CAUSE']['CauseCode']), int(wzConfig['CAUSE']['SubCauseCode'])]

###
#   Get WZ SCHEDULE Information...
###

    wzStartDate     = wzConfig['SCHEDULE']['WZStartDate']
    wzStartTime     = wzConfig['SCHEDULE']['WZStartTime']
    wzEndDate       = wzConfig['SCHEDULE']['WZEndDate']
    wzEndTime       = wzConfig['SCHEDULE']['WZEndTime']
    wzDaysOfWeek    = wzConfig['SCHEDULE']['WZDaysOfWeek']

    wzStartLat      = wzConfig['LOCATION']['WZStartLat']
    wzStartLon      = wzConfig['LOCATION']['WZStartLon']
    wzEndLat        = wzConfig['LOCATION']['WZEndLat']
    wzEndLon        = wzConfig['LOCATION']['WZEndLon']

    if wzStartDate == '':                                               #wz start date and time are mandatory
        wzStartDate = datetime.datetime.now().strftime('%Y-%m-%d')
        wzStartTime = time.strftime('%H:%M')
    pass


def update_config(cfg):
    global dataOutFile
    
    dataOutFileName = 'path-data--' + wzDesc + '--' + roadName + '.csv'
    dataOutFile = outDir + '/' + dataOutFileName
    cfg.truncate(0)
    cfg.seek(0)
    wzConfig['FILES']['VehiclePathDataDir'] = os.path.abspath(outDir).replace('\\', '/')
    wzConfig['FILES']['VehiclePathDataFile'] = dataOutFileName
    cfg.write(json.dumps(wzConfig, indent='    '))


#
#   ------------------  Process non blocking key press event... ----------------------
#
###

def keyPress(event):

    global  appRunning

    if appRunning == True:
    
        if event.keysym == 'Escape':
            gotKey = 'Esc'
        pass
    
        gotKey = event.char
        gotBtnPress(gotKey)                                         #gotBtnPress invokes processKeyPress
        ###processKeyPress(gotKey)                                  #Function to process key pressed...
    pass                                                            #only if the app is running...        


###
#
#   -------------------  END OF keyPress...  ----------------------------------------------
#
#   
#   -------------------  getNMEA_String...  ---------------------------------------------------------------------
#
###
#   Get and Parse NMEA String...
#
#   Do until ESC is pressed...  
###

def getNMEA_String():

###
#   Global variables...
###

    global      sio                                 #serial io
    global      GPSTime, GPSDate, prevGPSTime       #time, date and prev. GPS time
    global      keyMarker, dataLog                  #key marker and data log
    global      appRunning                          #until Esc is pressed
    global      GPSLat, GPSLon, GPSAlt              #needed for ref. pt, lane state and workers present locations


###
#   Local variables...
###

    GPSRate     = 10                                #GPS data rate in Hz
    #GPSDate     = ''                                #GPS Date
    #GPSTime     = ''                                #GPS Time
    #prevGPSTime = ''                                #previous GPS Time
    GPSSats     = 0                                 #No. of Satellites
    #GPSLat      = 0.0                               #Latitude in degrees in decimal
    #GPSLon      = 0.0                               #Longitude in degrees in decimal
    #GPSAlt      = 0.0                               #Altitude in meters
    GPSSpeed    = 0.0                               #Speed in m/s
    GPSHeading  = 0.0                               #Heading in degrees
    GPSHdop     = 0.0                               #Horizontal dilution of precision
    GGAValid    = False                             #Init value
    RMCValid    = False                             #Init value
    GSAValid    = False                             #Init value
    prevDistance = 0
    pi = 3.14159
   

    while (appRunning):                             #continue reading and processing NMEA string while TRUE
        NMEAData = sio.readline()                   #Read NMEA string from serial port COM7
        root.update()
        #print (NMEAData)

###
#
#       for more detail on NMEA sentence visit: ---  http://www.gpsinformation.org/dale/nmea.htm  ---
#
#       --- Parse GGA String---
#
###
    
        if NMEAData[0:6] == '$GPGGA' or NMEAData[0:6] == '$GNGGA':
            GGA_out = parseGxGGA(NMEAData,GPSTime,GPSSats,GPSAlt,GGAValid)

            if GGA_out[3] == True:
                GPSTime = GGA_out[0]
                GPSSats = GGA_out[1]
                GPSAlt  = GGA_out[2]
            pass
            #print ('GGA: ', GPSTime, GPSSats,GPSAlt)
        pass

###
#       --- Parse RMC ---
###
  
        if NMEAData[0:6] == '$GPRMC':
            RMC_out = parseGxRMC(NMEAData,GPSDate,GPSLat,GPSLon,GPSSpeed,GPSHeading,RMCValid)

            if RMC_out[5] == True:
                GPSDate     = RMC_out[0]
                GPSLat      = RMC_out[1]
                GPSLon      = RMC_out[2]
                GPSSpeed    = RMC_out[3]*(1852.0/3600.0)    #Knot = 1.852 km/hr, Convert to m/s
                GPSHeading  = RMC_out[4]
            pass
            #print ('RMC Output:', RMC_out)
        pass
        
###
#       --- Parse GSA ---
###

        if NMEAData[0:6] == '$GPGSA':
            GSA_out = parseGxGSA(NMEAData,GPSHdop,GSAValid)
            if GSA_out[1] == True:
                GPSHdop = GSA_out[0]
            pass
            #print ('GSA Hdop:', GSA_out)
        pass
        
        if dataLog:
            distanceToEndPt = round(gps_distance(GPSLat*pi/180, GPSLon*pi/180, wzEndLat*pi/180, wzEndLon*pi/180))
            if distanceToEndPt < 20: #Leaving Workzone
                logMsg('-------- Exiting Work Zone (by location, distance=' + str(distanceToEndPt) + ') -------')
                stopDataLog()
                #appRunning = False
            distanceToStartPt = round(gps_distance(GPSLat*pi/180, GPSLon*pi/180, wzStartLat*pi/180, wzStartLon*pi/180))
            if not gotRefPt and distanceToStartPt > prevDistance: #Auto mark reference point
                logMsg('-------- Auto Marking Reference Point (by location, distance=' + str(distanceToStartPt) + ') -------')
                markRefPt()
            prevDistance = distanceToStartPt

        else:
            distanceToStartPt = round(gps_distance(GPSLat*pi/180, GPSLon*pi/180, wzStartLat*pi/180, wzStartLon*pi/180))
            if distanceToStartPt < 100: #Entering Workzone
                logMsg('-------- Entering Work Zone (by location, distance=' + str(distanceToStartPt) + ') -------')
                startDataLog()
                prevDistance = distanceToStartPt
                #dataLog = True

###
#
#       Save GPS record to CSV file...
#
#       Construct output string including marker based on key hit and write to file..    
#       Log data to csv file...
#
#       <<<<<< DO THIS ONLY IF DATA LOG IS TRUE >>>>>>
#
###

        if (dataLog == True) and (GPSTime != prevGPSTime) and (GPSDate != ''):              #log data only if next sentence(GPSTime) is different from the previous
            time_date = GPSDate+'-'+GPSTime
            outStr  = time_date,GPSSats,GPSHdop,GPSLat,GPSLon,GPSAlt,GPSSpeed,GPSHeading,keyMarker[0],keyMarker[1]      #to CSV file...
            ##print (outStr)
            writeCSVFile (outStr)                       #write to CSV file
            keyMarker = ['','']                         #reset key marker
            prevGPSTime = GPSTime                       #set prevGPSTime to GPSTime             
        pass                                            #end of writing outStr

###
#       Save the last record with App Ended marker...
###


        if appRunning == False:                         #save the last record...
            logMsg('App not running, save last dataset and exit')
            time_date = GPSDate+'-'+GPSTime
            outStr  = time_date,GPSSats,GPSHdop,GPSLat,GPSLon,GPSAlt,GPSSpeed,GPSHeading,keyMarker[0],keyMarker[1]      #to CSV file...
            writeCSVFile (outStr)                       #write to CSV file
        pass

    return

###
#   
#   -------------------  END OF getNMEA_String...  ---------------------------------------------------------------------
#
#
#   -------------------  Process key press... ----------------------------------------------------------------------------
#
###

def gps_distance(lat1, lon1, lat2, lon2):
    R = 6371000
    avg_lat = (lat1+lat2)/2
    distance = R*math.sqrt((lat1-lat2)**2+math.cos(avg_lat)**2*(lon1-lon2)**2)
    return distance

def laneClicked(lane):
    global gotRefPt
    global laneStat
    global laneSymbols

    laneStat[lane] = not laneStat[lane]         #Lane open status (T or F)
    lc = 'LC'                                   #set lc to 'LC' - Lane Closed
    if laneStat[lane]:
        lc = 'LO'                               #toggle lane status to Lane Open
        lanes[lane]['bg']   = 'green'
        lanes[lane]['fg']   = 'white'
        laneLabels[lane]['fg'] = 'green'
        laneLabels[lane]['text'] = 'OPEN'
        laneLabels[lane].place(x=marginLeft+22 + (lane-1)*110, y=100)
        # laneSymbols[lane] = Label(image = laneClosedImg)
        # laneSymbols[lane].place(x=marginLeft+13 + (lane-1)*110, y=120)
    else:
        lanes[lane]['bg']   = 'gray92'
        lanes[lane]['fg']   = 'red3'
        laneLabels[lane]['fg'] = 'red3'
        laneLabels[lane]['text'] = 'CLOSED'
        laneLabels[lane].place(x=marginLeft+18 + (lane-1)*110, y=100)
        # laneSymbols[lane].destroy()

    if not gotRefPt:                       #if ref pt has not been marked yet
        lc = lc + '+RP'                         #lc + ref. pt
        gotRefPt = True                         #set to true
    pass

    lStat = 'Closed'
    if lc == 'LO': lStat = 'Open'
        
    markerStr = '   *** Lane '+str(lane)+' Status Marked: '+lStat+' @ '+str(GPSLat)+', '+str(GPSLon)+', '+str(GPSAlt)+' ***'
    logMsg('*** Lane '+str(lane)+' Status Marked: '+lStat+' @ '+str(GPSLat)+', '+str(GPSLon)+', '+str(GPSAlt)+' ***')
    keyMarker = [lc, str(lane)]
    displayStatusMsg(markerStr)

def workersPresentClicked():
    global gotRefPt
    global wpStat
    global keyMarker
    global worksersPresentLabel

    wpStat = not wpStat                         #Toggle wp/np

    if wpStat:
        bWP['text'] = 'Workers No\nLonger Present (w)'
        bWP['bg']   = 'gray92'
        bWP['fg']   = 'red3'
        worksersPresentLabel = Label(image = workersPresentImg)
        worksersPresentLabel.place(x=marginLeft+60 + (totalLanes)*110, y=100)
    else:
        bWP['text'] = 'Workers are\nPresent (w)'
        bWP['bg']   = 'green'
        bWP['fg']   = 'white'
        worksersPresentLabel.destroy()

    markerStr = '   *** Workers Presence Marked: '+str(wpStat)+' ***'
    logMsg('*** Workers Presence Marked: '+str(wpStat)+' ***')

    keyMarker[0] = 'WP'                         #WP marker
    if gotRefPt == False:
        keyMarker[0]='WP+RP'                    #WP+ref pt
        gotRefPt = True                         #gotRefPT True    
    keyMarker[1] = wpStat
    displayStatusMsg(markerStr)

def startDataLog():
    global dataLog
    global keyMarker

    dataLog = True

    markerStr = '   *** Data Logging Started ***'
    logMsg('*** Data Logging Started ***')

    keyMarker = ['Data Log', dataLog]

    overlay.destroy()
    enableForm()

    displayStatusMsg(markerStr)

def stopDataLog():
    global dataLog
    global keyMarker
    global appRunning

    dataLog = False

    markerStr = '   *** Data Logging Stopped ***'
    logMsg('*** Data Logging Stopped ***')

    keyMarker = ['Data Log', dataLog]

    displayStatusMsg(markerStr)
    appRunning = False

def markRefPt():
    global gotRefPt
    global keyMarker

    markerStr = '   *** Reference Point Marked @ '+str(GPSLat)+', '+str(GPSLon)+', '+str(GPSAlt)+' ***'
    logMsg('*** Reference Point Marked @ '+str(GPSLat)+', '+str(GPSLon)+', '+str(GPSAlt)+' ***')
    ##T.insert (END, markerStr)
    keyMarker = ['RP','']                       #reference point
    gotRefPt = True                             #got the reference point


def processKeyPress(key):
    logMsg('Key pressed: ' + key)

###
#   Few Globals...
###

    global  GPSDate, GPSTime, prevGPSTime           # 
    global  GPSLat, GPSLon, GPSAlt                  #from NMEA Parser
    
    global  gotRefPt, gotLCRP, keyMarker, dataLog   #
    global  laneStat, wpStat                        #for lane status - up to 8 lanes (1 to 9 in laneStat array)
    global  appRunning                              #boolean
    
###
#   few local inits
###

    outStr      = ''                                #output string
    keyMarker   = ['',0]                            #marker from key press
    gotMarker   = False                             #marker key pressed
                                                    #pressing the same lane # key will toggle the from close to open  
###
#   Data logging toggle
###    

    if key == 's' or key == 'S':                    #start/stop data logging
        dataLog = not dataLog                       #toggle logging
        if dataLog == True:
            markerStr = '   *** Data Logging Started ***'
            logMsg('*** Data Logging Started ***')
        else:
            markerStr = '   *** Data Logging Stopped ***'
            logMsg('*** Data Logging Stopped ***')
        keyMarker = ['Data Log', dataLog]
        gotMarker = True
    pass                                            #end of data log start/stop

###
#   Ref. point
###    

    if (key == 'r' or key == 'R') and gotRefPt == False and dataLog == True: #Mark reference point
        markerStr = '   *** Reference Point Marked @ '+str(GPSLat)+', '+str(GPSLon)+', '+str(GPSAlt)+' ***'
        logMsg('*** Reference Point Marked @ '+str(GPSLat)+', '+str(GPSLon)+', '+str(GPSAlt)+' ***')
        ##T.insert (END, markerStr)
        keyMarker = ['RP','']                       #reference point
        gotRefPt = True                             #got the reference point
        gotMarker = True                            #got the marker
    pass                                            #end of ref point

###
#   Workers present
###

    if key == 'w' or key == 'W':                    #workers present/not present
        wpStat = not wpStat                         #Toggle wp/np
        markerStr = '   *** Workers Presence Marked: '+str(wpStat)+' ***'
        logMsg('*** Workers Presence Marked: '+str(wpStat)+' ***')
        ##print (markerStr)
        ##T.insert (END, markerStr)
        keyMarker[0] = 'WP'                         #WP marker
        if gotRefPt == False:
            keyMarker[0]='WP+RP'                    #WP+ref pt
            gotRefPt = True                         #gotRefPT True    
        keyMarker[1] = wpStat

        gotMarker = True                            #got marker
    pass                                            #end of data log start/stop

###
#   lane number input for LC/LO...
###

    if key > '0' and key <= '8':                    #Mark lane# closed point
        lane = int(key)                             #lane number
        laneStat[lane] = not laneStat[lane]         #Lane open status (T or F)
        lc = 'LC'                                   #set lc to 'LC' - Lane Closed
        if laneStat[lane] == True:
            lc = 'LO'                               #toggle lane status to Lane Open
        if gotRefPt == False:                       #if ref pt has not been marked yet
            lc = lc + '+RP'                         #lc + ref. pt
            gotRefPt = True                         #set to true
        pass

        lStat = 'Closed'
        if lc == 'LO':       lStat = 'Open'
            
        markerStr = '   *** Lane '+str(key)+' Status Marked: '+lStat+' @ '+str(GPSLat)+', '+str(GPSLon)+', '+str(GPSAlt)+' ***'
        logMsg('*** Lane '+str(key)+' Status Marked: '+lStat+' @ '+str(GPSLat)+', '+str(GPSLon)+', '+str(GPSAlt)+' ***')
        ##print (markerStr)
        ##T.insert (END, markerStr)
        keyMarker = [lc, key]                 
        gotMarker = True
        ##writeData.writerow (markerStr)            #write complete outStr with marker at the end of kbhit check
    pass                                            #end of LC marker

###
#   Esc key...
###

    if key == '\x1b':                               #Esc key pressed... Quit the logging routine...
        markerStr = '   *** Application Ended ***'
        logMsg('*** Application Ended ***')
        ##print (markerStr)
        ##T.insert (END, markerStr)
        keyMarker = ['App Ended', '']
        gotMarker = True
        appRunning = not appRunning
    pass                                            #end of Esc key

###
#   Got marker...
#
#   output of this method is ONLY the updated keyMarker (global)...
#
#   concstructed output string is saved in getNMEA_String method...
###

    if gotMarker == True:
        xPos = 50
        yPos = 450
        displayStatusMsg(markerStr)
    pass                                            #end of marker tag

###
#   
#   -------------------  END OF processKeyPress...  ---------------------------------------------------------------------
#
#   
#   -------------------  writeCSVFile...  ---------------------------------------------------------------------
#
###

def writeCSVFile (write_str):
    global writeData                            #file handle
    
    writeData.writerow(write_str)               #write output to csv file...                           

###
#   
#   -------------------  END OF writeCSVFile...  ---------------------------------------------------------------------
#
###


def displayStatusMsg(msgStr):

    xPos = 45
    yPos = 400
    blankStr = ' '*190
    Text = Label(root,anchor='w', justify=LEFT, text=blankStr)
    Text.place(x=xPos,y=yPos)    

    Text = Label(root,anchor='w', justify=LEFT, text=msgStr)
    Text.place(x=xPos,y=yPos)    

###
#   Following functions added on Sept. 2018...
###

###
#   process button pressed...
###

def gotBtnPress(gotKey):
    #processKeyPress(gotKey)

    if gotKey == 'r' or gotKey == 's' or gotKey == 'w':     #start/stop data log, ref. pt and WP
        toggle_btn_text(gotKey)

    if gotKey >= '1' and gotKey <= '9':
        if gotRefPt == False:        
            toggle_btn_text(gotKey)                         #Toggle ref. pt. marker button text
        pass
        toggle_lane_color(gotKey)

    processKeyPress(gotKey)                                 #process key press

###
#   ----------------  End of gotBtnPress  ---------------------------        
###

###
#   toggle selected lane color
###


def toggle_lane_color(laneNum):

    global  lanes                                   #list to hold all button objects for lanes
   
    btnObj = lanes[int(laneNum)]
    if btnObj['bg'] == 'green':
        btnObj['bg'] = 'gray92'
        btnObj['fg'] = 'red3'
    else:
        btnObj['bg'] = 'green'
        btnObj['fg'] = 'white'
              
###
#   ----------------  End of toggle_lane_text  ---------------------------        
###

###
#  Alter button text
###

def toggle_btn_text(gotKey):

    global  gotReflanes
    
    if gotKey == 's':                                   #Start/Stop data log    
        if bDL['text'] == 'Manually Start\nData Log (s)':
            bDL['text'] = 'Manually Stop\nData Log (s)'
            bDL['bg'] = 'gray92'
            bDL['fg'] = 'red3'
        else:
            if bDL['text'] == 'Manually Stop\nData Log (s)':
                gotKey = '\x1b'
                processKeyPress(gotKey)
                # bDL['text'] = 'Start Data\nLog (s)'
                # bDL['bg']   = 'green'
                # bDL['fg']   = 'white'
        pass   
    pass


    #if gotKey == 'r':                                   #Ref point
    if (gotKey == 'r' or gotKey == 'w' or (gotKey >= '1' and gotKey <= '9')) and gotRefPt == False and dataLog == True:
    
        if bR['text'] == 'Mark Ref.\nPoint (r)':
            bR['text'] = 'Ref.Point\nMarked'
            bR['bg'] = 'gray92'
            bR['fg'] = 'red3'
        pass
    pass

    if gotKey == 'w':                                   #workers present toggle
        if bWP['text'] == 'Workers Not\nPresent (w)':
            bWP['text'] = 'Workers are\nPresent (w)'
            bWP['bg']   = 'gray92'
            bWP['fg']   = 'red3'
            
        else:
            if bWP['text'] == 'Workers are\nPresent (w)':
                bWP['text'] = 'Workers Not\nPresent (w)'
                bWP['bg']   = 'green'
                bWP['fg']   = 'white'
              
###
#   ----------------  End of toggle_btn_text  ---------------------------        
###

###
#  Quit Application....
###

def gotQuit():
    gotKey = '\x1b'
    processKeyPress(gotKey)
    if messagebox.askyesno('Quit', 'Sure you want to quit?') == True:
        sys.exit(0)

#---------------------------------------------------------------------


###
#  Update GPS comm port
###
def commSelect(*args):
    portNum= tkvar.get()

###
#  Check for GPS computer
###
def checkForGPS(root, portNum, first):
    ports = serial.tools.list_ports.comports(include_links=False)
    gpsFound = False
    if len(ports)==0:
        logMsg('No serial ports open')
        messagebox.showwarning('GPS Receiver Missing', '*** GPS Receiver missing ***\n\n')
    if (len(ports)>=1):
        for port in ports:
            if ('1546:01A6' in port.hwid):
                portNum = port.device
                gpsFound = True
                logMsg('GPS device found at port number: ' + portNum)
        if (not gpsFound) and first:
            logMsg('GPS device not directly found')
            mainframe = Frame(root)
            # Add a grid
            mainframe.pack()
            mainframe.columnconfigure(0, weight=1)
            mainframe.rowconfigure(0, weight=1)
            mainframe.pack(pady=100, padx=100)
            # Create a Tkinter variable
            tkvar = StringVar(root)
            tkvar.set(ports[0].device) #default is first comm port
            popupMenu = OptionMenu(mainframe, tkvar, *ports)
            logMsg('Creating comm port popup menu')
            Label(mainframe, text='Choose a comm port').pack()
            popupMenu.pack()
            tkvar.trace('w', commSelect)
        return portNum
        
def openLog():
    global logFile
    if os.path.exists(logFileName):
        append_write = 'a' # append if already exists
    else:
        append_write = 'w' # make a new file if not
    logFile = open(logFileName, append_write)

def logMsg(msg):
    formattedTime = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S') + '+00:00'
    logFile.write('[' + formattedTime + '] ' + msg + '\n')

def enableForm():
    for i in range(1, totalLanes+1):
        if i != dataLane:
            lanes[i]['fg'] = 'white'
            lanes[i]['bg'] = 'green'
            lanes[i]['state'] = NORMAL
    bWP['fg'] = 'white'
    bWP['bg'] = 'green'
    bWP['state'] = NORMAL
###
#   Few Variables... also used in different functions...
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


###
#   Few inits...
###

kt          = 0                                 #local count variable
dataLog     = False                             #data logging off
#outStr      = ''                                #output string in 'tuple'
keyMarker   = ['',0]                            #marker from key press
appRunning  = True                              #set application running to TRUE
gotRefPt    = False                             #got Ref. Point
gotLCRP     = False                             #if no RP yet, set RP and LC the same data point
gotMarker   = False                             #marker key pressed
wpStat      = False                             #workers not present
                                                #pressing the same lane # key will toggle the from close to open  

#############################################################################
# MAIN LOOP
#############################################################################

###
#   import and get root
#
#   Add description on Tkinter package here...
#
###


local_config_path = './Config Files/ACTIVE_CONFIG.json'
cDT       = datetime.datetime.now().strftime('%Y%m%d_')+time.strftime('%H%M%S')
date_time = datetime.datetime.now().strftime('%Y/%m/%d - ')+time.strftime('%H:%M:%S')

###
#   Open output file for data logging...
###

logFileName = './data_collection_log.txt'
logFile = ''
openLog()
logMsg('*** Running Vehicle Path Data Acquisition ***')

logMsg('Reading local config file')
outDir      = './WZ_VehPathData'
dataOutFile = ''
configRead()

root = Tk()
root.title('Work Zone Mapping - Vehicle Path Data Acquisition')
root.geometry(str(max(800, totalLanes*110+350))+'x500')

# root.bind_all('<Key>', keyPress)                #key press event...


#############################################################################
#
# LAYOUT...
#
#############################################################################

lbl_top = Label(text='Vehicle Path Data Acquisition\n\n', font='Helvetica 14', fg='royalblue', pady=10)
lbl_top.pack()

winSize = Label(root, height=30, width=120) #width was 110
winSize.pack()

laneLine = ImageTk.PhotoImage(Image.open('./images/verticalLine_thin.png'))
carImg = ImageTk.PhotoImage(Image.open('./images/caricon.png'))
carlabel = Label(image = carImg)
workersPresentImg = ImageTk.PhotoImage(Image.open('./images/workersPresentSign_small.png'))
laneClosedImg = ImageTk.PhotoImage(Image.open('./images/laneClosedSign_small.jpg'))

marginLeft = 100

# def setLaneClosed(i):
#     laneSymbols[i] = Label(image = laneClosedImg)
#     laneSymbols[i].place(x=marginLeft+13 + (i-1)*110, y=120)
# def setWorkersPresent():
#     worksersPresentLabel = Label(image = workersPresentImg)
#     worksersPresentLabel.place(x=marginLeft+60 + (totalLanes)*110, y=100)
laneBoxes = [0]*(totalLanes+1)
laneLabels = [0]*(totalLanes+1)
laneSymbols = [0]*(totalLanes+1)
laneLines = [0]*(totalLanes+1)
for i in range(totalLanes):
    laneLines[i] = Label(image = laneLine)
    laneLines[i].place(x=marginLeft + i*110, y=50)
    if i+1 == dataLane:
        carlabel.place(x=marginLeft+10 + i*110, y=50)
    else:
        laneBoxes[i+1] = Label(justify=LEFT,anchor=W,padx=50,pady=90)
        laneBoxes[i+1].place(x=marginLeft+10 + i*110, y=50)
        laneLabels[i] = Label(text='OPEN',justify=CENTER,font='Calibri 22 bold',fg='green')
        laneLabels[i].place(x=marginLeft+22 + i*110, y=100)
    if i == totalLanes-1:
        laneLines[i+1] = Label(image = laneLine)
        laneLines[i+1].place(x=marginLeft + (i+1)*110, y=50)

lanes = [0]*(totalLanes+1)
laneStat = [True]*(totalLanes+1) #all 8 lanes are open (default), Lane 0 is not used...


def createButton(id):
    global lanes
    lanes[id] = Button(text='Lane '+str(id), font='Helvetica 10', state=DISABLED, width=11, height=4, command=lambda:laneClicked(id))
    lanes[id].place(x=marginLeft+10 + (id-1)*110, y=300)

for i in range(1, totalLanes+1):
    createButton(i)

###
#   Mark Workers Present...
###

bWP = Button(text='Workers are\nPresent', font='Helvetica 10', state=DISABLED, width=11, height=4, command=lambda:workersPresentClicked('w'))
bWP.place(x=marginLeft+60 + (totalLanes)*110, y=300)

###
#   Quit...
###


bStart = Button(text='Manually Start\nApplication', font='Helvetica 10', padx=5, bg='green', fg='white', command=startDataLog)
bStart.place(x=100, y=510)

bRef = Button(text='Manually Mark\nRef Pt', font='Helvetica 10', padx=5, bg='green', fg='white', command=markRefPt)
bRef.place(x=250, y=510)

bEnd = Button(text='Manually End\nApplication', font='Helvetica 10', padx=5, bg='red3', fg='gray92', command=stopDataLog)
bEnd.place(x=500, y=510)

# bQuit = Button(text='Quit (Esc)', font='Helvetica 10', fg = 'white', bg='red3',padx=5, command=gotQuit)
# bQuit.place(x=400,y=380)

###
#   Application Message Window...
###

appMsgWin = Button(text='Application Message Window...                                             ',      \
                font='Courier 10', justify=LEFT,anchor=W,padx=10,pady=10)
appMsgWin.place(x=50, y=390)


overlay = Label(text='Application will begin data collection\nwhen the set starting location has been reached', bg='gray', font='Calibri 28')
overlay.place(x=(marginLeft+80 + (totalLanes)*110)/2-160, y=200)
##############################################################
#   ------------------ END of LAYOUT -------------------------
##############################################################

###
#
#   Open serial com port...U-Blox opens COM7 as virtual port on USB...
#
###

#configRead()

gps_found = False
first = True
while not gps_found:
    logMsg('Searching for GPS device')
    try:
        portNum     = 'COM4'
        baudRate    = 115200
        timeOut     = 1
        portNum = checkForGPS(root, portNum, first)
        first = False
        ser         = serial.Serial(port=portNum, baudrate=baudRate, timeout=timeOut)               #open serial port
        msgStr      = 'Vehicle Path Data Acquisition is Ready - Logging Will Start When Start Location is Reached'
        displayStatusMsg(msgStr)                                                        #system ready
        gps_found = True

    except SerialException as e:
        logMsg('Failed to find GPS device, SerialException: ' + str(e))
        MsgBox = messagebox.askquestion ('GPS Receiver NOT Found','*** GPS Receiver NOT Found, Connect to a USB Port ***\n\n'   \
                    '   --- Press Yes to try again, No to exit the application ---',icon = 'warning')
        if MsgBox == 'no':
            logMsg('User exited application')
            logFile.close()
            sys.exit(0)
        #if MsgBox == 'no':
            #sys.exit(0)
        

    
###
#   EOL is not supported in PySerial for readline() in Python 3.6.
#   must use sio
###

logMsg('Creating serial IO connection')
sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))             

###
#   Get current date and time...
###

###
#   Open outFile for csv write...
#   make sure newline is set to null, otherwise will get extra cr.. 
###

#configRead(local_config_path)


logMsg('Opening path data output file: ' + dataOutFile)
outFile     = open(dataOutFile,'w',newline='')
writeData   = csv.writer(outFile)

###
#   Write Title in the data logging file...
###

titleLine = 'GPS Date & Time','# of Sats','HDOP','Latitude','Longitude','Altitude(m)','Speed(m/s)','Heading(Deg)','Marker','Value'
writeCSVFile(titleLine)

###
#
#   -----------------------  Start Main Function  --------------------------------------------------------
#
###

logMsg('Starting main loop')
startMainFunc()                                         #main function, starts NMEA processing 

logMsg('Main loop ended, closing streams/files')

###
#   Done, close everything...
###

ser.close()                                             #close serial IO
outFile.close()                                         #end of data acquisition and logging
# road_name = roadName
# begin_date = wzStartDate.replace('/', '-')
# end_date = wzEndDate.replace('/', '-')
# name_id = road_name + '--' + begin_date + '--' + end_date

# zip_name = 'wzdc-exports--' + name_id + '.zip'
# export_files()
# messagebox.showinfo('Veh Path Data Acq. Ended', 'Vehicle Path Data Acq Ended\nCollecting and zipping files\nOutput location: \n' + zip_name)
build_export_file = './WZ_BuildMsgs_and_Export.py'
logMsg('Opening export script: ' + build_export_file + ', and closing data acquisition')
logMsg('Closing log file from data acquisition')
logFile.close()
root.destroy()
subprocess.call([sys.executable, build_export_file], shell=True) #, shell=True
# os.system(build_export_file) #_------------------------------------------------------------ FAILED
#os.remove(local_config_path)
sys.exit(0)
root.mainloop()
