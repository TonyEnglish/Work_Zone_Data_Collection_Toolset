#!/usr/bin/env python3
###
#   Software module builds .exer (xml format) file for RSZW/LC message for UPER encoding
#   This is based on the proposed NEW CAMP Version of ASN.1 definition proposed to SAE standard for RSM - J2945/4...
#
#   Developed By J. Parikh (CAMP) / Nov. 2017
#   Modified by J. Parikh for RSM V 0.5 - December, 2017
#   Modified by J. Parikh for RSM V 1.0 - January, 2018
#   Modified by J. Parikh for RSM V 4.4 - February, 2018
#   Modified by J. Parikh for RSM V 4.8 - March, 2018
#   Modified by J. Parikh for RSM V 5.1 - May, 2018
#
#   Revised to Software Ver 2.51    --    Jun, 2018
#       Set new referencePoint for each segment
#       Repeat referencepPoint for each segment
#
#       Repeat Event Info...   
#           eventID
#           msgSegmentInfo
#           startDateTime, endDateTime
#           eventRecurrence
###
#
#
#   Revised to Software Ver 1.51   --     May, 2018
#       Added following:
#           <eventInfo>...</eventInfo>          --To address other RSM applications from SwRI...
#
#           Under following conditions, the generated WZ map nodes are split into multiple segments:
#           1.  When number of nodes generated per lane exceeds 64 (2..63)
#           2.  When expected UPER encoded message size exceeds 1200 octets (PDU Upper limit is 1500) +
#               space for header and security for about 300 octets
#
#           The point of segmentation generated in the "wz_msg_segmentation" is based on:
#           1.  1 node is equivalent to approx. 10 octets when nodes are presented as xyz_offset,
#                 therefore total 110 nodes per message segment makes map data approx. 1100 octets
#           2.  1 node is equivalent to approx. 15 octets when nodes are represented as 3d_absolute of lat, lot, alt,
#                 therefore total 75 nodes per message segment
#
#           <regionInfo>...</regionInfo>        --To address other RSM applications from SwRI...
#
#   Revised to Software Ver 1.48       Mar, 2018
#   Revised to Software Ver 1.44       Feb, 2018
#
###

###
#   Following function constructs the "Common Container" based on RSM.4.4 ASN.1 Definition 
###

# import xmltodict

def build_xml_CC (xmlFile,idList,eDateTime,endDateTime,timeOffset,wzDaysOfWeek,c_sc_codes,refPoint,appHeading,hTolerance, \
                  speedLimit,laneWidth,rW,eL,lS,arrayMapPt,msgSegList,currSeg,descName):

###
#       Following data are passed from the caller for constructing Common Container...
###
#       idLIst      = message ID, Station ID and Event ID [142,aabbccdd,255]
#       eDateTime   = event start date & time [yyyy,mm,dd,hh,mm,ss]
#       durDateTime = event duration date & time [yyyy,mm,dd,hh,mm,ss]
#       timeOffset  = offset in minutes from UTC -300 minutes
#       c_sc_codes  = cause and subcause codes [c,sc]
#       refPoint    = reference point [lat,lon,alt]
#       appHeading  = applicable heading in degrees (0..360) at the ref point 
#       hTolerance  = heading tolerance in degrees (0..360)
#       slType      = speedLimit [0,1,2,3,4,5]
#       speedList   = allowed max speed in mph [0,0,45,60,0,70] --- MUST match with slType
#       rW          = roadWidth (m)
#       eL          = eventLength (m)
#       lS          = laneStat lane status array
#       appMapPt    = array containing approach map points constructed earlier before calling this function
#       msgSegList  = generated list based on message segmentation containing following:
#                       [[# of segments, nodes per segment],
#                        [seg #(1), start node, end node for approach lane] 
#                        [seg #(1), start node, end node (max nodes per lane - approach lane nodes) for wz lane]
#                        [seg #2, start node, end node (max nodes per lane)for wz lane]
#                        [seg #n, until all wz nodes are done]]
#       currSeg     = current message segment for processing
#
#
###

###
#   Write initial xml lines in the output xml file...
#   Following introductory lines are written in the calling routine (WZ_MapBuilder.py)...
###
      
##    xmlFile.write ("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n\n" + \
##                   "<!-- \n" + \
##                   "\t CAMP xml file for RSZW/LC Mapping Project\n" + \
## 		     "\t File Name: "+xmlFile+"\n" + \
##                   "\t Created: "+cDT+"\n\n-->\n")

    tab = "\t"                                                                              #define tab char equal editor's tab value...
    tab = "  "                                                                              #define tab char equal to 2 spaces...
    laneWidth = round(laneWidth*100)                                                        #define laneWidth in cm
 
    # message = {}
    # message['MessageFrame'] = {}

###
#   RSM: MessageFrame...  Following are REPEATED for all Message Segments...
###

    # message['MessageFrame']['messageId'] = idList[0]
    # message['MessageFrame']['value'] = {}
    # xmlFile.write ("<MessageFrame>\n"  + \
    #                1*tab+"<messageId>"+str(idList[0])+"</messageId>\n"   + \
    #                1*tab+"<value>\n")

###
#   RSM: Common Container for RSZW/LC...
###

    # message['MessageFrame']['value']['RoadsideSafetyMessage'] = {}
    # message['MessageFrame']['value']['RoadsideSafetyMessage']['version'] = 1
    # message['MessageFrame']['value']['RoadsideSafetyMessage']['commonContainer'] = {}
    # commonContainer = message['MessageFrame']['value']['RoadsideSafetyMessage']['commonContainer']
    commonContainer = {}
    # xmlFile.write (2*tab+"<RoadsideSafetyMessage>\n"  + \
    #                3*tab+"<version>1</version>\n\n"   + \
    #                3*tab+"<commonContainer>\n")

###
#   Event Info...   Repeat for all message segments
#       eventID
#       msgSegmentInfo
#       startDateTime, endDateTime
#       eventRecurrence
###

    # commonContainer['#comment'] = '\n\t\t ...Event ID...(no Message ID)\n'
    # xmlFile.write ("<!--\n\t\t ...Event ID...(no Message ID)\n-->\n")                       ###comment in XML file
    commonContainer['eventInfo'] = {}
    commonContainer['eventInfo']['eventID'] = idList[1]
    # xmlFile.write (4*tab+"<eventInfo>\n" + \
    #                5*tab+"<eventID>"+str(idList[1])+"</eventID>\n")

