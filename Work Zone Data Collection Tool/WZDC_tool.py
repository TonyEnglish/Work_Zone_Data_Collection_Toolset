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

from    azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

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
def input_file_dialog():
    global local_config_path
    # global local_updated_config_path
    filename = filedialog.askopenfilename(initialdir=config_directory, title="Select Input File", filetypes=[("Config File","*.json")])
    if len(filename): 
        local_config_path = filename
        log_msg('Reading configuration file')
        try:
            read_config()

            log_msg('Setting configuration path: ' + local_config_path)
            # local_config_file = abs_path
            set_config_description(local_config_path)
            wz_config_file.set(local_config_path)
        except Exception as e:
            print(e)
            log_msg('ERROR: Config read failed, ' + str(e))
            messagebox.showerror('Configuration File Reading Failed', 'Configuration file reading failed. Please load a valid configuration file')

# Open and read config file
def read_config():
    global wz_config
    file = local_config_path
    if os.path.exists(file):
        cfg = open(file, 'r+')
        wz_config = json.loads(cfg.read())
        get_config_vars()
        cfg.close()

# Read configuration file
def get_config_vars():

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
    global  total_lanes                                      #total number of lanes in wz
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
    global  wz_start_lat                                     #wz start date
    global  wz_start_lon                                     #wz start time
    global  beginingAccuracy
    global  wz_end_lat                                       #wz end date
    global  wz_end_lon                                       #wz end time
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
    global  map_image_zoom
    global  map_image_center_lat
    global  map_image_center_lon
    global  mapImageMarkers
    global  marker_list
    global  map_image_map_type
    global  map_image_height
    global  map_image_width
    global  map_image_format
    global  mapImageString

    global  map_failed
    
    feed_info_id            = wz_config['FeedInfoID']

    wzDesc                  = wz_config['GeneralInfo']['Description']
    roadName                = wz_config['GeneralInfo']['RoadName']
    roadNumber              = wz_config['GeneralInfo']['RoadNumber']
    direction               = wz_config['GeneralInfo']['Direction']
    beginningCrossStreet    = wz_config['GeneralInfo']['BeginningCrossStreet']
    endingCrossStreet       = wz_config['GeneralInfo']['EndingCrossStreet']
    beginningMilepost       = wz_config['GeneralInfo']['BeginningMilePost']
    endingMilepost          = wz_config['GeneralInfo']['EndingMilePost']
    eventStatus             = wz_config['GeneralInfo']['EventStatus']
    creationDate            = wz_config['GeneralInfo'].get('CreationDate', '')
    updateDate              = wz_config['GeneralInfo'].get('UpdateDate', datetime.datetime.now().strftime(time_format_iso))

    typeOfWork = wz_config['TypesOfWork']
    if not typeOfWork: typeOfWork = []

    total_lanes              = int(wz_config['LaneInfo']['NumberOfLanes'])           #total number of lanes in wz
    laneWidth               = float(wz_config['LaneInfo']['AverageLaneWidth'])      #average lane width in meters
    lanePadApp              = float(wz_config['LaneInfo']['ApproachLanePadding'])   #approach lane padding in meters
    lanePadWZ               = float(wz_config['LaneInfo']['WorkzoneLanePadding'])   #WZ lane padding in meters
    dataLane                = int(wz_config['LaneInfo']['VehiclePathDataLane'])     #lane used for collecting veh path data
    lanes_obj               = list(wz_config['LaneInfo']['Lanes'])

    speedList               = wz_config['SpeedLimits']['NormalSpeed'], wz_config['SpeedLimits']['ReferencePointSpeed'], \
                              wz_config['SpeedLimits']['WorkersPresentSpeed']

    c_sc_codes              = [int(wz_config['CauseCodes']['CauseCode']), int(wz_config['CauseCodes']['SubCauseCode'])]

    startDateTime           = wz_config['Schedule']['StartDate']
    wzStartDate             = datetime.datetime.strptime(startDateTime, time_format_iso).strftime("%m/%d/%Y")
    wzStartTime             = datetime.datetime.strptime(startDateTime, time_format_iso).strftime("%H:%M")
    startDateAccuracy       = wz_config['Schedule'].get('StartDateAccuracy', 'estimated')
    endDateTime             = wz_config['Schedule']['EndDate']
    wzEndDate               = datetime.datetime.strptime(endDateTime, time_format_iso).strftime("%m/%d/%Y")
    wzEndTime               = datetime.datetime.strptime(endDateTime, time_format_iso).strftime("%H:%M")
    endDateAccuracy         = wz_config['Schedule'].get('EndDateAccuracy', 'estimated')
    wzDaysOfWeek            = wz_config['Schedule']['DaysOfWeek']

    wz_start_lat              = wz_config['Location']['BeginningLocation']['Lat']
    wz_start_lon              = wz_config['Location']['BeginningLocation']['Lon']
    beginingAccuracy        = wz_config['Location']['BeginningAccuracy']
    wz_end_lat                = wz_config['Location']['EndingLocation']['Lat']
    wz_end_lon                = wz_config['Location']['EndingLocation']['Lon']
    endingAccuracy          = wz_config['Location']['EndingAccuracy']

    wzLocationMethod        = wz_config['metadata']['wz_location_method']
    lrsType                 = wz_config['metadata']['lrs_type']
    locationVerifyMethod    = wz_config['metadata']['location_verify_method']
    dataFeedFrequencyUpdate = wz_config['metadata']['datafeed_frequency_update']
    timestampMetadataUpdate = wz_config['metadata']['timestamp_metadata_update']
    contactName             = wz_config['metadata']['contact_name']
    contactEmail            = wz_config['metadata']['contact_email']
    issuingOrganization     = wz_config['metadata']['issuing_organization']

    map_image_zoom            = wz_config['ImageInfo']['Zoom']
    map_image_center_lat       = wz_config['ImageInfo']['Center']['Lat']
    map_image_center_lon       = wz_config['ImageInfo']['Center']['Lon']
    mapImageMarkers         = wz_config['ImageInfo']['Markers'] # Markers:List of {Name, Color, Location {Lat, Lon, ?Elev}}
    marker_list = []
    for marker in mapImageMarkers:
        marker_list.append("markers=color:" + marker['Color'].lower() + "|label:" + marker['Name'] + "|" + str(marker['Location']['Lat']) + "," + str(marker['Location']['Lon']) + "|")
    map_image_map_type         = wz_config['ImageInfo']['MapType']
    map_image_height          = wz_config['ImageInfo']['Height']
    map_image_width           = wz_config['ImageInfo']['Width']
    map_image_format          = wz_config['ImageInfo']['Format']
    mapImageString          = wz_config['ImageInfo']['ImageString']

    if mapImageString:
        # TODO: Specify exception class
        try:
            fh = open(map_file_name, "wb")
            fh.write(base64.b64decode(mapImageString))
            fh.close()
            map_failed = False
        except:
            shutil.copy(map_failed_img, map_file_name)
            map_failed = True
    else:
        shutil.copy(map_failed_img, map_file_name)
        map_failed = True
 
