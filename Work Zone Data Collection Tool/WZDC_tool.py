#!/usr/bin/env python3

import  os.path
import  sys
import  subprocess
import  re

import  csv                                             #csv file processor
import  datetime                                        #Date and Time methods...
import  time                                            #do I need time???
import  math                                            #math library for math functions
import  random                                          #random number generator
import  json                                            #json manipulation
import  shutil
import  requests
import  urllib.request
import  serial                                  #serial communication
import  io                                      #serial i/o function
import  string                                  #string functions
import  csv                                     #CSV file read/write
import  serial.tools.list_ports                      #used to enumerate COMM ports
from    serial import SerialException           #serial port exception
import  base64

import  zipfile
import  xmltodict                                       #dict to xml converter

from    azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

# from    tkinter         import *   
from    tkinter         import Button, Tk, Frame, Label, LEFT, W, IntVar, StringVar, Radiobutton, CENTER, Listbox, Scrollbar, END, Entry, SUNKEN, DISABLED, OptionMenu, NORMAL
from    tkinter         import messagebox
from    tkinter         import filedialog
from    PIL             import ImageTk, Image

from    parseNMEA       import parseGxGGA           #parse GGA for Time, Alt, #of Satellites
from    parseNMEA       import parseGxRMC           #parse RMC for Date, Lat, Lon, Speed, Heading
from    parseNMEA       import parseGxGSA           #parse GSA for Hdop

sys.path.append('..')
from    Translators.rsm_2_wzdx_translator   import wzdx_creator         #RSM to WZDx Translator


# TODO: Upload updated configuration file
# TODO: Consider uploading ZIP archive of CSV and config file (if updated)


# Load local configuration file
def inputFileDialog():
    global local_config_path
    global local_updated_config_path
    filename = filedialog.askopenfilename(initialdir=configDirectory, title="Select Input File", filetypes=[("Config File","*.json")])
    if len(filename): 
        local_config_path = filename
        local_updated_config_path = local_config_path.replace(json_ext, '_updated.json')
        logMsg('Reading configuration file')
        try:
            configRead()

            logMsg('Setting configuration path: ' + local_config_path)
            # local_config_file = abs_path
            set_config_description(local_config_path)
            wzConfig_file.set(local_config_path)
        except Exception as e:
            print(e)
            logMsg('ERROR: Config read failed, ' + str(e))
            messagebox.showerror('Configuration File Reading Failed', 'Configuration file reading failed. Please load a valid configuration file')
    pass

# Open and read config file
def configRead():
    global wzConfig
    file = local_config_path
    if os.path.exists(file):
        cfg = open(file, 'r+')
        wzConfig = json.loads(cfg.read())
        getConfigVars()
        # update_config(cfg)
        cfg.close()

# Read configuration file
def getConfigVars():

###
#   Following are global variables are later used by other functions/methods...
###

    # WZDx Feed Info ID
    global  feed_info_id
    
    # General Information
    global  wzDesc                                          #WZ Description
    global  roadName
    global  roadNumber
    global  direction
    global  beginningCrossStreet
    global  endingCrossStreet
    global  beginningMilepost
    global  endingMilepost
    global  eventStatus
    global  creationDate
    global  updateDate

    # Types of Work
    global  typeOfWork

    # Lane Information
    global  totalLanes                                      #total number of lanes in wz
    global  laneWidth                                       #average lane width in meters
    global  lanePadApp                                      #approach lane padding in meters
    global  lanePadWZ                                       #WZ lane padding in meters
    global  dataLane                                        #lane used for collecting veh path data
    global  lanes_obj

    # Speed Limits
    global  speedList                                       #speed limits

    # Cause Codes
    global  c_sc_codes                                      #cause/subcause code

    # Schedule
    global  startDateTime
    global  wzStartDate                                     #wz start date
    global  wzStartTime                                     #wz start time
    global  startDateAccuracy
    global  endDateTime
    global  wzEndDate                                       #wz end date
    global  wzEndTime                                       #wz end time
    global  endDateAccuracy
    global  wzDaysOfWeek                                    #wz active days of week

    # Location
    global  wzStartLat                                     #wz start date
    global  wzStartLon                                     #wz start time
    global  beginingAccuracy
    global  wzEndLat                                       #wz end date
    global  wzEndLon                                       #wz end time
    global  endingAccuracy
    
    # WZDx Metadata
    global  wzLocationMethod
    global  lrsType
    global  locationVerifyMethod
    global  dataFeedFrequencyUpdate
    global  timestampMetadataUpdate
    global  contactName
    global  contactEmail
    global  issuingOrganization

    # Image Info
    global  mapImageZoom
    global  mapImageCenterLat
    global  mapImageCenterLon
    global  mapImageMarkers
    global  marker_list
    global  mapImageMapType
    global  mapImageHeight
    global  mapImageWidth
    global  mapImageFormat
    global  mapImageString

    global  mapFailed
    
    feed_info_id            = wzConfig['FeedInfoID']

    wzDesc                  = wzConfig['GeneralInfo']['Description']
    roadName                = wzConfig['GeneralInfo']['RoadName']
    roadNumber              = wzConfig['GeneralInfo']['RoadNumber']
    direction               = wzConfig['GeneralInfo']['Direction']
    beginningCrossStreet    = wzConfig['GeneralInfo']['BeginningCrossStreet']
    endingCrossStreet       = wzConfig['GeneralInfo']['EndingCrossStreet']
    beginningMilepost       = wzConfig['GeneralInfo']['BeginningMilePost']
    endingMilepost          = wzConfig['GeneralInfo']['EndingMilePost']
    eventStatus             = wzConfig['GeneralInfo']['EventStatus']
    creationDate            = wzConfig['GeneralInfo'].get('CreationDate', '')
    updateDate              = wzConfig['GeneralInfo'].get('UpdateDate', datetime.datetime.now().strftime(time_format_iso))

    typeOfWork = wzConfig['TypesOfWork']
    if not typeOfWork: typeOfWork = []

    totalLanes              = int(wzConfig['LaneInfo']['NumberOfLanes'])           #total number of lanes in wz
    laneWidth               = float(wzConfig['LaneInfo']['AverageLaneWidth'])      #average lane width in meters
    lanePadApp              = float(wzConfig['LaneInfo']['ApproachLanePadding'])   #approach lane padding in meters
    lanePadWZ               = float(wzConfig['LaneInfo']['WorkzoneLanePadding'])   #WZ lane padding in meters
    dataLane                = int(wzConfig['LaneInfo']['VehiclePathDataLane'])     #lane used for collecting veh path data
    lanes_obj               = list(wzConfig['LaneInfo']['Lanes'])

    speedList               = wzConfig['SpeedLimits']['NormalSpeed'], wzConfig['SpeedLimits']['ReferencePointSpeed'], \
                              wzConfig['SpeedLimits']['WorkersPresentSpeed']

    c_sc_codes              = [int(wzConfig['CauseCodes']['CauseCode']), int(wzConfig['CauseCodes']['SubCauseCode'])]

    startDateTime           = wzConfig['Schedule']['StartDate']
    wzStartDate             = datetime.datetime.strptime(startDateTime, time_format_iso).strftime("%m/%d/%Y")
    wzStartTime             = datetime.datetime.strptime(startDateTime, time_format_iso).strftime("%H:%M")
    startDateAccuracy       = wzConfig['Schedule'].get('StartDateAccuracy', 'estimated')
    endDateTime             = wzConfig['Schedule']['EndDate']
    wzEndDate               = datetime.datetime.strptime(endDateTime, time_format_iso).strftime("%m/%d/%Y")
    wzEndTime               = datetime.datetime.strptime(endDateTime, time_format_iso).strftime("%H:%M")
    endDateAccuracy         = wzConfig['Schedule'].get('EndDateAccuracy', 'estimated')
    wzDaysOfWeek            = wzConfig['Schedule']['DaysOfWeek']

    wzStartLat              = wzConfig['Location']['BeginningLocation']['Lat']
    wzStartLon              = wzConfig['Location']['BeginningLocation']['Lon']
    beginingAccuracy        = wzConfig['Location']['BeginningAccuracy']
    wzEndLat                = wzConfig['Location']['EndingLocation']['Lat']
    wzEndLon                = wzConfig['Location']['EndingLocation']['Lon']
    endingAccuracy          = wzConfig['Location']['EndingAccuracy']

    wzLocationMethod        = wzConfig['metadata']['wz_location_method']
    lrsType                 = wzConfig['metadata']['lrs_type']
    locationVerifyMethod    = wzConfig['metadata']['location_verify_method']
    dataFeedFrequencyUpdate = wzConfig['metadata']['datafeed_frequency_update']
    timestampMetadataUpdate = wzConfig['metadata']['timestamp_metadata_update']
    contactName             = wzConfig['metadata']['contact_name']
    contactEmail            = wzConfig['metadata']['contact_email']
    issuingOrganization     = wzConfig['metadata']['issuing_organization']

    mapImageZoom            = wzConfig['ImageInfo']['Zoom']
    mapImageCenterLat       = wzConfig['ImageInfo']['Center']['Lat']
    mapImageCenterLon       = wzConfig['ImageInfo']['Center']['Lon']
    mapImageMarkers         = wzConfig['ImageInfo']['Markers'] # Markers:List of {Name, Color, Location {Lat, Lon, ?Elev}}
    marker_list = []
    for marker in mapImageMarkers:
        marker_list.append("markers=color:" + marker['Color'].lower() + "|label:" + marker['Name'] + "|" + str(marker['Location']['Lat']) + "," + str(marker['Location']['Lon']) + "|")
    mapImageMapType         = wzConfig['ImageInfo']['MapType']
    mapImageHeight          = wzConfig['ImageInfo']['Height']
    mapImageWidth           = wzConfig['ImageInfo']['Width']
    mapImageFormat          = wzConfig['ImageInfo']['Format']
    mapImageString          = wzConfig['ImageInfo']['ImageString']

    if mapImageString:
        try:
            fh = open(mapFileName, "wb")
            fh.write(base64.b64decode(mapImageString))
            fh.close()
            mapFailed = False
        except:
            shutil.copy(map_failed_img, mapFileName)
            mapFailed = True
    else:
        shutil.copy(map_failed_img, mapFileName)
        mapFailed = True
 
