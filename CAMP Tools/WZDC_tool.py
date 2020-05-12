#!/usr/bin/env python3

import  os.path
import  sys
import  subprocess

import  csv                                             #csv file processor
import  datetime                                        #Date and Time methods...
import  time                                            #do I need time???
import  math                                            #math library for math functions
import  random                                          #random number generator
import  json                                            #json manipulation
import  shutil
import  requests
import  serial                                  #serial communication
import  io                                      #serial i/o function
import  string                                  #string functions
import  csv                                     #CSV file read/write
import  serial.tools.list_ports                      #used to enumerate COMM ports
from    serial import SerialException           #serial port exception

import  zipfile
import  xmltodict                                       #dict to xml converter

from    azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

from    tkinter         import *   
from    tkinter         import messagebox
from    tkinter         import filedialog
from    PIL             import ImageTk, Image


from    parseNMEA       import parseGxGGA           #parse GGA for Time, Alt, #of Satellites
from    parseNMEA       import parseGxRMC           #parse RMC for Date, Lat, Lon, Speed, Heading
from    parseNMEA       import parseGxGSA           #parse GSA for Hdop


from    wz_vehpath_lanestat_builder import buildVehPathData_LaneStat

from    wz_map_constructor  import getLanePt            #get lat/lon points for lanes 
from    wz_map_constructor  import getEndPoint          #calculates lat/lon for an end point from distance and heading (bearing)
                                                        #   called from getLanePt
from    wz_map_constructor  import getDist              #get distance in meters between pair of lat/lon points
                                                        #   called from getLanePt

from    wz_xml_builder         import build_xml_CC         #common container
from    wz_xml_builder         import build_xml_WZC        #WZ container
from    rsm_2_wzdx_translator  import wzdx_creator         #WZDx Translator

from    wz_msg_segmentation    import buildMsgSegNodeList  #msg segmentation node list builder


def inputFileDialog():
    global local_config_path
    filename = filedialog.askopenfilename(initialdir=configDirectory, title="Select Input File", filetypes=[("Config File","*.json")])
    if len(filename): 
        local_config_path = filename
        logMsg('Reading configuration file')
        try:
            configRead()

            logMsg('Setting configuration path: ' + local_config_path)
            # local_config_file = abs_path
            set_config_description(local_config_path)
            wzConfig_file.set(local_config_path)
            btnBegin['state']   = 'normal'                    #enable the start button for map building...
            btnBegin['bg']      = 'green'
        except Exception as e:
            logMsg('ERROR: Config read failed, ' + str(e))
            messagebox.showerror('Configuration File Reading Failed', 'Configuration file reading failed. Please load a valid configuration file')
    pass

def configRead():
    global wzConfig
    file = local_config_path
    if os.path.exists(file):
        cfg = open(file, 'r+')
        wzConfig = json.loads(cfg.read())
        getConfigVars()
        # update_config(cfg)
        cfg.close()

def getConfigVars():

###
#   Following are global variables are later used by other functions/methods...
###

    # global  vehPathDataFile                                 #collected vehicle path data file
    global  sampleFreq                                      #GPS sampling freq.

    global  totalLanes                                      #total number of lanes in wz
    global  laneWidth                                       #average lane width in meters
    global  lanePadApp                                      #approach lane padding in meters
    global  lanePadWZ                                       #WZ lane padding in meters
    global  dataLane                                        #lane used for collecting veh path data
    global  wzDesc                                          #WZ Description

    global  speedList                                       #speed limits
    global  c_sc_codes                                      #cause/subcause code

    global  wzStartDate                                     #wz start date
    global  wzStartTime                                     #wz start time    
    global  wzEndDate                                       #wz end date
    global  wzEndTime                                       #wz end time
    global  wzDaysOfWeek                                    #wz active days of week

    global  wzStartLat                                     #wz start date
    global  wzStartLon                                     #wz start time    
    global  wzEndLat                                       #wz end date
    global  wzEndLon                                       #wz end time

    global  roadName
    # global  roadNumber
    # global  beginningCrossStreet
    # global  endingCrossStreet
    # global  beginningMilepost
    # global  endingMilepost
    # global  issuingOrganization
    # global  creationDate
    # global  updateDate
    # global  isArchitecturalChange

    dirName     = wzConfig['FILES']['VehiclePathDataDir']   #veh path data file directory
    fileName    = wzConfig['FILES']['VehiclePathDataFile']  #veh path data file name

    sampleFreq      = int(wzConfig['SERIALPORT']['DataRate'])           #data sampling freq

    totalLanes      = int(wzConfig['LANES']['NumberOfLanes'])           #total number of lanes in wz
    laneWidth       = float(wzConfig['LANES']['AverageLaneWidth'])      #average lane width in meters
    lanePadApp      = float(wzConfig['LANES']['ApproachLanePadding'])   #approach lane padding in meters
    lanePadWZ       = float(wzConfig['LANES']['WorkzoneLanePadding'])   #WZ lane padding in meters
    dataLane        = int(wzConfig['LANES']['VehiclePathDataLane'])     #lane used for collecting veh path data
    wzDesc          = wzConfig['LANES']['Description']                  #WZ Description

    speedList       = wzConfig['SPEED']['NormalSpeed'], wzConfig['SPEED']['ReferencePointSpeed'], \
                      wzConfig['SPEED']['WorkersPresentSpeed']

    c_sc_codes      = [int(wzConfig['CAUSE']['CauseCode']), int(wzConfig['CAUSE']['SubCauseCode'])]

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

    roadName        = wzConfig['INFO']['RoadName']
    # roadNumber      = wzConfig['INFO']['RoadNumber']
    # beginningCrossStreet  = wzConfig['INFO']['beginningCrossStreet']
    # endingCrossStreet = wzConfig['INFO']['endingCrossStreet']
    # beginningMilepost = wzConfig['INFO']['beginningMilepost']
    # endingMilepost = wzConfig['INFO']['endingMilepost']
    # issuingOrganization = wzConfig['INFO']['issuingOrganization']
    # creationDate = wzConfig['INFO']['creationDate']
    # updateDate = wzConfig['INFO']['updateDate']
    # isArchitecturalChange = wzConfig['INFO']['isArchitecturalChange']

