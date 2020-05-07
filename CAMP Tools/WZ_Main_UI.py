#!/usr/bin/env python3
###
#   This software module to:
#   A. Parse the vehicle path data collected through traversing WZ lanes
#       A.1 construct node points for representing lane geometry for both approach and WZ lanes 
#           a. WZ map - Read collected vehicle path data file - lat,lon,elev,heading,speed,time, and few other elements
#           a. reference point - start of WZ   
#           b. approach lane geometry
#           b. WZ lane geometry 
#       A.2 Lane attributes
#           a. Lane closures (both offset from RP and nodeAttributeXYlist of taperToLeft and taperToRight
#           b. Support of opening of the closed lane up to 4 times
#           c.Presence of workers at designated area (zone) support of up to 4 zones 
#       A.3 WZ length
#       A.4 eventID, Duration, speed limits. etc.
#
#   B. Construct .exer (XML Format) file for WZ as prescribed in ASN.1 for RSM (SAE J2945/4 WIP) including:
#   C. Construct .js (javaScript) file containing several arrays for visualization overlay on Google Satellite map

#
#   By J. Parikh / Nov, 2017
#   Revised June 2018
#   Revised Aug  2018
#
#   Ver 2.0 -   Proposed new RSM/XML(EXER) for ASN.1 and map visualization
#
###

import  os.path
import sys
import subprocess

###
#     Open and read csv file...    
###

import  csv                                             #csv file processor
import  datetime                                        #Date and Time methods...
import  time                                            #do I need time???
import  math                                            #math library for math functions
import  random                                          #random number generator
import  json                                            #json manipulation
import  shutil
import  requests

from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

###
#   Following modules create:
#   .exer file (xml format) for based on ASN.1 definition for RSM as proposed to SAE for J2945/4 and J2735 (Data Dictionary)
###



###
#   Following to get user input for WZ config file name and display output for user...
### ---------------------------------------------------------------------------------------------------------------------

###
#   User input/output for work zone map builder is created using 'Tkinter' (TK Interface) module. The  Tkinter
#   is the standard Python interface to the Tk GUI toolkit from Scriptics (formerly developed by Sun Labs).
#
#   The public interface is provided through a number of Python modules. The most important interface module is the
#   Tkinter module itself.
#
#   Just import the Tkinter module to use
#
###

###

###if sys.version_info[0] == 3:
from tkinter                import *   
from tkinter                import messagebox
from tkinter                import filedialog

###
#   Following added to read and parse WZ config file
###

import  configparser                                    #config file parser 

global uper_failed
uper_failed = False
### ------------------------------------------------------------------------------------------------------------------
#
#   Local methods/functions...
###

###
#   ACTIONS... input file dialog...
###

# def inputFileDialog():
#     filename = filedialog.askopenfilename(initialdir=configDirectory, title='Select Input File', filetypes=[('Config File','*.json')])
#     if len(filename): 
#         wzConfig_file.set(filename)
#         configRead(filename)
#         set_config_description(filename)
#         btnBegin['state']   = 'normal'                    #enable the start button for map building...
#         btnBegin['bg']      = 'green'        
#     pass

##
#   -------------- End of input_file_dialog ------------------
##


# def displayStatusMsg(xPos, yPos, msgStr):

#     blankStr = ' '*256
#     Text = Label(root,anchor='w', justify=LEFT, text=blankStr)
#     Text.place(x=xPos,y=yPos)    

#     Text = Label(root,anchor='w', justify=LEFT, text=msgStr)
#     Text.place(x=xPos,y=yPos)    


##
#   -------------- End of display_msg_str ---------------------
##

# def quitIt():
    
#     if messagebox.askyesno('Quit', 'Sure you want to quit?') == True:
#         sys.exit(0)  
##
#   -------------- End of quitIt ------------------
##

# def viewMapLogFile():
#     return
#     WZ_mapLogFile = './WZ_MapMsg/map_builder_log.txt'
#     if os.path.exists(WZ_mapLogFile):
#         os.system('notepad ' + WZ_mapLogFile)        
    
#     else:
#         messagebox.showinfo('WZ Map Log File','Work Zone Map Log File ' + WZ_mapLogFile + ' NOT Found ...')
##
#   -------------- End of viewLogFile ------------------------
##
def configRead(file):
    global wzConfig
    if os.path.exists(file):
        try:
            cfg = open(file)
            wzConfig = json.loads(cfg.read())
            cfg.close()
            getConfigVars()
        except Exception as e:
            messagebox.showinfo('Read Config File', 'Configuration file read failed: ' + file + '\n' + str(e))
    else:
        messagebox.showinfo('Read Config', 'Configuration file NOT FOUND: ' + file + '\n' + str(e))

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

    # global  vehPathDataFile                                 #collected vehicle path data file
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

    dirName     = wzConfig['FILES']['VehiclePathDataDir']   #veh path data file directory
    fileName    = wzConfig['FILES']['VehiclePathDataFile']  #veh path data file name

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
    logMsg('Copying config file to ' + local_config_path)
    config_file = wzConfig_file.get()
    if os.path.exists(local_config_path):
        os.remove(local_config_path)
    shutil.copy(config_file, local_config_path)
    data_acq_file = 'WZ_VehPathDataAcq_automated.py'
    logMsg('Opening data acquisition file: ' + data_acq_file + ', and closing main ui')
    logMsg('Closing log file in Main UI')
    logFile.close()
    root.destroy()
    subprocess.call([sys.executable, data_acq_file]) #, shell=True
    # os.system(data_acq_file)
    sys.exit(0)