###
#   Message segmentation section...   Repeated for all segments
#   Added - June, 2018
###
    # commonContainer['eventInfo']['#comment'] = '\n...Message segmentation...\n'
    # xmlFile.write ("<!--\n\t\t ...Message segmentation... \n-->\n")                         ###comment in XML file
    commonContainer['eventInfo']['msgSegmentInfo'] = {}
    commonContainer['eventInfo']['msgSegmentInfo']['totalMsgSegments'] = msgSegList[0][0]
    commonContainer['eventInfo']['msgSegmentInfo']['thisSegmentNum'] = currSeg
    # xmlFile.write (5*tab+"<msgSegmentInfo>\n" + \
    #                6*tab+"<totalMsgSegments>"+str(msgSegList[0][0])+"</totalMsgSegments>\n" + \
    #                6*tab+"<thisSegmentNum>"+str(currSeg)+"</thisSegmentNum>\n" + \
    #                5*tab+"</msgSegmentInfo>\n")
    
###
#   Event start/end date & time... REPEAT for all message segments ...
###

    # commonContainer['eventInfo']['#comment'] = '\n...Event start Date and Time...\n'
    # xmlFile.write ("<!--\n\t\t ...Event start Date & Time...\n-->\n")                       ###comment in XML file

###
#   WZ start date and time are required. If not specified, use current date and 00h:00m
#   WZ end date and time are optional, if not present, skip it
###

    commonContainer['eventInfo']['startDateTime'] = {}
    commonContainer['eventInfo']['startDateTime']['year'] = eDateTime[2]
    commonContainer['eventInfo']['startDateTime']['month'] = eDateTime[0]
    commonContainer['eventInfo']['startDateTime']['day'] = eDateTime[1]
    commonContainer['eventInfo']['startDateTime']['hour'] = eDateTime[3]
    commonContainer['eventInfo']['startDateTime']['minute'] = eDateTime[4]
    commonContainer['eventInfo']['startDateTime']['offset'] = timeOffset
    # xmlFile.write (5*tab+"<startDateTime>\n" + \
    #                6*tab+"<year>"+str(eDateTime[0])+"</year>\n" + \
    #                6*tab+"<month>"+str(eDateTime[1])+"</month>\n" + \
    #                6*tab+"<day>"+str(eDateTime[2])+"</day>\n" + \
    #                6*tab+"<hour>"+str(eDateTime[3])+"</hour>\n" + \
    #                6*tab+"<minute>"+str(eDateTime[4])+"</minute>\n" + \
    #                6*tab+"<offset>"+str(timeOffset)+"</offset>\n" + \
    #                5*tab+"</startDateTime>\n")
    
###
#       Event duration - End date & time can be optional...
###

    # commonContainer['eventInfo']['#comment'] = '\n...Event end Date and Time...\n'
    # xmlFile.write ("<!--\n\t\t ...Event end Date and Time...\n-->\n")                       ###comment in XML file
           
    if str(endDateTime[0]) != "":
        commonContainer['eventInfo']['endDateTime'] = {}
        commonContainer['eventInfo']['endDateTime']['year'] = endDateTime[2]
        commonContainer['eventInfo']['endDateTime']['month'] = endDateTime[0]
        commonContainer['eventInfo']['endDateTime']['day'] = endDateTime[1]
        commonContainer['eventInfo']['endDateTime']['hour'] = endDateTime[3]
        commonContainer['eventInfo']['endDateTime']['minute'] = endDateTime[4]
        # xmlFile.write (5*tab+"<endDateTime>\n" + \
        #                6*tab+"<year>"+str(endDateTime[0])+"</year>\n" + \
        #                6*tab+"<month>"+str(endDateTime[1])+"</month>\n" + \
        #                6*tab+"<day>"+str(endDateTime[2])+"</day>\n" + \
        #                6*tab+"<hour>"+str(endDateTime[3])+"</hour>\n" + \
        #                6*tab+"<minute>"+str(endDateTime[4])+"</minute>\n" + \
        #                5*tab+"</endDateTime>\n")
    # else:
        # commonContainer['eventInfo']['#comment'] = '\n...Event End Date and Time NOT Specified...\n'
    #    xmlFile.write ("<!--\n\t\t ...Event End Date and Time NOT Specified...\n-->\n")    

###
#       Whole bloody section on event recurrences is required here...
###

###
#       Event Recurrence...
###

    commonContainer['eventInfo']['eventRecurrence'] = {}
    commonContainer['eventInfo']['eventRecurrence']['EventRecurrence'] = {}
    commonContainer['eventInfo']['eventRecurrence']['EventRecurrence']['startTime'] = {}
    commonContainer['eventInfo']['eventRecurrence']['EventRecurrence']['startTime']['hour'] = eDateTime[3]
    commonContainer['eventInfo']['eventRecurrence']['EventRecurrence']['startTime']['minute'] = eDateTime[4]
    commonContainer['eventInfo']['eventRecurrence']['EventRecurrence']['startTime']['second'] = 0
    commonContainer['eventInfo']['eventRecurrence']['EventRecurrence']['endTime'] = {}
    commonContainer['eventInfo']['eventRecurrence']['EventRecurrence']['endTime']['hour'] = endDateTime[3]
    commonContainer['eventInfo']['eventRecurrence']['EventRecurrence']['endTime']['minute'] = endDateTime[4]
    commonContainer['eventInfo']['eventRecurrence']['EventRecurrence']['endTime']['second'] = 0
    commonContainer['eventInfo']['eventRecurrence']['EventRecurrence']['startDate'] = {}
    commonContainer['eventInfo']['eventRecurrence']['EventRecurrence']['startDate']['year'] = eDateTime[2]
    commonContainer['eventInfo']['eventRecurrence']['EventRecurrence']['startDate']['month'] = eDateTime[0]
    commonContainer['eventInfo']['eventRecurrence']['EventRecurrence']['startDate']['day'] = eDateTime[1]
    commonContainer['eventInfo']['eventRecurrence']['EventRecurrence']['endDate'] = {}
    commonContainer['eventInfo']['eventRecurrence']['EventRecurrence']['endDate']['year'] = endDateTime[2]
    commonContainer['eventInfo']['eventRecurrence']['EventRecurrence']['endDate']['month'] = endDateTime[0]
    commonContainer['eventInfo']['eventRecurrence']['EventRecurrence']['endDate']['day'] = endDateTime[1]
    days_of_week = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    days_of_week_convert = {'monday': 'Mon', 'tuesday': 'Tue', 'wednesday': 'Wen', 'thursday': 'Thu', 'friday': 'Fri', 'saturday': 'Sat', 'sunday': 'Sun'}
    for day in days_of_week:
        commonContainer['eventInfo']['eventRecurrence']['EventRecurrence'][day] = {str(days_of_week_convert[day] in wzDaysOfWeek).lower(): None}
    #commonContainer['eventInfo']['eventRecurrence']['EventRecurrence']['exclusion'] = {'false': None}