def set_config_description(config_file):
    if config_file:
        startDate_split = wzStartDate.split('/')
        start_date = startDate_split[0] + '/' + startDate_split[1] + '/' + startDate_split[2]
        endDate_split = wzEndDate.split('/')
        end_date = endDate_split[0] + '/' + endDate_split[1] + '/' + endDate_split[2]
        config_description = '----Selected Config File----\nDescription: ' + wzDesc + '\nRoad Name: ' + roadName + \
            '\nDate Range: ' + start_date + ' to ' + end_date + '\nConfig Path: ' + os.path.relpath(config_file)
        logMsg('Configuration File Summary: \n' + config_description)
        msg['text'] = config_description
    else:
        msg['text'] = 'No config file found, please select a config file below'

def launch_WZ_veh_path_data_acq():
    root.destroy()
    window.quit()

def downloadBlob(local_blob_path, blobName):
    logMsg('Downloading blob: ' + blobName + ', from container: ' + container_name + ', to local path: ' + local_blob_path)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blobName)
    with open(local_blob_path, 'wb') as download_file:
        download_file.write(blob_client.download_blob().readall())

def downloadConfig():
    global local_config_path
    blobName = listbox.get(listbox.curselection())
    logMsg('Blob selected to download: ' + blobName)

    blob_full_name = blob_names_dict[blobName]

    #Check if unpublished work zone already exists, ask user if they want to overwrite
    file_found = False
    unapprovedContainer = 'unapprovedworkzones'
    unpublished_config_name = 'configurationfiles/' + blob_full_name
    try:
        temp_container_client = blob_service_client.get_container_client(unapprovedContainer)
        temp_blob_client = temp_container_client.get_blob_client(unpublished_config_name)
        props = temp_blob_client.get_blob_properties()
        logMsg('Blob: ' + unpublished_config_name + ', found in container: ' + unapprovedContainer)
        file_found = True
    except:
        logMsg('Blob: ' + unpublished_config_name + ', not found in container: ' + unapprovedContainer)
        pass
    if file_found:
        MsgBox = messagebox.askquestion('Work zone already exists','This Work zone already exists\nIf you continue you will overwrite the unpublished work zone data. Would you like to continue?',icon = 'warning')
        if MsgBox == 'no':
            logMsg('User denied overwrite of unapproved work zone data')
            return
        logMsg('User accepted overwrite of unapproved work zone data')

    local_blob_path = configDirectory + '/' + blobName
    local_config_path = local_blob_path

    downloadBlob(local_blob_path, blob_full_name)

    logMsg('Reading configuration file')
    try:
        configRead()

        abs_path = os.path.abspath(local_blob_path)
        logMsg('Setting configuration path: ' + abs_path)
        # local_config_file = abs_path
        set_config_description(local_blob_path)
        wzConfig_file.set(local_config_path)
        btnBegin['state']   = 'normal'                    #enable the start button for map building...
        btnBegin['bg']      = 'green'
    except Exception as e:
        logMsg('ERROR: Config read failed, ' + str(e))
        messagebox.showerror('Configuration File Reading Failed', 'Configuration file reading failed. Please load a valid configuration file')

def internet_on():
    url='http://www.google.com/'
    timeout=5
    try:
        _ = requests.get(url, timeout=timeout)
        return True
    except requests.ConnectionError:
        return False

def logMsg(msg):
    formattedTime = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S') + '+00:00'
    logFile.write('[' + formattedTime + '] ' + msg + '\n')

##
#   ---------------------------- END of Functions... -----------------------------------------
##
        
###
#   tkinter root window...
###

window = Tk()
window.title('Work Zone Data Collection')
window.geometry('1300x500')
root = Frame(width=1300, height=500)
root.place(x=0, y=0)
# root = Frame(window)
# root.place(x=0, y=0)
# root.configure(bg='white')

###
#   WZ config parser object....
###

wzConfig        = {}

###
#   --------------------------------------------------------------------------------------------------
###
#   Get current date and time...
###

cDT = datetime.datetime.now().strftime('%m/%d/%Y - ') + time.strftime('%H:%M:%S')

###
#   Map builder output log file...
###
logFileName = './data_collection_log.txt'
if os.path.exists(logFileName):
    append_write = 'a' # append if already exists
else:
    append_write = 'w' # make a new file if not
logFile = open(logFileName, append_write)         #log file
##logMsg ('\n *** - '+wzDesc+' - ***\n')
logMsg('*** Running Main UI ***')

if not internet_on():
    logMsg('Internet connectivity test failed, application exiting')
    messagebox.showerror('No internet connection was detected', 'The first component of this application requires an internet connection to function. Please reconnect and restart this application')
    sys.exit(0)
logMsg('Internet connectivity test succeeded')

