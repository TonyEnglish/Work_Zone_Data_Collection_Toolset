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

from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

###
#   Following modules create:
#   .exer file (xml format) for based on ASN.1 definition for RSM as proposed to SAE for J2945/4 and J2735 (Data Dictionary)
###



###
#   Following to get user input for WZ config file name and display output for user...
### ---------------------------------------------------------------------------------------------------------------------

###
#   User input/output for work zone map builder is created using "Tkinter" (TK Interface) module. The  Tkinter
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

def inputFileDialog():
    filename = filedialog.askopenfilename(initialdir=configDirectory, title="Select Input File", filetypes=[("Config File","*.json")])
    if len(filename): 
        wzConfig_file.set(filename)
        configRead(filename)
        set_config_description(filename)
        btnBegin["state"]   = "normal"                    #enable the start button for map building...
        btnBegin["bg"]      = "green"        
    pass

##
#   -------------- End of input_file_dialog ------------------
##


def displayStatusMsg(xPos, yPos, msgStr):

    blankStr = " "*256
    Text = Label(root,anchor='w', justify=LEFT, text=blankStr)
    Text.place(x=xPos,y=yPos)    

    Text = Label(root,anchor='w', justify=LEFT, text=msgStr)
    Text.place(x=xPos,y=yPos)    


##
#   -------------- End of display_msg_str ---------------------
##

def buildWZMap():
    return
    global uper_failed
    
    if len(wzConfig_file.get()): 
        startMainProcess()

        if msgSegList[0][0] == -1:                          #Segmentation failed...
            messagebox.showinfo("WZ Map Builder", " ... ERROR -- in building message segmentation -- ERROR ...\n\n"+ \
                                                  "Review map_builder.log file in WP_MapMsg folder for detail...")
        elif uper_failed:
            messagebox.showinfo("WZ Map Builder", "UPER RSM Conversion failed\nEnsure Java is installed and\nadded to your system PATH")
        else:
            messagebox.showinfo("WZ Map Builder", "WZ Map Completed Successfully\nReview map_builder.log file in WP_MapMsg Folder...")
        pass
    
        btnView["state"]    = "normal"                      #enable button to view log file...
        btnView["bg"]       = "green"                       #set bg color to green
        btnStart["state"]   = "disabled"                    #disable start button so map can't be built more than once...
        btnStart["bg"]      = "gray75"        

    else:
        messagebox.showinfo("Read Config", "Choose WZ Configuration file!!!")

##
#   -------------- End of build_WZ_map ------------------------
##

def quitIt():
    
    if messagebox.askyesno("Quit", "Sure you want to quit?") == True:
        sys.exit(0)  
##
#   -------------- End of quitIt ------------------
##

def viewMapLogFile():
    return
    WZ_mapLogFile = "./WZ_MapMsg/map_builder_log.txt"
    if os.path.exists(WZ_mapLogFile):
        os.system("notepad " + WZ_mapLogFile)        
    
    else:
        messagebox.showinfo("WZ Map Log File","Work Zone Map Log File " + WZ_mapLogFile + " NOT Found ...")
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
            messagebox.showinfo("Read Config File", "Configuration file read failed: " + file + "\n" + str(e))
    else:
        messagebox.showinfo("Read Config", "Configuration file NOT FOUND: " + file + "\n" + str(e))

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
#   Assure that the vehicle path data file directory and file name exist.
#   If NOT, ask user to go back to WZ Configuration Step and correct file location
#   This can happen if the directory/file name is changed after doing the WZ configuration step...
#
#   Added on Nov. 6, 2018
#
###
#   vehPathDataFile - input data file
###

    # vehPathDataFile = dirName + "/" + fileName                          #complete file name with directory
           
    # if os.path.exists(dirName) == False:
    #     messagebox.showinfo("Veh Path Data Dir", "Vehicle Path Data file directory:\n\n"+dirName+"\n\nNOT found, correct directory name in WZ Configuration step...")
    #     btnStart["state"] = "disabled"                                  #enable button to view log file...
    #     btnStart["bg"] = "gray75"        
    #     sys.exit(0)

    # if os.path.exists(vehPathDataFile) == False:
    #     messagebox.showinfo("Veh Path Data file", "Vehicle Path Data file:\n\n"+fileName+"\n\nNOT found, correct file name in WZ Configuration step...")
    #     btnStart["state"] = "disabled"                                  #enable button to view log file...
    #     btnStart["bg"] = "gray75"        
    #     sys.exit(0)

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

    if wzStartDate == "":                                               #wz start date and time are mandatory
        wzStartDate = datetime.datetime.now().strftime("%Y-%m-%d")
        wzStartTime = time.strftime("%H:%M")
    pass

