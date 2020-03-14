#!/usr/bin/env python3
###
#
#   This module was originally in the WZ_MapBuilder.py main module
#
#   Separated as callable module
#   
#   August 22, 2018
#
###
#   Function: Read vehicle path data file and build following: 
#
#       Input:
#           vehPathDataFile - collected vehicle path data file
#           totLanes        - total number lanes in WZ
#           sampleFreq      - GPS data sampling frequency used for computing distance traveled and locations of LC/LO/WP, etc.
#
#       Output:
#           pathPt          - array containing vehicle path data points used for determining lane geometry node points
#                             speed,lat,lon,alt,heading            
#           laneStat        - array consisting of lane status indicating lane closures and openings
#           wpStat          - array consisting of workers presence status
#           refPoint        - reference point indicating start of event (lat,lon,alt)
#           refPtIdx        - index in pathPt array for reference point
#           wzLen           - computed WZ length
#           
#
###


import  csv                                                 #csv file processor

#def buildVehPathData_LaneStat (vehPathDataFile,totalLanes,pathPt,laneStat,wpStat,refPoint,refPtIdx,appHeading,wzLen,sampleFreq):
def buildVehPathData_LaneStat (vehPathDataFile,totalLanes,pathPt,laneStat,wpStat,refPoint,atRefPoint,sampleFreq):


    newFormat   = True                                      #set new data format to true...
    gotRefPt    = False                                     #default 
    laneStatIdx = 0                                         #laneStat + lcOffset array index
    wpStatIdx   = 0                                         #wpStat array index
    rowKt       = 0                                         #input record processing counter

    refPtIdx    = 0                                         #ref point index
    wzLen       = 0                                         #wz length in meters
    appHeading  = 0                                         #applicable heading angle
   
###
#   Following variables are modified in this function and the modified value is available only if they are declared
#   as global for it's value to be available in the calling main function. Otherwise, it remains as local and updated value
#   is not affacted in the calling routine.
####

#    global  refPtIdx
#    global  wzLen       
                     
###
#   Store total lanes in laneStat list at the first location
#   Following for total lanes added on Nov. 2, 2017
###

    laneStat.insert(laneStatIdx,list((totalLanes,0,0,0)))   #Total lanes is stored in the first(0) location in array, rest values are set to zero
    laneStatIdx += 1                                        #Incr the index for next set of values

###
#   Read input file as csv and process each record...
###

    with open(vehPathDataFile, newline='') as csvFile:
        csvReader = csv.reader(csvFile)
        next (csvReader)                                    ###skip the first header line

        for row in csvReader:
        
###
#       *** OLD CSV FORMAT ***          NO LONGER USED...  March-2018
#
#       Input Data:   ---- This is for DENSO Application CSV file for RSZW/LC Application
#       row[6]  = veh speed in meter
#       row[7]  = left turn signal - indication of start of WZ (Ref. Pt.)
#       row[11] = Lat
#       row[12] = Lon
#       row[13] = Heading
###
#       ---------------------------------------------
###
#       *** NEW CSV FORMAT ***
#
#       Input Data:   ---- This is NEW CSV file format for RSZW/LC Mapping Application ----
#       row[0]  =   GPSTime/GPSDate
#       row[1]  =   # of Satellites
#       row[2]  =   HDOP
#       row[3]  =   Latitude (Decimal Degrees)
#       row[4]  =   Longitude (Decimal Degrees)
#       row[5]  =   Altitude (meters)
#       row[6]  =   Speed (m/s)
#       row[7]  =   Heading (angle degrees)
#       row[8,9]=   Indicates a marker
#                   "RP" Reference Point - Use lat,lon,alt from the same line
#                   "LC" Lane Closed - followed by lane number
#                   "LC+RP" Lane Closed + Ref. Point - followed by lane number (if ref. point not indicated) 
#                   "LO" Lane Opened - followed by lane number
#                   "WP" Workers Present" - followed by TRUE/FALSE
#                   "WP+RP" Workers lcwpStatPresent + Ref. Point - WP + Ref. Point (if Ref. Pt is not indicated)   
#                   "Data Log" followed by TRUE (When FALSE, no data is logged. Previous record time shows when logging stopped)
#                   "Application Ended", followed by null
#
#
#       pathPt  =   An array to hold following for creating map points for approach and wz lanes with indications for WP and LC/LO
#                   index, speed, lat, lon, alt, heading, wp status, lane# and status
#
###
#       Process input line based on input format
#               = Flase, Old format                 NO LONGER IN USE...
#               = True, New format
###
#       --------------- OLD FORMAT NOT USED... -----------------------------------------

            if newFormat == False:                      #process input data from old format
                pathPt.insert(rowKt,list((round(float(row[6]),4),round(float(row[11]),8),   \
                                          round(float(row[12]),8),round(float(row[13]),3))))

                ##print (rowKt,pathPt[rowKt])            
###
#               Left Turn signal indicates start of WZ (Ref. Point) and also start of lane closure...
###
                if ((row[7] == "1") and (refPtIdx == 0)):
                    refPoint[0] = row[11]                       #lat
                    refPoint[1] = row[12]                       #lon
                    #print ("\n --- Reference Point = ",rowKt,refPoint)
                    refPtIdx = rowKt                            #got the ref point & Index
                pass                                            #end of ref. pt if stmt

                rowKt += 1                                      #process next record
            pass                                                #end of inputFormat == False (Old Format)