# Set description box in UI from config file
def set_config_description(config_file):
    global isConfigReady
    global autoRadioButton
    global manualRadioButton

    if config_file:
        startDate_split = wzStartDate.split('/')
        start_date = startDate_split[0] + '/' + startDate_split[1] + '/' + startDate_split[2]
        endDate_split = wzEndDate.split('/')
        end_date = endDate_split[0] + '/' + endDate_split[1] + '/' + endDate_split[2]
        config_description = '----Selected Config File----\nDescription: ' + wzDesc + '\nRoad Name: ' + roadName + \
            '\nDate Range: ' + start_date + ' to ' + end_date + '\nConfig Path: ' + os.path.relpath(config_file)
        logMsg('Configuration File Summary: \n' + config_description)
        msg['text'] = config_description
        msg['fg'] = 'black'
        isConfigReady = True
        updateMainButton()
        
        if wzStartLat and wzEndLat:
            autoRadioButton['state'] = NORMAL
            # v.set(1)
        else:
            autoRadioButton['state'] = DISABLED
            v.set(2)
    else:
        msg['text'] = 'NO CONFIGURATION FILE SELECTED'
        msg['fg'] = 'red'

# Move on to data collection/acquisition
def launch_WZ_veh_path_data_acq():
    global needsImage
    global configUpdated
    global manualDetection
    global wzStartLat
    global wzStartLon
    global wzEndLat
    global wzEndLon

    # If mamual detection:
    if v.get() == 2:
        manualDetection = True
        configUpdated = True
        needsImage = True
        wzStartLat = 0
        wzStartLon = 0
        wzEndLat = 0
        wzEndLon = 0

    root.destroy()
    window.quit()

# Download blobl from Azure blob storage
def downloadBlob(local_blob_path, blobName):
    logMsg('Downloading blob: ' + blobName + ', from container: ' + container_name + ', to local path: ' + local_blob_path)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blobName)
    with open(local_blob_path, 'wb') as download_file:
        download_file.write(blob_client.download_blob().readall())

# Download configuration file from Azure blob storage and read file
def downloadConfig():
    global local_config_path
    global local_updated_config_path
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
    local_updated_config_path = local_config_path.replace(json_ext, '_updated.json')

    downloadBlob(local_blob_path, blob_full_name)

    logMsg('Reading configuration file')
    try:
        configRead()

        abs_path = os.path.abspath(local_blob_path)
        logMsg('Setting configuration path: ' + abs_path)
        # local_config_file = abs_path
        set_config_description(local_blob_path)
        wzConfig_file.set(local_config_path)
    except Exception as e:
        logMsg('ERROR: Config read failed, ' + str(e))
        print(e)
        messagebox.showerror('Configuration File Reading Failed', 'Configuration file reading failed. Please load a valid configuration file')

# Check internet connectivity by pinging google.com
def internet_on():
    url='http://www.google.com/'
    timeout=5
    try:
        _ = requests.get(url, timeout=timeout)
        return True
    except requests.ConnectionError:
        return False

# Format and log emssage to file
def logMsg(msg):
    formattedTime = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S') + '+00:00'
    try:
        logFile.write('[' + formattedTime + '] ' + msg + '\n')
    except:
        pass

# Enable/disable Begin Data Collection button
def updateMainButton():
    if isConfigReady and isGPSReady:
        btnBegin['state']   = 'normal'
        btnBegin['bg']      = 'green'
    else:
        btnBegin['state']   = 'disabled'
        btnBegin['bg']     = '#F0F0F0'

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

needsImage = False
configUpdated = False
manualDetection = False
mapFailed = False

json_ext = '.json'
geojson_ext = '.geojson'
uper_ext = '.uper'
xml_ext = '.xml'

time_format_iso = "%Y-%m-%dT%H:%M:%SZ"

map_failed_img = './images/map_failed.png'
helvetica_14 = 'Helvetica 14'
choose_local_config = 'Choose Local\nConfig File'

###
#   WZ config parser object....
###

wzConfig        = {}

cDT = datetime.datetime.now().strftime('%m/%d/%Y - ') + time.strftime('%H:%M:%S')

# Output log file
logFileName = './data_collection_log.txt'
if os.path.exists(logFileName):
    append_write = 'a' # append if already exists
else:
    append_write = 'w' # make a new file if not
logFile = open(logFileName, append_write)         #log file
logMsg('*** Running Main UI ***')

# Check java version for RSM binary conversion
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

configDirectory = './Config Files'
local_config_path = ''
local_updated_config_path = ''
isConfigReady = False

lbl_top = Label(root, text='Work Zone Data Collection\n', font=helvetica_14, fg='royalblue', pady=10)
lbl_top.place(x=550, y=10)

msg = Label(root, text='NO CONFIGURATION FILE SELECTED',bg='slategray1', fg='red',justify=LEFT,anchor=W,padx=10,pady=10, font=('Calibri', 12))
msg.place(x=100, y=80)



# Retrieve zure cloud connection string from environment variable
connect_str_env_var = 'AZURE_STORAGE_CONNECTION_STRING'
connect_str = os.getenv(connect_str_env_var)
has_azure_connection = False
if not connect_str:
    has_azure_connection = False
    logMsg('Error: Failed to load connection string from environment variable: ' + connect_str_env_var)
    # logFile.close()

    # messagebox.showerror('Unable to retrieve azure credentials', 'Unable to Retrieve Azure Credentials:\nTo enable cloud connection, configure your \
    # \nenvironment variables and restart your command window')
    # sys.exit(0)
else:
    has_azure_connection = True
    logMsg('Loaded connection string from environment variable: ' + connect_str_env_var)

download_file_path = './Config Files/local_config.json'
mapFileName = "./mapImage.png"
refreshImg = ImageTk.PhotoImage(Image.open('./images/refresh_small.png'))

