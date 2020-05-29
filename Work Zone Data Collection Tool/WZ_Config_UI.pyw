#!/usr/bin/env python3

###
#
#   This user input for work zone configuration is created using "Tkinter" (TK Interface) module. The  Tkinter
#   is the standard Python interface to the Tk GUI toolkit from Scriptics (formerly developed by Sun Labs).
#
#   Both Tk and Tkinter are available on most Unix platforms, as well as on Windows and Macintosh systems.
#   Tkinter consists of a number of modules. The Tk interface is provided by a binary extension module named _tkinter.
#   This module contains the low-level interface to Tk, and should never be used directly by application programmers.
#   It is usually a shared library (or DLL), but might in some cases be statically linked with the Python interpreter.

#   The public interface is provided through a number of Python modules. The most important interface module is the
#   Tkinter module itself.
#
#   Just import the Tkinter module to use
###

###
#   Developed at Crash Avoidance Metrics Partners, LLC (CAMP)
#     by N. Probert and J. Parikh / Jul - Sept, 2018
#                   Ver. 1.0
#
###


import      sys
from        math        import *
from        socket      import *
from        struct      import *

import      os.path
from        datetime    import *
from        time        import *

###
#   Imports...
###

if sys.version_info[0] == 3:
    from    tkinter     import *
    
else:
    from    Tkinter     import *

from        tkinter     import messagebox
from        tkinter     import filedialog

import      configparser

###
#   import and get root
#
#   Add description on Tkinter package here...
#
###

root = Tk()
root.title('CAMP V2I-SA Work Zone Configuration v1.0')
root.geometry ('1024x850')
root.resizable(0,0)                                     #window set to fixed, can't expand with mouse

#############################################################################
#
# VARIABLES and DEFAULT VALUES...
#
#############################################################################
#
###
#   --------------------------------------------------------------------------------------------------
###
#   Get current date and time...
###

cDT = datetime.now().strftime("%Y/%m/%d - %H:%M:%S")

DO_NOT_MODIFY       = ('###\n'      \
                       '#             ... DO NOT MODIFY THIS CONFIGURATION FILE ...\n#\n'       \
                       '#             THE FILE WILL BE OVER WRITTEN BY THE WZ CONFIG USER INPUT \n'       \
                       '#             \'Config_UI\' PROGRAM...\n#\n'     \
                       '#             UPDATED: ' + datetime.now().strftime("%Y/%m/%d - %H:%M:%S") + '\n'            \
                       '###\n\n')

###
#   Serial port...
###

serial_port = 'COM7'
baud_rate   = '115201'
timeout     = '1'                                   #timeout = 1 sec
veh_path_data_rate = '10'                           #data acquisition = 10Hz

###
#   WZ config file names...
###
    
cfg_input_file      = StringVar()
#cfg_input_file.set("WZ_Default_Config.wzc") 

cfg_output_file     = StringVar()
veh_path_data_file  = StringVar()
veh_path_data_dir   = StringVar()
wz_description      = StringVar()

###
#   WZ config parameters...
###

num_lanes           = StringVar()                   #no of lanes in wz
num_lanes.set(1)                                    #default = 1

lane_width          = StringVar()                   #average lane width
lane_width.set('3.6')                               #default 3.6m

app_lane_pad        = StringVar()                   #approach lane padding
wz_lane_pad         = StringVar()                   #wz lane padding

veh_path_data_lane  = StringVar()                   #vehicle path data lane
veh_path_data_lane.set(1)                           #default lane 1

###
#   WZ speed limits...
###

normal_speed        = StringVar()                   #normal road speed limit
refpt_speed         = StringVar()                   #speed limit at start of wz
worker_speed        = StringVar()                   #speed limit when workers present

###
#   WZ type...
###

cause_code          = StringVar()                   #cause code
cause_code.set(3)                                   #roadwork
subcause_code       = StringVar()
subcause_code.set(0)                                #optional use-specific

###
#   Work zone schedule - start and end dates...
###

start_date  = StringVar()                   #wz start date
start_date.set(date.today())                #set today's date

end_date    = StringVar()                   #wz end date
end_date.set(date.today())                  #set today's date

start_year  = StringVar()
start_year.set(datetime.now().year)