###
#       Cause and optional subcause codes...
###

    # xmlFile.write ("<!--\n\t\t ...Cause/Sub cause codes...\n-->\n")       
    # commonContainer['eventInfo']['#comment'] = '\n...Cause/Sub cause codes...\n'                   ###comment in XML file
    commonContainer['eventInfo']['causeCode'] = c_sc_codes[0]
    commonContainer['eventInfo']['subCauseCode'] = c_sc_codes[1]
    # xmlFile.write (5*tab+"<causeCode>"+str(c_sc_codes[0])+"</causeCode>\n" + \
    #                5*tab+"<subCauseCode>"+str(c_sc_codes[1])+"</subCauseCode>\n")
    
###
#   End of event Info...
###

    # xmlFile.write (4*tab+"</eventInfo>\n")

###
#   Start of regionInfo
#       applicableHeading    ... Repeat for all message segments...
#       referencePoint, type ... Repeat for all message segments...  
#       speedLimit
#       eventLength
#       approachRegion
#
###

    # commonContainer['#comment'] = '\n...Region Info Section...\n'
    # xmlFile.write ("<!--\n\t\t ...Region Info Section...\n-->\n")                           ###comment in XML file
    commonContainer['regionInfo'] = {}
    # xmlFile.write (4*tab+"<regionInfo>\n")

###
#   Applicable Heading and Tolerance... REPEAT for message segments ...
#
#   Convert heading to int before converting to str
####

    appHeading = round(float(appHeading))    

    # commonContainer['regionInfo']['#comment'] = '\n...Applicable Heading / Tolerance...\n'
    # xmlFile.write ("<!--\n\t\t ...Applicable Heading / Tolerance...\n-->\n")        ###comment in XML file
    commonContainer['regionInfo']['applicableHeading'] = {}
    commonContainer['regionInfo']['applicableHeading']['heading'] = appHeading
    commonContainer['regionInfo']['applicableHeading']['tolerance'] = hTolerance
    # xmlFile.write (5*tab+"<applicableHeading>\n" + \
    #                6*tab+"<heading>"+str(appHeading)+"</heading>\n" + \
    #                6*tab+"<tolerance>"+str(hTolerance)+"</tolerance>\n" + \
    #                5*tab+"</applicableHeading>\n")
    
###
#   Reference Point...    REPEAT for all message segments   ...
#
#   However following is done in the calling routine since wzMapPt is not available here...
#       Update refPoint to a new value for different message segment > 1.
#       Since the distance between the original reference point and the first node for message segment 2 to the last segment is 
#       too far apart (xyz_offset) to be represented in just one offset node. To alleviate the issue, for every segment, a new reference
#       point is set as same as the first node point of of the lane for which the vehicle path data was collected.
###
#
#   1. Convert ref point lat/lon degrees to 1/10th of micro degrees (multiply by 10^7)
###

    lat  = int(float(refPoint[0]) * 10000000)
    lon  = int(float(refPoint[1]) * 10000000)
    elev = round(float(refPoint[2]))                                           		    ###in meters no fraction

    # commonContainer['regionInfo']['#comment'] = '\n...Reference Point - Lat/Long in Micro Degrees...\n'
    # xmlFile.write ("<!--\n\t\t ...Reference Point - Lat/Long in Micro Degrees...\n-->\n")   ###comment in XML file
    commonContainer['regionInfo']['referencePoint'] = {}
    commonContainer['regionInfo']['referencePoint']['lat'] = lat
    commonContainer['regionInfo']['referencePoint']['long'] = lon
    commonContainer['regionInfo']['referencePoint']['elevation'] = elev
    # xmlFile.write (5*tab+"<referencePoint>\n" + \
    #                6*tab+"<lat>"+str(lat)+"</lat>\n" + \
    #                6*tab+"<long>"+str(lon)+"</long>\n" + \
    #                6*tab+"<elevation>"+str(elev)+"</elevation>\n" + \
    #                5*tab+"</referencePoint>\n")
###
#   Reference Point Type...
###

    # commonContainer['regionInfo']['#comment'] = '\n...Reference Point Type...\n'
    # xmlFile.write ("<!--\n\t\t ...Reference Point Type...\n-->\n")                          ###comment in XML file
    commonContainer['regionInfo']['referencePointType'] = {"startOfEvent": None}
    commonContainer['regionInfo']['descriptiveName'] = descName
    # xmlFile.write (5*tab+"<referencePointType><startOfEvent/></referencePointType>\n" + \
    #                5*tab+"<descriptiveName>"+descName+"</descriptiveName>\n")


###
#   Following - ONLY for the message segment #1...         
###
#   Speed limits...  type, speed and unit...
###
#       As of Nov. 2017...
#       speedLimit list is defined as follows: The values are input by the user...
#           0. type  = "vehicleMaxSpeed"
#           1. speed =  normal (what is on approach lanes...)
#           2.          in WZ at the reference point + applicable speed for WZ lane as node attribute
#           3.          when workers present (applicable only for WZ lane as node attribute)
#           4. unit  = "mph" or "kph" or "mpsXpt02"
#
#       The speed limit set here is at the start of the event (at the reference point)...
#       In case of CSW, it would be the advisory speed...
###                       

    if currSeg == 1:
        # commonContainer['regionInfo']['#comment'] = '\n...Speed Limit at the Ref. Point...\n'
        # xmlFile.write ("\n<!--\n\t\t  ...Speed Limit at the Ref. Point...\n-->\n")      ###comment in XML file
        commonContainer['regionInfo']['speedLimit'] = {}
        commonContainer['regionInfo']['speedLimit']['type'] = {}
        commonContainer['regionInfo']['speedLimit']['type'][speedLimit[0]] = None
        commonContainer['regionInfo']['speedLimit']['speed'] = speedLimit[2]
        commonContainer['regionInfo']['speedLimit']['speedUnits'] = {}
        commonContainer['regionInfo']['speedLimit']['speedUnits'][speedLimit[4]] = None
        # xmlFile.write (5*tab+"<speedLimit>\n" + \
        #                6*tab+"<type>"+speedLimit[0]+"</type>\n" + \
        #                6*tab+"<speed>"+str(speedLimit[2])+"</speed>\n" + \
        #                6*tab+"<speedUnits>"+speedLimit[4]+"</speedUnits>\n" + \
        #                5*tab+"</speedLimit>\n")
    pass