def loadCloudContent():
    global blob_service_client
    global blob_names_dict
    global container_name

    global frame
    global listbox
    global load_config
    global config_label_or
    global diag_wzConfig_file

    global wzConfig_file
    global wzConfig_file_name

    try:
        frame.destroy()
        listbox.destroy() #?
        load_config.destroy()
        config_label_or.destroy()
        diag_wzConfig_file.destroy()
        wzConfig_file_name.destroy()
    except:
        try:
            config_label_or.destroy()
            diag_wzConfig_file.destroy()
            wzConfig_file_name.destroy()
        except:
            pass


    # If internet connection detected, load cloud config files
    if internet_on() and has_azure_connection:
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
            if json_ext in blob_name:
                blob_names_dict[blob_name] = blob.name
                listbox.insert(END, blob_name)

        logMsg('Blobs sorted, filtered and inserted into listbox')
        load_config = Button(root, text='Load Cloud Configuration File', font='Helvetica 10', padx=5, command=downloadConfig)
        load_config.place(x=100, y=320)

        config_label_or = Label(root, text='OR', font='Helvetica 10', padx=5)
        config_label_or.place(x=150, y=352)

        diag_wzConfig_file = Button(root, text=choose_local_config, command=inputFileDialog, anchor=W,padx=5, font='Helvetica 10')
        diag_wzConfig_file.place(x=115,y=380)

        # wzConfig_file = StringVar()
        # wzConfig_file_name = Entry(root, relief=SUNKEN, state=DISABLED, textvariable=wzConfig_file, width=50)
        # wzConfig_file_name.place(x=220,y=390)
        try:
            wzConfig_file_name = Entry(root, relief=SUNKEN, state=DISABLED, textvariable=wzConfig_file, width=50)
            wzConfig_file_name.place(x=220,y=390)
        except:
            wzConfig_file = StringVar()
            wzConfig_file_name = Entry(root, relief=SUNKEN, state=DISABLED, textvariable=wzConfig_file, width=50)
            wzConfig_file_name.place(x=220,y=390)
    elif not internet_on:
        config_label_error = Label(root, text='No internet connection detected\nConnect to download\ncloud configuration files', bg='slategray1', font='Helvetica 10', padx=10, pady=10)
        config_label_error.place(x=150, y=200)

        diag_wzConfig_file = Button(root, text=choose_local_config, command=inputFileDialog, anchor=W,padx=5, font='Helvetica 10')
        diag_wzConfig_file.place(x=115,y=280)

        # wzConfig_file = StringVar()
        try:
            wzConfig_file_name = Entry(root, relief=SUNKEN, state=DISABLED, textvariable=wzConfig_file, width=50)
            wzConfig_file_name.place(x=220,y=290)
        except:
            wzConfig_file = StringVar()
            wzConfig_file_name = Entry(root, relief=SUNKEN, state=DISABLED, textvariable=wzConfig_file, width=50)
            wzConfig_file_name.place(x=220,y=290)

        refreshButton = Button(root, image = refreshImg, command=loadCloudContent)
        refreshButton.place(x=50, y=200)
    else:
        # config_label_error = Label(root, text='No azure connection string detected\nConnect to download\ncloud configuration files', bg='slategray1', font='Helvetica 10', padx=10, pady=10)
        # config_label_error.place(x=150, y=200)

        diag_wzConfig_file = Button(root, text=choose_local_config, command=inputFileDialog, anchor=W,padx=5, font='Helvetica 10')
        diag_wzConfig_file.place(x=115,y=210)

        # wzConfig_file = StringVar()
        try:
            wzConfig_file_name = Entry(root, relief=SUNKEN, state=DISABLED, textvariable=wzConfig_file, width=50)
            wzConfig_file_name.place(x=220,y=220)
        except:
            wzConfig_file = StringVar()
            wzConfig_file_name = Entry(root, relief=SUNKEN, state=DISABLED, textvariable=wzConfig_file, width=50)
            wzConfig_file_name.place(x=220,y=220)

radioHeight = 210
Label(root, text='Beginning and Ending of Work Zone Locations', font='Helvetica 12 bold', padx=10, pady=10).place(x=800,y=radioHeight)
v = IntVar()

autoRadioButton = Radiobutton(root, text="Automatic Detection (Recommended)", variable=v, value=1) #, indicatoron=0
manualRadioButton = Radiobutton(root, text="Manual Detection", variable=v, value=2)
v.set(1)
autoRadioButton.place(x=850, y=radioHeight+35)
manualRadioButton.place(x=850, y=radioHeight+60)


notes = '''Automatic detection uses the locations from the configuration file for the starting
and ending locations of data collection. Manual detection allows you to
manually start and end data collection. The manually set locations will be
set as the the automatic locations next time the work zone is mapped'''
notes_label = Label(root, text=notes,justify=CENTER, bg='slategray1',anchor=W, font=('Helvetica', 10))
notes_label.place(x=760, y=radioHeight+85)

loadCloudContent()

# instructions = '''This is the initialization component of the Work Zone Data Collection tool.
# To begin collecting data, first load a configuration file and verify
# your GPS connection. You may load a configuration file from the 
# connection. from the list of published configuration
# files and load the file, or select a local configuration file. When
# the correct configuration file is selected and shown in the description
# box, select the 'Begin Data Collection' button to start data acquisition.
# The data acquisition component does not require an internet connection
# and will not record data until the set starting location is reached.'''
# instr_label = Label(root, text=instructions,justify=CENTER, bg='slategray1',anchor=W,padx=10,pady=10, font=('Calibri', 12))
# instr_label.place(x=700, y=30)

btnBegin = Button(root, text='Begin Data\nCollection', font=helvetica_14,border=2,state=DISABLED,command=launch_WZ_veh_path_data_acq, anchor=W,padx=20,pady=10)
btnBegin.place(x=570,y=390)

isGPSReady = False

# test serial port for GPS device (check for NMEA string)
def testGPSConnection(retry=False, *args):
    global isGPSReady
    gpsFix = False
    gpsFound = False
    try:
        ser = serial.Serial(port=tkPortVar.get()[0:5].strip(), baudrate=tkBaudVar.get(), timeout=1.1, )
        sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))
        
        NMEAData = sio.readline()
        if NMEAData:
            for i in range(20):
                NMEAData = sio.readline()
                # print(NMEAData)
                if NMEAData[0:3] == '$GP':
                    gpsFound = True
                    if NMEAData[0:6] == '$GPVTG' and NMEAData.split(',')[1]:
                        gpsFix = True
                        break
                    elif NMEAData[0:6] == '$GPGGA' and NMEAData.split(',')[2]:
                        gpsFix = True
                        break

                elif NMEAData[0:3] == '$GN':
                    gpsFound = True
                    if NMEAData[0:6] == '$GNVTG' and NMEAData.split(',')[1]:
                        gpsFix = True
                        break
                    elif NMEAData[0:6] == '$GNGGA' and NMEAData.split(',')[2]:
                        gpsFix = True
                        break
    except:
        return False
    if gpsFound:
        if gpsFix:
            commLabel['text']   = 'GPS DEVICE FOUND'
            commLabel['fg']     = 'green'
            isGPSReady = True
            updateMainButton()
            return True
        else:
            commLabel['text']   = 'INVALID GPS POSITION'
            commLabel['fg']     = 'orange'
            return TRUE
    else:
        btnBegin['state']   = 'disabled'
        btnBegin['bg']     = '#F0F0F0'
        commLabel['text']   = 'GPS DEVICE NOT FOUND'
        commLabel['fg']     = 'red'
        isGPSReady = False
        return False

gpsHeight = 75
def showSerialDropdowns():
    serialButton.destroy()
    baudLabel.place(x=850, y=gpsHeight+60)
    baudPopupMenu.place(x=850, y=gpsHeight+80)
    dataLabel.place(x=950, y=gpsHeight+60)
    dataPopupMenu.place(x=950, y=gpsHeight+80)

# Set baud rate and data rate labels
baudLabel = Label(root, text='Baud Rate (bps)')
baudRates = ['4800', '9600', '19200', '57600', '115200']
tkBaudVar = StringVar(window)
tkBaudVar.set('115200') #default is 10 Hz, 115200bps
baudPopupMenu = OptionMenu(root, tkBaudVar, *baudRates)