# Set description box in UI from config file
def set_config_description(config_file):
    global is_config_ready
    global auto_radio_button
    global manual_radio_button

    if config_file:
        start_date_split = wzStartDate.split('/')
        start_date = start_date_split[0] + '/' + start_date_split[1] + '/' + start_date_split[2]
        end_date_split = wzEndDate.split('/')
        end_date = end_date_split[0] + '/' + end_date_split[1] + '/' + end_date_split[2]
        config_description = '----Selected Config File----\nDescription: ' + wzDesc + '\nRoad Name: ' + roadName + \
            '\nDate Range: ' + start_date + ' to ' + end_date + '\nConfig Path: ' + os.path.relpath(config_file)
        log_msg('Configuration File Summary: \n' + config_description)
        msg['text'] = config_description
        msg['fg'] = 'black'
        is_config_ready = True
        update_main_button()
        
        if wz_start_lat and wz_end_lat:
            auto_radio_button['state'] = NORMAL
            # v.set(1)
        else:
            auto_radio_button['state'] = DISABLED
            v.set(2)
    else:
        msg['text'] = 'NO CONFIGURATION FILE SELECTED'
        msg['fg'] = 'red'

# Move on to data collection/acquisition
def launch_wz_veh_path_data_acq():
    global needs_image
    global config_updated
    global manual_detection
    global wz_start_lat
    global wz_start_lon
    global wz_end_lat
    global wz_end_lon

    # If mamual detection:
    if v.get() == 2:
        manual_detection = True
        config_updated = True
        needs_image = True
        wz_start_lat = 0
        wz_start_lon = 0
        wz_end_lat = 0
        wz_end_lon = 0

    root.destroy()
    window.quit()

# Download blobl from Azure blob storage
def download_blob(local_blob_path, blob_name):
    log_msg('Downloading blob: ' + blob_name + ', from container: ' + container_name + ', to local path: ' + local_blob_path)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    with open(local_blob_path, 'wb') as download_file:
        download_file.write(blob_client.download_blob().readall())

# Download configuration file from Azure blob storage and read file
def download_config():
    global local_config_path
    # global local_updated_config_path
    blob_name = listbox.get(listbox.curselection())
    log_msg('Blob selected to download: ' + blob_name)

    blob_full_name = blob_names_dict[blob_name]

    #Check if unpublished work zone already exists, ask user if they want to overwrite
    file_found = False
    unapproved_container = 'unapprovedworkzones'
    unpublished_config_name = 'configurationfiles/' + blob_full_name
    # TODO: Specify exception class
    try:
        temp_container_client = blob_service_client.get_container_client(unapproved_container)
        temp_blob_client = temp_container_client.get_blob_client(unpublished_config_name)
        log_msg('Blob: ' + unpublished_config_name + ', found in container: ' + unapproved_container)
        file_found = True
    except:
        log_msg('Blob: ' + unpublished_config_name + ', not found in container: ' + unapproved_container)
    if file_found:
        msg_box = messagebox.askquestion('Work zone already exists','This Work zone already exists\nIf you continue you will overwrite the unpublished work zone data. Would you like to continue?',icon = 'warning')
        if msg_box == 'no':
            log_msg('User denied overwrite of unapproved work zone data')
            return
        log_msg('User accepted overwrite of unapproved work zone data')

    local_blob_path = config_directory + '/' + blob_name
    local_config_path = local_blob_path
    
    download_blob(local_blob_path, blob_full_name)

    log_msg('Reading configuration file')
    try:
        read_config()

        abs_path = os.path.abspath(local_blob_path)
        log_msg('Setting configuration path: ' + abs_path)
        set_config_description(local_blob_path)
        wz_config_file.set(local_config_path)
    except Exception as e:
        log_msg('ERROR: Config read failed, ' + str(e))
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
def log_msg(msg):
    formattedTime = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S') + '+00:00'
    try:
        log_file.write('[' + formattedTime + '] ' + msg + '\n')
    except:
        pass

# Enable/disable Begin Data Collection button
def update_main_button():
    if is_config_ready and is_gps_ready:
        btn_begin['state']   = 'normal'
        btn_begin['bg']      = 'green'
    else:
        btn_begin['state']   = 'disabled'
        btn_begin['bg']     = '#F0F0F0'

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

needs_image = False
config_updated = False
manual_detection = False
map_failed = False

json_ext = '.json'
geojson_ext = '.geojson'
uper_ext = '.uper'
xml_ext = '.xml'
text_font = 'Helvetica 10'

time_format_iso = "%Y-%m-%dT%H:%M:%SZ"

map_failed_img = './images/map_failed.png'
helvetica_14 = 'Helvetica 14'
choose_local_config = 'Choose Local\nConfig File'

###
#   WZ config parser object....
###

wz_config        = {}

cdt = datetime.datetime.now().strftime('%m/%d/%Y - ') + time.strftime('%H:%M:%S')

# Output log file
log_file_name = './data_collection_log.txt'
if os.path.exists(log_file_name):
    append_write = 'a' # append if already exists
else:
    append_write = 'w' # make a new file if not
log_file = open(log_file_name, append_write)         #log file
log_msg('*** Running Main UI ***')

# # Check java version for RSM binary conversion
# try:
#     java_version = subprocess.check_output(['java', '-version'], stderr=subprocess.STDOUT).decode('utf-8')
#     version_number = java_version.splitlines()[0].split()[2].strip('"')
#     major, minor, _ = version_number.split('.')
#     if (int(major) == 1 and int(minor) >= 8) or int(major) >= 1:
#         log_msg('Java version check successful. Java version detected was ' + major + '.' + minor)
#     else:
#         log_msg('ERROR: Incorrect java version. Java version detected was ' + major + '.' + minor)
#         log_msg('Closing Application')
#         log_file.close()
#         messagebox.showerror('Java version incorrect', 'This application requires Java version >=1.8 or jdk>=8.0. Java version detected was ' + major + '.' + minor + ', please update your java version and add it to your system path')
#         sys.exit(0)
# except FileNotFoundError as e:
#     log_msg('ERROR: Java installation not found')
#     log_msg('Closing Application')
#     log_file.close()
#     messagebox.showerror('Java Not Installed', 'This application requires Java to run, with version >=1.8 or jdk>=8.0. Ensure that java is inatalled, added to the system path, and that you have restarted your command window')
#     sys.exit(0)
# except Exception as e:
#     log_msg('ERROR: Unable to Verify Java Version, error: ' + str(e))
#     messagebox.showwarning('Unable to Verify Java Version', 'Unable to verify java version. Ensure that you have Java version >=1.8 or jdk>=8.0 installed and added to your system path')

config_directory = './Config Files'
local_config_path = ''
# local_updated_config_path = ''
is_config_ready = False

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
    log_msg('Error: Failed to load connection string from environment variable: ' + connect_str_env_var)
    # Unable to Retrieve Azure Credentials. To enable cloud connection, configure your environment variables and restart your command window
else:
    has_azure_connection = True
    log_msg('Loaded connection string from environment variable: ' + connect_str_env_var)

download_file_path = './Config Files/local_config.json'
map_file_name = "./mapImage.png"
refresh_img = ImageTk.PhotoImage(Image.open('./images/refresh_small.png'))