###
#   Event length in meters...
###

    if currSeg == 1:
        # commonContainer['regionInfo']['#comment'] = '\n\t\t...Event Length...\n'
        # xmlFile.write ("\n<!--\n\t\t...Event Length...\n-->\n")                         ###comment in XML file
        commonContainer['regionInfo']['eventLength'] = eL
        # xmlFile.write (5*tab+"<eventLength>"+str(eL)+"</eventLength>\n")
    pass

###
#   Road Width... in cms
#   Eliminated in Feb. 2018 in ASN.1
#   Where is laneWidth???
###

  ###   xmlFile.write ("<!--\n\t\t...Road Width...\n-->\n")                             ###comment in XML file
  ###   xmlFile.write (4*tab+"<roadWidth>"+str(int(rW))+"</roadWidth>\n\n")
        
###
#   Start of approachRegion...
#
#   Scale factor for Approach Lanes Node Points is set to 1 (Default)...
###

    alScale = 1                                             #default approach lane scale factor                                                                  
    if currSeg == 1:
        # commonContainer['regionInfo']['#comment'] = '\n\t\t...Start of Approach Region...\n'
        # commonContainer['regionInfo']['#comment'] = ('    ...APPROACH LANES: Map Waypoints...\n' + \
                    #    6*tab+'Total nodes per lane - '+str(len(arrayMapPt))+'\n')
        # xmlFile.write ("\n<!--\n\t\t...Start of Approach Region...\n-->\n")             ###comment in XML file
        # xmlFile.write ("<!--    ...APPROACH LANES: Map Waypoints...\n" + \
        #                6*tab+"Total nodes per lane - "+str(len(arrayMapPt))+"\n" + \
        #                "-->\n")

        commonContainer['regionInfo']['approachRegion'] = {}
        commonContainer['regionInfo']['approachRegion']['roadwayGeometry'] = {}
        commonContainer['regionInfo']['approachRegion']['roadwayGeometry']['scale'] = alScale
        commonContainer['regionInfo']['approachRegion']['roadwayGeometry']['rsmLanes'] = {}
        # xmlFile.write (5*tab+"<approachRegion>\n" + \
        #                6*tab+"<roadwayGeometry>\n" + \
        #                7*tab+"<scale>"+str(alScale)+"</scale>\n" + \
        #                7*tab+"<rsmLanes>\n")

        #print ("TL and arrayMapPt = ", tL, len(arrayMapPt))

###
#   For a lane closure starting at the ref. point, approach lane "connectsTO" a lane
#   for travel.
#
#   The following value is setup for testing only... 
#
###

        commonContainer['regionInfo']['approachRegion']['roadwayGeometry']['rsmLanes']['RSMLane'] = []
        connToList = [(1,1),(2,2),(3,3),(4,4),(5,5),(6,6),(7,7),(8,8)]      #connectsTo list for approach lanes leading to WZ

        tL = lS[0][0]                                                       #number of lanes
        ln = 0
        while ln < tL:
            preName = "Lane "
            if ln == 0:     preName = "Left Lane: Lane "
            if ln == tL-1:  preName = "Right Lane: Lane "
            # commonContainer['regionInfo']['approachRegion']['roadwayGeometry']['rsmLanes']['#comment'] = '\n\t\t    Approach Lane #"+str(ln+1)+"    \n'
            # xmlFile.write ("<!--\n\t\t    Approach Lane #"+str(ln+1)+"    \n-->\n")

###
#
#       USE either of the following:
##
#       Use the following ONLY if there is NO ConnectingLane using "connectsTo"...
#
#       laneID       --> 0..n
#       lanePosition --> 1..n (starting from the left lane)
#
###

#        if (connToList[ln][0] == connToList[ln][1]):                   #connects to the same lane...
#            xmlFile.write (5*tab+"<ApproachLane>\n" + \
#                           6*tab+"<laneID>"+str(ln)+"</laneID>\n" + \
#                           6*tab+"<lanePosition>"+str(ln+1)+"</lanePosition>\n")
#        pass           

###
#       Following is needed for all cases... Either connectsTo or NOT...
###
            RSMLane = {}
            RSMLane['laneID'] = ln+1
            RSMLane['lanePosition'] = ln+1
            RSMLane['laneName'] = "Lane #" + str(ln+1)
            RSMLane['laneWidth'] = laneWidth
            RSMLane['laneGeometry'] = {}
            RSMLane['laneGeometry']['nodeSet'] = {}
            RSMLane['laneGeometry']['nodeSet']['NodeLLE'] = []
            # xmlFile.write (8*tab+"<RSMLane>\n" + \
            #                9*tab+"<laneID>"+str(ln+1)+"</laneID>\n" + \
            #                9*tab+"<lanePosition>"+str(ln+1)+"</lanePosition>\n" + \
            #                9*tab+"<laneName>Lane #" + str(ln+1)+"</laneName>\n" + \
            #                9*tab+"<laneGeometry>\n" + \
            #                10*tab+"<nodeSet>\n")
###
#       Repeat the following for all nodes in approach for lane ln+1
###

            kt = 0
            while kt < len(arrayMapPt):                                     #lat/lon/alt for each data point
                NodeLLE = {}
                #print ("kt, ln:", kt, ln)

###
#           Convert lat/lon degrees to 1/10th of micro degrees (multiply by 10^7)
#           Multiply converted lat/lon by the scaling factor...
#
#       NOTE:
#          ASN.1 value range defined in J2735 (-900000000) .. (900000001)
#
###
                #lat = int(float(refPoint[0]) * 10000000)
                lat = int((arrayMapPt[kt][ln*5+0]) * 10000000)
                lon = int((arrayMapPt[kt][ln*5+1]) * 10000000)
                elev = round(arrayMapPt[kt][ln*5+2])                        #in full meters only

                NodeLLE['nodePoint'] = {}
                NodeLLE['nodePoint']['node-3Dabsolute'] = {}
                NodeLLE['nodePoint']['node-3Dabsolute']['lat'] = lat
                NodeLLE['nodePoint']['node-3Dabsolute']['long'] = lon
                NodeLLE['nodePoint']['node-3Dabsolute']['elevation'] = elev
                # NodeLLE['nodePoint']['#comment'] = '\t\t\t\t\t  Approach Lane#/Node# - '+str(ln+1)+'/'+str(kt+1)
                # xmlFile.write (11*tab+"<NodeLLE>" + "\t\t\t\t\t<!--  Approach Lane#/Node# - "+str(ln+1)+"/"+str(kt+1)+"  -->\n" + \
                #                12*tab+"<nodePoint>\n" + \
                #                13*tab+"<node-3Dabsolute>\n" + \
                #                14*tab+"<lat>"+str(lat)+"</lat>\n" + \
                #                14*tab+"<long>"+str(lon)+"</long>\n" + \
                #                14*tab+"<elevation>"+str(elev)+"</elevation>\n" + \
                #                13*tab+"</node-3Dabsolute>\n" + \
                #                12*tab+"</nodePoint>\n")