start_month = StringVar()
start_month.set(datetime.now().month)

start_day   = StringVar()
start_day.set(datetime.now().day)

end_year    = StringVar()
end_year.set(datetime.now().year)

end_month   = StringVar()
end_month.set(datetime.now().month)

end_day     = StringVar()
end_day.set(datetime.now().day)

###
#   Work zone schedule - start and end time...
###

start_time_hour     = StringVar()
start_time_hour.set('00')

start_time_minute   = StringVar()
start_time_minute.set('00')

end_time_hour       = StringVar()
end_time_hour.set('23')
end_time_minute     = StringVar()
end_time_minute.set('59')

###
#   Work zone schedule - day of week, check boxes...
###

week_day_sun = StringVar()
week_day_mon = StringVar()
week_day_tue = StringVar()
week_day_wed = StringVar()
week_day_thu = StringVar()
week_day_fri = StringVar()
week_day_sat = StringVar()
#week_day_sun.set(0)                             #1 is on, 0 is off
#week_day_mon.set(0)
#week_day_tue.set(0)
#week_day_wed.set(0)
#week_day_thu.set(0)
#week_day_fri.set(0)
#week_day_sat.set(0)

#############################################################################
# ACTIONS
#############################################################################

def input_file_dialog():
    filename = filedialog.askopenfilename(initialdir=".", title="Select Input file", filetypes=[("Config File","*.wzc")])
    if len(filename):
        cfg_input_file.set(filename)
        cfg_output_file.set(filename)                   #set default config output same as congig input file
        config_read(filename)                           #read config input file
        
        if config['FILES']['VehiclePathDataDir'] != '':     #get veh path data file name if not blank
            veh_path_data_file.set((config['FILES']['VehiclePathDataDir'])+"//"+ \
                                   (config['FILES']['VehiclePathDataFile'])) #get veh path data file from config file        
  
def output_file_dialog():
    filename = filedialog.askopenfilename(initialdir=".", title="Select Output file", filetypes=[("Config File","*.wzc")])
    if len(filename):
        cfg_output_file.set(filename)

def data_file_dialog():
    filename = filedialog.askopenfilename(initialdir=".", title="Select Vehicle Path Data file", filetypes=[("Data Files","*.csv")])
    if len(filename):
        veh_path_data_file.set(filename)

###
#   Check for WZ end date, it can't be before the start date, if so, return TRUE
###

def check_End_Date_Time():
    sDT = int(start_year.get())*10000 + int(start_month.get())*100 + int(start_day.get())
    eDT = int(end_year.get())*10000   + int(end_month.get())*100   + int(end_day.get())

    sTime = int(start_time_hour.get())*60 + int(start_time_minute.get())
    eTime = int(end_time_hour.get())*60   + int(end_time_minute.get())
    
    if eDT < sDT:                                       #end date is before the start date
        return True

    if eDT == sDT and eTime < sTime:                    #end time is before the start time
        return True
      
    
#############################################################################
# LAYOUT...
#############################################################################

lbl_top = Label(text='CAMP V2I-SA Work Zone Configuration v1.0', font='Helvetica 16', fg='royalblue')
lbl_top.grid(row=0, sticky='w', padx=320, pady=20)

###
#   WZ configuration input file...
###

lbl_file        = Label(text='  Work Zone Configuration Files  ', relief=SUNKEN, bg='paleturquoise1', font='Helvetica 12').grid(row=1, sticky='w', padx=450, pady=10)
#lbl_input_file  = Label(text='  Existing WZ Config File:').grid(row=2, sticky='w')
text_input_file = Entry(relief=SUNKEN, textvariable=cfg_input_file, width=100).grid(row=2, sticky='w', padx=180)
diag_input_file = Button(text=' Select Config File  ', anchor='w', bg='gray87', command=input_file_dialog).grid(row=2, sticky='w', padx=10, pady=3)

###
#   WZ configuration output file...
###

#lbl_output_file  = Label(text='  Save as WZ Config File:', anchor='w').grid(row=3, sticky='w')
text_output_file = Entry(relief=SUNKEN, textvariable=cfg_output_file, width=100).grid(row=3, sticky='w', padx=180)
diag_output_file = Button(text=' Save Config File*   ', anchor='w', bg='gray87', command=output_file_dialog).grid(row=3, sticky='w', padx=10, pady=3)