def load_cloud_content():
    global blob_service_client
    global blob_names_dict
    global container_name

    global frame
    global listbox
    global load_config
    global config_label_or
    global diag_wz_config_file

    global wz_config_file
    global wz_config_file_name

    # TODO: Specify Exception Class
    try:
        frame.destroy()
        listbox.destroy()
        load_config.destroy()
        config_label_or.destroy()
        diag_wz_config_file.destroy()
        wz_config_file_name.destroy()
    except:
        # TODO: Specify Exception Class
        try:
            config_label_or.destroy()
            diag_wz_config_file.destroy()
            wz_config_file_name.destroy()
        except:
            pass


    # If internet connection detected, load cloud config files
    if internet_on() and has_azure_connection:
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        container_name = 'publishedconfigfiles'
        container_client = blob_service_client.get_container_client(container_name)
        

        log_msg('Listing blobs in container:' + container_name)
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
        def get_modified_time_delta(blob):
            time_delta = now-blob.last_modified.replace(tzinfo=None)
            return time_delta

        blob_names_dict = {}
        blob_list_sorted = []
        for blob in blob_list:
            log_msg('Blob Name: ' + blob.name)
            blob_list_sorted.append(blob) #stupid line but this turns blob_list into a sortable list
        blob_list_sorted.sort(key=get_modified_time_delta) #sort files on last_modified date
        for blob in blob_list_sorted:
            blob_name = blob.name.split('/')[-1]
            if json_ext in blob_name:
                blob_names_dict[blob_name] = blob.name
                listbox.insert(END, blob_name)

        log_msg('Blobs sorted, filtered and inserted into listbox')
        load_config = Button(root, text='Load Cloud Configuration File', font=text_font, padx=5, command=download_config)
        load_config.place(x=100, y=320)

        config_label_or = Label(root, text='OR', font=text_font, padx=5)
        config_label_or.place(x=150, y=352)

        diag_wz_config_file = Button(root, text=choose_local_config, command=input_file_dialog, anchor=W,padx=5, font=text_font)
        diag_wz_config_file.place(x=115,y=380)
        # TODO: Specify Exception Class
        try:
            wz_config_file_name = Entry(root, relief=SUNKEN, state=DISABLED, textvariable=wz_config_file, width=50)
            wz_config_file_name.place(x=220,y=390)
        except:
            wz_config_file = StringVar()
            wz_config_file_name = Entry(root, relief=SUNKEN, state=DISABLED, textvariable=wz_config_file, width=50)
            wz_config_file_name.place(x=220,y=390)
    elif not internet_on:
        config_label_error = Label(root, text='No internet connection detected\nConnect to download\ncloud configuration files', bg='slategray1', font=text_font, padx=10, pady=10)
        config_label_error.place(x=150, y=200)

        diag_wz_config_file = Button(root, text=choose_local_config, command=input_file_dialog, anchor=W,padx=5, font=text_font)
        diag_wz_config_file.place(x=115,y=280)

        # TODO: Specify Exception Class
        try:
            wz_config_file_name = Entry(root, relief=SUNKEN, state=DISABLED, textvariable=wz_config_file, width=50)
            wz_config_file_name.place(x=220,y=290)
        except:
            wz_config_file = StringVar()
            wz_config_file_name = Entry(root, relief=SUNKEN, state=DISABLED, textvariable=wz_config_file, width=50)
            wz_config_file_name.place(x=220,y=290)

        refresh_button = Button(root, image = refresh_img, command=load_cloud_content)
        refresh_button.place(x=50, y=200)
    else:
        diag_wz_config_file = Button(root, text=choose_local_config, command=input_file_dialog, anchor=W,padx=5, font=text_font)
        diag_wz_config_file.place(x=115,y=210)

        # TODO: Specify Exception Class
        try:
            wz_config_file_name = Entry(root, relief=SUNKEN, state=DISABLED, textvariable=wz_config_file, width=50)
            wz_config_file_name.place(x=220,y=220)
        except:
            wz_config_file = StringVar()
            wz_config_file_name = Entry(root, relief=SUNKEN, state=DISABLED, textvariable=wz_config_file, width=50)
            wz_config_file_name.place(x=220,y=220)

radioHeight = 210
Label(root, text='Beginning and Ending of Work Zone Locations', font='Helvetica 12 bold', padx=10, pady=10).place(x=800,y=radioHeight)
v = IntVar()

auto_radio_button = Radiobutton(root, text="Automatic Detection (Recommended)", variable=v, value=1) #, indicatoron=0
manual_radio_button = Radiobutton(root, text="Manual Detection", variable=v, value=2)
v.set(1)
auto_radio_button.place(x=850, y=radioHeight+35)
manual_radio_button.place(x=850, y=radioHeight+60)


notes = '''Automatic detection uses the locations from the configuration file for the starting
and ending locations of data collection. Manual detection allows you to
manually start and end data collection. The manually set locations will be
set as the the automatic locations next time the work zone is mapped'''
notes_label = Label(root, text=notes,justify=CENTER, bg='slategray1',anchor=W, font=('Helvetica', 10))
notes_label.place(x=760, y=radioHeight+85)

load_cloud_content()

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

btn_begin = Button(root, text='Begin Data\nCollection', font=helvetica_14,border=2,state=DISABLED,command=launch_wz_veh_path_data_acq, anchor=W,padx=20,pady=10)
btn_begin.place(x=570,y=390)

is_gps_ready = False

# test serial port for GPS device (check for NMEA string)
def test_gps_connection(retry=False, *args):
    global is_gps_ready
    gps_fix = False
    gps_found = False
    try:
        ser = serial.Serial(port=tk_port_var.get()[0:5].strip(), baudrate=tk_baud_var.get(), timeout=1.1, )
        sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))
        
        nmea_data = sio.readline()
        if nmea_data:
            for i in range(20):
                nmea_data = sio.readline()
                if nmea_data[0:3] == '$GP' or nmea_data[0:3] == '$GN':
                    gps_found = True
                    if ((nmea_data[0:6] == '$GPVTG' or nmea_data[0:6] == '$GNVTG') and nmea_data.split(',')[1]) or ((nmea_data[0:6] == '$GPGGA' or nmea_data[0:6] == '$GNGGA') and nmea_data.split(',')[2]):
                        gps_fix = True
                        break

    except SerialException:
        # TODO: Add message window to display this message
        messagebox.showinfo('Port Closed', 'Serial port: ' + str(tk_port_var.get()) + ' is closed, if this is the GPS device please ensure that no other programs are already utilizing the device')
        return False

    if gps_found:
        if gps_fix:
            comm_label['text']   = 'GPS DEVICE FOUND'
            comm_label['fg']     = 'green'
            is_gps_ready = True
            update_main_button()
            return True
        else:
            comm_label['text']   = 'INVALID GPS POSITION'
            comm_label['fg']     = 'orange'
            return True
    else:
        btn_begin['state']   = 'disabled'
        btn_begin['bg']     = '#F0F0F0'
        comm_label['text']   = 'GPS DEVICE NOT FOUND'
        comm_label['fg']     = 'red'
        is_gps_ready = False
        return False

gpsHeight = 75
def showSerialDropdowns():
    serial_button.destroy()
    baud_label.place(x=850, y=gpsHeight+60)
    baud_popup_menu.place(x=850, y=gpsHeight+80)
    data_label.place(x=950, y=gpsHeight+60)
    data_popup_menu.place(x=950, y=gpsHeight+80)