dataLabel = Label(root, text='Data Rate (Hz)')
dataRates = ['1', '2', '5', '10']
tkDataVar = StringVar(window)
tkDataVar.set('10') #default is 10 Hz, 115200bps
dataPopupMenu = OptionMenu(root, tkDataVar, *dataRates)
serialButton = Button(root, text='Show Advanced Serial Settings', command=showSerialDropdowns)
serialButton.place(x=850, y=gpsHeight+60)

ports = serial.tools.list_ports.comports(include_links=False)
if not ports: ports = ['NO DEVICES FOUND']

# Frame for COMM port options
mainframe = Frame(root)
mainframe.place(x=850, y=gpsHeight)
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)

# Create COMM port popup menu
logMsg('Creating comm port popup menu')
commLabel = Label(mainframe, text='GPS DEVICE NOT FOUND', font='Helvetica 13 bold', fg='red')
tkPortVar = StringVar(window)
popupMenu = OptionMenu(mainframe, tkPortVar, *ports)
commLabel.pack()
popupMenu.pack()

# Update COMM ports popup menu and search for GPS device
def updatePortsDropdown():
    global popupMenu
    global ports
    ports = serial.tools.list_ports.comports(include_links=False)
    if not ports: ports = ['NO DEVICES FOUND']
    currentValue = tkPortVar.get()
    popupMenu.destroy()
    popupMenu = OptionMenu(mainframe, tkPortVar, *ports)
    popupMenu.pack()
    searchPorts()

# Search COMM ports for GPS device
def searchPorts():
    try:
        tkPortVar.trace_vdelete("w", tkPortVar.trace_id)
    except:
        pass
    for port in ports:
        tkPortVar.set(port)
        if (testGPSConnection(True)):
            break
    tkPortVar.trace_id = tkPortVar.trace("w", testGPSConnection)


# refreshImg = ImageTk.PhotoImage(Image.open('./images/refresh_small.png'))                                         # Car image
btnTestGps = Button(root, image = refreshImg, command=updatePortsDropdown)                                  # Label with car image , command=loadCloudContent
btnTestGps.place(x=800, y=gpsHeight+30)

def on_closing():
    logFile.close()
    sys.exit(0)

window.protocol("WM_DELETE_WINDOW", on_closing)
window.after(500, searchPorts)
window.mainloop()
  

################################################################################################################
###
#--------------------------------------------------- WZ_VehPathDataAcq -----------------------------------------
###
################################################################################################################

# Start data collection function
def startMainFunc():
    global  appRunning                          #boolean
    if (appRunning):
        logMsg('App running, starting getNMEA_String loop')
        getNMEA_String()                        #Get NMEA String and process it until 'appRunning is True...'
    else:
        logMsg('App not running, exiting')

# Retrieve NMEA string and GPS data from device
def getNMEA_String():

###
#   Global variables...
###

    global      sio                                 #serial io
    global      GPSTime, GPSDate, prevGPSTime       #time, date and prev. GPS time
    global      keyMarker, dataLog                  #key marker and data log
    global      appRunning                          #until Esc is pressed
    global      GPSLat, GPSLon, GPSAlt              #needed for ref. pt, lane state and workers present locations
    global      carPosLat, carPosLon, carPosHeading


###
#   Local variables...
###

    #GPSRate     = 10                                #GPS data rate in Hz
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
    # GGAValid    = False                             #Init value
    # RMCValid    = False                             #Init value
    # GSAValid    = False                             #Init value
    prevDistance = 0
    pi = 3.14159
    isFirstTime = True
    i = 0
    isNearEnd = False
    prevLat = 0
    prevLon = 0

    # i = 1

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
        try:
            if NMEAData[0:6] == '$GPGGA' or NMEAData[0:6] == '$GNGGA':
                GGA_out = parseGxGGA(NMEAData,GPSTime,GPSSats,GPSAlt)
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

            if NMEAData[0:6] == '$GPRMC' or NMEAData[0:6] == '$GNRMC':
                RMC_out = parseGxRMC(NMEAData,GPSDate,GPSLat,GPSLon,GPSSpeed,GPSHeading)
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

            if NMEAData[0:6] == '$GPGSA' or NMEAData[0:6] == '$GNGSA':
                GSA_out = parseGxGSA(NMEAData,GPSHdop)
                if GSA_out[1] == True:
                    GPSHdop = GSA_out[0]
                pass
                #print ('GSA Hdop:', GSA_out)
            pass
        except Exception as e:
            logMsg('ERROR: GPS parsing failed. ' + str(e))
            continue

        # Update marker position on map
        carPosLat = GPSLat
        carPosLon = GPSLon
        carHeading = GPSHeading
        updatePosition()
        
        if dataLog:
            distanceToEndPt = round(dist(GPSLat*pi/180, GPSLon*pi/180, wzEndLat*pi/180, wzEndLon*pi/180))
            # TODO: Add check for direction of travel
            if distanceToEndPt < 20 and gotRefPt and not manualDetection:
                minLineDist, t = dist_to_line(prevLat*pi/180, prevLon*pi/180, GPSLat*pi/180, GPSLon*pi/180, wzEndLat*pi/180, wzEndLon*pi/180)
                if minLineDist < 20 and t > 0 and t < 1:
                    logMsg('-------- Exiting Work Zone (by location, distance=' + str(distanceToEndPt) + ') -------')
                    stopDataLog()
            # TODO: Auto mark reference point
            elif not gotRefPt and distanceToStartPt > prevDistance and i >= 10: #Auto mark reference point
                logMsg('-------- Auto Marking Reference Point (by location, distance=' + str(distanceToStartPt) + ') -------')
                markRefPt()


        # Automatically start/end data collection
        if dataLog:
            distanceToEndPt = round(dist(GPSLat*pi/180, GPSLon*pi/180, wzEndLat*pi/180, wzEndLon*pi/180))
            if distanceToEndPt < 20 and distanceToEndPt > prevDistance and gotRefPt and not manualDetection: #Leaving Workzone
                logMsg('-------- Exiting Work Zone (by location, distance=' + str(distanceToEndPt) + ') -------')
                stopDataLog()
                #appRunning = False
            distanceToStartPt = round(dist(GPSLat*pi/180, GPSLon*pi/180, wzStartLat*pi/180, wzStartLon*pi/180))
            if not gotRefPt and distanceToStartPt > prevDistance and i >= 10: #Auto mark reference point
                logMsg('-------- Auto Marking Reference Point (by location, distance=' + str(distanceToStartPt) + ') -------')
                markRefPt()
            if gotRefPt:
                prevDistance = distanceToEndPt
            else:
                prevDistance = distanceToStartPt
            # isFirstTime = False
            i += 1

        else:
            distanceToStartPt = round(dist(GPSLat*pi/180, GPSLon*pi/180, wzStartLat*pi/180, wzStartLon*pi/180))
            if distanceToStartPt < 50 and not manualDetection: #Entering Workzone
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
##

# Calculate accurate distance between GPS points
def dist(lat1, lon1, lat2, lon2):
    R = 6371000
    avg_lat = (lat1+lat2)/2
    distance = R*math.sqrt((lat1-lat2)**2+math.cos(avg_lat)**2*(lon1-lon2)**2)
    return distance

# TODO: Determine if need lon=lon*cos(lat)
def dist_to_line(v1, v2, w1, w2, p1, p2):
    l = dist(v1, v2, w1, w2) ** 2
    t = max(0, min(1, dot(dif(p1, p2, v1, v1), dif(w1, w2, v1, v2))))
    pp1 = v1 + t * (w1 - v1)
    pp2 = v2 + t * (w2 - v2)
    return dist(p1, p2, pp1, pp2), t

def dot(v1, v2, w1, w2):
    return v1 * w1 + v2 * w2

def dif(v1, v2, w1, w2):
    return v1 - w1, v2 - w2

# Toggle lane closures
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
    else:
        lanes[lane]['bg']   = 'gray92'
        lanes[lane]['fg']   = 'red3'
        laneLabels[lane]['fg'] = 'red3'
        laneLabels[lane]['text'] = 'CLOSED'
        laneLabels[lane].place(x=marginLeft+10 + (lane-1)*110, y=100)

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