###
#   Vehicle path data file...
###

#lbl_data_file  = Label(text='  Collected Vehicle Path\nData File:', anchor='w').grid(row=4, sticky='w')
text_data_file = Entry(relief=SUNKEN, textvariable=veh_path_data_file, width=100).grid(row=4, sticky='w', padx=180)
diag_data_file = Button(text=' Select Vehicle Path\nData File* ', anchor='w', bg='gray87', command=data_file_dialog).grid(row=4, sticky='w', padx=10, pady=3)

###
#   Work zone information...
###

lbl_work = Label(text='  Work Zone Information  ', relief=SUNKEN, bg='paleturquoise1', font='Helvetica 12').grid(row=5, sticky='w', padx=470, pady=15)
lbl_description = Label(text='  Work Zone Description:', anchor='w').grid(row=6, sticky='w')
text_description = Entry(relief=SUNKEN, textvariable=wz_description, width=100).grid(row=6, sticky='w', padx = 180)


###
#   Lane information...
###

lbl_work1 = Label(text='Lane Information', font='Helvetica 10 bold', fg="Blue").grid(row=7, pady=10, sticky='w', padx = 80)
lbl_num_lanes   = Label(text='  Number of Lanes (1-8)*', anchor='w').grid(row=8, sticky='w')
text_num_lanes  = Spinbox(from_=1,to=8,width=2, textvariable=num_lanes).grid(row=8, sticky='w', padx = 230)
lbl_lane_data   = Label(text='  Vehicle Path Data Lane (1-8)*', anchor='w').grid(row=9, sticky='w')
text_lane_data  = Spinbox(from_=1,to=8,width=2, textvariable=veh_path_data_lane).grid(row=9, sticky='w', padx = 230)
lbl_lane_width  = Label(text='  Ave. Lane Width (m)*', anchor='w').grid(row=10, sticky='w')
text_lane_width = Entry(relief=SUNKEN, textvariable=lane_width, width=4).grid(row=10, sticky='w', padx = 230)

###
#   Lane padding 
###

lbl_lane_width = Label(text='  Approach Lane Padding (m):', anchor='w').grid(row=12, sticky='w')
text_lane_width = Entry(relief=SUNKEN, textvariable=app_lane_pad, width=4).grid(row=12, sticky='w', padx = 230)

lbl_lane_width = Label(text='  Work Zone Lane Padding (m):', anchor='w').grid(row=13, sticky='w')
text_lane_width = Entry(relief=SUNKEN, textvariable=wz_lane_pad, width=4).grid(row=13, sticky='w', padx = 230)

###
#   message line...
###

msg_Text = Label(text='  * Indicates required input', font='Helvetica 10', fg='maroon').grid(row=14, sticky='w')

###
#   Speed limits...
###

lbl_work2 = Label(text='Speed Limits (5-80 mph)', font='Helvetica 10 bold', fg='Blue').grid(row=7, sticky='w', padx = 430)
lbl_speed_normal = Label(text='Normal Speed*', anchor='w').grid(row=8, sticky='w', padx = 420)
text_speed_normal = Spinbox(from_=5,to=80,increment=5, width=2, textvariable=normal_speed).grid(row=8, sticky='e', padx = 650)
lbl_speed_refpt = Label(text='At the Ref. Point (Start of WZ)*', anchor='w').grid(row=9, sticky='w', padx = 420)
text_speed_refpt = Spinbox(from_=5,to=80,increment=5, width=2, textvariable=refpt_speed).grid(row=9, sticky='e', padx = 650)
lbl_speed_worker = Label(text='When Workers are Present*', anchor='w').grid(row=10, sticky='w', padx = 420)
text_speed_worker = Spinbox(from_=5,to=80,increment=5, width=2, textvariable=worker_speed).grid(row=10, sticky='e',padx = 650)

###
#   Work zone type...
###