# Set baud rate and data rate labels
baud_label = Label(root, text='Baud Rate (bps)')
baud_rates = ['4800', '9600', '19200', '57600', '115200']
tk_baud_var = StringVar(window)
tk_baud_var.set('115200') #default is 10 Hz, 115200bps
baud_popup_menu = OptionMenu(root, tk_baud_var, *baud_rates)

data_label = Label(root, text='Data Rate (Hz)')
data_rates = ['1', '2', '5', '10']
tk_data_var = StringVar(window)
tk_data_var.set('10') #default is 10 Hz, 115200bps
data_popup_menu = OptionMenu(root, tk_data_var, *data_rates)
serial_button = Button(root, text='Show Advanced Serial Settings', command=showSerialDropdowns)
serial_button.place(x=850, y=gpsHeight+60)

ports = serial.tools.list_ports.comports(include_links=False)
if not ports: ports = ['NO DEVICES FOUND']

# Frame for COMM port options
mainframe = Frame(root)
mainframe.place(x=850, y=gpsHeight)
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)

# Create COMM port popup menu
log_msg('Creating comm port popup menu')
comm_label = Label(mainframe, text='GPS DEVICE NOT FOUND', font='Helvetica 13 bold', fg='red')
tk_port_var = StringVar(window)
popup_menu = OptionMenu(mainframe, tk_port_var, *ports)
comm_label.pack()
popup_menu.pack()

# Update COMM ports popup menu and search for GPS device
def update_ports_dropdown():
    global popup_menu
    global ports
    ports = serial.tools.list_ports.comports(include_links=False)
    if not ports: ports = ['NO DEVICES FOUND']
    popup_menu.destroy()
    popup_menu = OptionMenu(mainframe, tk_port_var, *ports)
    popup_menu.pack()
    search_ports()

# Search COMM ports for GPS device
def search_ports():
    # TODO: Specify Exception Class
    try:
        tk_port_var.trace_vdelete("w", tk_port_var.trace_id)
    except:
        pass
    for port in ports:
        tk_port_var.set(port)
        if (test_gps_connection(True)):
            break
    tk_port_var.trace_id = tk_port_var.trace("w", test_gps_connection)

                                     # Car image
btn_test_gps = Button(root, image = refresh_img, command=update_ports_dropdown)                                  # Label with car image , command=load_cloud_content
btn_test_gps.place(x=800, y=gpsHeight+30)

def on_closing():
    log_file.close()
    sys.exit(0)

window.protocol("WM_DELETE_WINDOW", on_closing)
window.after(500, search_ports)
window.mainloop()
  

################################################################################################################
###
#--------------------------------------------------- WZ_VehPathDataAcq -----------------------------------------
###
################################################################################################################

# Start data collection function
def start_main_func():
    global  app_running                          #boolean
    if (app_running):
        log_msg('App running, starting get_nmea_string loop')
        get_nmea_string()                        #Get NMEA String and process it until 'app_running is True...'
    else:
        log_msg('App not running, exiting')

# Retrieve NMEA string and GPS data from device
def get_nmea_string():

###
#   Global variables...
###

    global      sio                                 #serial io
    global      gps_time, gps_date, prev_gps_time       #time, date and prev. GPS time
    global      key_marker, data_log                  #key marker and data log
    global      app_running                          #until Esc is pressed
    global      gps_lat, gps_lon, gps_alt              #needed for ref. pt, lane state and workers present locations
    global      car_pos_lat, car_pos_lon, car_pos_heading


###
#   Local variables...
###

    gps_sats     = 0                                 #No. of Satellites
    gps_speed    = 0.0                               #Speed in m/s
    gps_heading  = 0.0                               #Heading in degrees
    gps_hdop     = 0.0                               #Horizontal dilution of precision
    prev_distance = 0
    pi = 3.14159
    i = 0
    prevLat = 0
    prevLon = 0

    while (app_running):                             #continue reading and processing NMEA string while TRUE
        nmea_data = sio.readline()                   #Read NMEA string from serial port COM7
        root.update()

###
#
#       for more detail on NMEA sentence visit: ---  http://www.gpsinformation.org/dale/nmea.htm  ---
#
#       --- Parse GGA String---
#
###
        try:
            if nmea_data[0:6] == '$GPGGA' or nmea_data[0:6] == '$GNGGA':
                gga_out = parseGxGGA(nmea_data,gps_time,gps_sats,gps_alt)
                if gga_out[3] == True:
                    gps_time = gga_out[0]
                    gps_sats = gga_out[1]
                    gps_alt  = gga_out[2]
                pass
            pass

    ###
    #       --- Parse RMC ---
    ###

            if nmea_data[0:6] == '$GPRMC' or nmea_data[0:6] == '$GNRMC':
                RMC_out = parseGxRMC(nmea_data,gps_date,gps_lat,gps_lon,gps_speed,gps_heading)
                if RMC_out[5] == True:
                    gps_date     = RMC_out[0]
                    gps_lat      = RMC_out[1]
                    gps_lon      = RMC_out[2]
                    gps_speed    = RMC_out[3]*(1852.0/3600.0)    #Knot = 1.852 km/hr, Convert to m/s
                    gps_heading  = RMC_out[4]
                pass
            pass
            
    ###
    #       --- Parse GSA ---
    ###

            if nmea_data[0:6] == '$GPGSA' or nmea_data[0:6] == '$GNGSA':
                gsa_out = parseGxGSA(nmea_data,gps_hdop)
                if gsa_out[1] == True:
                    gps_hdop = gsa_out[0]
                pass
            pass
        except Exception as e:
            log_msg('ERROR: GPS parsing failed. ' + str(e))
            continue

        # Update marker position on map
        car_pos_lat = gps_lat
        car_pos_lon = gps_lon
        car_pos_heading = gps_heading
        update_position()
        
        # if data_log:
        #     distance_to_end_pt = round(dist(gps_lat*pi/180, gps_lon*pi/180, wz_end_lat*pi/180, wz_end_lon*pi/180))
        #     # TODO: Add check for direction of travel
        #     if distance_to_end_pt < 20 and got_ref_pt and not manual_detection:
        #         minLineDist, t = dist_to_line(prevLat*pi/180, prevLon*pi/180, gps_lat*pi/180, gps_lon*pi/180, wz_end_lat*pi/180, wz_end_lon*pi/180)
        #         if minLineDist < 20 and t > 0 and t < 1:
        #             log_msg('-------- Exiting Work Zone (by location, distance=' + str(distance_to_end_pt) + ') -------')
        #             stop_data_log()
        #     # TODO: Auto mark reference point
        #     elif not got_ref_pt and distance_to_start_pt > prev_distance and i >= 10: #Auto mark reference point
        #         log_msg('-------- Auto Marking Reference Point (by location, distance=' + str(distance_to_start_pt) + ') -------')
        #         mark_ref_pt()


        # Automatically start/end data collection
        if data_log:
            distance_to_end_pt = round(dist(gps_lat*pi/180, gps_lon*pi/180, wz_end_lat*pi/180, wz_end_lon*pi/180))
            if distance_to_end_pt < 20 and distance_to_end_pt > prev_distance and got_ref_pt and not manual_detection: #Leaving Workzone
                log_msg('-------- Exiting Work Zone (by location, distance=' + str(distance_to_end_pt) + ') -------')
                stop_data_log()
            distance_to_start_pt = round(dist(gps_lat*pi/180, gps_lon*pi/180, wz_start_lat*pi/180, wz_start_lon*pi/180))
            if not got_ref_pt and distance_to_start_pt > prev_distance and i >= 10: #Auto mark reference point
                log_msg('-------- Auto Marking Reference Point (by location, distance=' + str(distance_to_start_pt) + ') -------')
                mark_ref_pt()
            if got_ref_pt:
                prev_distance = distance_to_end_pt
            else:
                prev_distance = distance_to_start_pt
            i += 1

        else:
            distance_to_start_pt = round(dist(gps_lat*pi/180, gps_lon*pi/180, wz_start_lat*pi/180, wz_start_lon*pi/180))
            if distance_to_start_pt < 50 and not manual_detection: #Entering Workzone
                log_msg('-------- Entering Work Zone (by location, distance=' + str(distance_to_start_pt) + ') -------')
                start_data_log()
                prev_distance = distance_to_start_pt

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

        if (data_log == True) and (gps_time != prev_gps_time) and (gps_date != ''):              #log data only if next sentence(gps_time) is different from the previous
            time_date = gps_date+'-'+gps_time
            out_str  = time_date,gps_sats,gps_hdop,gps_lat,gps_lon,gps_alt,gps_speed,gps_heading,key_marker[0],key_marker[1]      #to CSV file...

            write_csv_file(out_str)                       #write to CSV file
            key_marker = ['','']                         #reset key marker
            prev_gps_time = gps_time                       #set prev_gps_time to gps_time             
        pass                                            #end of writing out_str