# Toggle worker presence
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

# Start data logging
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

# Stop data logging and move to message building
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

# Mark reference point
def markRefPt():
    global gotRefPt
    global keyMarker

    if not gotRefPt:
        markerStr = '   *** Reference Point Marked @ '+str(GPSLat)+', '+str(GPSLon)+', '+str(GPSAlt)+' ***'
        logMsg('*** Reference Point Marked @ '+str(GPSLat)+', '+str(GPSLon)+', '+str(GPSAlt)+' ***')
        ##T.insert (END, markerStr)
        keyMarker = ['RP','']                       #reference point
        gotRefPt = True                             #got the reference point

        displayStatusMsg(markerStr)

def markStartPt():
    global wzConfig
    global wzStartLat
    global wzStartLon

    bStart['state'] = DISABLED
    bStart['bg'] = 'gray92'

    wzConfig['Location']['BeginningLocation']['Lat'] = GPSLat
    wzConfig['Location']['BeginningLocation']['Lon'] = GPSLon
    wzStartLat = GPSLat
    wzStartLon = GPSLon

    markerStr = '   *** Starting Point Marked @ '+str(GPSLat)+', '+str(GPSLon)+', '+str(GPSAlt)+' ***'
    logMsg('*** Starting Point Marked @ '+str(GPSLat)+', '+str(GPSLon)+', '+str(GPSAlt)+' ***')
    displayStatusMsg(markerStr)

    startDataLog()

def markEndPt():
    global wzConfig
    global wzEndLat
    global wzEndLon

    wzConfig['Location']['EndingLocation']['Lat'] = GPSLat
    wzConfig['Location']['EndingLocation']['Lon'] = GPSLon
    wzEndLat = GPSLat
    wzEndLon = GPSLon


    centerLat = (float(wzStartLat) + float(wzEndLat))/2
    centerLon = (float(wzStartLon) + float(wzEndLon))/2
    center = str(centerLat) + ',' + str(centerLon)

    north = max(float(wzStartLat), float(wzEndLat))
    south = min(float(wzStartLat), float(wzEndLat))
    east = max(float(wzStartLon), float(wzEndLon))
    west = min(float(wzStartLon), float(wzEndLon))
    calcZoomLevel(north, south, east, west, imgWidth, imgHeight)

    wzConfig['ImageInfo']['Zoom'] = zoom
    wzConfig['ImageInfo']['Center']['Lat'] = centerLat
    wzConfig['ImageInfo']['Center']['Lon'] = centerLon
    markers = []
    markers.append({'Name': 'Start', 'Color': 'Green', 'Location': {'Lat': wzStartLat, 'Lon': wzStartLon, 'Elev': None}})
    markers.append({'Name': 'End', 'Color': 'Red', 'Location': {'Lat': wzEndLat, 'Lon': wzEndLon, 'Elev': None}})
    wzConfig['ImageInfo']['Markers'] = markers
    wzConfig['ImageInfo']['MapType'] = mapImageMapType
    wzConfig['ImageInfo']['Height'] = mapImageHeight
    wzConfig['ImageInfo']['Width'] = mapImageWidth
    wzConfig['ImageInfo']['Format'] = mapImageFormat
    wzConfig['ImageInfo']['ImageString'] = ""


    markerStr = '   *** Ending Point Marked @ '+str(GPSLat)+', '+str(GPSLon)+', '+str(GPSAlt)+' ***'
    logMsg('*** Ending Point Marked @ '+str(GPSLat)+', '+str(GPSLon)+', '+str(GPSAlt)+' ***')
    displayStatusMsg(markerStr)

    stopDataLog()

# Write line to CSV data vile
def writeCSVFile(write_str):
    global writeData                            #file handle
    
    writeData.writerow(write_str)               #write output to csv file...

# Display message in status window
def displayStatusMsg(msgStr):

    xPos = marginLeft-80+45
    yPos = 410
    blankStr = ' '*190
    Text = Label(root,anchor='w', justify=LEFT, text=blankStr)
    Text.place(x=xPos,y=yPos)    

    Text = Label(root,anchor='w', justify=LEFT, text=msgStr)
    Text.place(x=xPos,y=yPos)    


# Enable buttons and remove overlay message
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



GPSDate     = ''                                #GPS Date
GPSTime     = ''                                #GPS Time
prevGPSTime = ''                                #previous GPS Time
GPSLat      = 0.0                               #Latitude in degrees in decimal
GPSLon      = 0.0                               #Longitude in degrees in decimal
GPSAlt      = 0.0                               #Altitude in meters

dataLog     = False                             #data logging off
appRunning  = True                              #set application running to TRUE
keyMarker   = ['',0]                            #marker from key press
gotRefPt    = False                             #got Ref. Point
wpStat      = False                             #workers not present
                                                #pressing the same lane # key will toggle the from close to open  

# local_config_path = './Config Files/ACTIVE_CONFIG.json'
cDT = datetime.datetime.now().strftime('%m/%d/%Y - ') + time.strftime('%H:%M:%S')
ctrDT = datetime.datetime.now().strftime('%Y%m%d-') + time.strftime('%H%M%S')

files_list      = []


commPort = tkPortVar.get()[0:4]
baudRate = int(tkBaudVar.get())
dataRate = int(tkDataVar.get())

logMsg('*** Running Vehicle Path Data Acquisition ***')

outDir      = './WZ_VehPathData'
vehPathDataFileName = 'path-data--' + wzDesc.lower().strip().replace(' ', '-') + '--' + roadName.lower().strip().replace(' ', '-') + '.csv'
vehPathDataFile = outDir + '/' + vehPathDataFileName

##########################################################################
#
# Setup data collection UI
#
############################################################################

marginLeft = 750
window_width = max(1400, totalLanes*100+300+marginLeft)
window.geometry(str(window_width)+'x750')
root = Frame(width=window_width, height=750)
root.place(x=0, y=0)
# root.bind_all('<Key>', keyPress)                #key press event...

laneStat = [True]*(totalLanes+1) #all 8 lanes are open (default), Lane 0 is not used...

lbl_top = Label(root, text='Vehicle Path Data Acquisition\n\n', font=helvetica_14, fg='royalblue', pady=10)
lbl_top.place(x=window_width/2-250/2, y=10)

laneLine = ImageTk.PhotoImage(Image.open('./images/verticalLine_thin.png'))                             # Lane Line
carImg = ImageTk.PhotoImage(Image.open('./images/caricon.png'))                                         # Car image
carlabel = Label(root, image = carImg)                                                                  # Label with car image
workersPresentImg = ImageTk.PhotoImage(Image.open('./images/workersPresentSign_small.png'))             # Workers present image
userPositionImg = ImageTk.PhotoImage(Image.open('./images/blue-circle.png'))                            # Workers present image

plusImg = ImageTk.PhotoImage(Image.open('./images/plus.png'))
minusImg = ImageTk.PhotoImage(Image.open('./images/minus.png'))

arrowUpImg = ImageTk.PhotoImage(Image.open('./images/arrow_up.png'))
arrowRightImg = ImageTk.PhotoImage(Image.open('./images/arrow_right.png'))
arrowDownImg = ImageTk.PhotoImage(Image.open('./images/arrow_down.png'))
arrowLeftImg = ImageTk.PhotoImage(Image.open('./images/arrow_left.png'))


mapFileName = "./mapImage.png"

zoom = 10
imgHeight = 640
imgWidth = 640
center = "40.4742350,-104.9692566"
imgFormat = "png"
vertBound = 0
horizBound = 0
carPosLat = 0
carPosLon = 0
carPosHeading = 0
markerHeight = 20
markerWidth = 20

if not marker_list:
    marker_list = []
    marker_list.append("markers=color:green|label:Start|" + str(wzStartLat) + "," + str(wzStartLon) + "|")
    marker_list.append("markers=color:red|label:End|" + str(wzEndLat) + "," + str(wzEndLon) + "|")