lbl_work3 = Label(text='Work Zone Type', font='Helvetica 10 bold', fg='Blue').grid(row=7, sticky='e', padx = 350)
lbl_cause_code = Label(text='Cause Code*', anchor='w').grid(row=8, sticky='e', padx = 380)
text_cause_code = Entry(relief=SUNKEN, textvariable=cause_code,width=2).grid(row=8, sticky='e', padx = 350)
lbl_lane_width = Label(text='Subcause Code', anchor='w').grid(row=9, sticky='e', padx = 380)
text_subcause_code = Entry(relief=SUNKEN, textvariable=subcause_code, width=2).grid(row=9, sticky='e', padx = 350)

###
#   Work zone schedule...
###

lbl_work = Label(text='  Work Zone Schedule  ', relief=SUNKEN, bg='paleturquoise1', font='Helvetica 12').grid(row=14, sticky='w', padx=475, pady=20)

###
#   Work zone start and end dates...
###
#   WZ start date...
###

syear = start_year.get()
smon  = start_month.get()
sday  = start_day.get()

##lbl_start_date  = Label(text='Start Date (YYYY:MM:DD)', font='Helvetica 10 bold').grid(row=15, sticky='w', padx=150, pady=10)
##text_start_year = Spinbox(from_=syear,to=str(int(syear)+20),width=4, textvariable=start_year, font='Helvetica 10').grid(row=16, sticky='w', padx=180)
##text_start_mon  = Spinbox(from_=smon,to=12,width=2, textvariable=start_month, font='Helvetica 10').grid(row=16, sticky='w', padx=245)
##text_start_day  = Spinbox(from_=sday,to=31,width=2, textvariable=start_day,   font='Helvetica 10').grid(row=16, sticky='w', padx=290)

lbl_start_date  = Label(text='Start Date (YYYY:MM:DD)', font='Helvetica 10 bold', fg='Blue').grid(row=15, sticky='w', padx=100, pady=10)
text_start_year = Spinbox(from_=syear,to=str(int(syear)+20),width=4, textvariable=start_year, font='Helvetica 10').grid(row=16, sticky='w', padx=130)
text_start_mon  = Spinbox(from_=smon,to=12,width=2, textvariable=start_month, font='Helvetica 10').grid(row=16, sticky='w', padx=195)
text_start_day  = Spinbox(from_=sday,to=31,width=2, textvariable=start_day,   font='Helvetica 10').grid(row=16, sticky='w', padx=240)


###
#  WZ start time...
###

lbl_start_time  = Label(text=' Start Time (HH:MM)', font='Helvetica 10 bold', fg='Blue').grid(row=15, sticky='e', padx=360)
text_start_hour = Spinbox(from_=0,to=23,width=2, textvariable=start_time_hour, font='Helvetica 10').grid(row=16, sticky='e', padx=450)
text_start_min  = Spinbox(from_=0,to=59,width=2, textvariable=start_time_minute, font='Helvetica 10').grid(row=16, sticky='e', padx=400)

###
#   WZ end date...
###

eyear = end_year.get()
emon  = end_month.get()
eday  = end_day.get()

##lbl_end_date = Label(text='End Date (YYYY:MM:DD)', font='Helvetica 10 bold').grid(row=17, sticky='w', padx = 150, pady=10)
##text_end_year = Spinbox(from_=eyear,to=str(int(eyear)+20),width=4, textvariable=end_year, font='Helvetica 10').grid(row=18, padx = 180, sticky='w')
##text_end_mon  = Spinbox(from_=emon,to=12,width=2, textvariable=end_month, font='Helvetica 10').grid(row=18, padx = 245, sticky='w')
##text_end_day  = Spinbox(from_=eday,to=31,width=2, textvariable=end_day,   font='Helvetica 10').grid(row=18, padx = 290, sticky='w')

lbl_end_date = Label(text='End Date (YYYY:MM:DD)', font='Helvetica 10 bold', fg='Blue').grid(row=17, sticky='w', padx = 100, pady=10)
text_end_year = Spinbox(from_=eyear,to=str(int(eyear)+20),width=4, textvariable=end_year, font='Helvetica 10').grid(row=18, padx = 130, sticky='w')
text_end_mon  = Spinbox(from_=emon,to=12,width=2, textvariable=end_month, font='Helvetica 10').grid(row=18, padx = 195, sticky='w')
text_end_day  = Spinbox(from_=eday,to=31,width=2, textvariable=end_day,   font='Helvetica 10').grid(row=18, padx = 240, sticky='w')