try:
    java_version = subprocess.check_output(['java', '-version'], stderr=subprocess.STDOUT).decode('utf-8')
    version_number = java_version.splitlines()[0].split()[2].strip('"')
    major, minor, _ = version_number.split('.')
    if (int(major) == 1 and int(minor) >= 8) or int(major) >= 1:
        logMsg('Java version check successful. Java version detected was ' + major + '.' + minor)
    else:
        logMsg('ERROR: Incorrect java version. Java version detected was ' + major + '.' + minor)
        logMsg('Closing Application')
        logFile.close()
        messagebox.showerror('Java version incorrect', 'This application requires Java version >=1.8 or jdk>=8.0. Java version detected was ' + major + '.' + minor + ', please update your java version and add it to your system path')
        sys.exit(0)
except FileNotFoundError as e:
    logMsg('ERROR: Java installation not found')
    logMsg('Closing Application')
    logFile.close()
    messagebox.showerror('Java Not Installed', 'This application requires Java to run, with version >=1.8 or jdk>=8.0. Ensure that java is inatalled, added to the system path, and that you have restarted your command window')
    sys.exit(0)
except Exception as e:
    logMsg('ERROR: Unable to Verify Java Version, error: ' + str(e))
    messagebox.showwarning('Unable to Verify Java Version', 'Unable to verify java version. Ensure that you have Java version >=1.8 or jdk>=8.0 installed and added to your system path')
    
#############################################################################
# Tkinter LAYOUT to read user input for WZ config file name...
#############################################################################

# wzConfig_file = StringVar()
configDirectory = './Config Files'
local_config_path = ''

lbl_top = Label(root, text='Work Zone Data Collection\n', font='Helvetica 14', fg='royalblue', pady=10)
lbl_top.place(x=300, y=20)

# winSize = Label(root, height=15, width=100)
# winSize.place()

msg = Label(root, text='No config file found, please select a config file below',bg='slategray1',justify=LEFT,anchor=W,padx=10,pady=10, font=('Calibri', 12))
msg.place(x=100, y=80)


connect_str_env_var = 'AZURE_STORAGE_CONNECTION_STRING'
connect_str = os.getenv(connect_str_env_var)
if not connect_str:
    logMsg('ERROR: Failed to load connection string from environment variable: ' + connect_str_env_var)
    logFile.close()
    messagebox.showerror('Unable to retrieve azure credentials', 'Unable to Retrieve Azure Credentials:\nTo enable cloud connection, configure your \
    \nenvironment variables and restart your command window')
    sys.exit(0)
else:
    logMsg('Loaded connection string from environment variable: ' + connect_str_env_var)

download_file_path = './Config Files/local_config.json'
#print('\nDownloading blob to \n\t' + download_file_path)

blob_service_client = BlobServiceClient.from_connection_string(connect_str)
container_name = 'publishedconfigfiles'
container_client = blob_service_client.get_container_client(container_name)
#blob_client = blob_service_client.get_blob_client(container='', blob='')


logMsg('Listing blobs in container:' + container_name)
blob_list = container_client.list_blobs()

frame = Frame(root)
frame.place(x=100, y=200)

listbox = Listbox(frame, width=50, height=6, font=('Helvetica', 12), bg='white')
listbox.pack(side='left', fill='y')

scrollbar = Scrollbar(frame, orient='vertical')
scrollbar.config(command=listbox.yview)
scrollbar.pack(side='right', fill='y')

listbox.config(yscrollcommand=scrollbar.set)

now = datetime.datetime.now()
def getModTimeDelta(blob):
    time_delta = now-blob.last_modified.replace(tzinfo=None)
    return time_delta

blob_names_dict = {}
blobListSorted = []
for blob in blob_list:
    logMsg('Blob Name: ' + blob.name)
    blobListSorted.append(blob) #stupid line but this turns blob_list into a sortable list
blobListSorted.sort(key=getModTimeDelta) #reverse=True, #sort files on last_modified date
for blob in blobListSorted:
    blob_name = blob.name.split('/')[-1]
    if '.json' in blob_name:
        blob_names_dict[blob_name] = blob.name
        listbox.insert(END, blob_name)

logMsg('Blobs sorted, filtered and inserted into listbox')
load_config = Button(root, text='Load Cloud Configuration File', font='Helvetica 10', padx=5, command=downloadConfig)
load_config.place(x=100, y=320)

config_label_or = Label(root, text='OR', font='Helvetica 10', padx=5)
config_label_or.place(x=150, y=352)

diag_wzConfig_file = Button(root, text='Choose Local\nConfig File', command=inputFileDialog, anchor=W,padx=5, font='Helvetica 10')
diag_wzConfig_file.place(x=115,y=380)

wzConfig_file = StringVar()
wzConfig_file_name = Entry(root, relief=SUNKEN, state=DISABLED, textvariable=wzConfig_file, width=50)
wzConfig_file_name.place(x=220,y=390)

instructions = '''This component requires a good internet connection.
This is the configuration file selection component of the 
Work Zone Data Collection tool. To use the tool,
select a file from the list of punlished configuration files and
select 'Download Config'. When the correct configuration file
is selected and shown in the description box, select the
'Begin Data Collection' button to start data acquisition.
The data acquisition component does not require an internet connection
and will not record data until the set starting location is reached.'''
instr_label = Label(root, text=instructions,justify=CENTER, bg='slategray1',anchor=W,padx=10,pady=10, font=('Calibri', 12))
instr_label.place(x=700, y=100)