###
#       < < < < < < FOLLOWING NEW DATA FORMAT in USE > > > > > > 
#
#       process input row for new input data format...
###

            if newFormat == True:                               #process input data from new format
                      
###
#               Ref point marker. All lat/lon are represented in micro degrees. The collected lat/lon are in degrees.
#               The values are multiplied by 10000000 in the function where xml is being created...
#
###
        
                if gotRefPt == False and (row[8] == "RP" or row[8] == "LC+RP" or row[8] == "WP+RP"):    #ref pt marker support for old and new marker                 
                    refPoint[0] = row[3]                        #lat
                    refPoint[1] = row[4]                        #lon
                    refPoint[2] = row[5]                        #alt
                    appHeading  = row[7]                        #applicableHeading for XML file. Currently taken from the mapping vehilce heading at ref. point
                    refPtIdx    = rowKt                         #current input line (starts with 0)
                    gotRefPt    = True
                    #print ("\n --- Reference Point @ data point",refPtIdx,"(lat,Lon,Alt):",row[3], ",", row[4], ",", row[5])
                pass                                            #end of reference point
            
###
#               Lane closed marker
###
                if row[8] == "LC" or row[8] == "LC+RP":         #lane closed marker
                    lc = int(row[9])                            #lane number starts from 0
                    laneStat.insert(laneStatIdx,list((rowKt,lc,1,int(wzLen))))   #LC location, lane number, status flag, and offset from ref. pt.
                    laneStatIdx += 1                            #incr array index
                    #print ("laneStat for LC:", laneStat)
                    #print (" --- Lane #",lc,"Closed @ data point",rowKt,"(lat,Lon,Alt):",row[3],row[4],row[5])
                pass                                            #end of lc marker processed

###
#               Lane opened marker
###
                if row[8] == "LO":                              #lane opened marker
                    lc = int(row[9])                            #lane number starts from 0
                    laneStat.insert(laneStatIdx,list((rowKt,lc,0,int(wzLen))))   #LO location, lane number, status flag and offset from ref. pt.
                    laneStatIdx += 1                            #incr array index
                    #print ("laneStat for LO:", laneStat)
                    #print (" --- Lane #",lc,"Opened @ data point",rowKt,"(lat,Lon,Alt):",row[3],row[4],row[5])
                pass                                            #end of lc marker processed

###
#               Workers present / not present Marker
###
                if row[8] == "WP" or row[8] == "WP+RP":         #WP Flag
                    #print ("WP FOUND", row[8], row[9])
                    row[9] = row[9].upper()
                    if row[9] == "TRUE":  wp = 1
                    if row[9] == "FALSE": wp = 0
                    wpStat.insert(wpStatIdx,list((rowKt,wp,int(wzLen)))) #WP Status flag (converted from boolean to 0/1), location and offset from Ref Point
                    wpStatIdx += 1                              #incr index
                    stat = "Start"
                    if row[9] == "FALSE": stat = "End"
                    #print ("wpStat: ", wpStatIdx, wpStat)
                    #print (" --- *** ---",stat,"of workers present - ", row[9], "@ data point", rowKt,"(Lat,Lon,Alt):",row[3], row[4], row[5])
                pass          

###
#               Stop processing input file when hit "App Ended" marker...
###
                if row[8] != "App Ended":
###
#               Insert(save) vehicle path data point to pathPt array ...
###
                    pathPt.insert(rowKt,list((round(float(row[6]),4),round(float(row[3]),8),   \
                                             round(float(row[4]),8),round(float(row[5]),2),round(float(row[7]),4))))
                    ##print(rowKt,pathPt[rowKt])
                    rowKt += 1                                      #incr array pointer 
###
#                   add veh. speed. from Ref. Point till end of WZ to compute WZ Length...
###
                    if (refPtIdx != 0):
                        wzLen = wzLen + float(row[6])/sampleFreq    #add distance travel to wzLen
                    pass
                pass                                                #end of input data record
            pass                                                    #end of inputFormat == 1
        pass                                                        #end of input file = for loop

        ###print ("WZ LEN = ",wzLen)


###
#       Do I have closed/opened lanes?
#
#       print/log following in the calling routine...
###

        #if laneStatIdx > 1:                                     #have lane closures...NOTE: Index 0 location is dummy value...
        #    print ("\n ---Lane closed/opend offset from the Ref. Point in meters---")
        #    for L in range(1, laneStatIdx):
        #        stat = "Closed"
        #        if laneStat[L][2] == 0: stat = "Opened"
        #        print ("\t ---Lane:",laneStat[L][1],stat,"Offset from Ref. Point:",int(laneStat[L][3]),"meters")
        #    pass
        #pass                                            

###
#       Do for workers present/not present zone?          
###

        #if wpStatIdx > 0:                                       #have workers present/not present
        #    print ("\n ---Workers present/not present offset from the Ref. Point in meters---")
        #    for w in range(0, wpStatIdx):
        #        print ("\t ---Workers Present @ data point:",wpStat[w][0],wpStat[w][1],"Offset:",wpStat[w][2])
        #    pass
        #pass                                            
        

### totDataPt = len(list(pathPt))                               #total data points THIS VARIABLE IS NOT USED...

###
#   close the collected veh path data file
###
    csvFile.close()                                             #close the vehicle path data file

    atRefPoint[0] = refPtIdx
    atRefPoint[1] = int(wzLen)
    atRefPoint[2] = float(appHeading)
    
    ###print ("in Func...", atRefPoint)

    return  