###
#  WZ end time...
###

lbl_end_time = Label(text=' End Time (HH:MM)', font='Helvetica 10 bold', fg='Blue').grid(row=17, sticky='e', padx=360)
text_end_hour = Spinbox(from_=0,to=23,width=2, textvariable=end_time_hour, font='Helvetica 10').grid(row=18, sticky='e', padx=450)
text_end_min = Spinbox(from_=0,to=59,width=2, textvariable=end_time_minute, font='Helvetica 10').grid(row=18, sticky='e', padx=400)

###
#   days of week...
###

gap = 65
lbl_date3   = Label(text='Days of Week', font='Helvetica 10 bold', fg='Blue').grid(row=15, sticky='w', padx = 520, pady=10)
chk_day_sun = Checkbutton(text='Sun', font='Helvetica 9 bold', variable=week_day_sun).grid(row=16, sticky='w', padx = 350+gap*0)
chk_day_mon = Checkbutton(text='Mon', font='Helvetica 9 bold', variable=week_day_mon).grid(row=16, sticky='w', padx = 350+gap*1)
chk_day_tue = Checkbutton(text='Tue', font='Helvetica 9 bold', variable=week_day_tue).grid(row=16, sticky='w', padx = 350+gap*2)
chk_day_wed = Checkbutton(text='Wed', font='Helvetica 9 bold', variable=week_day_wed).grid(row=16, sticky='w', padx = 350+gap*3)
chk_day_thu = Checkbutton(text='Thu', font='Helvetica 9 bold', variable=week_day_thu).grid(row=16, sticky='w', padx = 350+gap*4)
#chk_day_fri = Checkbutton(text='Fri', font='Helvetica 9 bold', variable=week_day_fri).grid(row=20, sticky='w', padx = 350+gap*5)
#chk_day_sat = Checkbutton(text='Sat', font='Helvetica 9 bold', variable=week_day_sat).grid(row=20, sticky='w', padx = 350+gap*5)

#chk_day_thu = Checkbutton(text='Thu', font='Helvetica 9 bold', variable=week_day_thu).grid(row=20, sticky='e', padx = 500-gap*0)
chk_day_fri = Checkbutton(text='Fri', font='Helvetica 9 bold', variable=week_day_fri).grid(row=16, sticky='e', padx = 680-gap*1)
chk_day_sat = Checkbutton(text='Sat', font='Helvetica 9 bold', variable=week_day_sat).grid(row=16, sticky='e', padx = 690-gap*2)

###
#   --------------------------- END of LAYOUT --------------------------------
###
#
###
#   Copy configuration file data to proper variables before display...
###

def config_copyin():

###
#   serial port..
#
#   Default value is already set in variables section.
#   These values are not going to be modified by the user...
#   no need to set any values here...    
###

##
#   files - user to provide file names...
#   However, the default config input file must be read first...
##

      
##
#   lanes
##
    wz_description.set(config['LANES']['Description'])
    num_lanes.set(config['LANES']['NumberOfLanes'])
    lane_width.set(config['LANES']['AverageLaneWidth'])
    app_lane_pad.set(config['LANES']['ApproachLanePadding'])
    wz_lane_pad.set(config['LANES']['WorkzoneLanePadding'])
    veh_path_data_lane.set(config['LANES']['VehiclePathDataLane'])
##    
#   speed
##
    normal_speed.set(config['SPEED']['NormalSpeed'])
    refpt_speed.set(config['SPEED']['ReferencePointSpeed'])
    worker_speed.set(config['SPEED']['WorkersPresentSpeed'])
##
#   cause
##
    cause_code.set(config['CAUSE']['CauseCode'])
    subcause_code.set(config['CAUSE']['SubcauseCode'])