###
#       Save the last record with App Ended marker...
###


        if app_running == False:                         #save the last record...
            log_msg('App not running, save last dataset and exit')
            time_date = gps_date+'-'+gps_time
            out_str  = time_date,gps_sats,gps_hdop,gps_lat,gps_lon,gps_alt,gps_speed,gps_heading,key_marker[0],key_marker[1]      #to CSV file...
            write_csv_file(out_str)                       #write to CSV file
        pass

    return

###
#   
#   -------------------  END OF get_nmea_string...  ---------------------------------------------------------------------
#
##

# Calculate accurate distance between GPS points
def dist(lat1, lon1, lat2, lon2):
    r = 6371000
    avg_lat = (lat1+lat2)/2
    distance = r*math.sqrt((lat1-lat2)**2+math.cos(avg_lat)**2*(lon1-lon2)**2)
    return distance

# TODO: Determine if need lon=lon*cos(lat)
# def dist_to_line(v1, v2, w1, w2, p1, p2):
#     l = dist(v1, v2, w1, w2) ** 2
#     t = max(0, min(1, dot(dif(p1, p2, v1, v1), dif(w1, w2, v1, v2))))
#     pp1 = v1 + t * (w1 - v1)
#     pp2 = v2 + t * (w2 - v2)
#     return dist(p1, p2, pp1, pp2), t

# def dot(v1, v2, w1, w2):
#     return v1 * w1 + v2 * w2

# def dif(v1, v2, w1, w2):
#     return v1 - w1, v2 - w2

# Toggle lane closures
def lane_clicked(lane):
    global got_ref_pt
    global lane_stat
    global key_marker
    global lane_Symbols

    lane_stat[lane] = not lane_stat[lane]         #Lane open status (T or F)
    lc = 'LC'                                   #set lc to 'LC' - Lane Closed
    if lane_stat[lane]:
        lc = 'LO'                               #toggle lane status to Lane Open
        lanes[lane]['bg']   = 'green'
        lanes[lane]['fg']   = 'white'
        lane_labels[lane]['fg'] = 'green'
        lane_labels[lane]['text'] = 'OPEN'
        lane_labels[lane].place(x=margin_left+22 + (lane-1)*110, y=100)
    else:
        lanes[lane]['bg']   = 'gray92'
        lanes[lane]['fg']   = 'red3'
        lane_labels[lane]['fg'] = 'red3'
        lane_labels[lane]['text'] = 'CLOSED'
        lane_labels[lane].place(x=margin_left+10 + (lane-1)*110, y=100)

    if not got_ref_pt:                       #if ref pt has not been marked yet
        lc = lc + '+RP'                         #lc + ref. pt
        got_ref_pt = True                         #set to true
    pass

    lStat = 'Closed'
    if lc == 'LO': lStat = 'Open'
        
    marker_str = '   *** Lane '+str(lane)+' Status Marked: '+lStat+' @ '+str(gps_lat)+', '+str(gps_lon)+', '+str(gps_alt)+' ***'
    log_msg('*** Lane '+str(lane)+' Status Marked: '+lStat+' @ '+str(gps_lat)+', '+str(gps_lon)+', '+str(gps_alt)+' ***')
    key_marker = [lc, str(lane)]
    display_status_msg(marker_str)

# Toggle worker presence
def workers_present_clicked():
    global got_ref_pt
    global wp_stat
    global key_marker
    global workers_present_label

    wp_stat = not wp_stat                         #Toggle wp/np

    if wp_stat:
        btn_wp['text'] = 'Workers No\nLonger Present'
        btn_wp['bg']   = 'gray92'
        btn_wp['fg']   = 'red3'
        workers_present_label = Label(root, image = workers_present_img)
        workers_present_label.place(x=margin_left+60 + (total_lanes)*110, y=100)
    else:
        btn_wp['text'] = 'Workers are\nPresent'
        btn_wp['bg']   = 'green'
        btn_wp['fg']   = 'white'
        workers_present_label.destroy()

    marker_str = '   *** Workers Presence Marked: '+str(wp_stat)+' ***'
    log_msg('*** Workers Presence Marked: '+str(wp_stat)+' ***')

    key_marker[0] = 'WP'                         #WP marker
    if got_ref_pt == False:
        key_marker[0]='WP+RP'                    #WP+ref pt
        got_ref_pt = True                         #got_ref_pt True    
    key_marker[1] = wp_stat
    display_status_msg(marker_str)

# Start data logging
def start_data_log():
    global data_log
    global key_marker

    data_log = True

    marker_str = '   *** Data Logging Started ***'
    log_msg('*** Data Logging Started ***')

    key_marker = ['Data Log', data_log]

    overlay.destroy()
    enable_form()

    display_status_msg(marker_str)

# Stop data logging and move to message building
def stop_data_log():
    global data_log
    global key_marker
    global app_running

    data_log = False

    marker_str = '   *** Data Logging Stopped ***'
    log_msg('*** Data Logging Stopped ***')

    key_marker = ['Data Log', data_log]

    display_status_msg(marker_str)
    app_running = False

# Mark reference point
def mark_ref_pt():
    global got_ref_pt
    global key_marker

    if not got_ref_pt:
        marker_str = '   *** Reference Point Marked @ '+str(gps_lat)+', '+str(gps_lon)+', '+str(gps_alt)+' ***'
        log_msg('*** Reference Point Marked @ '+str(gps_lat)+', '+str(gps_lon)+', '+str(gps_alt)+' ***')
        key_marker = ['RP','']                       #reference point
        got_ref_pt = True                             #got the reference point

        display_status_msg(marker_str)

