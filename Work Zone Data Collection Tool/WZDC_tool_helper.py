from    tkinter         import *   
from    tkinter         import messagebox
from    tkinter         import filedialog


def setupVehPathDataAcqUI(root, window_width, totalLanes, dataLane, marginLeft, laneLine, carlabel, laneClicked, workersPresentClicked):
    lanes = [0]*(totalLanes+1)
    laneBoxes = [0]*(totalLanes+1)
    laneLabels = [0]*(totalLanes+1)
    laneSymbols = [0]*(totalLanes+1)
    laneLines = [0]*(totalLanes+1)

    lbl_top = Label(root, text='Vehicle Path Data Acquisition\n\n', font='Helvetica 14', fg='royalblue', pady=10)
    lbl_top.place(x=window_width/2-250/2, y=10)



    # Initialize lane images
    for i in range(totalLanes):
        laneLines[i] = Label(root, image = laneLine)
        laneLines[i].place(x=marginLeft + i*110, y=50)
        if i+1 == dataLane:
            carlabel.place(x=marginLeft+8 + i*110, y=50)
        else:
            laneBoxes[i+1] = Label(root, justify=LEFT,anchor=W,padx=50,pady=90)
            laneBoxes[i+1].place(x=marginLeft+10 + i*110, y=50)
            laneLabels[i+1] = Label(root, text='OPEN',justify=CENTER,font='Calibri 22 bold',fg='green')
            laneLabels[i+1].place(x=marginLeft+22 + i*110, y=100)
        if i == totalLanes-1:
            laneLines[i+1] = Label(root, image = laneLine)
            laneLines[i+1].place(x=marginLeft + (i+1)*110, y=50)


    # This is required because otherwise the lane command laneClicked(lane #) cannot be set in a for loop
    def createButton(id):
        laneBtn = Button(root, text='Lane '+str(id), font='Helvetica 10', state=DISABLED, width=11, height=4, command=lambda:laneClicked(id))
        laneBtn.place(x=marginLeft+10 + (id-1)*110, y=300)
        return laneBtn

    # Create lane buttons dynamically to number of lanes
    for i in range(1, totalLanes+1):
        lanes[i] = createButton(i)

    # Toggle workers present button
    bWP = Button(root, text='Workers are\nPresent', font='Helvetica 10', state=DISABLED, width=11, height=4, command=lambda:workersPresentClicked())
    bWP.place(x=marginLeft+60 + (totalLanes)*110, y=300)

    # # Debug buttons, hidden by small frame
    # bStart = Button(root, text='Manually Start\nApplication', font='Helvetica 10', padx=5, bg='green', fg='white', command=startDataLog)
    # bStart.place(x=100, y=510)
    # bRef = Button(root, text='Manually Mark\nRef Pt', font='Helvetica 10', padx=5, bg='green', fg='white', command=markRefPt)
    # bRef.place(x=250, y=510)
    # bEnd = Button(root, text='Manually End\nApplication', font='Helvetica 10', padx=5, bg='red3', fg='gray92', command=stopDataLog)
    # bEnd.place(x=500, y=510)

    ###
    #   Application Message Window...
    ###

    appMsgWin = Button(root, text='Application Message Window...                                             ',      \
                    font='Courier 10', justify=LEFT,anchor=W,padx=10,pady=10)
    appMsgWin.place(x=50, y=390)

    overlayWidth = 710
    overlayx = window_width/2 - overlayWidth/2
    overlay = Label(root, text='Application will begin data collection\nwhen the set starting location has been reached', bg='gray', font='Calibri 28')
    overlay.place(x=overlayx, y=200)

    return overlay, bWP, lanes, laneLabels


    
def startMainFunc():
    global  appRunning                          #boolean
    if (appRunning):
        logMsg('App running, starting getNMEA_String loop')
        getNMEA_String()                        #Get NMEA String and process it until 'appRunning is True...'
    else:
        logMsg('App not running, exiting')

# def update_config(cfg):
#     global dataOutFile
    
#     dataOutFileName = 'path-data--' + wzDesc + '--' + roadName + '.csv'
#     dataOutFile = outDir + '/' + dataOutFileName
#     cfg.truncate(0)
#     cfg.seek(0)
#     wzConfig['FILES']['VehiclePathDataDir'] = os.path.abspath(outDir).replace('\\', '/')
#     wzConfig['FILES']['VehiclePathDataFile'] = dataOutFileName
#     cfg.write(json.dumps(wzConfig, indent='    '))

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
    isFirstTime = True

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
            if not gotRefPt and distanceToStartPt > prevDistance and not isFirstTime: #Auto mark reference point
                logMsg('-------- Auto Marking Reference Point (by location, distance=' + str(distanceToStartPt) + ') -------')
                markRefPt()
            prevDistance = distanceToStartPt
            isFirstTime = False

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