def downloadBlob(local_blob_path, blobName):
    logMsg('Downloading blob: ' + blobName + ', from container: ' + container_name + ', to local path: ' + local_blob_path)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blobName)
    with open(local_blob_path, 'wb') as download_file:
        download_file.write(blob_client.download_blob().readall())

def downloadConfig():
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
    # blob_blob_service = BlockBlobService(account_name="{Storage Account Name}", account_key="{Storage Account Key}")
    # if blob_blob_service.exists(container_name, blob_full_name.replace('json', 'zip')):
    #     messagebox.showwarning('Work zone already exists', 'If you continue you will overwrite the unpublished work zone data')

    local_blob_path = configDirectory + '/' + blobName

    downloadBlob(local_blob_path, blob_full_name)

    logMsg('Reading configuration file')
    configRead(local_blob_path)

    abs_path = os.path.abspath(local_blob_path)
    logMsg('Setting configuration path: ' + abs_path)
    wzConfig_file.set(abs_path)
    set_config_description(local_blob_path)
    btnBegin['state']   = 'normal'                    #enable the start button for map building...
    btnBegin['bg']      = 'green'

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

def laneClicked(i):
    print(i)

##
#   ---------------------------- END of Functions... -----------------------------------------
##
        
###
#   tkinter root window...
###

root = Tk()
root.title('Work Zone Data Collection')
root.geometry('1300x500')
#root.configure(bg='white')

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
    messagebox.showerror('No internet connection was detected', 'This application requires an internet connection to function\nPlease reconnect and restart this application')
    sys.exit(0)
logMsg('Internet connectivity test succeeded')
### --------------------------------------------------------------------------------------------------
#       Following are local variables with set default values...
#
#	Setup array for collected data for mapping, construcyed node points for approach and WZ lanes, and
#       reference point
### --------------------------------------------------------------------------------------------------

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

       
#############################################################################
# Tkinter LAYOUT to read user input for WZ config file name...
#############################################################################

wzConfig_file = StringVar()
configDirectory = './Config Files'
local_config_path = './Config Files/ACTIVE_CONFIG.json'

#with open(download_file_path, 'wb') as download_file:
#    download_file.write(blob_client.download_blob().readall())

lbl_top = Label(text='Work Zone Data Collection\n', font='Helvetica 14', fg='royalblue', pady=10)
lbl_top.pack()

winSize = Label(root, height=15, width=100)
winSize.pack()

msg = Label(text='No config file found, please select a config file below',bg='slategray1',justify=LEFT,anchor=W,padx=10,pady=10, font=('Calibri', 12))
msg.place(x=100, y=80)

###
#   Get WZ configuration input file...
###

# diag_wzConfig_file  = Button(text='Choose Different\nLocal Config File', command=inputFileDialog, anchor=W,padx=5)
# diag_wzConfig_file.place(x=10,y=220)

# wzConfig_file_name  = Entry(relief=SUNKEN, textvariable=wzConfig_file, width=80)
# wzConfig_file_name.place(x=150,y=235)


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

# listbox = Listbox(root, height=10, width=30)
# listbox.place(x=700, y=50)
# Scrollbar(listbox, orient='vertical')
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
load_config = Button(text='Load Configuration File', font='Helvetica 10', padx=5, command=downloadConfig)
load_config.place(x=100, y=320)
instructions = '''This component requires a good internet connection.
This is the configuration file selection component of the 
Work Zone Data Collection tool. To use the tool,
select a file from the list of punlished configuration files and
select 'Download Config'. When the correct configuration file
is selected and shown in the description box, select the
'Begin Data Collection' button to start data acquisition.
The data acquisition component will not record data until the set
starting location is reached.'''
instr_label = Label(text=instructions,justify=CENTER, bg='slategray1',anchor=W,padx=10,pady=10, font=('Calibri', 12))
instr_label.place(x=700, y=100)

btnBegin = Button(text='Begin Data\nCollection', font='Helvetica 14',border=2,state=DISABLED,command=launch_WZ_veh_path_data_acq, anchor=W,padx=20,pady=10)
btnBegin.place(x=570,y=350)

root.mainloop()