def mark_start_pt():
    global wz_config
    global wz_start_lat
    global wz_start_lon

    btn_start['state'] = DISABLED
    btn_start['bg'] = 'gray92'

    wz_config['Location']['BeginningLocation']['Lat'] = gps_lat
    wz_config['Location']['BeginningLocation']['Lon'] = gps_lon
    wz_start_lat = gps_lat
    wz_start_lon = gps_lon

    marker_str = '   *** Starting Point Marked @ '+str(gps_lat)+', '+str(gps_lon)+', '+str(gps_alt)+' ***'
    log_msg('*** Starting Point Marked @ '+str(gps_lat)+', '+str(gps_lon)+', '+str(gps_alt)+' ***')
    display_status_msg(marker_str)

    start_data_log()

def mark_end_pt():
    global wz_config
    global wz_end_lat
    global wz_end_lon

    wz_config['Location']['EndingLocation']['Lat'] = gps_lat
    wz_config['Location']['EndingLocation']['Lon'] = gps_lon
    wz_end_lat = gps_lat
    wz_end_lon = gps_lon


    center_lat = (float(wz_start_lat) + float(wz_end_lat))/2
    center_lon = (float(wz_start_lon) + float(wz_end_lon))/2
    center = str(center_lat) + ',' + str(center_lon)

    north = max(float(wz_start_lat), float(wz_end_lat))
    south = min(float(wz_start_lat), float(wz_end_lat))
    east = max(float(wz_start_lon), float(wz_end_lon))
    west = min(float(wz_start_lon), float(wz_end_lon))
    calc_zoom_level(north, south, east, west, map_image_width, map_image_height)

    wz_config['ImageInfo']['Zoom'] = zoom
    wz_config['ImageInfo']['Center']['Lat'] = center_lat
    wz_config['ImageInfo']['Center']['Lon'] = center_lon
    markers = []
    markers.append({'Name': 'Start', 'Color': 'Green', 'Location': {'Lat': wz_start_lat, 'Lon': wz_start_lon, 'Elev': None}})
    markers.append({'Name': 'End', 'Color': 'Red', 'Location': {'Lat': wz_end_lat, 'Lon': wz_end_lon, 'Elev': None}})
    wz_config['ImageInfo']['Markers'] = markers
    wz_config['ImageInfo']['MapType'] = map_image_map_type
    wz_config['ImageInfo']['Height'] = map_image_height
    wz_config['ImageInfo']['Width'] = map_image_width
    wz_config['ImageInfo']['Format'] = map_image_format
    wz_config['ImageInfo']['ImageString'] = ""


    marker_str = '   *** Ending Point Marked @ '+str(gps_lat)+', '+str(gps_lon)+', '+str(gps_alt)+' ***'
    log_msg('*** Ending Point Marked @ '+str(gps_lat)+', '+str(gps_lon)+', '+str(gps_alt)+' ***')
    display_status_msg(marker_str)

    stop_data_log()

# Write line to CSV data vile
def write_csv_file(write_str):
    global write_data                            #file handle
    
    write_data.writerow(write_str)               #write output to csv file...

# Display message in status window
def display_status_msg(msg_str):

    x_pos = margin_left-80+45
    y_pos = 410
    blank_str = ' '*190
    text_label = Label(root,anchor='w', justify=LEFT, text=blank_str)
    text_label.place(x=x_pos,y=y_pos)    

    text_label = Label(root,anchor='w', justify=LEFT, text=msg_str)
    text_label.place(x=x_pos,y=y_pos)    


# Enable buttons and remove overlay message
def enable_form():
    for i in range(1, total_lanes+1):
        if i != dataLane:
            lanes[i]['fg'] = 'white'
            lanes[i]['bg'] = 'green'
            lanes[i]['state'] = NORMAL
        else:
            lanes[i]['text'] = 'Lane ' + str(i) + '\n(Vehicle Lane)'
    btn_wp['fg'] = 'white'
    btn_wp['bg'] = 'green'
    btn_wp['state'] = NORMAL



gps_date     = ''                                #GPS Date
gps_time     = ''                                #GPS Time
prev_gps_time = ''                                #previous GPS Time
gps_lat      = 0.0                               #Latitude in degrees in decimal
gps_lon      = 0.0                               #Longitude in degrees in decimal
gps_alt      = 0.0                               #Altitude in meters

data_log     = False                             #data logging off
app_running  = True                              #set application running to TRUE
key_marker   = ['',0]                            #marker from key press
got_ref_pt    = False                             #got Ref. Point
wp_stat      = False                             #workers not present
                                                #pressing the same lane # key will toggle the from close to open  

cdt = datetime.datetime.now().strftime('%m/%d/%Y - ') + time.strftime('%H:%M:%S')

files_list      = []


comm_port = tk_port_var.get()[0:4]
baud_rate = int(tk_baud_var.get())
data_rate = int(tk_data_var.get())

log_msg('*** Running Vehicle Path Data Acquisition ***')

out_dir      = './WZ_VehPathData'
veh_path_data_file_name = 'path-data--' + wzDesc.lower().strip().replace(' ', '-') + '--' + roadName.lower().strip().replace(' ', '-') + '.csv'
veh_path_data_file = out_dir + '/' + veh_path_data_file_name

##########################################################################
#
# Setup data collection UI
#
############################################################################

margin_left = 750
window_width = max(1400, total_lanes*100+300+margin_left)
window.geometry(str(window_width)+'x750')
root = Frame(width=window_width, height=750)
root.place(x=0, y=0)
# root.bind_all('<Key>', keyPress)                #key press event...

lane_stat = [True]*(total_lanes+1) #all 8 lanes are open (default), Lane 0 is not used...

lbl_top = Label(root, text='Vehicle Path Data Acquisition\n\n', font=helvetica_14, fg='royalblue', pady=10)
lbl_top.place(x=window_width/2-250/2, y=10)

lane_line = ImageTk.PhotoImage(Image.open('./images/verticalLine_thin.png'))                             # Lane Line
car_img = ImageTk.PhotoImage(Image.open('./images/caricon.png'))                                         # Car image
car_label = Label(root, image = car_img)                                                                  # Label with car image
workers_present_img = ImageTk.PhotoImage(Image.open('./images/workersPresentSign_small.png'))             # Workers present image
userPositionImg = ImageTk.PhotoImage(Image.open('./images/blue-circle.png'))                            # Workers present image


map_file_name = "./mapImage.png"

zoom = 10

# re-initialized
map_image_height = 640
map_image_width = 640
center = "40.4742350,-104.9692566"
imgFormat = "png"
vert_bound = 0
horiz_bound = 0
car_pos_lat = 0
car_pos_lon = 0
car_pos_heading = 0
marker_height = 20
marker_width = 20

if not marker_list:
    marker_list = []
    marker_list.append("markers=color:green|label:Start|" + str(wz_start_lat) + "," + str(wz_start_lon) + "|")
    marker_list.append("markers=color:red|label:End|" + str(wz_end_lat) + "," + str(wz_end_lon) + "|")