btnBegin = Button(root, text='Begin Data\nCollection', font='Helvetica 14',border=2,state=DISABLED,command=launch_WZ_veh_path_data_acq, anchor=W,padx=20,pady=10)
btnBegin.place(x=570,y=350)

def on_closing():
    logFile.close()
    sys.exit(0)

window.protocol("WM_DELETE_WINDOW", on_closing)

window.mainloop()


################################################################################################################
###
#--------------------------------------------------- WZ_VehPathDataAcq -----------------------------------------
###
################################################################################################################

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



###
#   Open output file for data logging...
###

logMsg('*** Running Vehicle Path Data Acquisition ***')

outDir      = './WZ_VehPathData'
vehPathDataFileName = 'path-data--' + wzDesc + '--' + roadName + '.csv'
vehPathDataFile = outDir + '/' + vehPathDataFileName
# wzConfig['FILES']['VehiclePathDataDir'] = os.path.abspath(outDir).replace('\\', '/')
# wzConfig['FILES']['VehiclePathDataFile'] = dataOutFileName

# root = Tk()
# root.title('Work Zone Data Collection - Vehicle Path Data Acquisition')
# root.geometry(str(max(800, totalLanes*110+350))+'x500')
# root = Frame(window)
# root.place(x=0, y=0)
window.geometry(str(max(800, totalLanes*110+350))+'x500')
root = Frame(width=max(800, totalLanes*110+350), height=500)
root.place(x=0, y=0)

# root.bind_all('<Key>', keyPress)                #key press event...


#############################################################################
#
# LAYOUT...
#
#############################################################################

lbl_top = Label(root, text='Vehicle Path Data Acquisition\n\n', font='Helvetica 14', fg='royalblue', pady=10)
lbl_top.place(x=300, y=20)

# winSize = Label(root, height=30, width=120) #width was 110
# winSize.pack()

laneLine = ImageTk.PhotoImage(Image.open('./images/verticalLine_thin.png'))
carImg = ImageTk.PhotoImage(Image.open('./images/caricon.png'))
carlabel = Label(root, image = carImg)
workersPresentImg = ImageTk.PhotoImage(Image.open('./images/workersPresentSign_small.png'))
laneClosedImg = ImageTk.PhotoImage(Image.open('./images/laneClosedSign_small.jpg'))

marginLeft = 100

laneBoxes = [0]*(totalLanes+1)
laneLabels = [0]*(totalLanes+1)
laneSymbols = [0]*(totalLanes+1)
laneLines = [0]*(totalLanes+1)
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

lanes = [0]*(totalLanes+1)
laneStat = [True]*(totalLanes+1) #all 8 lanes are open (default), Lane 0 is not used...


def createButton(id):
    global lanes
    lanes[id] = Button(root, text='Lane '+str(id), font='Helvetica 10', state=DISABLED, width=11, height=4, command=lambda:laneClicked(id))
    lanes[id].place(x=marginLeft+10 + (id-1)*110, y=300)

for i in range(1, totalLanes+1):
    createButton(i)


###
#   Mark Workers Present...
###

bWP = Button(root, text='Workers are\nPresent', font='Helvetica 10', state=DISABLED, width=11, height=4, command=lambda:workersPresentClicked())
bWP.place(x=marginLeft+60 + (totalLanes)*110, y=300)
###
#   Quit...
###


bStart = Button(root, text='Manually Start\nApplication', font='Helvetica 10', padx=5, bg='green', fg='white', command=startDataLog)
bStart.place(x=100, y=510)

bRef = Button(root, text='Manually Mark\nRef Pt', font='Helvetica 10', padx=5, bg='green', fg='white', command=markRefPt)
bRef.place(x=250, y=510)

bEnd = Button(root, text='Manually End\nApplication', font='Helvetica 10', padx=5, bg='red3', fg='gray92', command=stopDataLog)
bEnd.place(x=500, y=510)

# bQuit = Button(text='Quit (Esc)', font='Helvetica 10', fg = 'white', bg='red3',padx=5, command=gotQuit)
# bQuit.place(x=400,y=380)

###
#   Application Message Window...
###

appMsgWin = Button(root, text='Application Message Window...                                             ',      \
                font='Courier 10', justify=LEFT,anchor=W,padx=10,pady=10)
appMsgWin.place(x=50, y=390)


overlay = Label(root, text='Application will begin data collection\nwhen the set starting location has been reached', bg='gray', font='Calibri 28')
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


logMsg('Opening path data output file: ' + vehPathDataFile)
outFile     = open(vehPathDataFile,'w',newline='')
writeData   = csv.writer(outFile)

###
#   Write Title in the data logging file...
###

titleLine = 'GPS Date & Time','# of Sats','HDOP','Latitude','Longitude','Altitude(m)','Speed(m/s)','Heading(Deg)','Marker','Value'
writeCSVFile(titleLine)

###
#
#   -----------------------  Start Main Function  -----------------------------
#
###

window.protocol("WM_DELETE_WINDOW", on_closing)

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
# build_export_file = './WZ_BuildMsgs_and_Export.py'
# logMsg('Opening export script: ' + build_export_file + ', and closing data acquisition')
logMsg('Ending data acquisition')
# logFile.close()
root.destroy()
window.quit()
# subprocess.call([sys.executable, build_export_file], shell=True) #, shell=True
# os.system(build_export_file) #_------------------------------------------------------------ FAILED
# os.remove(local_config_path)
# sys.exit(0)
# root.mainloop()





# ------------------------------------------------------- WZ_BuildMsgs_and_Export --------------------------------------------------------
laneStat = []
wpStat = []