def gps_distance(lat1, lon1, lat2, lon2):
    R = 6371000
    avg_lat = (lat1+lat2)/2
    distance = R*math.sqrt((lat1-lat2)**2+math.cos(avg_lat)**2*(lon1-lon2)**2)
    return distance

def laneClicked(lane):
    global gotRefPt
    global laneStat
    global keyMarker
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
        laneLabels[lane].place(x=marginLeft+10 + (lane-1)*110, y=100)
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
        bWP['text'] = 'Workers No\nLonger Present'
        bWP['bg']   = 'gray92'
        bWP['fg']   = 'red3'
        worksersPresentLabel = Label(root, image = workersPresentImg)
        worksersPresentLabel.place(x=marginLeft+60 + (totalLanes)*110, y=100)
    else:
        bWP['text'] = 'Workers are\nPresent'
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

    displayStatusMsg(markerStr)

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
        raise SerialException('No open COM ports detected')
    else:
        for port in ports:
            if ('1546:01A6' in port.hwid):
                portNum = port.device
                gpsFound = True
                logMsg('GPS device found at port number: ' + portNum)
        if (not gpsFound) and first:
            logMsg('GPS device not directly found')
            mainframe = Frame(root, pady=100, padx=100)
            # Add a grid
            mainframe.place(x=300, y=600)
            mainframe.columnconfigure(0, weight=1)
            mainframe.rowconfigure(0, weight=1)
            mainframe.place(x=300, y=600)
            # Create a Tkinter variable
            tkvar = StringVar(root)
            tkvar.set(ports[0].device) #default is first comm port
            popupMenu = OptionMenu(mainframe, tkvar, *ports)
            logMsg('Creating comm port popup menu')
            Label(mainframe, text='Choose a comm port').pack()
            popupMenu.pack()
            tkvar.trace('w', commSelect)
        return portNum

# Format and write message to file
def enableForm():
    for i in range(1, totalLanes+1):
        if i != dataLane:
            lanes[i]['fg'] = 'white'
            lanes[i]['bg'] = 'green'
            lanes[i]['state'] = NORMAL
        else:
            lanes[i]['text'] = 'Lane ' + str(i) + '\n(Vehicle Lane)'
    bWP['fg'] = 'white'
    bWP['bg'] = 'green'
    bWP['state'] = NORMAL



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

# local_config_path = './Config Files/ACTIVE_CONFIG.json'
cDT = datetime.datetime.now().strftime('%m/%d/%Y - ') + time.strftime('%H:%M:%S')
ctrDT = datetime.datetime.now().strftime('%Y%m%d-') + time.strftime('%H%M%S')


###
#   Initialize data collection variables
###
pathPt          = []			#test vehicle path data points generated by WZ_VehPathDataAcq.py module
appMapPt        = [] 		        #array to hold approach lanes map node points
wzMapPt         = []                    #array to hold wz lanes map node points
refPoint        = [0,0,0]               #Ref. point (lat, lon, alt), initial value... ONLY ONE reference point...
appHeading      = 0                     #applicable Heading to the WZ event at the ref. point. Needed for XML for RSM Message

###
#	Variables for book keeping...
###

refPtIdx        = 0                     #index into pathPt array where the reference point is...
gotRefPt        = False                 #default 

###
#	For fixed equidistant node selection for approach and WZ lanes
#
#       As of Feb. 2018 --  Node point selection based on equidistant is NO LONGER in use...
#                           Replace by dynamic node point selection based on right triangle using change in heading angle method... 
###

appMapPtDist    = 50                    #set distance in meters between map data points for approach lanes - not used in the algo.
wzMapPtDist     = 200	                #set distance in meters between map data point for WZ map - not used in the algo.

###
#	Keep track of lane status such as point where lane closed or open is marked within WZ for each lane
#       including offset from ref. pt.
#
#       Contains 4 elements - [data point#, lane#, lane status (0-open/1-closed), offset from ref. point)  
###

laneStat        = []                    #contains lane status, data point#, lane #, 0/1 0=open, 1=closed and offset from ref point.
                                        #Generated from lane closed/opened marker from colleted data
laneStatIdx     = 0                     #laneStat + lcOffset array index

###
#	Keep track of workers present status such as point where they are present and then not present at **road level**
#       including offset from the reference point
###

wpStat          = []                    #array to hold WP location, WP status and offset from ref. point default - no workers present
wpStatIdx       = 0                     #wpStat array index    

###
#       Work zone length
###

wzLen           = 0                     #init WZ length

msgSegList      = []                    #WZ message node segmentation list

files_list      = []