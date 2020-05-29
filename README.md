# V2X-manual-data-collection

Infrastructure and V2X Mapping Needs Assessment and Development Support​

Tasks 6-7

![Tasks 6-7 Diagram](https://github.com/TonyEnglish/V2X-manual-data-collection/blob/master/task_6_7_diagram_screenshot.jpg)

# Work Zone Data Collection Tool

The WZDC tool is an open source, standards based work zone capturing tool. Using a gps and a computer, a user can drive through a work zone and mark important elements of the work zone, including lane closures, speed limits and the presence of workers. This data is captured and output as RSM messages in xml and binary (uper) formats as well as a WZDx message. This tool was built alongside the TMC cloud website, which enables the creation of configuration files and the visualization of work zones. 

# Configuration File Loading and GPS Connection Test
![Config Loading UI](https://github.com/TonyEnglish/V2X-manual-data-collection/blob/master/config_loading_ui_screenshot.jpg)
This component of the application enables a user to load a configuration file and verify their GPS connection. This configuration file can be loaded from the Cloud or from a local directory. A configuration file can be created at https://neaeraconsulting.com/V2X_ConfigCreator.
The tool automatically scans usb COM ports for a GPS device. The baudrate and data rate can be configured if needed
When a configuration file is loaded and a GPS connection is confirmed, data collection may begin

# Data Collection/Acquisition
![Data Colelction UI](https://github.com/TonyEnglish/V2X-manual-data-collection/blob/master/data_collection_ui_screenshot.jpg)
This is the data collection component. Data collection begins when a set starting location is reached and ends when the ending location is reached (both set in configuration file). A user can mark lane closures and the presence of workers. The user interface shows the current state of the work zone, including the vehicle lane (set in configuration file). All of the data collected is saved in a CSV path data file, which will be used for message generation

# Message Generation and Upload to Cloud
![Upload UI](https://github.com/TonyEnglish/V2X-manual-data-collection/blob/master/upload_ui_screenshot.jpg)
After data collection is completed, message generation begins. The recorded path data (including lane closure/worker presence) is processed into an RSM (xml) message. This message is then converted into binary (UPER format). The xml message, along with some additional information included in the configuration file, is then converted into a WZDx message. These messages (and the CSV data file) are added to a ZIP archive. When the user has an internet conenction, they can initiate the upload to the cloud, where the messages are unzipped and organized. These messages are available to visualize, verify and publish on https://neaeraconsulting.com/V2x_Home.

# Requirements

Python 3.0
- esptool
- azure-storage-blob
- image
- wheel
- serial

Java 1.8 or JDK 8

# Updates
5/22/2020
- Upgraded GPS data compression based on J2945/1
  - Now utilizes radius of curvature error computation detailed in J2945/1 (option 1)
- Added additional information to config file and WZDx
  - Information previously unavailable was added to the configuration file for use in WZDx message generation
  - This includes: lane restrictions, lane types, work type, road name, accuracy fields, and many more
- Updated automatic GPS device search
  - Moved GPS connection test to config loading page

5/11/2020
- Integrated Azure cloud connection
  - Downloading of published configuration files
  - Uploading of completed data files
- Improved path data collection UI
- Added logging
- Combined components into a single program
- Increased compatibility by lowering Java version of Binary (uper) converter

4/27/2020
- Made edits from end-to-end testing
  - Updated time/date formatting to match configuration files generated from TMC
  - App now exits and begins export upon completion of data collection
  - Export process now conforms to new naming convention (road_name--start_date--end_date)
  
- Included extra data in config
  - Road_name now included and utilized in WZDx output message
  - *More data to come

4/14/2020
- Automated major components
  - Created new Work Zone Data Collection main interface
  - Data acquisition automatically starts and stops based on locations set in config
  - Automated export sequence now zips together WZDx and RSM (XML and UPER) files
  - Decompiled and edited UPER conversion JAR file to allow for command line interfacing

3/30/2020
- Added POC RSM to WZDx translator
  - Verified WZDx files against example files from https://github.com/usdot-jpo-ode/jpo-wzdx/tree/master/create-feed/examples
- Updated CAMP RSM output
  - Integrated xmltodict library to make RSM generation more dynamic
- Updated CAMP gps COMM port detection
- Added requirements file

# Abbreviations

CAMP tool: Crash Avoidance Metrics Partnership

RSM: Roadside Safety Message

WZDx: Workzone Data Exchange
