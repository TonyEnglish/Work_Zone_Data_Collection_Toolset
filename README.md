# V2X-manual-data-collection

Infrastructure and V2X Mapping Needs Assessment and Development Support​

Tasks 6-7

![Tasks 6-7 Diagram](https://github.com/TonyEnglish/V2X-manual-data-collection/blob/master/task_6_7_diagram_screenshot.jpg)

# Work Zone Data Collection Tool

The WZDC tool is an open source work zone capturing tool. Using a gps and a computer, a user can drive through a work zone and mark important elements of the work zone, including lane closures, speed limits, and the presence of workers. This data is captured and output as RSM messages in xml and binary (uper) formats and a WZDx message. 

# Requirements

Python 3.0
- esptool
- azure-storage-blob
- image

Java 1.8 or JDK 8

# Updates
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