def inputFileDialog(filename):

    if len(filename):
        configRead(filename)
    pass

##
#   -------------- End of input_file_dialog ------------------
##

def buildWZMap(filename):
    global uper_failed
    global error
    global error_message
    
    startMainProcess()

    if msgSegList[0][0] == -1:                          #Segmentation failed...
        error = True
        error_message = 'Failed to build message segmentation'
        logMsg('Error in building message segmentation')
    elif uper_failed:   
        error = True
        error_message = 'Failed to run message builder UPER conversion'
        logMsg('UPER RSM Conversion failed\nEnsure Java is installed and\nadded to your system PATH')
    else:
        logMsg('WZ Map Completed Successfully\nReview map_builder.log file in WP_MapMsg Folder...')
    pass

def build_messages():
    global uper_failed
    global files_list
    
###
#   Data elements for 'common' container...
###

    msgID       = 33                                #RSM message ID is assigned as 33

###
#   Generate rendom eventID between 0 and 32767
###

    eventID     = '0000000'+str(hex(random.randint(0, 32767))).replace('0x','')     #randomly generated between 0 and 32767 in hex
    eventID     = eventID[len(eventID)-8:len(eventID)]                              #hex string of 4 octetes padded with 0 in the front

###
#   idList - message ID and Event Id
###

    idList      = [msgID,eventID]                           #msgID and eventID only. No stationId        


###
#   Set
#       WZ start date and time and end date and time in yyyy,mm,dd,hh,mm
#       UTC time offset
#       headway tolerance
#       road width - NOT used any more...
#       event length same as workzone length
###

    wzStart     = wzStartDate.split('/') + wzStartTime.split(':')
    wzEnd       = wzEndDate.split('/')   + wzEndTime.split(':')

    timeOffset  = -300                                      #UTC time offset in minutes for Eastern Time Zone
    hTolerance  = 20                                        #applicable heading tolerance set to 20 degrees (+/- 20deg?)

    roadWidth   = totalLanes*laneWidth*100                  #roadWidth in cm
    eventLength = wzLen                                     #WZ length in meters, computed earlier


###
#   Set speed limits in WZ as vehicle max speed..from user input saved in config file...
###

    speedLimit  = ['<vehicleMaxSpeed/>',speedList[0],speedList[1],speedList[2],'<mph/>']#NEW Version of XER... Nov. 2017

### -------------------------------------------------
#
#   BUILD XML (exer) file for 'Common Container'...
#
### -------------------------------------------------

###
#
#   Build multiple .exer (XML) files for segmented message.
#   Build one file for each message segment
#
#   Created June, 2018
#
####

    currSeg = 1                                             #current message segment
    totSeg  = msgSegList[0][0]                              #total message segments
    rsmSegments = []
        
    wzdx_outFile = './WZ_MapMsg/WZDx_File-' + ctrDT + '.geojson'
    logMsg('WZDx output file path: ' + wzdx_outFile)
    wzdxFile = open(wzdx_outFile, 'w')
    files_list.append(wzdx_outFile)
    
    devnull = open(os.devnull, 'w')

    while currSeg <= totSeg:                                #repeat for all segments

###
### Create and open output xml file...
###
       
        ##xml_outFile = './WZ_XML_File/RSZW_MAP_xmlFile-' + str(currSeg)+'_of_'+str(totSeg)+'.exer'
        xml_outFile = './WZ_MapMsg/RSZW_MAP_xml_File-' + ctrDT + '-' + str(currSeg)+'_of_'+str(totSeg)+'.xml'
        logMsg('RSM XML output file path: ' + xml_outFile)
        uper_outFile = './WZ_MapMsg/RSZW_MAP_xml_File-' + ctrDT + '-' + str(currSeg)+'_of_'+str(totSeg)+'.uper'
        logMsg('RSM UPER output file path: ' + uper_outFile)
        xmlFile = open(xml_outFile, 'w')
        files_list.append(xml_outFile)
        files_list.append(uper_outFile)
    
###
#   Write initial xml lines in the output xml file...
#   Introductory lines...
###
      
        # xmlFile.write ('<?xml version=\'1.0\' encoding=\'UTF-8\'?>\n' + \
        #                '<!-- \n' + \
        #                '\t CAMP xml file for RSZW/LC Mapping Project\n' + \
        #                '\t Message segment file '+ str(currSeg)+' of '+str(totSeg)+'...\n\n' + \
        #                '\t Version 1.5 - June, 2018\n' + \
        #                '\t for RSMv5.1 ASN\n' + \
        #                '\t File Name: '+xml_outFile+'\n' + \
        #                '\t Created: '+cDT+'\n\n-->\n')

###
#   Build common container...
#
#   Update refPoint to a new value for different message segment > 1.
#   Since the distance between the original reference point and the first node for message segment 2 to the last segment could be 
#   too far apart (xyz_offset) to be represented in just one offset node. To alleviate the issue, for every segment, a new reference
#   point is set as follows:
#
#   1st segment   - Original marked reference point
#   2..n segments - Use first set of node points and select for the open lane for which vehicle path data is collected.
#                   The first set of node points are the same as the last set of node points of of the previous segment.
#                   They are repeated for map matching purpose
###

        startNode = 1
        if currSeg == startNode:    
            newRefPt = refPoint
        else:
            dL = (dataLane - 1) * 4                                 #location pinter in wzMapPt list
            startNode = msgSegList[currSeg+1][1]                    #wz start node, index in wzMapPt is startNode-1 
            newRefPt  = (wzMapPt[startNode-1][dL+0],wzMapPt[startNode-1][dL+1],wzMapPt[startNode-1][dL+2])
        pass