# Calculate map bounds from google maps zoom level
def getCurrentMapBounds():
    global horizBound
    global vertBound

    # zoom = math.log(pixelWidth * 360 / angle / GLOBE_WIDTH) / math.log(2)
    # GLOBE_WIDTH * e ^ (zoom * math.log(2)) = pixelWidth * 360 / angle

    GLOBE_WIDTH = 256
    scale = 360 / (GLOBE_WIDTH * math.e**(zoom * math.log(2)))
    horizBound = imgWidth * scale
    vertBound = imgHeight * scale * math.cos(centerLat*math.pi/180) #.77 -78.388249  * math.cos(centerLat*math.pi/180)

# Caculate pixel location on screen from bounds (Linear Interpolation)
def getPixelLocation(lat, lon):
    x = (lon - centerLon) / (horizBound / 2)
    y = -(lat - centerLat) / (vertBound / 2) # / math.cos(lat*math.pi/180) * math.cos(centerLat*math.pi/180)
    x = round((imgWidth/2) + x * (imgWidth/2) - (markerWidth/2))
    y = round((imgHeight/2) + y * (imgHeight/2) - (markerHeight/2))
    if (x < 0 or x > imgWidth) or (y < 0 or y > imgHeight):
        x = -1
        y = -1
    return x, y

# Calculate google maps zoom level to fit a rectangle
def calcZoomLevel(north, south, east, west, pixelWidth, pixelHeight):
    global zoom
    global centerLat

    GLOBE_WIDTH = 256
    ZOOM_MAX = 21
    angle = east - west
    if angle < 0:
        angle += 360
    zoomHoriz = round(math.log(pixelWidth * 360 / angle / GLOBE_WIDTH) / math.log(2)) - 1

    angle = north - south
    centerLat = (north + south) / 2
    if angle < 0:
        angle += 360
    zoomVert = round(math.log(pixelHeight * 360 / angle / GLOBE_WIDTH * math.cos(centerLat*math.pi/180)) / math.log(2)) - 1

    zoom = max(min(zoomHoriz, zoomVert, ZOOM_MAX), 0)
    getCurrentMapBounds()


### Center Location
# If center coordinates present in configuration file, write center to global vars
if mapImageCenterLat and mapImageCenterLon:
    centerLat = float(mapImageCenterLat)
    centerLon = float(mapImageCenterLon)
    center = str(centerLat) + ',' + str(centerLon)
# If center coordinates not present and automatic detection, recalculate center based on coordinates
elif not manualDetection:
    centerLat = (float(wzStartLat) + float(wzEndLat))/2
    centerLon = (float(wzStartLon) + float(wzEndLon))/2
    center = str(centerLat) + ',' + str(centerLon)
# If center coordinates not present and manual detection, do nothing


### Zoom Level
# If zoom level set in configuration file, write zoom to global var
if mapImageZoom:
    zoom = int(mapImageZoom)
    getCurrentMapBounds()
# If zoom level not set and automatic detection, recalculate zoom level
elif not manualDetection:
    north = max(float(wzStartLat), float(wzEndLat))
    south = min(float(wzStartLat), float(wzEndLat))
    east = max(float(wzStartLon), float(wzEndLon))
    west = min(float(wzStartLon), float(wzEndLon))
    calcZoomLevel(north, south, east, west, imgWidth, imgHeight)
# If zoom level not set and manual detection, do nothing


### Map Image
# If manual detection, set image to map_failed
if manualDetection: #No map image to load
    shutil.copy(map_failed_img, mapFileName)
    mapFailed = True
# If automatic detection, attempt to load image
# else:
#     # If internet on, load cloud image
#     if internet_on():
#         get_static_google_map(mapFileName, center=center, zoom=zoom, imgsize=(imgWidth, imgHeight), imgformat="png", markers=marker_list)
#         mapFailed = False
    # If no internet, leave image as is (This image was set from the configuration file ImageString)
mapImg = ImageTk.PhotoImage(Image.open(mapFileName))

# Exit data collection loop and quit
def end_application():
    global appRunning
    appRunning = False
    logFile.close()
    sys.exit(0)

# Initialize UI lane variables
lanes = [0]*(totalLanes+1)
laneBoxes = [0]*(totalLanes+1)
laneLabels = [0]*(totalLanes+1)
laneSymbols = [0]*(totalLanes+1)
laneLines = [0]*(totalLanes+1)

# Zoom in or out by 1 unit
# def changeZoom(incr):
#     global mapImg
#     global zoom
#     global mapLabel
#     zoom += incr
#     get_static_google_map(mapFileName, center=center, zoom=zoom, imgsize=(imgWidth, imgHeight), imgformat="png", markers=marker_list) #, markers=marker_list
#     mapImg = ImageTk.PhotoImage(Image.open(mapFileName))             # Workers present image
#     mapLabel.configure(image = mapImg)
#     getCurrentMapBounds()
#     updatePosition()

# # Move 1/5 of the screen size based on direct
# def moveMap(direct):
#     global centerLat
#     global centerLon
#     global center
#     global mapImg
#     global mapLabel

#     fract = 1/5
#     distanceVert = 0
#     distanceHoriz = 0
#     if direct == 'u':
#         distanceVert = vertBound*fract
#     elif direct == 'd':
#         distanceVert = -vertBound*fract
#     elif direct == 'r':
#         distanceHoriz = horizBound*fract
#     elif direct == 'l':
#         distanceHoriz = -horizBound*fract
#     centerLat += distanceVert
#     centerLon += distanceHoriz
#     center = str(centerLat) + ',' + str(centerLon)

#     get_static_google_map(mapFileName, center=center, zoom=zoom, imgsize=(imgWidth, imgHeight), imgformat="png", markers=marker_list) #, markers=marker_list
#     mapImg = ImageTk.PhotoImage(Image.open(mapFileName))             # Workers present image
#     mapLabel.configure(image = mapImg)
#     updatePosition()

mapLabel = Label(root, image = mapImg)
mapLabel.place(x=50, y=60)

# If manual detection, no map to move so do not place buttons
# if not manualDetection:
#     bZoomIn = Button(root, image=plusImg, font='Helvetica 10', command=lambda:changeZoom(1), highlightthickness = 0, bd = 0)
#     bZoomIn.place(x=540, y=68)
#     bZoomOut = Button(root, image=minusImg, font='Helvetica 10', command=lambda:changeZoom(-1), highlightthickness = 0, bd = 0)
#     bZoomOut.place(x=540, y=102)

#     bMoveUp = Button(root, image=arrowUpImg, font='Helvetica 10', command=lambda:moveMap("u"), highlightthickness = 0, bd = 0)
#     bMoveUp.place(x=610, y=60)
#     bMoveRight = Button(root, image=arrowRightImg, font='Helvetica 10', command=lambda:moveMap("r"), highlightthickness = 0, bd = 0)
#     bMoveRight.place(x=635, y=85)
#     bMoveDown = Button(root, image=arrowDownImg, font='Helvetica 10', command=lambda:moveMap("d"), highlightthickness = 0, bd = 0)
#     bMoveDown.place(x=610, y=110)
#     bMoveLeft = Button(root, image=arrowLeftImg, font='Helvetica 10', command=lambda:moveMap("l"), highlightthickness = 0, bd = 0)
#     bMoveLeft.place(x=585, y=85)

carLabel = Label(root, image = userPositionImg, highlightthickness = 0, borderwidth = 0, width= 0, height = 0)

# Update position of marker on screen
def updatePosition():
    global carLabel
    if not mapFailed:
        x, y = getPixelLocation(carPosLat, carPosLon)
        carLabel.place(x=x + 50, y=y + 60)
    else:
        carLabel.place(x=-1 + 50, y=-1 + 60)

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


if manualDetection:
    bStart = Button(root, text='Mark Start of\nWork Zone', font='Helvetica 10', padx=5, bg='green', fg='white', command=markStartPt)
    bStart.place(x=marginLeft-100+150, y=510)
    bEnd = Button(root, text='Mark End of\nWork Zone', font='Helvetica 10', padx=5, bg='red3', fg='gray92', command=markEndPt)
    bEnd.place(x=marginLeft-100+450, y=510)

###
#   Application Message Window...
###

appMsgWin = Button(root, text='Application Message Window...                                             ',      \
                font='Courier 10', justify=LEFT,anchor=W,padx=10,pady=10)