###
#           Before closing the "NodeLLE, see if there are any node attributes that should be
#           added for the node. The attributes can be for example, vehicleMaxSpeed, taperLeft,
#           taper right, laneClosed, etc.
#
#           These attributes are generally not applicable to the approach lanes but certainly
#           would apply to the WZ lanes...
###

                # xmlFile.write (11*tab+"</NodeLLE>\n")
                RSMLane['laneGeometry']['nodeSet']['NodeLLE'].append(NodeLLE)
                kt = kt + 1                                                 #incr row (next node point for same lane
            pass                                                            #end of while

###
#       End of nodeSet and laneGeometry...
###

            # xmlFile.write (10*tab+"</nodeSet>\n" + \
            #                9*tab+"</laneGeometry>\n")
       
###
#       Use the following ONLY if there is ConnectingLane using "connectsTo"...
#
#       laneID       --> 1..n (unique number but not necessarily in sequence!!)
#       lanePosition --> 1..n (starting from the left lane)
#
#       connectsTo and "ConnectingLane"   --> uses "laneID"
#
###
            if (connToList[ln][0] != connToList[ln][1]):                    #connects to different lane...
                RSMLane['connectsTo'] = {}
                RSMLane['connectsTo']['LaneID'] = [connToList[ln][0], connToList[ln][1]]
                # xmlFile.write (9*tab+"<connectsTo>\n" + \
                #                10*tab+"<LaneID>"+str(connToList[ln][0])+"</LaneID>\n" + \
                #                10*tab+"<LaneID>"+str(connToList[ln][1])+"</LaneID>\n" + \
                #                9*tab+"</connectsTo>\n")
            pass    

###
#       End of RSMLane    
###

            # xmlFile.write (8*tab+"</RSMLane>\n")

            commonContainer['regionInfo']['approachRegion']['roadwayGeometry']['rsmLanes']['RSMLane'].append(RSMLane)
            ln = ln + 1                                                     #next lane
        pass                                                                #end of while

        # xmlFile.write (7*tab+"</rsmLanes>\n" + \
        #                6*tab+"</roadwayGeometry>\n" + \
        #                5*tab+"</approachRegion>\n" + \
        #                4*tab+"</regionInfo>\n")                             #end of approachLanes and regionInfo
    pass

###
#   Close regionInfo tag for message segment > 1
###

    # if currSeg > 1:  xmlFile.write (4*tab+"</regionInfo>\n")
    
###
##
#       *****************  ... End of Common Container...  *****************
##
###

    # xmlFile.write (3*tab+"</commonContainer>\n")                            #end of common container...    
    # commonContainer['#comment'] = '\n\t\t...END of COMMON CONTAINER...'
    # xmlFile.write ("\n<!--\n\t\t...END of COMMON CONTAINER...\t\t-->\n")    ###comment in XML file                      
    return commonContainer


###
#       *****************  ... RSM: Start of Workzone Container...  *****************    
#
#       NOTE: Added <scale> nn </scale> to change resolution from 1/10th microdegrees (default) to ...
#       In the following, it's scaled up to microdegrees...
#       
###     ----------------------------------------------------------------------------------------------------------

###
#   Following function generates "Work Zone" container .exer file using xml tags
#   defined in rsm4.4.asn for WZ lanes.
#
#   updated in June, 2018 for ASN. version 5.1...
#
#####

def build_xml_WZC (xmlFile,speedLimit,laneWidth,laneStat,wpStat,arrayMapPt,RN,msgSegList,currSeg):

    ##print ("in build_xml_WZC, current segment", currSeg)
    
###
#   Following data elements are passed by the calling routine
#
#   xmlFile     -   output .exer file in xml format
#   speedLimit  -   List of speed limits for all lanes in WZ for:
#                       normal speed limit (not in work zone)
#                       speed limit in work zone
#                       speed limit in work zone when workers are present
#   laneWidth   -   lane width from the user input config file, converted to cms here... (Added on 3-11-2019)
#   laneStat    -   list containing information about lane status - Lane#, Data point#, LC or LO, Offset in meters from ref. pt. 
#   wpStat      -   list of WP status
#   arrayMapPt  -   array of node lists generated in getLanePt function
#   RN          -   Boolean - True:  Generate reduced nodes for closed lanes
#                           - False: Generate all nodes for closed lanes
###

###
#   Set scale factor for WZ Lanes Node Points to 10 set as default...
###

    totLane     = laneStat[0][0]                                                            #total number of lanes
    wzLaneScale = 10                    #WZ Lane scale factor(default)
    laneWidth   = int(laneWidth*100)    #in cms
    tab         = "\t"                  #tab char (4 spaces)
    tab         = "  "                  #replace tab char with 2 spaces

###
#   Start WZ lane map waypoints...
###

    rszContainer = {}
    # rszContainer['#comment'] = '   ...Work Zone Lanes: Map way points...   '
    # xmlFile.write ("\n<!--   ...Work Zone Lanes: Map way points...   -->\n\n")
    # xmlFile.write (3*tab+"<rszContainer>\n")

###
#   Added on Jan. 25, 2018
#   Add <laneStatus>..<LaneInfo> for each lane... in WZ
#
#   NOTE: Modify the following ONLY if the lane is closed for the entire WZ
#       Otherwise, specified in <nodeAttributes>
#       If both are present, <nodeAttributes> will be ignored...
#
###
#
###
#   Add <laneStatus> for each lane...
#
#   Revised on March 19, 2019...
#
#   As per DENSO logic in the OBU, this upper level "laneClosed" is used ONLY when, once the lane is closed, remains closed for
#   the entire work zone. If in the work zone, a lane has multiple lane closures, it is indicated at a node level.
#   In such case, the upper level lane status (closed/open) for the entire lane shall not be included. Otherwise, the application logic
#   will ignore the node level attributes.
#
#   The correct way should be to use the upper level lane status unless specified at the node attribute level which should take precedence...
#
#   Following logic is commented out since in this implementation, lane status is captured at node level and specified in node attribute.
#
#   Date Modified: March 12, 2019
#
###


#########  FOLLOWING IS COMMENTED...