###
#   Build xml for common container...
###
        # build_xml_CC (xmlFile,idList,wzStart,wzEnd,timeOffset,c_sc_codes,newRefPt,appHeading,hTolerance, \
        #               speedLimit,roadWidth,eventLength,laneStat,appMapPt,msgSegList,currSeg,wzDesc)
        commonContainer = build_xml_CC (xmlFile,idList,wzStart,wzEnd,timeOffset,wzDaysOfWeek,c_sc_codes,newRefPt,appHeading,hTolerance, \
                      speedLimit,laneWidth,roadWidth,eventLength,laneStat,appMapPt,msgSegList,currSeg,wzDesc)

        #if currSeg == 1:
            #logMsg('\n ---Constructed Approach Lane Node Points/Lane: '+str(len(appMapPt))+'\t(Must between 2 and 63)')
            #logMsg('\n ---Message Segmentation for Work Zone Lanes')        
        #pass

        #logMsg('\t ---Segment#: '+str(currSeg)+'Start Node#: '+str(startNode)+'\n\t\t New Ref. Pt: '+str(newRefPt))

###
#       WZ length, LC characteristic, workers present, etc. 
###
    
        wpFlag  = 0                         #Workers present flag, 0=no, 1=yes   NOT Used in RSM (was for BIM)
        RN      = False                     #Boolean - True: Generate reduced nodes for closed lanes
                                            #        - False: Generate all nodes for closed lanes
###
#   Build WZ container
###
        # build_xml_WZC (xmlFile,speedLimit,laneWidth,laneStat,wpStat,wzMapPt,RN,msgSegList,currSeg)
        rszContainer = build_xml_WZC (xmlFile,speedLimit,laneWidth,laneStat,wpStat,wzMapPt,RN,msgSegList,currSeg)

        rsm = {}
        rsm['MessageFrame'] = {}
        rsm['MessageFrame']['messageId'] = idList[0]
        rsm['MessageFrame']['value'] = {}
        rsm['MessageFrame']['value']['RoadsideSafetyMessage'] = {}
        rsm['MessageFrame']['value']['RoadsideSafetyMessage']['version'] = 1
        rsm['MessageFrame']['value']['RoadsideSafetyMessage']['commonContainer'] = commonContainer
        rsm['MessageFrame']['value']['RoadsideSafetyMessage']['rszContainer'] = rszContainer

        rsmSegments.append(rsm)

        rsm_xml = xmltodict.unparse(rsm, short_empty_elements=True, pretty=True, indent='  ')
        xmlFile.write(rsm_xml)

    
###
#   Done, finito, close files
###   

        xmlFile.close()
        subprocess.call(['java', '-jar', './CVMsgBuilder v1.4 distribution/dist_xmltouper/CVMsgBuilder_xmltouper_v8.jar', str(xml_outFile), str(uper_outFile)],stdout=devnull)
        if not os.path.exists(uper_outFile) or os.stat(uper_outFile).st_size == 0:
            logMsg('ERROR: RSM UPER conversion FAILED, ensure that you have java installed (>=1.8 or jdk>=8) and added to your system path')
            messagebox.showerror('RSM Binary conversion FAILED', 'RSM Binary (UPER) conversion failed\nEnsure that you have java installed (version>=1.8 or jdk>=8) and added to your system path\nThen run WZ_BuildMsgs_and_Export.pyw')
            logMsg('Exiting Application')
            logFile.close()
            sys.exit(0)

        currSeg = currSeg+1
    pass
    info = {}
    info['road_name'] = roadName
    # info['road_number'] = roadNumber
    # info['beginning-cross_street'] = beginningCrossStreet
    # info['ending_cross_street'] = endingCrossStreet
    # info['beginning_milepost'] = beginningMilepost
    # info['ending_milepost'] = endingMilepost
    # info['issuing_organization'] = issuingOrganization
    # info['creation_date'] = creationDate
    # info['update_date'] = updateDate
    # info['is_architectural_change'] = isArchitecturalChange
    logMsg('Converting RSM XMl to WZDx message')
    wzdx = wzdx_creator(rsmSegments, dataLane, info)
    wzdxFile.write(json.dumps(wzdx, indent=2))
    wzdxFile.close()

###
#   May want to print WZ length per segment and total WZ length...
###

    logMsg('--- Done Building WZ MAP ---')
    #logFile.close()    

###
#   > > > > > > > > > > > START MAIN PROCESS < < < < < < < < < < < < < < <
###

def startMainProcess():

    global  vehPathDataFile                                         #collected vehicle path data file name
    global  refPtIdx                                                #data point number where reference point is set
    global  wzLen                                                   #work zone length in meters
    global  wzMapLen                                                #Mapped approach and wz lane length in meters
    global  appHeading                                              #approach heading

    global  msgSegList                                              #WZ message segmentation list
##  global  wzMapBuiltSuccess                                       #WZ map built successful or not flag
##  wzMapBuiltSuccess = False                                       #Default set to False                                  
    
    totRows = len(list(csv.reader(open(vehPathDataFile)))) - 1      ###total records or lines in file

    logMsg('*** - '+wzDesc+' - ***')    
    logMsg('--- Processing Input File: '+vehPathDataFile+', Total input lines: '+str(totRows))

