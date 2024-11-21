[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=TonyEnglish_V2X-manual-data-collection&metric=bugs)](https://sonarcloud.io/dashboard?id=TonyEnglish_V2X-manual-data-collection)
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=TonyEnglish_V2X-manual-data-collection&metric=reliability_rating)](https://sonarcloud.io/dashboard?id=TonyEnglish_V2X-manual-data-collection)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=TonyEnglish_V2X-manual-data-collection&metric=sqale_rating)](https://sonarcloud.io/dashboard?id=TonyEnglish_V2X-manual-data-collection)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=TonyEnglish_V2X-manual-data-collection&metric=security_rating)](https://sonarcloud.io/dashboard?id=TonyEnglish_V2X-manual-data-collection)

# Work Zone Data Collection Toolset

## Project Description

This project is an open source, proof of concept work zone data collection tool. The purpose of this tool is to allow a construction manager in the field and transportation system manager at the Infrastructure Owner Operator (IOO) back-office to map work zones and distribute generated map messages to third parties. This project is part of a larger effort on understanding mapping needs for V2X applications, funded by USDOT. This repository is a deliverable under the project and supports the Development and Demonstration of Proof-of-Concept of an Integrated Work Zone Mapping Toolset.

![Tasks 6-7 Diagram](https://github.com/TonyEnglish/Work_Zone_Data_Collection_Toolset/blob/master/images/POC_WZ_Toolset.jpg)

This repository contains the following components:

- POC Work Zone Data Collection (WZDC) tool
- POC RSM(XML) to WZDx Translator
- Sample Files

Related repositories:

- [V2X Mobile Application](https://github.com/TonyEnglish/V2X_MobileApplication)
- [V2X Website](https://github.com/TonyEnglish/V2X_Website)
- [V2X Azure Functions](https://github.com/TonyEnglish/V2X_AzureFunctions)

## Prerequisites

Requires:

- Python 3.6 (or higher)
  - azure-storage-blob
  - esptool
  - image
  - wheel
  - serial
  - requests
- Environment Variables (Optional, Contact Tony English at [tony@neaeraconsulting.com](mailto://tony@neaeraconsulting.com) for more information)

## Usage

This toolset utilizes a website for configuration file creation and visualization of work zones. This website is not currently hosted. If you would like to host your own WZDC tool website, please see the [V2X Website](https://github.com/TonyEnglish/V2X_Website) repository for more information.

The WZDC tool is a python-based tool that utilizes a user interface. Steps for starting and running the tool are listed below and are described in further detail here: [POC Toolset User Guide](https://github.com/TonyEnglish/Work_Zone_Data_Collection_Toolset/blob/master/POC%20Toolset%20User%20Guide.pdf)

Video tutorials for each tool:
Website- Edit Work Zone - https://youtu.be/fBRkcWIBCWI
WZDC Mobile app - https://youtu.be/PMs6gDkm7NY
WZDC Computer app - https://youtu.be/pfD8pcYpGcE
Website - Config File - https://youtu.be/mm1Cm24tOIc

### Building

No building/compiling is required for this tool.

### Testing

There are currently no test cases for this proof of concept tool.

### Execution

#### Step 1: Run the WZDC script (from the Work Zone Data Collection Folder)

```
python WZDC_tool.py
```

#### Step 2: Load configuration file and confirm GPS connection

![Config Loading UI](https://github.com/TonyEnglish/Work_Zone_Data_Collection_Toolset/blob/master/images/WZDC_tool_initialization_screen.jpg)
This component of the application enables a user to load a configuration file and verify their GPS connection. This configuration file can be loaded from the Cloud or from a local directory.
The tool automatically scans usb COM ports for a GPS device. The baudrate and data rate can be configured if needed
When a configuration file is loaded and a GPS connection is confirmed, data collection may begin

#### Step 3: Map work zone

![Data Colelction UI](https://github.com/TonyEnglish/Work_Zone_Data_Collection_Toolset/blob/master/images/WZDC_tool_automatic_data_collection_screen.JPG)
This is the data collection component. Data collection begins when a set starting location is reached and ends when the ending location is reached (both set in configuration file). A user can mark lane closures and the presence of workers. The user interface shows the current state of the work zone, including the vehicle lane (set in configuration file). All of the data collected is saved in a CSV path data file, which will be used for message generation

![Data Colelction UI](https://github.com/TonyEnglish/Work_Zone_Data_Collection_Toolset/blob/master/images/WZDC_tool_manual_data_collection_screen.JPG)
This is the Manual Detection mode of the data collection component. In this mode, data collection starts when the user presses the 'Mark Start of Work Zone' button. Data collection ends when the user presses the 'Mark End of Work Zone' button. These locations are saved as the automatic start/end locations for use the next time that work zone is mapped.

#### Step 4: Upload generated messages to the cloud

![Upload UI](https://github.com/TonyEnglish/Work_Zone_Data_Collection_Toolset/blob/master/images/upload_ui_screenshot.jpg)
After data collection is completed, message generation begins. The recorded path data (including lane closure/worker presence) is processed into an RSM (xml) message. This message is then converted into binary (UPER format). The xml message, along with some additional information included in the configuration file, is then converted into a WZDx message. These messages (and the CSV data file) are added to a ZIP archive. When the user has an internet conenction, they can initiate the upload to the cloud, where the messages are unzipped and organized.

## Additional Notes

This toolset was developed as a proof of concept and is not able to provide a full solution for all types of work zones. Future work may expand the functionality of the tool to address more work zone types and add other features such as authentication or a mobile app version of the tool.

This tool functions alongside a POC TMC website (no longer actively hosted). Instructions for utilizing this website are located here: [POC Toolset User Guide](https://github.com/TonyEnglish/Work_Zone_Data_Collection_Toolset/blob/master/POC%20Toolset%20User%20Guide.pdf)

Documentation for this project is located here: [Documentation](https://github.com/TonyEnglish/Work_Zone_Data_Collection_Toolset/tree/master/Documentation). This documentation includes:

- V2X POC Interface Control Document
- V2X POC System Engineering Report
- V2X POC Test Case Results Report
- WZDC Tool Documentation Updates
  - Describes message generation

## Version History and Retention

**Status:** prototype

**Release Frequency:** This project is updated approximately once every 2 weeks

**Release History:** See [CHANGELOG.md](https://github.com/TonyEnglish/Work_Zone_Data_Collection_Toolset/blob/master/CHANGELOG.md)

**Retention:** This project will remain publicly accessible for a minimum of five years (until at least 08/15/2025).

## License

This project is licensed under the CMIT License - see the [License.md](https://github.com/TonyEnglish/Work_Zone_Data_Collection_Toolset/blob/master/LICENSE.md) for more details.

## Contributions

Instructions are listed below, please read [CONTRIBUTING.md](https://github.com/TonyEnglish/Work_Zone_Data_Collection_Toolset/blob/master/CONTRIBUTING.md) for more details.

- Report bugs and request features via [Github Issues](https://github.com/TonyEnglish/Work_Zone_Data_Collection_Toolset/issues).
- [Email us](mailto://tony@neaeraconsulting.com) your ideas on how to improve this proof of concept toolset.
- Create a [Github pull request](https://github.com/TonyEnglish/Work_Zone_Data_Collection_Toolset/pulls) with new functionality or fixing a bug.
- Triage tickets and review update-tickets created by other users.

### Guidelines

- Issues
  - Create issues using the SMART goals outline (Specific, Measurable, Actionable, Realistic and Time-Aware)
- PR (Pull Requests)
  - Create all pull requests from the master branch
  - Create small, narrowly focused PRs
  - Maintain a clean commit history so that they are easier to review

## Contact Information

Contact Name: Tony English
Contact Information: [tony@neaeraconsulting.com](mailto://tony@neaeraconsulting.com)

## Acknowledgements

To track how this government-funded code is used, we request that if you decide to build additional software using this code please acknowledge its Digital Object Identifier in your software's README/documentation.

Digital Object Identifier: https://doi.org/10.21949/1519288

## Abbreviations

CAMP tool: Crash Avoidance Metrics Partnership

POC: Proof of Concept

RSM: Roadside Safety Message

WZDC Tool: Work Zone Data Collection Tool

WZDx: Workzone Data Exchange