###

##    laneInfo = totLane*[0,0]                        #set all lane info - open and offset to 0 from ref. pt. (value pair)
   
##    for ls in range (1, len(laneStat)):
##        if laneStat[ls][2] == 1:                    #This lane is closed in
##            ll = laneStat[ls][1] - 1
##            laneInfo[ll*2+0] = 1                    #mark as lc
##            laneInfo[ll*2+1] = int(laneStat[ls][3]) #Offset from ref. pt.
##        pass
##    pass


##    xmlFile.write (4*tab+"<laneStatus>\n")

##    for ls in range (0, totLane):
##        lStat   = "<false/>"
##        offset  = 0
##        if laneInfo[ls*2+0] == 1:
##            lStat  = "<true/>"
##            offset = laneInfo[ls*2+1]
##        pass
            
##        xmlFile.write (5*tab+"<LaneInfo>\n" + \
##                       6*tab+"<lanePosition>"+str(ls+1)+"</lanePosition>\n" + \
##                       6*tab+"<laneClosed>"+lStat+"</laneClosed>\n" + \
##                       6*tab+"<laneCloseOffset>"+str(offset)+"</laneCloseOffset>\n" + \
##                       5*tab+"</LaneInfo>\n")
##    pass

##    xmlFile.write (4*tab+"</laneStatus>\t\t\t\t<!---  End of Lane Status  -->\n\n")    #end of laneStatus...
   
###
#   Add <peoplePresent> if workers are present...
#
#   As indicated above for <laneStatus>, in case of <peoplePresent>, the information is provided at the node level and NOT to be
#   to be provided at the upper level. If present, the DENSO logic ignores it at the node level and won't warn the driver for multiple
#   <peoplePresent> zones in the map.
#
#   Updated on March 12, 2019
#
###

##    pP = "<false/>"                                 #Default to false
##    if len(wpStat) > 0 and wpStat[0][1] == 1:
##        pP = "<true/>"                              #workers present is set...
##    pass

##    xmlFile.write (4*tab+"<peoplePresent>"+pP+"</peoplePresent>\n\n")        

###
#   Add speedLimit for the entire WZ under rszContainer. speedLimit can be updated at node level
#   when appropriate - e.g. workers present, otherwise the limit is applied for the entire WZ.
###

    rszContainer['speedLimit'] = {}
    rszContainer['speedLimit']['type'] = {}
    rszContainer['speedLimit']['type'][speedLimit[0]] = None
    rszContainer['speedLimit']['speed'] = speedLimit[2]
    rszContainer['speedLimit']['speedUnits'] = {}
    rszContainer['speedLimit']['speedUnits'][speedLimit[4]] = None
    # xmlFile.write (4*tab+"<speedLimit>\n" + \
    #                5*tab+"<type>"+speedLimit[0]+"</type>\n" + \
    #                5*tab+"<speed>"+str(speedLimit[2])+"</speed>\n" + \
    #                5*tab+"<speedUnits>"+speedLimit[4]+"</speedUnits>\n" + \
    #                4*tab+"</speedLimit>\n\n")

###
#   ... Start of WZ Lane Geometry ...
###       

    # rszContainer['#comment'] = '<!--\t ...S T A R T   of   L A N E   G E O M E T R Y...\n' + \
                #    8*tab+'Total node points per lane - '+str(len(arrayMapPt))+'\n'
    # xmlFile.write ("<!--\t ...S T A R T   of   L A N E   G E O M E T R Y...\n" + \
    #                8*tab+"Total node points per lane - "+str(len(arrayMapPt))+"\n" + \
    #                "-->\n") 
    rszContainer['rszRegion'] = {}
    rszContainer['rszRegion']['roadwayGeometry'] = {}
    rszContainer['rszRegion']['roadwayGeometry']['scale'] = wzLaneScale
    rszContainer['rszRegion']['roadwayGeometry']['rsmLanes'] = {}
    rszContainer['rszRegion']['roadwayGeometry']['rsmLanes']['RSMLane'] = []
    # xmlFile.write (4*tab+"<rszRegion>\n" + \
    #                5*tab+"<roadwayGeometry>\n" +  \
    #                6*tab+"<scale>"+str(wzLaneScale)+"</scale>\n")
    # xmlFile.write (6*tab+"<rsmLanes>\n")
    laneTaperStat = [{"left": False, "right": False}]*totLane
    ln = 0
    while ln < totLane:
        
        preName = "Lane #"
        if ln == 0:         preName = "Left Lane: Lane #"
        if ln == totLane-1: preName = "Right Lane: Lane #"
        
        ##print ("Working on Lane: ",ln+1, "tot lane = ",totLane)
        # rszContainer['#comment'] = '\n\t    ...Work Zone Lane #'+str(ln+1)+'...\n'
        # xmlFile.write ("<!--\n\t    ...Work Zone Lane #"+str(ln+1)+"...\n-->\n")
        RSMLane = {}
        RSMLane['laneID'] = ln+1
        RSMLane['lanePosition'] = ln+1
        RSMLane['laneName'] = preName+str(ln+1)
        RSMLane['laneWidth'] = laneWidth
        RSMLane['laneGeometry'] = {}
        RSMLane['laneGeometry']['nodeSet'] = {}
        RSMLane['laneGeometry']['nodeSet']['NodeLLE'] = []
        # xmlFile.write (7*tab+"<RSMLane>\n" + \
        #                8*tab+"<laneID>"+str(ln+1)+"</laneID>\n" + \
        #                8*tab+"<lanePosition>"+str(ln+1)+"</lanePosition>\n" + \
        #                8*tab+"<laneName>"+preName+str(ln+1)+"</laneName>\n" + \
        #                8*tab+"<laneWidth>"+str(laneWidth)+"</laneWidth>\n" + \
        #                8*tab+"<laneGeometry>\n" + \
        #                9*tab+"<nodeSet>\n")

###
#       Repeat the following for all nodes in WZ for lane ln+1
#
#       Following revised to support multiple message segments (message segmentation)
#
#       For each lane, the nodes will be from startNode to endNode as constructed in msgSegList
#       The msgSegList is organized as follows:
#
#       msgSegList[0]  = (totMsgSeg, maxNPL)
#       msgSegList[1]  = (1,startNode for appLane,endNode of appLane)    --- NOTE --- approach lane nodes ARE NOT SPLIT in multiple msg Seg.
#       msgSegList[2]  = (segNum,startNode for wzLane,endNode of wzLane)
#               ...
#               ...
#       msgSegList[n]  = (segNum,startNode for wzLane,endNode of wzLane)

