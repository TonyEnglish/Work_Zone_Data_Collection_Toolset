# Updates
8/14/2020
- Updating README to comply with ITS Codehub standards
- Adding LICENSE, CONTRIBUTING and CHANGELOG files

8/6/2020
- Added map images to configuration file
- Manual detection of start/end location
  - Allows user to mark start and end location manually (instead of marking GPS locations in TMC website)
  - Manually marked locations are saved as automatic detection locations after data collection

7/9/2020
- Updated generation of lane tapers
  - Lane tapering length based on https://mutcd.fhwa.dot.gov/htm/2009/part6/part6c.htm (Table 6C-4)
- Added live map to data collection UI
  - Map displays current location as well as the start and end locations of the work zone
  - Map utilizes static pictures, and it can be utilized while offline (after the initial map is downloaded)

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