##
#   wz schedule - start and end dates, times and days of week
##
    if len(config['SCHEDULE']['WZStartDate']):
        start_date.set(config['SCHEDULE']['WZStartDate'])
        year,mon,day = map(str, config['SCHEDULE']['WZStartDate'].split('-'))
        start_year.set(year)
        start_month.set(mon)
        start_day.set(day)

    if len(config['SCHEDULE']['WZEndDate']):
        end_date.set(config['SCHEDULE']['WZEndDate'])
        year,mon,day = map(str, end_date.get().split('-'))
        end_year.set(year)
        end_month.set(mon)
        end_day.set(day)

    if len(config['SCHEDULE']['WZStartTime']):
        hours, minutes = map(str, config['SCHEDULE']['WZStartTime'].split(':'))
        start_time_hour.set(hours)
        start_time_minute.set(minutes)

    if len(config['SCHEDULE']['WZEndTime']):
        hours, minutes = map(str, config['SCHEDULE']['WZEndTime'].split(':'))
        end_time_hour.set(hours)
        end_time_minute.set(minutes)
##
#   days of week
##
    week = config['SCHEDULE']['WZDaysOfWeek']
    days = week.split(',')
    week_day_sun.set(0)
    week_day_mon.set(0)
    week_day_tue.set(0)
    week_day_wed.set(0)
    week_day_thu.set(0)
    week_day_fri.set(0)
    week_day_sat.set(0)

    for jk in range (0, len(days)):
        if days[jk]=="Sun":     week_day_sun.set(1)
        if days[jk]=="Mon":     week_day_mon.set(1)
        if days[jk]=="Tue":     week_day_tue.set(1)
        if days[jk]=="Wed":     week_day_wed.set(1)
        if days[jk]=="Thu":     week_day_thu.set(1)
        if days[jk]=="Fri":     week_day_fri.set(1)
        if days[jk]=="Sat":     week_day_sat.set(1)
	
###
# - - - - - - - - - - END OF CONFIG COPYIN - - - - - - -
###

#############################################################################
# READ CONFIGURATION
#############################################################################

###
# read and config file and Check file length > 0
###

def config_read(file):
    if os.path.exists(file):
        try:
            cfg = open(file)
            config.read_file(cfg)
            cfg.close()
            config_copyin()
		
        except Exception as e:
            #print ("in except...copy_in", e)
            messagebox.showinfo("Read Config", "Configuration file read failed: " + file + "\n" + str(e))
    else:
        messagebox.showinfo("Read Config", "Configuration file NOT FOUND: " + file + "\n" + str(e))

###
# - - - - - - - - - - END OF CONFIG READ FUNCTION - - - - - - - - - - -
###


###
# configuration object
###

config = configparser.ConfigParser(delimiters=('='))

config_file = "wz_default_config.wzc"

###
# Process config file from user input..
###

if len(sys.argv) >= 2:
	config_file = sys.argv[1]

###
# uncomment following if need to preload from default or command line
###

config_read(config_file)

#############################################################################
# SAVE CONFIGURATION
#############################################################################

def config_copyout():

# DO_NOT_MODIFY Message...
    
# serial port
    #config['SERIALPORT']['SerialPort']  = serial_port.get()
    #config['SERIALPORT']['BaudRate']    = baud_rate.get()
    #config['SERIALPORT']['TimeOut']     = timeout.get()
    #config['SERIALPORT']['DataRate']    = veh_path_data_rate.get()

###
#   files...
#
#   Process config input file...
#   The default config input file must be read first that provides the config file sections
###

    cwd = os.getcwd()                           #current working directory
    
###    
#   config input file... User may not specify this file name...
###    
    
    if cfg_input_file.get():                       
        if ("/" in cfg_input_file.get() or "//" in cfg_input_file.get()) == False:
            config['FILES']['CfgInputFile']         = cwd+"//"+cfg_input_file.get()
        else:
            config['FILES']['CfgInputFile']         = cfg_input_file.get()
    pass            

###    
#   config output file...
###

    if ("/" in cfg_output_file.get() or "//" in cfg_output_file.get()) == False:
        config['FILES']['CfgOutputFile']         = cwd+"//"+cfg_output_file.get()
    else:
        config['FILES']['CfgOutputFile']         = cfg_output_file.get()

###
#   vehicle path data file - directory and file name...
#
#   Pop up message if Vehicle Path Data file name is blank...
###


    if veh_path_data_file.get() == "":
        raise Exception ("\n*** Vehicle Path Data File name is required ***")


    if ("/" in veh_path_data_file.get() or "//" in veh_path_data_file.get()) == True:
        config['FILES']['VehiclePathDataDir']   = os.path.split(veh_path_data_file.get())[0]
        config['FILES']['VehiclePathDataFile']  = os.path.split(veh_path_data_file.get())[1]
    else:
        config['FILES']['VehiclePathDataDir']   = cwd                  
        config['FILES']['VehiclePathDataFile']  = veh_path_data_file.get()
    