# Calculate map bounds from google maps zoom level
def get_current_map_bounds():
    global horiz_bound
    global vert_bound

    # zoom = math.log(pixelWidth * 360 / angle / globe_width) / math.log(2)
    # globe_width * e ^ (zoom * math.log(2)) = pixelWidth * 360 / angle

    globe_width = 256
    scale = 360 / (globe_width * math.e**(zoom * math.log(2)))
    horiz_bound = map_image_width * scale
    vert_bound = map_image_height * scale * math.cos(center_lat*math.pi/180) #.77 -78.388249  * math.cos(center_lat*math.pi/180)

# Caculate pixel location on screen from bounds (Linear Interpolation)
def getPixelLocation(lat, lon):
    x = (lon - center_lon) / (horiz_bound / 2)
    y = -(lat - center_lat) / (vert_bound / 2) # / math.cos(lat*math.pi/180) * math.cos(center_lat*math.pi/180)
    x = round((map_image_width/2) + x * (map_image_width/2) - (marker_width/2))
    y = round((map_image_height/2) + y * (map_image_height/2) - (marker_height/2))
    if (x < 0 or x > map_image_width) or (y < 0 or y > map_image_height):
        x = -1
        y = -1
    return x, y

# Calculate google maps zoom level to fit a rectangle
def calc_zoom_level(north, south, east, west, pixelWidth, pixelHeight):
    global zoom
    global center_lat

    globe_width = 256
    zoom_max = 21
    angle = east - west
    if angle < 0:
        angle += 360
    zoom_horiz = round(math.log(pixelWidth * 360 / angle / globe_width) / math.log(2)) - 1

    angle = north - south
    center_lat = (north + south) / 2
    if angle < 0:
        angle += 360
    zoom_vert = round(math.log(pixelHeight * 360 / angle / globe_width * math.cos(center_lat*math.pi/180)) / math.log(2)) - 1

    zoom = max(min(zoom_horiz, zoom_vert, zoom_max), 0)
    get_current_map_bounds()


### Center Location
# If center coordinates present in configuration file, write center to global vars
if map_image_center_lat and map_image_center_lon:
    center_lat = float(map_image_center_lat)
    center_lon = float(map_image_center_lon)
    center = str(center_lat) + ',' + str(center_lon)
# If center coordinates not present and automatic detection, recalculate center based on coordinates
elif not manual_detection:
    center_lat = (float(wz_start_lat) + float(wz_end_lat))/2
    center_lon = (float(wz_start_lon) + float(wz_end_lon))/2
    center = str(center_lat) + ',' + str(center_lon)
# If center coordinates not present and manual detection, do nothing


### Zoom Level
# If zoom level set in configuration file, write zoom to global var
if map_image_zoom:
    zoom = int(map_image_zoom)
    get_current_map_bounds()
# If zoom level not set and automatic detection, recalculate zoom level
elif not manual_detection:
    north = max(float(wz_start_lat), float(wz_end_lat))
    south = min(float(wz_start_lat), float(wz_end_lat))
    east = max(float(wz_start_lon), float(wz_end_lon))
    west = min(float(wz_start_lon), float(wz_end_lon))
    calc_zoom_level(north, south, east, west, map_image_width, map_image_height)
# If zoom level not set and manual detection, do nothing


### Map Image
# If manual detection, set image to map_failed
if manual_detection: #No map image to load
    shutil.copy(map_failed_img, map_file_name)
    map_failed = True
map_img = ImageTk.PhotoImage(Image.open(map_file_name))

# Exit data collection loop and quit
def end_application():
    global app_running
    app_running = False
    log_file.close()
    sys.exit(0)

# Initialize UI lane variables
lanes = [0]*(total_lanes+1)
lane_boxes = [0]*(total_lanes+1)
lane_labels = [0]*(total_lanes+1)
lane_Symbols = [0]*(total_lanes+1)
lane_lines = [0]*(total_lanes+1)

map_label = Label(root, image = map_img)
map_label.place(x=50, y=60)

user_car_label = Label(root, image = userPositionImg, highlightthickness = 0, borderwidth = 0, width= 0, height = 0)

# Update position of marker on screen
def update_position():
    global user_car_label
    if not map_failed:
        x, y = getPixelLocation(car_pos_lat, car_pos_lon)
        user_car_label.place(x=x + 50, y=y + 60)
    else:
        user_car_label.place(x=-1 + 50, y=-1 + 60)

# Initialize lane images
for i in range(total_lanes):
    lane_lines[i] = Label(root, image = lane_line)
    lane_lines[i].place(x=margin_left + i*110, y=50)
    if i+1 == dataLane:
        car_label.place(x=margin_left+8 + i*110, y=50)
    else:
        lane_boxes[i+1] = Label(root, justify=LEFT,anchor=W,padx=50,pady=90)
        lane_boxes[i+1].place(x=margin_left+10 + i*110, y=50)
        lane_labels[i+1] = Label(root, text='OPEN',justify=CENTER,font='Calibri 22 bold',fg='green')
        lane_labels[i+1].place(x=margin_left+22 + i*110, y=100)
    if i == total_lanes-1:
        lane_lines[i+1] = Label(root, image = lane_line)
        lane_lines[i+1].place(x=margin_left + (i+1)*110, y=50)

# This is required because otherwise the lane command lane_clicked(lane #) cannot be set in a for loop
def create_button(id):
    lane_btn = Button(root, text='Lane '+str(id), font=text_font, state=DISABLED, width=11, height=4, command=lambda:lane_clicked(id))
    lane_btn.place(x=margin_left+10 + (id-1)*110, y=300)
    return lane_btn

# Create lane buttons dynamically to number of lanes
for i in range(1, total_lanes+1):
    lanes[i] = create_button(i)

# Toggle workers present button
btn_wp = Button(root, text='Workers are\nPresent', font=text_font, state=DISABLED, width=11, height=4, command=lambda:workers_present_clicked())
btn_wp.place(x=margin_left+60 + (total_lanes)*110, y=300)


if manual_detection:
    btn_start = Button(root, text='Mark Start of\nWork Zone', font=text_font, padx=5, bg='green', fg='white', command=mark_start_pt)
    btn_start.place(x=margin_left-100+150, y=510)
    btn_end = Button(root, text='Mark End of\nWork Zone', font=text_font, padx=5, bg='red3', fg='gray92', command=mark_end_pt)
    btn_end.place(x=margin_left-100+450, y=510)

###
#   Application Message Window...
###

app_msg_win = Button(root, text='Application Message Window...                                             ',      \
                font='Courier 10', justify=LEFT,anchor=W,padx=10,pady=10)
app_msg_win.place(x=margin_left-80+50, y=400)
overlay_width = 710
overlay_x = margin_left + (window_width - margin_left)/2 - overlay_width/2
overlay = Label(root, text='Application will begin data collection\nwhen the starting location has been reached', bg='gray', font='Calibri 28')
if manual_detection:
    overlay['text'] = 'Application will begin data collection\nwhen the starting location is marked'
overlay.place(x=overlay_x, y=200)


##############################################################
#   ------------------ END of LAYOUT -------------------------
##############################################################


