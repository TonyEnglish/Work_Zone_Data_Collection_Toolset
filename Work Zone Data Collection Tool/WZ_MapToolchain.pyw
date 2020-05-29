#!/usr/bin/env python3

###
#
#   This user input for work zone configuration is created using "Tkinter" (TK Interface) module. The  Tkinter
#   is the standard Python interface to the Tk GUI toolkit from Scriptics (formerly developed by Sun Labs).
#
#   The public interface is provided through a number of Python modules. The most important interface module is the
#   Tkinter module itself.
#
#   Just import the Tkinter module to use
###

###
#   Developed at Crash Avoidance Metrics Partners, LLC (CAMP)
#     by J. Parikh / Jul-Sep, 2018
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
#   thread
###

if sys.version_info[0] == 3:
    from    tkinter     import *
    from    tkinter     import      messagebox
else:
    from    Tkinter     import *




#############################################################################
#
# LAUNCH Programs
#
#############################################################################


def launch_WZ_veh_path_data_acq():

    WZ_dataacq = "WZ_VehPathDataAcq.pyw"
    if os.path.exists(WZ_dataacq):
        os.system("WZ_VehPathDataAcq.pyw")
        
    else:
        messagebox.showinfo("WZ Vehicle Path Data Acq","WZ Vehicle Path Data Acquisition NOT Found...")
        

def launch_WZ_config():

    WZ_config = "WZ_Config_UI.pyw"
    if os.path.exists(WZ_config):
        os.system("WZ_Config_UI.pyw")        
        
    else:
        messagebox.showinfo("WZ Config","Work Zone Config NOT Found...")  


def launch_WZ_map_builder():
    
    WZ_maping_file = "WZ_MapBuilder.pyw"
    if os.path.exists(WZ_maping_file):
        os.system('WZ_MapBuilder.pyw')
    else:
        messagebox.showinfo("WZ Mapping","Work Zone Map Builder NOT Found...")   


def launch_WZ_map_visualizer():

    msg_API = "NOTE: This module requires Google MAP API Key to display \
    the generated WZ Map on Google Satellite View.\n\n Insert YOUR Google API Key in file \n \
    \"./WZ_Visualizer/RSZW_MapVisualizer.html\" as follows\n\n \
    <script type=\"text/javascript\" \n \
        src=\"https://maps.google.com/maps/api/js?key=YOUR API KEY&libraries=geometry\"> \n \
    </script>\n\n \
    For more information visit: https://developers.google.com/maps/documentation/javascript/get-api-key \n\n \
                                 C O N T I N U E ???"
    
###
#   Display  warning/info message to user...
###

    if messagebox.askyesno("Google Map API Warning!!!",msg_API) == True:       
                           
        WZ_viz_file = "./WZ_Visualizer/RSZW_MapVisualizer.html"
        if os.path.exists(WZ_viz_file):
            os.chdir("./WZ_Visualizer")
            os.system('RSZW_MapVisualizer.html')
            os.chdir ("..")
        else:
            messagebox.showinfo("WZ Visualizer","Work Zone Visualizer NOT Found...")   


def launch_WZ_msg_builder():
    if os.path.exists:
        os.chdir("./CVMsgBuilder v1.4 distribution")
        os.system('java -jar dist\CVMsgBuilder.jar')
        os.chdir ("..")
    else:
        messagebox.showinfo("CV Message Builder Tool NOT Found...")   


def quit_it():
    if messagebox.askyesno("Quit", "Sure you want to quit?") == True:
        sys.exit(0)



###
#   import and get root
#
#   Add description on Tkinter package here...
#
###

root = Tk()
root.title('CAMP V2I-SA Work Zone Mapping Toolchain v1.0')

#############################################################################
# LAYOUT...
#############################################################################

lbl_top = Label(text='  CAMP V2I-SA Work Zone Map Builder, Map Visualizer and \nMessage Builder Toolchain v1.0  ', font='Helvetica 14', fg='royalblue')
lbl_top.pack()

winSize = Label(root, height=16, width=75) #height was 12
winSize.pack()
root.resizable(0,0)

###
#   WZ Vehicle Path Data Acq....
###

vPath = Button(text='Vehicle Path\nData Acq. ', font='Helvetica 10', bg='paleturquoise1', padx=5, command=launch_WZ_veh_path_data_acq)
vPath.place(x=100, y=100)

###
#   WZ User Configuration Input...
###

wzCfg = Button(text='Work Zone\nConfiguration', font='Helvetica 10', bg='paleturquoise1', padx=5, command=launch_WZ_config)
wzCfg.place(x=400, y=100)


###
#   WZ Map Builder...
###

wzMap = Button(text='Map Builder', font='Helvetica 10', bg='paleturquoise1', padx=5, command=launch_WZ_map_builder)
wzMap.place(x=100, y=190)

###
#   WZ Visualization...
###

wzViz = Button(text='Map Visualizer', font='Helvetica 10', bg='paleturquoise1', padx=5, command=launch_WZ_map_visualizer)
wzViz.place(x=395, y=190)


###
#   WZ map message builder...
###

wzMsg = Button(text='Message Builder', font='Helvetica 10', bg='paleturquoise1', padx=5, command=launch_WZ_msg_builder)
wzMsg.place(x=82, y=250)

###
#   QUIT...
###

xitB = Button(text='Quit', font='Helvetica 10', fg = 'white', bg='red3', padx=5, command=quit_it)
xitB.place(x=435, y=250)

###
#   Draw separator line...
###

canvas = Canvas(root, width = 620, height = 390)
canvas.pack()

canvas.create_line(10, 15, 610, 15, fill='royalblue')
canvas.create_line(10, 18, 610, 18, fill='royalblue')

###
#   Toolchain Concept Image...
###

img = PhotoImage(file="./WZ_Images/WZ_Map_Msg_Toolchain2.png")
canvas.create_image(0,20, anchor=NW, image=img)                             #display toolchain concept

#############################################################################
# MAIN LOOP
#############################################################################

# run class mainloop
root.protocol("WM_DELETE_WINDOW", quit_it)
root.mainloop()