#       Revised June 6, 2018
###

        #kt = 0                                                          
        kt = msgSegList[currSeg+1][1] - 1                               #wz start and end nodes/seg starts
        prevLaneStat = 0                                                #previous lane state (open)
        prevLaneTaperStat = 0                                                #previous lane state (open)
        prevWPStat   = 0                                                #previous WP state (no WP)
        connToFlag   = 0                                                #set flag for connectsTo 0
        
###     while kt < len(arrayMapPt):                                     #lat/lon/alt for each data point

        while kt < msgSegList[currSeg+1][2]:                            #end node #    
            #print ("kt (node), lane#:", kt, ln)

###
#           First Get lane and WP status at the current node for the lane...
###
            currLaneStat        = arrayMapPt[kt][ln*5+3]                       #get lc/lo status for the node
            currLaneTaperStat   = arrayMapPt[kt][ln*5+4]                       #get lc/lo status for the node
            currWPStat          = arrayMapPt[kt][len(arrayMapPt[kt])-2]        #get WP flag for the node

            ##print ("Lane=",ln," node=",kt,"pStat=",prevLaneStat,"cStat=",currLaneStat)
            ##print ("wpStat:",int(arrayMapPt[kt][len(arrayMapPt[kt])-1]))

###
#           Added on Jan. 26, 2018
#
#           Following determines if the lane is closed at the previous node for the lane,
#               If so AND RS is TRUE, NO NEED to write node and node attributes. This will reduce the DSRC message size
#
#           If the lane is opened again before the end of the WZ, node geometry is specified from lane opening
#           till it's closed again OR end of WZ.
#
###         NOTE: For a lane that is closed from ref. pt. till the end of the WZ, TWO nodes are required.
#               1. first node at the ref. point and 
#               2. last node at the end of the WZ    
#
###
            lcMsg = ""; wpMsg = ""
            
            if currLaneStat == 1:   lcMsg = " ... Lane is closed ..."
            if currWPStat   == 1:   wpMsg = " ... Workers Present ..."


            lcStat = False
            if currLaneStat == prevLaneStat and currLaneStat == 1 and RN == True:
                lcStat = True
                if kt == len(arrayMapPt)-1:     lcStat = False          #Forced last node point...      
            pass

            if lcStat == False:                                         #do the following if lcStat is False, do all nodes             
###
#               Convert lat/lon degrees to 1/10th of micro degrees (multiply by 10^7) and add the node
#               Multiply the converted lat/lon with the scaling factor
#           NOTE:
#               ASN.1 value range defined in J2735 (-900000000) .. (900000001)
#
###
                lat = int((arrayMapPt[kt][ln*5+0]) * 10000000)
                lon = int((arrayMapPt[kt][ln*5+1]) * 10000000)
                elev = round(arrayMapPt[kt][ln*5+2])                    #in full meters
                NodeLLE = {}
                NodeLLE['nodePoint'] = {}
                NodeLLE['nodePoint']['node-3Dabsolute'] = {}
                NodeLLE['nodePoint']['node-3Dabsolute']['lat'] = lat
                NodeLLE['nodePoint']['node-3Dabsolute']['long'] = lon
                NodeLLE['nodePoint']['node-3Dabsolute']['elevation'] = elev
                # rszContainer['#comment'] = '\t\t\t\t\t<!--  WZ Lane#/Node# - '+str(ln+1)+'/'+str(kt+1)+lcMsg+wpMsg
                # xmlFile.write (10*tab+"<NodeLLE>" + "\t\t\t\t\t<!--  WZ Lane#/Node# - "+str(ln+1)+"/"+str(kt+1)+lcMsg+wpMsg+"  -->\n" + \
                #                11*tab+"<nodePoint>\n" + \
                #                12*tab+"<node-3Dabsolute>\n" + \
                #                13*tab+"<lat>"+str(lat)+"</lat>\n" + \
                #                13*tab+"<long>"+str(lon)+"</long>\n" + \
                #                13*tab+"<elevation>"+str(elev)+"</elevation>\n" + \
                #                12*tab+"</node-3Dabsolute>\n" + \
                #                11*tab+"</nodePoint>\n")
               
###
#               Add Attributes here, IF....
#
#               1. Workers are present (TRUE), add new speed limit attribute
#               2. Lane closure/open, add lane taper attributes
#
#               Check for workers presence (0/1)
#               Check for lo/lc (0/1) for the current lane/node
#
#               Check following logic for adding node attributes...
###
                updatedTapers = False
                if currLaneStat != prevLaneStat or currWPStat != prevWPStat or currLaneTaperStat != prevLaneTaperStat:
                    NodeLLE['nodeAttributes'] = {}
                    # xmlFile.write (11*tab+"<nodeAttributes>\n")               
  
###
#                   Provide node attributes if lc/lo status change or WP status change for the node...
###
                    #print ("lane,kt,curr and prev lane status:",ln,kt,currLaneStat, prevLaneStat)        
                    #print ("lane,kt,curr and prev WP status:",ln,kt,currWPStat, prevWPStat)

###
#                   -- WP status change (workers not present to present), speedLimit[3]
#                   -- WP status change (workers present to not present), speedLimit[2]
#
#                   Check for PP(people present) status change...
###

                    if currWPStat != prevWPStat:                        #WP status change
                        print(currWPStat)
                        if currWPStat == 1:                             #start of wp
                            sLoc = 3
                            pP = {"true": None}
                            # pP = "<peoplePresent><true/></peoplePresent>"
                        pass
            
                        if currWPStat == 0:                             #end of WP
                            sLoc = 2
                            pP = {"false": None}
                            # pP = "<peoplePresent><false/></peoplePresent>"
                        pass                
###
#                       update speed limit attributes followed by workers present as defined in ASN.1...
###

                        ###xmlFile.write (12*tab+""+pP+"\n")            #must come after node's speed attribute
                        NodeLLE['nodeAttributes']['speedLimit'] = {}
                        NodeLLE['nodeAttributes']['speedLimit']['type'] = {}
                        NodeLLE['nodeAttributes']['speedLimit']['type'][speedLimit[0]] = None
                        NodeLLE['nodeAttributes']['speedLimit']['speed'] = speedLimit[sLoc]
                        NodeLLE['nodeAttributes']['speedLimit']['speedUnits'] = {}
                        NodeLLE['nodeAttributes']['speedLimit']['speedUnits'][speedLimit[4]] = None
                        NodeLLE['nodeAttributes']['peoplePresent'] = pP
                        # xmlFile.write (12*tab+"<speedLimit>\n" + \
                        #                13*tab+"<type>"+speedLimit[0]+"</type>\n" + \
                        #                14*tab+"<speed>"+str(speedLimit[sLoc])+"</speed>\n" + \
                        #                14*tab+"<speedUnits>"+speedLimit[4]+"</speedUnits>\n" + \
                        #                12*tab+"</speedLimit>\n")
                        # xmlFile.write (12*tab+""+pP+"\n")               #must come after node's speed attribute


                        prevWPStat = currWPStat                         #set WP status
                    pass