gps_found = False
first = True
while not gps_found:
    try:
        ser         = serial.Serial(port=comm_port, baudrate=baud_rate, timeout=1.1, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)               #open serial port
        msg_str      = '   Vehicle Path Data Acquisition is Ready - Logging Will Start When Start Location is Reached'
        display_status_msg(msg_str)                                                        #system ready
        gps_found = True

    except SerialException as e:
        log_msg('Failed to find GPS device, SerialException: ' + str(e))
        msg_box = messagebox.askquestion ('GPS Receiver NOT Found','*** GPS Receiver NOT Found ***, Reconnect to USB Port ***\n\n'   \
                    '   --- Press Yes to try again, No to exit the application ---',icon = 'warning')
        if msg_box == 'no':
            log_msg('User exited application')
            log_file.close()
            sys.exit(0)                                                 #system ready

###
#   EOL is not supported in PySerial for readline() in Python 3.6.
#   must use sio
###

log_msg('Creating serial IO connection')
sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))

#   Open out_file for csv write...
log_msg('Opening path data output file: ' + veh_path_data_file)
out_file     = open(veh_path_data_file,'w',newline='')
write_data   = csv.writer(out_file)

# Write heading to file
title_line = 'GPS Date & Time','# of Sats','HDOP','Latitude','Longitude','Altitude(m)','Speed(m/s)','Heading(Deg)','Marker','Value'
write_csv_file(title_line)

###
#
#   -----------------------  Start Main Function  -----------------------------
#
###

log_msg('Starting main loop')

window.protocol("WM_DELETE_WINDOW", end_application)
start_main_func()                                         #main function, starts NMEA processing 

log_msg('Main loop ended, closing streams/files')

###
#   Done, close everything...
###

ser.close()                                             #close serial IO
out_file.close()                                         #end of data acquisition and logging
log_msg('Ending data acquisition')
root.destroy()
window.quit()

def uploadFile():
    upload_container = "workzoneuploads"
    if internet_on():
        log_msg('Creating blob in azure: ' + blob_name + ', in container: ' + upload_container)
        blob_client = blob_service_client.get_blob_client(container=upload_container, blob=blob_name)
        log_msg('Uploading zip archive to blob')
        with open(veh_path_data_file, 'rb') as data:
            blob_client.upload_blob(data, overwrite=True)
        log_msg('Closing log file in Message Builder and Export')
        log_file.close()
        messagebox.showinfo('Upload Successful', 'Data upload successful! Please navigate to\nhttp://www.neaeraconsulting.com/V2x_Verification\nto view and verify the mapped workzone.\nYou will find your data under\n' + name_id)
        sys.exit(0)
    else:
        log_msg('Attempted uploadArchive, no internet connection detected')
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
log_msg('*** Running Message Builder and Export ***')

description = wzDesc.lower().strip().replace(' ', '-')
road_name = roadName.lower().strip().replace(' ', '-')
name_id = description + '--' + road_name
blob_name = 'path-data--' + name_id + '.csv'

def prepare_data_file():
    global blob_name
    if config_updated:
        blob_name = blob_name.replace('.csv', '--update-image.csv')
        # updateConfigImage()

    valid, msgs = validate_data_file()
    if not valid:
        messages = '\n'
        for msg in msgs:
            messages = messages + msg + '\n'
        message = 'CSV Data File Not Valid' + '\n' + '------' + messages + '------' + '\n' + 'Fix these issues before uploading' + '\n'
        messagebox.showerror('Data File Invalid',message + 'After fixing, upload to to https://neaeraconsulting.com/V2X_Upload')
        sys.exit(0)

    if has_azure_connection:
        log_msg('Loaded connection string from environment variable: ' + connect_str_env_var)
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        container_name = 'workzonedatauploads'

        load_config['bg'] = 'green'
        load_config['state']= NORMAL
        loading_label.destroy()
    else:
        log_msg('Closing log file in Message Builder and Export')
        log_file.close()
        messagebox.showinfo('Upload Data File', 'Data file generation complete. Please upload the\ngenerated CSV file: ' + veh_path_data_file.split('/')[-1] + '\nto https://neaeraconsulting.com/V2X_Upload')
        sys.exit(0)

def validate_data_file():
    laneList = range(1, total_lanes)
    print(laneList)
    markerList = ['Data Log', 'RP', 'WP+RP', 'LC+RP', 'WP', 'LC', 'LO', '']
    markerValueDict = {'Data Log': ['True', 'False'], 'RP': '', 'WP+RP': ['True', 'False'], 'LC+RP': laneList, 
    'WP': ['True', 'False'], 'LC': laneList, 'LO': laneList, '': ''}

    lane_stat = [0]*9
    wp_stat = False
    messages = []
    file_valid = True
    got_rp = False
    i = 0
    with open(veh_path_data_file, 'r') as f:
        headers = f.readline()
        data = f.readline().rstrip('\n')
        while data:
            i += 1
            valid, msg, lane_stat, wp_stat, got_rp = validate_data_line(data, markerList, markerValueDict, lane_stat, wp_stat, got_rp)
            if not valid:
                vileValid = False
                messages.append('Line ' + str(i) + " " + msg)

            data = f.readline().rstrip('\n')

        if not got_rp == True:
            file_valid = False
            messages.append(" No reference point found by end")
        if not wp_stat == False:
            file_valid = False
            messages.append("Workers present not false at end")
        if not lane_stat == [0]*9:
            file_valid = False
            messages.append("All lanes not open at end")
                
    return file_valid, messages

def validate_data_line(line, markerList, markerValueDict, lane_stat, wp_stat, got_rp):
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
    if not re.match('([0-9]){4}\/(0[1-9]|1[0-2])\/([0-9]){2}-(0[0-9]|1[0-9]|2[0-4]):([0-5][0-9]):([0-5][0-9]):([0-9]){2}', time): 
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

    adv_valid, adv_msg, lane_stat, wp_stat, got_rp = validate_data_line_advanced(line, markerValueDict, lane_stat, wp_stat, got_rp)
    if not adv_valid or not valid:
        valid = False
    for msg_str in adv_msg:
        msg.append(msg_str)

    return valid, msg, lane_stat, wp_stat, got_rp

def validate_data_line_advanced(line, markerValueDict, lane_stat, wp_stat, got_rp):
    fields = line.split(',')
    msg = ''
    valid = True

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
    if marker == 'RP' or  marker == 'LC+RP' or  marker == 'LC+WP':
        got_rp = True

    if value in markerValueDict['LC']:
        # Verify lane closure continuity
        if marker == 'LC' or  marker == 'LC+RP':
            if lane_stat[value] != 0: 
                valid = False
                msg = "Lane closure invalid, closed lane being closed: " + str(marker) + ":" + str(value)
            else: 
                lane_stat[value] = 1
        if marker == 'LO':
            if lane_stat[value] != 1: 
                valid = False
                msg = "Lane closure invalid, open lane being opened: " + str(marker) + ":" + str(value)
            else: 
                lane_stat[value] = 0
    else:
        # This error is caught by the basic validator
        pass

    # Verify worker presence continuity
    if marker == 'WP' or  marker == 'WP+RP':
        if str(wp_stat) == value:
            valid = False
            msg = "Worker Presence change invalid, wp: " + str(wp_stat) + ", value: " + str(value)
        else: 
            wp_stat = not wp_stat
    
    return valid, msg, lane_stat, wp_stat, got_rp

root.after(500, prepare_data_file)

window.mainloop()