appMsgWin.place(x=marginLeft-80+50, y=400)
overlayWidth = 710
overlayx = marginLeft + (window_width - marginLeft)/2 - overlayWidth/2
overlay = Label(root, text='Application will begin data collection\nwhen the starting location has been reached', bg='gray', font='Calibri 28')
if manualDetection:
    overlay['text'] = 'Application will begin data collection\nwhen the starting location is marked'
overlay.place(x=overlayx, y=200)


##############################################################
#   ------------------ END of LAYOUT -------------------------
##############################################################


gps_found = False
first = True
while not gps_found:
    try:
        ser         = serial.Serial(port=commPort, baudrate=baudRate, timeout=1.1, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)               #open serial port
        msgStr      = '   Vehicle Path Data Acquisition is Ready - Logging Will Start When Start Location is Reached'
        displayStatusMsg(msgStr)                                                        #system ready
        gps_found = True

    except SerialException as e:
        logMsg('Failed to find GPS device, SerialException: ' + str(e))
        MsgBox = messagebox.askquestion ('GPS Receiver NOT Found','*** GPS Receiver NOT Found ***, Reconnect to USB Port ***\n\n'   \
                    '   --- Press Yes to try again, No to exit the application ---',icon = 'warning')
        if MsgBox == 'no':
            logMsg('User exited application')
            logFile.close()
            sys.exit(0)                                                 #system ready

###
#   EOL is not supported in PySerial for readline() in Python 3.6.
#   must use sio
###

logMsg('Creating serial IO connection')
sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))

#   Open outFile for csv write...
logMsg('Opening path data output file: ' + vehPathDataFile)
outFile     = open(vehPathDataFile,'w',newline='')
writeData   = csv.writer(outFile)

# Write heading to file
titleLine = 'GPS Date & Time','# of Sats','HDOP','Latitude','Longitude','Altitude(m)','Speed(m/s)','Heading(Deg)','Marker','Value'
writeCSVFile(titleLine)

###
#
#   -----------------------  Start Main Function  -----------------------------
#
###

logMsg('Starting main loop')

window.protocol("WM_DELETE_WINDOW", end_application)
startMainFunc()                                         #main function, starts NMEA processing 

logMsg('Main loop ended, closing streams/files')

###
#   Done, close everything...
###

ser.close()                                             #close serial IO
outFile.close()                                         #end of data acquisition and logging
logMsg('Ending data acquisition')
# logFile.close()
root.destroy()
window.quit()


# Start 
# laneStat = []
# wpStat = []

# # Upload messag archive
# def uploadArchive():
#     if internet_on():
#         logMsg('Creating blob in azure: ' + zip_name + ', in container: ' + container_name)
#         blob_client = blob_service_client.get_blob_client(container=container_name, blob=zip_name)
#         logMsg('Uploading zip archive to blob')
#         with open(zip_name, 'rb') as data:
#             blob_client.upload_blob(data, overwrite=True)
#         logMsg('Closing log file in Message Builder and Export')
#         logFile.close()
#         messagebox.showinfo('Upload Successful', 'Data upload successful! Please navigate to\nhttp://www.neaeraconsulting.com/V2x_Verification\nto view and verify the mapped workzone.\nYou will find your data under\n' + name_id)
#         sys.exit(0)
#     else:
#         logMsg('Attempted uploadArchive, no internet connection detected')
#         messagebox.showerror('No Internet Cnnection', 'No internet connection detected\nConnect and try again')

def uploadFile():
    upload_container = "workzoneuploads"
    if internet_on():
        logMsg('Creating blob in azure: ' + blob_name + ', in container: ' + upload_container)
        blob_client = blob_service_client.get_blob_client(container=upload_container, blob=blob_name)
        logMsg('Uploading zip archive to blob')
        with open(vehPathDataFile, 'rb') as data:
            blob_client.upload_blob(data, overwrite=True)
        logMsg('Closing log file in Message Builder and Export')
        logFile.close()
        messagebox.showinfo('Upload Successful', 'Data upload successful! Please navigate to\nhttp://www.neaeraconsulting.com/V2x_Verification\nto view and verify the mapped workzone.\nYou will find your data under\n' + name_id)
        sys.exit(0)
    else:
        logMsg('Attempted uploadArchive, no internet connection detected')
        messagebox.showerror('No Internet Cnnection', 'No internet connection detected\nConnect and try again')

# Create upload button
window.geometry('400x300')
root = Frame(width=400, height=300)
root.place(x=0, y=0)

if has_azure_connection:
    load_config = Button(root, text='Upload Data\nFiles', state=DISABLED, font='Helvetica 20', padx=5,command=uploadFile)
    load_config.place(x=100, y=100)

loading_label = Label(root, text='Processing Data', font='Helvetica 28', bg='gray', padx=5)
loading_label.place(x=60, y=120)
##############################################################################################
#
# ---------------------------- Automatically Export Files ------------------------------------
#
###############################################################################################
logMsg('*** Running Message Builder and Export ***')

description = wzDesc.lower().strip().replace(' ', '-')
road_name = roadName.lower().strip().replace(' ', '-')
name_id = description + '--' + road_name
blob_name = 'path-data--' + name_id + '.csv'

def updateConfigImage():
    global needsImage
    global wzConfig
    global center

    centerLat = (float(wzStartLat) + float(wzEndLat))/2
    centerLon = (float(wzStartLon) + float(wzEndLon))/2
    center = str(centerLat) + ',' + str(centerLon)
    
    north = max(float(wzStartLat), float(wzEndLat))
    south = min(float(wzStartLat), float(wzEndLat))
    east = max(float(wzStartLon), float(wzEndLon))
    west = min(float(wzStartLon), float(wzEndLon))
    calcZoomLevel(north, south, east, west, imgWidth, imgHeight)

    marker_list = []
    marker_list.append("markers=color:green|label:Start|" + str(wzStartLat) + "," + str(wzStartLon) + "|")
    marker_list.append("markers=color:red|label:End|" + str(wzEndLat) + "," + str(wzEndLon) + "|")

    # encoded_string = ''
    # if internet_on():
    #     get_static_google_map(mapFileName, center=center, zoom=zoom, imgsize=(imgWidth, imgHeight), imgformat="png", markers=marker_list)
    #     with open(mapFileName, "rb") as image_file:
    #         encoded_string = base64.b64encode(image_file.read()).decode()
    #     needsImage = False

    wzConfig['ImageInfo']['Zoom'] = zoom
    wzConfig['ImageInfo']['Center']['Lat'] = centerLat
    wzConfig['ImageInfo']['Center']['Lon'] = centerLon
    wzConfig['ImageInfo']['ImageString'] = ''

    cfg = open(local_updated_config_path, 'w')
    cfg.write(json.dumps(wzConfig, indent='  '))
    cfg.close()

def prepareDataFile():
    global blob_name
    if updateConfigImage:
        blob_name = blob_name.replace('.csv', '--update-image.csv')

    valid, msgs = validateDataFile()
    print(valid)
    if not valid:
        messages = '\n'
        for msg in msgs:
            messages = messages + msg + '\n'
        message = 'CSV Data File Not Valid' + '\n' + '------' + messages + '------' + '\n' + 'Fix these issues before uploading' + '\n'
        messagebox.showerror('Data File Invalid',message + 'After fixing, upload to to https://neaeraconsulting.com/V2X_Upload')
        sys.exit(0)

    # logMsg('Removing local configuration file: ' + local_config_path)
    if configUpdated:
        os.remove(local_updated_config_path)

    if has_azure_connection:
        logMsg('Loaded connection string from environment variable: ' + connect_str_env_var)
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        container_name = 'workzonedatauploads'

        load_config['bg'] = 'green'
        load_config['state']= NORMAL
        loading_label.destroy()
    else:
        logMsg('Closing log file in Message Builder and Export')
        logFile.close()
        messagebox.showinfo('Upload Data File', 'Data file generation complete. Please upload the\ngenerated CSV file: ' + vehPathDataFile.split('/')[-1] + '\nto https://neaeraconsulting.com/V2X_Upload')
        sys.exit(0)