###
#                   Check lane status...
#
#                   Left two lanes...                                               
#                   Lane closed, Lanes 1 & 2, taper left = F, taper right = T
#                   Lane opened, Lanes 1 & 2  taper left = T, taper right = F 
#
#                   Right two lanes...                                              
#                   Lane closed, Lanes 3 & 4, taper left = T, taper right = F                                              
#                   Lane opened, Lanes 3 & 4  taper left = F, taper right = T                                              
###

           
                    if currLaneStat != prevLaneStat:                    #lane state changed lo <--> lc node, add attributes                    
                    
                        ##print ("in lane change stat...", ln, kt,currLaneStat)
                        
                        if currLaneStat == 1:                           #lane is closed at this node
                            connToFlag = 1                              #only for the closed lane "connectsTo" attribute
###
#                           determine toLane value for "connectsTo" tag by checking adjacent lane's node status,
#                           if open, assigned to toLane
###
                            if ln == 0:             toLane = ln+1
                            if ln == totLane-1:     toLane = ln-1
                            if ln > 0 and ln < totLane-1:
                                if arrayMapPt[kt][(ln+1)*4+3] == 0:     toLane = ln+1
                                if arrayMapPt[kt][(ln-1)*4+3] == 0:     toLane = ln-1
                            pass

###
#                           set node attribute for "laneClosed" 
###
                            lClosed = {"true": None} #"<laneClosed><true/></laneClosed>"
                        pass

                        if currLaneStat == 0:                           #lane is opened at this node
                            lClosed = {"false": None} #"<laneClosed><false/></laneClosed>"
                        pass

                        tLeftVal = False
                        tLeft = {"false": None}
                        tRightVal = False
                        tRight = {"false": None}

                        if currLaneTaperStat == 1:
                            tRightVal = True
                            tRight  = {"true": None}
                        elif currLaneTaperStat == 2:
                            tLeftVal = True
                            tLeft  = {"true": None}
                        
                        if laneTaperStat[ln]['left'] == tLeftVal: tLeft = None
                        if laneTaperStat[ln]['right'] == tRightVal: tRight = None

                        laneTaperStat[ln]['left'] = tLeftVal
                        laneTaperStat[ln]['right'] = tRightVal
###
#                       Write Lane taper attributes...
###
                        if tLeft != None: NodeLLE['nodeAttributes']['taperLeft'] = tLeft
                        if tRight != None: NodeLLE['nodeAttributes']['taperRight'] = tRight
                        NodeLLE['nodeAttributes']['laneClosed'] = lClosed
                        updatedTapers = True
                        # xmlFile.write (12*tab+""+tLeft+"\n" + \
                        #                12*tab+""+tRight+"\n" + \
                        #                12*tab+""+lClosed+"\n")

                        prevLaneStat = currLaneStat                     #set prev status same as current
                        prevLaneTaperStat = currLaneTaperStat                     #set prev status same as current
                    pass                                                #end of lc/lo attributes

                    if currLaneTaperStat != prevLaneTaperStat and currLaneTaperStat == 0:
                        tLeftVal = False
                        tLeft = {"false": None}
                        tRightVal = False
                        tRight = {"false": None}

                        if laneTaperStat[ln]['left'] == tLeftVal: tLeft = None
                        if laneTaperStat[ln]['right'] == tRightVal: tRight = None

                        laneTaperStat[ln]['left'] = tLeftVal
                        laneTaperStat[ln]['right'] = tRightVal
                        if not NodeLLE.get('nodeAttributes', False):
                            NodeLLE['nodeAttributes'] = {}
                        if tLeft != None: NodeLLE['nodeAttributes']['taperLeft'] = tLeft
                        if tRight != None: NodeLLE['nodeAttributes']['taperRight'] = tRight

###
#                   End of nodeAttributes...
###
                    # xmlFile.write (11*tab+"</nodeAttributes>\n")
                pass                                                    #end of node attributes

                RSMLane['laneGeometry']['nodeSet']['NodeLLE'].append(NodeLLE)
                # xmlFile.write (10*tab+"</NodeLLE>\n")                   #end of NodeLLE
                
            pass                                                        #end of lcStat check

            kt = kt + 1                                                 #incr for next node point for same lane
        pass                                                            #end of while - all nodes for the lane
        # xmlFile.write (9*tab+"</nodeSet>\n")                            #end of nodeset for the lane
        # xmlFile.write (8*tab+"</laneGeometry>\n")                       #end of laneGeoetry

###
#       For Closed Lane only, add "connectsTo" attribute for lane... 
#       Must have at least two lanes for "connectsTo"...
###

        if connToFlag == 1 and totLane > 1:
###
#           Write connectsTo tag...
###
            RSMLane['connectsTo'] = {}
            RSMLane['connectsTo']['LaneID'] = [ln+1, toLane+1]
            # xmlFile.write (8*tab+"<connectsTo>\n" + \
            #                9*tab+"<LaneID>"+str(ln+1)+"</LaneID>\n" + \
            #                9*tab+"<LaneID>"+str(toLane+1)+"</LaneID>\n" + \
            #                8*tab+"</connectsTo>\n")
        pass
        
        rszContainer['rszRegion']['roadwayGeometry']['rsmLanes']['RSMLane'].append(RSMLane)
        # xmlFile.write (7*tab+"</RSMLane>\n")                            #end of current lane
                       
        ln = ln + 1                                                     #next lane
        #print ("after ln incr:", ln)
    pass                                                                #end of while

    # xmlFile.write (6*tab+"</rsmLanes>\n" + \
    #                5*tab+"</roadwayGeometry>\n" + \
    #                4*tab+"</rszRegion>\n" + \
    #                3*tab+"</rszContainer>\n")                           #end of RSZ container

###
#   END OF RSM!!!
###                                               

    # xmlFile.write (2*tab+"</RoadsideSafetyMessage>\n")                  #end or RSM...
    

###
#   RSM: End of MessageFrame...  
###

    # xmlFile.write (1*tab+"</value>\n" + \
    #                "</MessageFrame>")


    return rszContainer                                                   #End of func!
                       