###
#   > > > > > > > > > > > START MAIN PROCESS < < < < < < < < < < < < < < <
###


##############################################################################################
#
# ----------------------------- END of startMainProcess --------------------------------------
#
###############################################################################################

def set_config_description(config_file):
    startDate_split = wzStartDate.split('/')
    start_date = startDate_split[0] + '/' + startDate_split[1] + '/' + startDate_split[2]
    endDate_split = wzEndDate.split('/')
    end_date = endDate_split[0] + '/' + endDate_split[1] + '/' + endDate_split[2]
    config_description = '----Selected Config File----\nDescription: ' + wzDesc + '\nRoad Name: ' + roadName + \
        '\nDate Range: ' + start_date + ' to ' + end_date + '\nConfig Path: ' + os.path.relpath(config_file)
    msg['text'] = config_description

def launch_WZ_veh_path_data_acq():
    config_file = wzConfig_file.get()
    if os.path.exists(local_config_path):
        os.remove(local_config_path)
    shutil.copy(config_file, local_config_path)
    #WZ_dataacq = "WZ_VehPathDataAcq_automated.pyw"
    #if os.path.exists(WZ_dataacq):
    #    os.system(WZ_dataacq)
    os.system('WZ_VehPathDataAcq_automated.pyw')
    sys.exit(0)
    #initialize(config_file, '')
    #else:
    #    messagebox.showinfo("WZ Vehicle Path Data Acq","WZ Vehicle Path Data Acquisition NOT Found...")

def downloadBlob(blobName):
    local_blob_path = './Config Files/' + blobName.split('/')[-1]
    blob_client = blob_service_client.get_blob_client(container='unzippedworkzonedatauploads', blob=blobName)
    with open(local_blob_path, "wb") as download_file:
        download_file.write(blob_client.download_blob().readall())

def downloadConfig():
    blobName = listbox.get(listbox.curselection())
    blob_full_name = blob_names_dict[blobName]
    downloadBlob(blob_full_name)

##
#   ---------------------------- END of Functions... -----------------------------------------
##
        
###
#   tkinter root window...
###

root = Tk()
root.title('Work Zone Data Collection')
root.geometry("1300x400")
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

cDT = datetime.datetime.now().strftime("%m/%d/%Y - ") + time.strftime("%H:%M:%S")

###
#   Map builder output log file...
###

logFile = open("./WZ_MapMsg/map_builder_log.txt", "w")         #log file
##logFile.write ("\n *** - "+wzDesc+" - ***\n")
logFile.write ("\n *** - Created: "+cDT+" ***\n")            

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
local_config_path = './Config Files/ACTIVE_CONFIG.json'



#with open(download_file_path, "wb") as download_file:
#    download_file.write(blob_client.download_blob().readall())

lbl_top = Label(text='Work Zone Data Collection\n', font='Helvetica 14', fg='royalblue', pady=10)
lbl_top.pack()

winSize = Label(root, height=15, width=100)
winSize.pack()

