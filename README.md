# V2X-manual-data-collection

Infrastructure and V2X Mapping Needs Assessment and Development Support​

Tasks 6-7

![Tasks 6-7 Diagram](https://github.com/TonyEnglish/V2X-manual-data-collection/blob/master/task_6_7_diagram_screenshot.jpg)

# CAMP Tool

The CAMP tool is an open source work zone capturing tool. Using a gps and a computer, a user can drive through a work zone and mark important elements of the work zone, including lane closures, speed limits, and the resence of workers. This data is captured and output as an RSM message in xml format. 

# Translators

A proof of concept RSM to WZDx translator has been developed. 

# Requirements

Python
Java

# Updates
4/14/2020
- Automated major components
  - Created new Work Zone Data Collection main interface
  - Data acquisition automatically starts and stops based on locations set in config
  - Automated export sequence now zips together WZDx and RSM (XML and UPER) files
  - Decompiled and edited UPER conversion JAR file to allow for command line interfacing

3/30/2020
- Added POC RSM to WZDx translator
- - Verified WZDx files against example files from https://github.com/usdot-jpo-ode/jpo-wzdx/tree/master/create-feed/examples
- Updated CAMP RSM output
- - Integrated xmltodict library to make RSM generation more dynamic
- Updated CAMP gps COMM port detection
- Added requirements file

# Abbreviations

CAMP tool: Crash Avoidance Metrics Partnership
RSM: Roadside Safety Message
WZDx: Workzone Data Exchange