###
#
#   Call function to read and parse the vehicle path data file created by the 'vehPathDataAcq.pyw'
#   to build vehicle path data array, lane status and workers presence status arrays.
#
#   refPtIdx, wzLen and appHeading values are returned in atRefPoint list...
#
#   Updated on Aug. 23, 2018
#   
###

    atRefPoint  = [0,0,0]                                           #temporary list to hold return values from function below 
    buildVehPathData_LaneStat(vehPathDataFile,totalLanes,pathPt,laneStat,wpStat,refPoint,atRefPoint,sampleFreq)

    refPtIdx    = atRefPoint[0]
    wzLen       = atRefPoint[1]
    appHeading  = atRefPoint[2]

    logMsg(' --- Start of Work Zone at Data Point: '+str(refPtIdx))
    logMsg('Reference Point @ '+refPoint[0]+', '+refPoint[1]+', '+refPoint[2])

    

###
#   ====================================================================================================
###
#    -----  Read and processed vehPathDataFile
#           Compiled pathPt, reference point and lane closures  -----
###
###
#   Function to populate Approach Lane Map points...
#
#   refPtIdx determined in the above function...
###

###
#   'laneType'              1 = Approach lanes, 2 = wz Lanes for mapping
#   'pathPt'                contains list of data points collected by driving the vehicle on one open WZ lane
#   'appMapPt/wzMapPt'      constructed node list for lane map for BIM (RSM)
#                           contains lat,lon,alt,lcloStat for each node, each lane + heading + WP flag + distVec (dist from prev. node)
#   'lanePadApp/lanePadWz'  lane padding in addition to laneWidth
#   'refPtIdx'              Data location of the reference point in pathPt array
#   'laneStat'              A two-dimensional list to hold lane status, 0=open, 1=closed.
#                               Generated from lane closed/opened marker from collected data
#                               List location [0,0,0] provides total number of lanes
#                               It holds for each lane closed/opened instance, data point index, lane number and lane status (1/0)
#   'wpStat'                list containing location where 'workers present' is set/unset
#   'dataLane'              Lane on which the vehicle path data for wz mapping was collected.
#                               'dataLane' is used to derive map data for the adjacent lanes. One lane to the left of the 'dataLane' and one to right in
#                               case of total 3 lanes. For more than 5 lanes, data from multiple lanes to be collected to create map for adjascent lanes
#   'laneWidth'             lane width in meters
#
#   For approach lanes, map for all lanes are created
#
#   For wz lanes, node points for map for all lanes including closed lanes are created.
#
###

    wzMapLen = [0,0]                                    #both approach and wz mapped length
    laneType = 1                                        #approach lanes
    getLanePt(laneType,pathPt,appMapPt,laneWidth,lanePadApp,refPtIdx,appMapPtDist,laneStat,wpStat,dataLane,wzMapLen)

    logMsg(' --- Mapped Approach Lanes: '+str(int(wzMapLen[0]))+' meters')

    
###
#
#   Now repeat the above for WZ map data point array starting from the ref point until end of the WZ
#   First WZ map point closest to the reference point is the next point after the ref. point.
#
###
    
    laneType    = 2                                     #wz lanes
    getLanePt(laneType,pathPt,wzMapPt,laneWidth,lanePadWZ,refPtIdx,wzMapPtDist,laneStat,wpStat,dataLane,wzMapLen)

    logMsg(' --- Mapped Work zone Lanes: '+str(int(wzMapLen[1]))+' meters')


###
#   print/log lane status and workers present/not present status...
###

    laneStatIdx = len(laneStat)
    if laneStatIdx > 1:                               #have lane closures...NOTE: Index 0 location is dummy value...
        logMsg(' --- Start/End of lane closure Offset from the reference point ---')
        for L in range(1, laneStatIdx):
            stat = 'Start'
            if laneStat[L][2] == 0: stat = 'End'
            logMsg('\t '+stat+' of lane '+str(laneStat[L][1])+' closure, at data point: '+str(laneStat[L][0])+', Offset: '+ \
                           str(int(laneStat[L][3]))+' meters')
        pass
    pass                                            

###
#       Do for workers present/not present zone?          
###
    wpStatIdx = len(wpStat)    
    if wpStatIdx > 0:                                       #have workers present/not present
        logMsg(' --- Start/End of workers present offset from the reference point ---')
        for w in range(0, wpStatIdx):
            stat = 'End'
            if wpStat[w][1] == 1:  stat = 'Start'
            logMsg('\t '+stat+' of workers present @ data point: '+str(wpStat[w][0])+  \
                           ', Offset: '+str(wpStat[w][2])+' meters')
        pass
    pass                                            