# # Create zip archive of messages
# def create_messages_and_zip():
#     global zip_name
#     global name_id
#     global blob_service_client
#     global container_name

#     if manualDetection:
#         updateConfigImage()

#     build_all_messages()
#     files_list.append(vehPathDataFile)
#     if configUpdated:
#         files_list.append(local_updated_config_path)
#     else:
#         files_list.append(local_config_path)

#     description = wzDesc.lower().strip().replace(' ', '-')
#     road_name = roadName.lower().strip().replace(' ', '-')
#     name_id = description + '--' + road_name
#     logMsg('Work zone name id: ' + name_id)
#     zip_name = 'wzdc-exports--' + name_id + '.zip'
#     logMsg('Creating zip archive: ' + zip_name)

#     zipObj = zipfile.ZipFile(zip_name, 'w')

#     for filename in files_list:
#         name = filename.split('/')[-1]
#         name_orig = name
#         name_wo_ext = name[:name.rfind('.')]
#         if '.csv' in filename.lower():
#             name = 'path-data--' + name_id + '.csv'
#         elif json_ext in filename.lower():
#             if configUpdated:
#                 if needsImage:
#                     name = 'config--' + name_id + '-updated-needsimage.json'
#                 else:
#                     name = 'config--' + name_id + '-updated.json'
#             else:
#                 name = 'config--' + name_id + json_ext
#         elif xml_ext in filename.lower():
#             number = name[name.rfind('-')+1:name.rfind('.')]
#             name = 'rsm-xml--' + name_id + '--' + number + xml_ext
#         elif uper_ext in filename.lower():
#             number = name[name.rfind('-')+1:name.rfind('.')]
#             name = 'rsm-uper--' + name_id + '--' + number + uper_ext
#         elif geojson_ext in filename.lower():
#             name = 'wzdx--' + name_id + geojson_ext
#         else:
#             continue
#         logMsg('Adding file to archive: ' + filename + ', as: ' + name)
#         zipObj.write(filename, name)

#     # close the Zip File
#     zipObj.close()

#     # logMsg('Removing local configuration file: ' + local_config_path)
#     if configUpdated:
#         os.remove(local_updated_config_path)

#     # connect_str_env_var = 'AZURE_STORAGE_CONNECTION_STRING'
#     # connect_str = os.getenv(connect_str_env_var)
#     if has_azure_connection:
#         logMsg('Loaded connection string from environment variable: ' + connect_str_env_var)
#         blob_service_client = BlobServiceClient.from_connection_string(connect_str)
#         container_name = 'workzonedatauploads'

#         load_config['bg'] = 'green'
#         load_config['state']= NORMAL
#         loading_label.destroy()
#     else:
#         logMsg('Closing log file in Message Builder and Export')
#         logFile.close()
#         messagebox.showinfo('Upload Generated Messages', 'Message generation complete. Please upload the\ngenerated ZIP file: ' + zip_name + '\nto https://neaeraconsulting.com/V2X_Upload')
#         sys.exit(0)

def validateDataFile():
    laneList = range(1, totalLanes)
    print(laneList)
    markerList = ['Data Log', 'RP', 'RP+WP', 'RP+LC', 'WP', 'LC', 'LO', '']
    markerValueDict = {'Data Log': ['True', 'False'], 'RP': '', 'RP+WP': ['True', 'False'], 'RP+LC': laneList, 
    'WP': ['True', 'False'], 'LC': laneList, 'LO': laneList, '': ''}

    laneStat = [0]*9
    wpStat = False
    messages = []
    fileValid = True
    gotRP = False
    i = 0
    with open(vehPathDataFile, 'r') as f:
        headers = f.readline()
        data = f.readline().rstrip('\n')
        while data:
            i += 1
            valid, msg, laneStat, wpStat, gotRP = validateDataLine(data, markerList, markerValueDict, laneStat, wpStat, gotRP)
            if not valid:
                vileValid = False
                messages.append('Line ' + str(i) + " " + msg)

            data = f.readline().rstrip('\n')

        if not gotRP == True:
            fileValid = False
            messages.append(" No reference point found by end")
        if not wpStat == False:
            fileValid = False
            messages.append("Workers present not false at end")
        if not laneStat == [0]*9:
            fileValid = False
            messages.append("All lanes not open at end")
                
    return fileValid, messages

def validateDataLine(line, markerList, markerValueDict):
    fields = line.split(',')
    msg = ''

    time    = fields[0]
    sats    = int(fields[1])
    hdop    = float(fields[2])
    lat     = float(fields[3])
    lon     = float(fields[4])
    elev    = float(fields[5])
    speed   = float(fields[6])
    heading = float(fields[7])
    marker  = fields[8]
    value   = fields[9]

    valid = True
    if not re.match('([0-9]){4}\/(0[1-9]|1[0-2])\/([0-9]){2}-(0[1-9]|1[0-9]|2[0-4]):([0-5][0-9]):([0-5][0-9]):([0-9]){2}', time): 
        valid = False
        msg = "GPS date time gormat invalid: " + str(time)
    if not (sats >= 0 and sats <= 12): 
        valid = False
        msg = "Number of sattelites invalid: " + str(sats)
    if not (hdop > 0): 
        valid = False
        msg = "HDOP format invalid: " + str(hdop)
    if not (lat >= -90 and lat <= 90): 
        valid = False
        msg = "Latitude invalid: " + str(lat)
    if not (lon >= -180 and lon <= 180): 
        valid = False
        msg = "Longitude invalid: " + str(lon)
    if not (elev >= -4096 and elev <= 61439): 
        valid = False
        msg = "Altitude invalid: " + str(elev)
    if not (speed >= 0 and speed <= 8191): 
        valid = False
        msg = "Speed invalid: " + str(speed)
    if not (heading >= 0 and heading <= 360): 
        valid = False
        msg = "Heading invalid: " + str(heading)
    if not (marker in markerList): 
        valid = False
        msg = "Marker invalid: " + str(marker)
    # Verify marker + value combination is valid
    try:
        if not (value in markerValueDict[marker]): 
            valid = False
            msg = "Marker and value combination invalid. Marker: " + str(marker) + ", Value: " + str(value)
    except KeyError as e:
        # This error is caught by the above check
        pass

    advValid, advMsg, laneStat, wpStat, gotRP = validateDataLineAdvanced(line, markerValueDict, laneStat, wpStat, gotRP)
    if not advValid or not valid:
        valid = False
    for msg_str in advMsg:
        msg.append(msg_str)

    return valid, msg, laneStat, wpStat, gotRP

def validateDataLineAdvanced(line, markerValueDict, laneStat, wpStat, gotRP):
    fields = line.split(',')
    msg = ''

    time    = fields[0]
    sats    = int(fields[1])
    hdop    = float(fields[2])
    lat     = float(fields[3])
    lon     = float(fields[4])
    elev    = float(fields[5])
    speed   = float(fields[6])
    heading = float(fields[7])
    marker  = fields[8]
    value   = fields[9]

    # Verify Reference Point
    if marker == 'RP' or  marker == 'RP+LC' or  marker == 'RP+LC':
        gotRP = True

    if value in markerValueDict['LC']:
        # Verify lane closure continuity
        if marker == 'LC' or  marker == 'RP+LC':
            if laneStat[value] != 0: 
                valid = False
                msg = "Lane closure invalid, closed lane being closed: " + str(marker) + ":" + str(value)
            else: 
                laneStat[value] = 1
        if marker == 'LO':
            if laneStat[value] != 1: 
                valid = False
                msg = "Lane closure invalid, open lane being opened: " + str(marker) + ":" + str(value)
            else: 
                laneStat[value] = 0
    else:
        # This error is caught by the basic validator
        pass

    # Verify worker presence continuity
    if marker == 'WP' or  marker == 'RP+WP':
        if str(wpStat) == value:
            valid = False
            msg = "Worker Presence change invalid, wp: " + str(wpStat) + ", value: " + str(value)
        else: 
            wpStat = not wpStat
    
    return valid, msg, laneStat, wpStat, gotRP

root.after(500, prepareDataFile)

# root.protocol("WM_DELETE_WINDOW", on_closing)

window.mainloop()