# lanes
    config['LANES']['Description']              = wz_description.get()
    config['LANES']['NumberOfLanes']            = num_lanes.get()
    config['LANES']['AverageLaneWidth']         = lane_width.get()
    config['LANES']['ApproachLanePadding']      = app_lane_pad.get()
    config['LANES']['WorkzoneLanePadding']      = wz_lane_pad.get()
    config['LANES']['VehiclePathDataLane']      = veh_path_data_lane.get()
    
# speed
    config['SPEED']['NormalSpeed']              = normal_speed.get()
    config['SPEED']['ReferencePointSpeed']      = refpt_speed.get()
    config['SPEED']['WorkersPresentSpeed']      = worker_speed.get()
    
# cause
    config['CAUSE']['CauseCode']                = cause_code.get()
    config['CAUSE']['SubcauseCode']             = subcause_code.get()

# schedule
    config['SCHEDULE']['WZStartDate']           = start_year.get()+"-"+start_month.get()+"-"+start_day.get()
    config['SCHEDULE']['WZEndDate']             = end_year.get()+"-"+end_month.get()+"-"+end_day.get()
    config['SCHEDULE']['WZStartTime']           = start_time_hour.get().format("%02d") + ":" + start_time_minute.get().format("%02d")
    config['SCHEDULE']['WZEndTime']             = end_time_hour.get().format("%02d") + ":" + end_time_minute.get().format("%02d")
    
##
# WZ days of week
##
	
    week = []
			
    if week_day_sun.get() == "1":
        week.append("Sun")
    if week_day_mon.get() == "1":
        week.append("Mon")
    if week_day_tue.get() == "1":
        week.append("Tue")
    if week_day_wed.get() == "1":
        week.append("Wed")
    if week_day_thu.get() == "1":
        week.append("Thu")
    if week_day_fri.get() == "1":
        week.append("Fri")
    if week_day_sat.get() == "1":
        week.append("Sat")

    config['SCHEDULE']['WZDaysOfWeek'] = str.join(',', week)

###
# - - - - - - - - END OF CONFIG COPYOUT for SAVING to FILE - - - - - - -
###
   
def config_save(file):

##    
# output file
##
    try:
        cfg = open(file, 'w')
        config_copyout()
        cfg.write (DO_NOT_MODIFY)
        config.write(cfg)
        cfg.close()
        messagebox.showinfo("Save Config", "Configuration file save successful: " + file)

    except Exception as e:
        #print ("in except...", e)
        messagebox.showinfo("Save Config", "Configuration file save FAILED: " + file + "\n" + str(e))


#############################################################################
# SAVE/QUIT
#############################################################################

def save_it():

    if check_End_Date_Time() == True:                                        #check WZ end date...
        messagebox.showinfo("Save Config", "WZ End Date & Time Must be After the Start Date & Time,\n\n \t... Fix it Before Saving the Config ...")
        return
    
    if len(cfg_output_file.get()):
        if os.path.exists(cfg_output_file.get()):
            if messagebox.askyesno("Save Config", "Sure you want to overwrite: " + cfg_output_file.get() + "?"):
                config_save(cfg_output_file.get())
        else:
            config_save(cfg_output_file.get())    
    else:
        messagebox.showinfo("Save Config", "No Output file to save!")   

def quit_it():
    if messagebox.askyesno("Quit", "Sure you want to quit?") == True:
        sys.exit(0)

# exit button
save = Button(text='Save', font='Helvetica 10 bold', fg = 'white', bg='green3', command=save_it).grid(row=25, sticky='w', padx=420, pady=20)
xitb = Button(text='Quit', font='Helvetica 10 bold', fg = 'white', bg='red3', command=quit_it).grid(row=25, sticky='e', padx=600, pady=20)

#############################################################################
# MAIN LOOP
#############################################################################

# run class mainloop
root.protocol("WM_DELETE_WINDOW", quit_it)
root.mainloop()