configDirectory = './Config Files'
most_recent_file = {'Name': '', 'Time': -1}
for config_file in os.listdir(configDirectory): #Find most recently edited config file in specified directory
    if '.json' in config_file and config_file != 'ACTIVE_CONFIG.json':
        time = os.path.getmtime(configDirectory + '/' + config_file)
        if time > most_recent_file['Time']:
            most_recent_file['Name'] = config_file
            most_recent_file['Time'] = time

msg = Label(text='No config file found, please select a config file below',bg='slategray1',justify=LEFT,anchor=W,padx=10,pady=10, font=("Calibri", 12))
msg.place(x=100, y=80)

###
#   Get WZ configuration input file...
###

diag_wzConfig_file  = Button(text='Choose Different\nLocal Config File', command=inputFileDialog, anchor=W,padx=5)
diag_wzConfig_file.place(x=10,y=220)

wzConfig_file_name  = Entry(relief=SUNKEN, textvariable=wzConfig_file, width=80)
wzConfig_file_name.place(x=150,y=235)


connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
if connect_str:
    download_file_path = './Config Files/local_config.json'
    #print("\nDownloading blob to \n\t" + download_file_path)

    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    container_client = blob_service_client.get_container_client("unzippedworkzonedatauploads")
    #blob_client = blob_service_client.get_blob_client(container='', blob='')

    blob_list = container_client.list_blobs()
    i = 0

    frame = Frame(root)
    frame.place(x=700, y=75)

    listbox = Listbox(frame, width=50, height=6, font=("Helvetica", 12), bg='slategray1')
    listbox.pack(side="left", fill="y")

    scrollbar = Scrollbar(frame, orient="vertical")
    scrollbar.config(command=listbox.yview)
    scrollbar.pack(side="right", fill="y")

    listbox.config(yscrollcommand=scrollbar.set)

    # listbox = Listbox(root, height=10, width=30)
    # listbox.place(x=700, y=50)
    # Scrollbar(listbox, orient="vertical")
    blob_names_dict = {}
    for blob in blob_list:
        blob_name = blob.name.split('/')[-1]
        if '.json' in blob_name:
            blob_names_dict[blob_name] = blob.name
            listbox.insert(END, blob_name)
        #temp_btn = Button(text=blob.name, font='Helvetica 10', fg = 'white', bg='green', padx=5, command=lambda:downloadBlob(blob.name))
        #temp_btn.place(x=50, y=0+30*i)
        #i += 1
        #print("\t" + blob.name)

    temp_btn = Button(text='Download Config', font='Helvetica 10', padx=5, command=lambda:downloadConfig())
    temp_btn.place(x=700, y=220)
else:
    messagebox.showinfo("Unable to retrieve azure credentials", "Unable to Retrieve Azure Credentials:\nTo enable cloud connection, configure your \
    \nenvironment variables and restart your command window")
    root.geometry("700x400")
#photoimage = PhotoImage(file="button_test.png").subsample(3, 3)
btnBegin = Button(text='Begin Data\nCollection', font='Helvetica 14',border=0,state=DISABLED,command=launch_WZ_veh_path_data_acq, anchor=W,padx=20,pady=10)
btnBegin.place(x=280,y=320)

if most_recent_file['Name']:
    rel_path = configDirectory + '/' + most_recent_file['Name']
    configRead(rel_path)
    wzConfig_file.set(os.path.abspath(rel_path))
    set_config_description(rel_path)
    btnBegin["state"]   = "normal"                    #enable the start button for map building...
    btnBegin["bg"]      = "green"        

###
#   Quit...
###

# btnQuit = Button(text='Quit',bg="red3",fg="white",command=quitIt, anchor=W,padx=5)
# btnQuit.place(x=440,y=330)


###
#   View Map Log File...
###

# btnView = Button(text='View\nLog File',bg="grey75",fg="white",state=DISABLED,command=viewMapLogFile, anchor=W,padx=5)
# btnView.place(x=630,y=320)


root.mainloop()