###
#   Get nodes list for each segmented message in message segmentation...
#
#   Following revised to address error in generating message segmentation
#       Revised - Jan. 22, 2019
#
#       If computed nodes per approach lane is > computed nodes per lane (Approach nodes/lane + min. 2 nodes for WZ lane in 1st segment)
#       msgSegList[0][0] is set to -1 indicating error in generating segmentation.
#
###

    msgSegList = buildMsgSegNodeList(len(appMapPt),len(wzMapPt),totalLanes)     #build message segment list

    if msgSegList[0][0] == -1:                                                  #Error
        ANPL = msgSegList[1][2]
        MNPL = msgSegList[0][1]
        logMsg('ERROR: MESSAGE SEGMENTATION FAILED')
        logMsg('\tThe 1st message segment must be able to include all nodes for approach lane plus at atleast first 2 nodes of WZ lane')
        logMsg('\tNodes per approach lane: '+str(ANPL)+' > allowed max nodes per lane: ' +str(MNPL)+' to stay within message payload size\n\t')
        logMsg('\tThe 1st message segment must be able to include all nodes for approach lane')
        logMsg('\tReduce length of vehicle path data for approach lane to no more than 1km and try again')
        messagebox.showerror('MESSAGE SEGMENTATION ERROR', 'Reduce length of vehicle path data for approach lane to no more than 1km and try again')
        # TODO: Fix this error/make this never happen. throw away some data from start of approach region?
        logFile.close()
        sys.exit(0)
        #logFile.close()                                                         #stopping the program, close file so eror message is saved...
        return                                                                  #return to caller                  

    else:    

        ANPL    = msgSegList[1][2]                                              #Approach lane Nodes Per Lane
        WZNPL   = msgSegList[len(msgSegList)-1][2]                              #Work zone lane Nodes Per Lane
        TNPL    = ANPL + WZNPL
        MS      = msgSegList[0][0]                                              #Constructed message segments
        NPL     = msgSegList[0][1]                                              #no of Nodes Per Lane
        logMsg('Total Nodes per Lane: ' +str(TNPL))
        logMsg('Total Nodes per Approach Lane: '+str(ANPL))
        logMsg('Total Nodes per WZ Lane: '  +str(WZNPL))
        logMsg('Total message segment(s): '  +str(MS))
        logMsg('Nodes per Message Segment: '+str(NPL))
        logMsg('Message segment list: '  +str(msgSegList))
    pass

###
#   Build XML File...
###
    logMsg('Building messages')
    build_messages()

def uploadArchive():
    if internet_on():
        logMsg('Creating blob in azure: ' + zip_name + ', in container: ' + container_name)
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=zip_name)
        logMsg('Uploading zip archive to blob')
        with open(zip_name, 'rb') as data:
            blob_client.upload_blob(data, overwrite=True)
        logMsg('Closing log file in Message Builder and Export')
        logFile.close()
        messagebox.showinfo('Upload Successful', 'Data upload successful! Please navigate to\nhttp://www.neaeraconsulting.com/V2x_Verification\nto view and verify the mapped workzone.\nYou will find your data under\n' + name_id)
        sys.exit(0)

    else:
        logMsg('Attempted uploadArchive, no internet connection detected')
        messagebox.showerror('No Internet Cnnection', 'No internet connection detected\nConnect and try again')


# root = Tk()
# root.title('Work Zone Data Export and Upload')
# root.geometry('400x300')
window.geometry('400x300')
root = Frame(width=400, height=300)
root.place(x=0, y=0)

load_config = Button(root, text='Upload Data\nFiles', state=DISABLED, font='Helvetica 20', padx=5,command=uploadArchive)
load_config.place(x=100, y=100)

loading_label = Label(root, text='Processing Data', font='Helvetica 28', bg='gray', padx=5)
loading_label.place(x=60, y=120)
##############################################################################################
#
# ---------------------------- Automatically Export Files ------------------------------------
#
###############################################################################################
# local_config_path = './Config Files/ACTIVE_CONFIG.json'

# openLog()
logMsg('*** Running Message Builder and Export ***')

# logMsg('Loading configuration file from local path: ' + local_config_path)
# configRead()

def do_stuff():
    global zip_name
    global name_id
    global blob_service_client
    global container_name
    startMainProcess()
    files_list.append(vehPathDataFile)
    files_list.append(local_config_path)

    description = wzDesc.lower().strip().replace(' ', '-')
    road_name = roadName.lower().strip().replace(' ', '-')
    name_id = description + '--' + road_name
    logMsg('Work zone name id: ' + name_id)
    zip_name = 'wzdc-exports--' + name_id + '.zip'
    logMsg('Creating zip archive: ' + zip_name)

    zipObj = zipfile.ZipFile(zip_name, 'w')

    for filename in files_list:
        name = filename.split('/')[-1]
        name_orig = name
        name_wo_ext = name[:name.rfind('.')]
        if '.csv' in filename.lower():
            name = 'path-data--' + name_id + '.csv'
        elif '.json' in filename.lower():
            name = 'config--' + name_id + '.json'
        elif '.xml' in filename.lower():
            number = name[name.rfind('-')+1:name.rfind('.')]
            name = 'rsm-xml--' + name_id + '--' + number + '.xml'
        elif '.uper' in filename.lower():
            number = name[name.rfind('-')+1:name.rfind('.')]
            name = 'rsm-uper--' + name_id + '--' + number + '.uper'
        elif '.geojson' in filename.lower():
            name = 'wzdx--' + name_id + '.geojson'
        else:
            continue
        logMsg('Adding file to archive: ' + filename + ', as: ' + name)
        zipObj.write(filename, name)

    # close the Zip File
    zipObj.close()

    logMsg('Removing local configuration file: ' + local_config_path)
    # os.remove(local_config_path)

    connect_str_env_var = 'AZURE_STORAGE_CONNECTION_STRING'
    connect_str = os.getenv(connect_str_env_var)
    #print('\nDownloading blob to \n\t' + download_file_path)
    logMsg('Loaded connection string from environment variable: ' + connect_str_env_var)
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    # container_client = blob_service_client.get_container_client('unzippedworkzonedatauploads')
    container_name = 'workzonedatauploads'
    load_config['bg'] = 'green'
    load_config['state']= NORMAL
    loading_label.destroy()

root.after(500, do_stuff)

# root.protocol("WM_DELETE_WINDOW", on_closing)

window.mainloop()