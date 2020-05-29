# Work Zone Data Collection Tool

The WZDC tool is an open source, standards based work zone capturing tool. Using a gps and a computer, a user can drive through a work zone and mark important elements of the work zone, including lane closures, speed limits and the presence of workers. This data is captured and output as RSM messages in xml and binary (uper) formats as well as a WZDx message. This tool was built alongside the TMC cloud website, which enables the creation of configuration files and the visualization of work zones. 

## Configuration File Loading and GPS Connection Test
![Config Loading UI](https://github.com/TonyEnglish/V2X-manual-data-collection/blob/master/config_loading_ui_screenshot.jpg)
This component of the application enables a user to load a configuration file and verify their GPS connection. This configuration file can be loaded from the Cloud or from a local directory. A configuration file can be created at https://neaeraconsulting.com/V2X_ConfigCreator.
The tool automatically scans usb COM ports for a GPS device. The baudrate and data rate can be configured if needed
When a configuration file is loaded and a GPS connection is confirmed, data collection may begin

## Data Collection/Acquisition
![Data Colelction UI](https://github.com/TonyEnglish/V2X-manual-data-collection/blob/master/data_collection_ui_screenshot.jpg)
This is the data collection component. Data collection begins when a set starting location is reached and ends when the ending location is reached (both set in configuration file). A user can mark lane closures and the presence of workers. The user interface shows the current state of the work zone, including the vehicle lane (set in configuration file). All of the data collected is saved in a CSV path data file, which will be used for message generation

## Message Generation and Upload to Cloud
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

# Sample Files

Data Collection Tool Output Files: Raw Output
- Work Zone: sample-work-zone--white-rock-cir
  - Configuration File: config--sample-work-zone--white-rock-cir.json
  - Path History (Breadcrumbs) File: path-data--sample-work-zone--white-rock-cir.csv
  - RSM (binary) File: rsm-uper--sample-work-zone--white-rock-cir.uper
  - RSM (xml) File: rsm-xml--sample-work-zone--white-rock-cir.xml
  - WZDx File: wzdx--sample-work-zone--white-rock-cir.geojson

Published Work Zone Files: Published
- Work Zone: sample-work-zone--white-rock-cir
  - Published WZDx File: Published-WZData--WZDx--sample-work-zone--white-rock-cir.geojson
  - Published RSM (xml) File: Published-WZData--rsm-xml--sample-work-zone--white-rock-cir--1-of-1.xml
  - Published RSM (binary) File: Published-WZData--rsm-uper--sample-work-zone--white-rock-cir--1-of-1.uper
