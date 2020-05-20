#!/usr/bin/env python3
###
#   Python functions do the following:
#
#   A. getLanePt    - Parse the vehicle path data array mapPt(appMapPt array for approach lanes and wzMapPt array for WZ lanes) to
#                     generate node points for lane geometry using right triangle method
#
#   A.1 getEndPoint - Calculates lat/lon for the end points from origin lat/lon, distance and bearing
#   A.2 getDist     - Compute distance between two lat/lon points in meters
###
#
#   By J. Parikh / Dec., 2017
#   Initial Ver 1.0
#
###

###
#   Import math library for computation
###

import math


###
#   The following function computes lat and lon for a point distance "d" meters and bearing (heading)from an origin
#   with known lat1, lat2.
#
#   See https://www.movable-type.co.uk/scripts/latlong.html for more detail.
#
#   The function computes node point lat/lon for the adjacent lane's lane width (d) apart and 90 degree bearing
#   from the vehicle path data lane.
#
#   lat1    = Latitude of origin
#   lon1    = Longitude of origin
#   bearing = Destination direction in degree
#   dist    = Destination distance in km
###

def getEndPoint(lat1,lon1,bearing,d):
    R = 6371.0*1000              #Radius of the Earth in meters
    brng = math.radians(bearing) #convert degrees to radians
    dist = d                     #convert distance in meters
    lat1 = math.radians(lat1)    #Current lat point converted to radians
    lon1 = math.radians(lon1)    #Current long point converted to radians
    lat2 = math.asin( math.sin(lat1)*math.cos(d/R) + math.cos(lat1)*math.sin(d/R)*math.cos(brng))
    lon2 = lon1 + math.atan2(math.sin(brng)*math.sin(d/R)*math.cos(lat1),math.cos(d/R)-math.sin(lat1)*math.sin(lat2))
    lat2 = math.degrees(lat2)
    lon2 = math.degrees(lon2)
    return lat2,lon2

### ------------------------------------------------------------------------------------

###
#   Following function computes distance between two lat/lon points in meters...
#   Added on - 8-28-2017...
###

def getDist(origin, destination):
    lat1, lon1 = origin                     #lat/lon of origin
    lat2, lon2 = destination                #lat/lon of dest    
    radius = 6371.0*1000                    #meters

    dlat = math.radians(lat2-lat1)          #in radians
    dlon = math.radians(lon2-lon1)
    
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c

    return d

def getChordLength(pt1, pt2):
    lat1 = math.radians(pt1[1])
    lon1 = math.radians(pt1[2])
    lat2 = math.radians(pt2[1])
    lon2 = math.radians(pt2[2])
    # lat1, lon1 = origin                     #lat/lon of origin
    # lat2, lon2 = destination                #lat/lon of dest    
    radius = 6371.0*1000                    #meters
    try:
        # This line very occasionally fails, out of range exception for math.acos
        d = radius*math.acos( math.cos(lat1)*math.cos(lat2)*math.cos(lon1-lon2) + math.sin(lat1)*math.sin(lat2) )
    except:
        dlat = lat2-lat1          #in radians
        dlon = lon2-lon1
        
        a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
            * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        d = radius * c

    return d

### ------------------------------------------------------------------------------------


###
#   For Approach Lanes: starting from the ref. point go back upto 1st data point and construct map points for approach lane
#   For WZ lanes: starting from the ref. point process all points in pathPt array until the end
#
#   Equidistant Method: *** NOT USED *** -  Select data point for building the array by computing specified distance (for equidistance)
#                       between points for both approach and wz maps. This method does not work for map matching for curved lanes since the
#                       the data points may fall outside the map matching bounding box on curved lanes.
#
#   Rt. Triangle Method: *** IN USE *** - Points are selected based on change in heading angle which forms a rectangle triangle.
#                       A rt. angle triangle is formulated between two points. If the computed height is > half the lane width,
#                       the node point is selected for map node point and so on. This technique of selecting node point provides
#                       better map matching. 
#
###


###
#   laneType    1=Approach Lanes, 2=WZ Lanes
#   pathPt      Array containing vehicle path data points
#   mapPt       Constructed array of node points
#   laneWidth   from user input in meters
#   lanePad     lane padding in meterslaneStat
#   refPtIdx    location index in pathPt array for reference point
#   mapPtDist   distance between node point - used for generating node points based on equidistance method
#               not used in the algorithm any more, right triangle method is used
#   laneStat    array to indicate lane closed/open status different locations
#   wpStat      array to indicate workers present/not present statatus
#   dataLane    lane on which the vehicle was driven for collecting vehicle path data
###

def insertMapPt(mapPt, pathPt, elementPos, tLanes, laneWidth, dL, lcwpStat, distVec):
    
    lla_ls_hwp  = [0]*((4*(tLanes))+3)                  #define llah list - 4 elements per node data point (lat,lon,alt,lo/lc)+heading+dist
                                                        #LO/LC (0/1), WP (0/1) status added on 11/13/2017

    bearingPP = pathPt[elementPos][4]            #bearing (heading) of the path point
    latPP     = pathPt[elementPos][1]            #lat/lon    
    lonPP     = pathPt[elementPos][2]
    altPP     = pathPt[elementPos][3]

###
#           now loop through all lanes as specified by the total number of lanes in the WZ for constructing node points for
#           adjacent lanes...
#
#           It is assumed that number of approach lanes are the same as WZ lanes.
###

    ln = 0
    while ln < tLanes:                      #loop through all lanes - Tot lanes are tLanes
        lW = abs(ln-dL)*laneWidth           #calculate next lane offset from the lane for which data is collected
        ##print (ln, lW)

        if ln == dL:                        #ln same as lane on which data was collected
            lla_ls_hwp[ln*4+0] = latPP      #lat, lon, alt, lcloStat for the lane
            lla_ls_hwp[ln*4+1] = lonPP
            lla_ls_hwp[ln*4+2] = altPP
            lla_ls_hwp[ln*4+3] = lcwpStat[ln]    
        pass

        if ln != dL:                        #Adjacent lanes only - not the data collected lane...
            if ln < dL:
                bearing = bearingPP - 90    #lane left to dataLane
            else:
                bearing = bearingPP + 90    #lane right to the dataLane
            pass

            ll = getEndPoint(latPP,lonPP,bearing,lW)    #get lat/lon for the point which is laneWidth apart from the data collected lane
            lla_ls_hwp[ln*4+0] = round(ll[0],8)         #computed lat of the adjacent lane...
            lla_ls_hwp[ln*4+1] = round(ll[1],8)         #computed lon of the adjacent lane   
            lla_ls_hwp[ln*4+2] = pathPt[elementPos][3]       #same altitude
            lla_ls_hwp[ln*4+3] = lcwpStat[ln]           #lc/lo Status of the lane at the node point                       
                                                        #end of if lineType
        pass                                                #end of if ln!= dL   
###
#            
#           Add current heading (bearing) in the last column for use in 
#           drawing rectangular bounding polygon on Google map in javaScript application for visualization...
#
#           Added: distance of selected nodepoint from previous node for future use...
#                  May 21, 2018
#
#           Note:   Old method was calculating "dist" as distance traversed by the vehicle.
#                   New method computes "distVec" as distance vector (produces very minor difference...)
#
###
        if ln == tLanes - 1:                        #if the current ln same as the last lane
            lla_ls_hwp[ln*4+4] = bearingPP          #add heading in the table
            lla_ls_hwp[ln*4+5] = lcwpStat[tLanes]   #add WP Status for the node in the table
        ####lla_ls_hwp[ln*4+6] = int(dist)          #add computed distVec, distance in meters from prev. node point in the table for future use
            lla_ls_hwp[ln*4+6] = int(distVec)       #add computed distVec, distance in meters from prev. node point in the table for future use
            ##print ("bearingPP: ", refPt, bearingPP)
        pass                                        #end of if ln
                
        ln = ln + 1                                 #next lane
    pass                                            #end of while loop

###
#           Store computed lat,lon,alt,lcloStat, for each node for each lane + last two elements in table heading and WP flag + distVec (dist from prev. node)
###

    mapPt.append(list(lla_ls_hwp))               #insert constructed lla_ls_hwp list for each node for each lane in mapPt array

def getLanePt(laneType,pathPt,mapPt,laneWidth,lanePad,refPtIdx,mapPtDist,laneStat,wpStat,dataLane,wzMapLen):

    
###
#   Total number of lanes are in loc [0][0] in laneStat array
###
    totDataPt = (len(list(pathPt)))                     #total data points (till end of array)
    tLanes  = laneStat[0][0]                            #total number of lanes...

    lcwpStat    = [0]*(tLanes+1)                        #Temporary list to store status of each node for each lane + WP state for the node
    dL      = dataLane - 1                              #set lane number starting 0 as the left most lane                             
    # bearingRP   = pathPt[refPt][4]                      #bearing (heading) at the reference point
    # latRP       = pathPt[refPt][1]                      #lat/lon/alt    
    # lonRP       = pathPt[refPt][2]
    # altRP       = pathPt[refPt][3]
    # ctrHead     = pathPt[refPt][4]                      #current heading
    distVec = 0
    stopIndex = 0
    startIndex = 0
    actualError = 0

    ALLOWABLEERROR = .5
    SMALLDELTAPHI = 0.01
    CHORDLENGTHTHRESHOLD = 500
    MAXESTIMATEDRADIUS = 8388607 #7FFFFF

    if laneType == 1:
        if refPtIdx < 3:
            for i in range(0, refPtIdx):
                insertMapPt(mapPt, pathPt, i, tLanes, laneWidth, dL, lcwpStat, distVec)
                distVec += pathPt[i][0]/10
                # Rework to use actualChordLength
                return
        else:
            stopIndex = refPtIdx
    else:
        stopIndex = totDataPt
        startIndex = refPtIdx

    # Step 1
    i = startIndex + 2
    Pstarting = pathPt[i-2]
    Pprevious = pathPt[i-1]
    Pnext = pathPt[i]
    totalDist = 0
    incrementDist = 0
    insertMapPt(mapPt, pathPt, i-2, tLanes, laneWidth, dL, lcwpStat, distVec)

    while i < stopIndex:
    # Step A
        requiredNode  = False                                 #set to False
        if laneType == 2:                                   #WZ Lane
            for lnStat in range(1, len(laneStat)):          #total number of lc/lo/wp are length of laneStat-1
                if laneStat[lnStat][0] == i-1:            #got LC/LO location
                    requiredNode = True                       #set to True
                    lcwpStat[laneStat[lnStat][1]-1] = laneStat[lnStat][2]       #get value from laneStat 
                pass
            pass

            for wpZone in range(0, len(wpStat)):
                if wpStat[wpZone][0] == i-1:                      #got WP Zone True/False
                    requiredNode = True                               #set to True 
                    lcwpStat[len(lcwpStat)-1] = wpStat[wpZone][1]   #toggle WP Zone status
                pass
            pass
        pass

    # Step 2
        eval = True
        actualChordLength = getChordLength(Pstarting, Pnext)
        if actualChordLength > CHORDLENGTHTHRESHOLD:
            actualError = ALLOWABLEERROR + 1
            eval = False
            # Go to step 7

    # Step 3
        deltaHeadings = Pnext[4] - Pstarting[4]
        deltaHeadings = deltaHeadings % 360
        deltaHeadings = abs(math.radians(deltaHeadings))

    # Step 4
        if deltaHeadings < SMALLDELTAPHI and eval:
            actualError = 0
            estimatedRadius = MAXESTIMATEDRADIUS
            eval = False
            # Go to step 8
        elif eval:
            estimatedRadius = actualChordLength/(2*math.sin(deltaHeadings/2))

    # Step 5
        d = estimatedRadius*math.cos(deltaHeadings/2)

    # Step 6
        if eval: #Allow step 4 to maintain 0 actualError
            actualError = estimatedRadius - d

    # Step 7
        if actualError > ALLOWABLEERROR or requiredNode:
            incrementDist = actualChordLength
            totalDist += incrementDist
            insertMapPt(mapPt, pathPt, i-1, tLanes, laneWidth, dL, lcwpStat, totalDist)

            Pstarting = pathPt[i-1]
            Pprevious = pathPt[i]
            if i != stopIndex-1:
                Pnext = pathPt[i+1]
            i += 1
    # Step 8
        else:
            if i != stopIndex-1:
                Pnext = pathPt[i+1]
            Pprevious = pathPt[i]
            i += 1

        if i == stopIndex:
            incrementDist = actualChordLength
            totalDist += incrementDist
            insertMapPt(mapPt, pathPt, i-1, tLanes, laneWidth, dL, lcwpStat, totalDist)
    # Step 9
        # Integrated into step 7
        
    if laneType == 1:
        wzMapLen[0] = totalDist
    else:
        wzMapLen[1] = totalDist

# def getLanePt(laneType,pathPt,mapPt,laneWidth,lanePad,refPtIdx,mapPtDist,laneStat,wpStat,dataLane,wzMapLen):

#     ###if laneType == 1: print("\n ---Constructing Node Points for Approach Lanes---")
#     ###if laneType == 2: print(" ---Constructing Node Points for Work Zone Lanes---")

#     totDataPt = (len(list(pathPt)))                     #total data points (till end of array)
#     if laneType == 1:                                   #"laneType" 1 = Approach lanes, 2 = wz Lanes 
#         incr = -1                                       #starting from the ref. point to the first data point for approach lanes                            
#     else:
#         incr = 1                                        #starting from the ref. point to the last data point for wz lanes
   
#     radMult = 3.14159265/180.0                          #to radian    
#     dL      = dataLane - 1                              #set lane number starting 0 as the left most lane                             
#     refPt   = refPtIdx                                  #starting from the ref. point to the first data point for WZ lanes
#     distTh  = 512.0                                     #max dist between waypoints (node points)
#     dist    = 0                                         #cumulative dist bet data points   
#     Kt      = 0
#     distVecTot = 0

# ###
# #
# #   Test of computation of height of a rt. triangle based on direct vector distance between the current node point and
# #   selected vahicle path point and NOT using traversed distance...
# #
# #   Testing on May 25, 2018
# #
# ###

#     originLL = pathPt[refPt][1], pathPt[refPt][2]
   
# ###
# #   Set starting data point for approach lane as refPoint - 1.
# ###

#     totDataPt = (len(list(pathPt)))                     #total data points (till end of array)
#     if laneType == 1:                                   #"laneType" 1 = Approach lanes, 2 = wz Lanes 
#         incr = -1                                       #starting from the ref. point to the first data point for approach lanes
#         refPt = refPt + incr
#     else:
#         incr = 1                                        #starting from the ref. point to the last data point for wz lanes
    
# ###
# #   Total number of lanes are in loc [0][0] in laneStat array
# ###

#     tLanes  = laneStat[0][0]                            #total number of lanes...

# ###
# #   
# #   Following "lla_ls_hwp" array to store:
# #       lat, lon, alt, laneStaus (open/close) for each lane +
# #       vehicleheading +
# #       workers present or not (1/0) +
# #       distance in meters of current selected node from the previous node for future use...
# #
# #   For example, in case of three lanes, it would have 15 elements that would look like following for lane 1,2 and 3
# #       lat1,lon1,atl1,lo/lc,lat2,lon2,alt2,lo/lc,lat3,lon3,alt3,lo/lc,heading,wp(0/1),dist
# #                              
# #   Added on Nov. 13, 2017
# #   Revised on May 21, 2018 
# #
# ###

#     lla_ls_hwp  = [0]*((4*(tLanes))+3)                  #define llah list - 4 elements per node data point (lat,lon,alt,lo/lc)+heading+dist
#                                                         #LO/LC (0/1), WP (0/1) status added on 11/13/2017
#                                                         #dist added on May 21, 2018
#     lcwpStat    = [0]*(tLanes+1)                        #Temporary list to store status of each node for each lane + WP state for the node

# ###                           
# #
# #   First get lat/lon/alt and bearing from the reference point
# #
# ###
#     bearingRP   = pathPt[refPt][4]                      #bearing (heading) at the reference point
#     latRP       = pathPt[refPt][1]                      #lat/lon/alt    
#     lonRP       = pathPt[refPt][2]
#     altRP       = pathPt[refPt][3]
#     ctrHead     = pathPt[refPt][4]                      #current heading
    
# ###
# #   if laneType is 1, create map data points for approach lanes (all lanes).
# #   if laneType is 2, create map data points for WZ lanes (all lanes).
# ###

#     lookAhead = 8                                       #look at 5 data points beyond the selected node point based on computed
#                                                         #height of the right angled triangle
#     while refPt >= 0 and refPt < totDataPt: # Stop case for forwards and backwards directions, either 
#         if (refPt != refPtIdx):                         #first point is the same as reference point, dist is 0
#             dist   = dist+(pathPt[refPt][0])/10.0       #cumulative vehicle travel distance in meters between data points
#         pass
       
#         headDiff = abs(ctrHead - pathPt[refPt][4])      #diff in heading between the current point (ctrHead) and the of current point
# ###
# #       Adjust the "headDiff" in degrees when the heading has crossed the 0 degree point
# #
# ###
#         if headDiff > 180:
#             headDiff = 360.0 - headDiff                 #vehicle heading crossed 0 degree...
#         pass

# ###
# #       Compute the height of the right triangle - headDiff = angle in degrees between the hypotenuse and base of right triangle
# #       (dist bet last slected waypoint and current vehicle path data point).   
# ###

#         ht = dist*math.tan(headDiff*radMult)            #compute "ht" of a rt. angle triangle from angle bet. adj. side &

# ###
# #   Test method using direct vector between two points...
# ###
#         destLL  = pathPt[refPt][1], pathPt[refPt][2]    #lat/lon of current path point
#         distVec = getDist(originLL, destLL)             #computed distance vector in meters  
#         htNew   = distVec*math.tan(headDiff*radMult)    #computed height

#        # if (refPt > 339 and refPt < 343):
#        #     print ("refPt, originLL, destLL:", refPt,originLL,destLL)
#        #    print ("refpt, headDiff, dist, distVec, ht, htNew = ", refPt,round(headDiff,2),round(dist,2),round(distVec,2),round(ht,2),round(htNew,2))
#        # pass            
        
# ###
# #       If the computed height is grater than the half lanewidth, see if next 8 points also have the height greater than the
# #           half lanewidth, then consider the current point for waypoint (node point)

# #       Otherwise - consider the current point as outlier and ignore it.
# ###
#         gotHt = False
#         htKt  = 0
# #-#        if (ht > (laneWidth/2.0)+lanePad) and (refPt < totDataPt-lookAhead) and (refPt > lookAhead):  #OLD way computed ht, based on cumulative distance for base
# #-#
# #-#            distNew = dist                              #current dist to distNew for lookAhead data points
# #-#            for jk in range (1,lookAhead+1):            #look at the next few points
# #-#                distNew     = distNew+(pathPt[refPt+(incr*jk)][0])/10.0
# #-#                headDiff    = abs(ctrHead - pathPt[refPt+(incr*jk)][4])
# #-#            
# #-#                if headDiff > 180:
# #-#                    headDiff = 360.0 - headDiff         #vehicle heading crossed 0 degree...
# #-#                pass
# #-# 
# #-#                htNext = distNew*math.tan(headDiff*radMult) #compute for next data point, "ht" of a rt. angle triangle from angle 
# #-#                                                            #bet. adj. side & hypotenuse and dist = adj. side (base of the triangle)            
# #-#                if (htNext > (laneWidth/2.0)+lanePad):
# #-#                    htKt = htKt + 1
# #-#                    #print ("htKt at:", htKt,refPt+(incr*jk),dist,htNext,headDiff)
# #-#                pass
# #-#            pass


# ###
# #       Save current distVec    
# ###
        
#         if (htNew > (laneWidth/2.0)+lanePad) and (refPt < totDataPt-lookAhead) and (refPt > lookAhead): #new way computed ht, based on distance vector for base    
#             distVecNew = distVec                                                        #current dist to distNew for lookAhead data points
#             for jk in range (1,lookAhead+1):                                            #look at the next few points

#                 destLLNew   = pathPt[refPt+(incr*jk)][1], pathPt[refPt+(incr*jk)][2]    #lat/lon of current path point
#                 distVecNew  = getDist(originLL, destLLNew)                              #computed distance vector    
                
#                 headDiff    = abs(ctrHead - pathPt[refPt+(incr*jk)][4])
            
#                 if headDiff > 180:
#                     headDiff = 360.0 - headDiff                                         #vehicle heading crossed 0 degree...
#                 pass

#                 htNext = distVecNew*math.tan(headDiff*radMult)  #compute for next data point, "ht" for rt. angle triangle from angle 
#                                                                 #bet. adj. side & hypotenuse and dist = adj. side (base of the triangle)            
#                 if (htNext > (laneWidth/2.0)+lanePad):
#                     htKt = htKt + 1
#                     ##print ("ht count at:", htKt,refPt,jk,round(distVecNew,3),round(htNext,3),round(headDiff,3))
#                 pass
#             pass

            
#             #refPt = refPt + incr
#             if htKt == lookAhead:                           #if all lookAhead points height is > half lane width+lane pad
#                 gotHt = True
#                 refPt = refPt - incr                        #set waypoint (node point) location as the previous refPt since the current
#                                                             #refPt has busted the triangle's "ht" requirement
#                 #print ("got HT:",laneType,refPt,round(dist,2))
#             pass
#         pass
        
# ###
# #
# #       Following conditional statement determines when to select node point for mapping.
# #       When either of the following criteria is true, node point is selected:
# #
# #       1. If computed height of the formed right angle triangle from the refPt to the current point is > half lane width+lane padding,
# #       2. Computed distance from the refPt to the current point is < "distTh" (32767cm as set in SAE J2735 for node offset) 
# #       3. Forced node point when either:
# #           i. Lane is closed or open is indicated (change in lane status)
# #           ii Workers are present/not present is indicated (wp state change)
# #       4. First data point as first node point   
# #
# ###
#         #print (refPt, Kt, ctrHead, headDiff, dist, ht)

# ###
# #       Following added on Oct. 25, 2017 to force a node point support when:
# #           1. Change in lane status (close or open)
# #           2. Workers present/not present in the work zone.
# #       
# #       Additional attibutes can be specified to these nodes as defined in the new version of BIM (RSM)
# #
# #       The laneStat list contains array index where Lane Close/Open or WP TRUE/FALSE has started
# #
# ###################################
# ####
# ####    DO NOT LOOP - get one value at a time and see if it's same as refPt. if so, set it to true and change to next value
# ####
# ####    Following logic applies ONLY for WZ lane data points and NOT for approach lane data points
# ####
# ###################################

                
#         gotNodeLoc  = False                                 #set to False
#         if laneType == 2:                                   #WZ Lane
#             for lnStat in range(1, len(laneStat)):          #total number of lc/lo/wp are length of laneStat-1
#                 if laneStat[lnStat][0] == refPt:            #got LC/LO location
#                     gotNodeLoc = True                       #set to True

#                     ##
#                     ##print ("laneStat[lnStat][1] and lnStat = ", laneStat[lnStat][1], lnStat)
#                     ##print ("laneStat[lnStat][2] and lnStat = ", laneStat[lnStat][2], lnStat, lcwpStat) 
#                     ##    
#                     lcwpStat[laneStat[lnStat][1]-1] = laneStat[lnStat][2]       #get value from laneStat 
#                     #print ("\n***LC/LO @ current pointer:",laneStat[lnStat][0],laneStat[lnStat][1],lcwpStat,lnStat)
#                 pass
#             pass

#             for wpZone in range(0, len(wpStat)):
#                 if wpStat[wpZone][0] == refPt:                      #got WP Zone True/False
#                     gotNodeLoc = True                               #set to True 
#                     lcwpStat[len(lcwpStat)-1] = wpStat[wpZone][1]   #toggle WP Zone status
#                     ##print ("\n***WP @ current pointer:",wpStat[wpZone][0],laneStat[lnStat][1],lcwpStat,lnStat)
#                 pass
#             pass
#         pass
     
# ####
# #       The following conditional segment sets the node point for mapping if anyone of the following is true...
# #
# #       1. Compute ht of the rt. angle triangle is > half the lane width + the lane pad
# #       2. Computed distance from the previous selected node point to the current point is > distTh (in J2735 XY offset must be < 32767cm).
# #       3. If this is the first node.
# #       4. Newly added on Oct. 25, 2017 - the marked point is where either Lane close or open starts or workers presence indicator is True or False
# #          These nodes will have additional attributes attached such as Taper left/right to indicate start/end of lane closure and workers present zones
# ##
# ##      Following logic moved from up above in the code to this location on... 12-6-2017 
# #
# #       Forced 1st data point(for approach lane) and last data point(for WZ lane) as node point (waypoint) for mapping ...
# ####

#         if refPt == totDataPt-1 or refPt == 1:
#             #print ("last refPt: ", refPt, totDataPt)
#             gotNodeLoc = True
#         pass
        
# ###
# #       if any of the following is true...
# ###

#         if (gotHt == True) or (dist > distTh) or (Kt == 0) or (gotNodeLoc == True):  #if any one of them is true
        
#            ### print ("*** After one of is TRUE ***", refPt, Kt, ctrHead, headDiff, next1headDiff, next2headDiff,dist, ht, gotNodeLoc)                       
# ###
# #           First get lat/lon/alt and bearing from the current data point
# ###

#             bearingPP = pathPt[refPt][4]            #bearing (heading) of the path point
#             latPP     = pathPt[refPt][1]            #lat/lon    
#             lonPP     = pathPt[refPt][2]
#             altPP     = pathPt[refPt][3] 
# ###
# #           now loop through all lanes as specified by the total number of lanes in the WZ for constructing node points for
# #           adjacent lanes...
# #
# #           It is assumed that number of approach lanes are the same as WZ lanes.
# ###            
#             ln = 0
#             while ln < tLanes:                      #loop through all lanes - Tot lanes are tLanes
#                 lW = abs(ln-dL)*laneWidth           #calculate next lane offset from the lane for which data is collected
#                 ##print (ln, lW)

#                 if ln == dL:                        #ln same as lane on which data was collected
#                     lla_ls_hwp[ln*4+0] = latPP      #lat, lon, alt, lcloStat for the lane
#                     lla_ls_hwp[ln*4+1] = lonPP
#                     lla_ls_hwp[ln*4+2] = altPP
#                     lla_ls_hwp[ln*4+3] = lcwpStat[ln]    
#                 pass
                    
#                 if ln != dL:                        #Adjacent lanes only - not the data collected lane...
#                     if ln < dL:
#                         bearing = bearingPP - 90    #lane left to dataLane
#                     else:
#                         bearing = bearingPP + 90    #lane right to the dataLane
#                     pass
                
                
#                     if laneType == 1 or laneType == 2:
#                         ll = getEndPoint(latPP,lonPP,bearing,lW)    #get lat/lon for the point which is laneWidth apart from the data collected lane
#                         lla_ls_hwp[ln*4+0] = round(ll[0],8)         #computed lat of the adjacent lane...
#                         lla_ls_hwp[ln*4+1] = round(ll[1],8)         #computed lon of the adjacent lane   
#                         lla_ls_hwp[ln*4+2] = pathPt[refPt][3]       #same altitude
#                         lla_ls_hwp[ln*4+3] = lcwpStat[ln]           #lc/lo Status of the lane at the node point                       
#                     pass                                            #end of if lineType
#                 pass                                                #end of if ln!= dL   
# ###
# #            
# #           Add current heading (bearing) in the last column for use in 
# #           drawing rectangular bounding polygon on Google map in javaScript application for visualization...
# #
# #           Added: distance of selected nodepoint from previous node for future use...
# #                  May 21, 2018
# #
# #           Note:   Old method was calculating "dist" as distance traversed by the vehicle.
# #                   New method computes "distVec" as distance vector (produces very minor difference...)
# #
# ###
#                 if ln == tLanes - 1:                        #if the current ln same as the last lane
#                     lla_ls_hwp[ln*4+4] = bearingPP          #add heading in the table
#                     lla_ls_hwp[ln*4+5] = lcwpStat[tLanes]   #add WP Status for the node in the table
#                 ####lla_ls_hwp[ln*4+6] = int(dist)          #add computed distVec, distance in meters from prev. node point in the table for future use
#                     lla_ls_hwp[ln*4+6] = int(distVec)       #add computed distVec, distance in meters from prev. node point in the table for future use
#                     ##print ("bearingPP: ", refPt, bearingPP)
#                 pass                                        #end of if ln
                        
#                 ln = ln + 1                                 #next lane
#             pass                                            #end of while loop

# ###
# #           Store computed lat,lon,alt,lcloStat, for each node for each lane + last two elements in table heading and WP flag + distVec (dist from prev. node)
# ###
 
#             mapPt.insert(Kt,list(lla_ls_hwp))               #insert constructed lla_ls_hwp list for each node for each lane in mapPt array
#             ##print ("refPt: ",refPt,"Kt: ",Kt, "Ln: ",ln)
#             ##print ("Lat/Lon/Alt/lcloStat,Head,wpStat,dist: ",lla_ls_hwp)

#             distVecTot = distVecTot+distVec
                    
#             dist = 0                                        #reset dist
#             originLL = pathPt[refPt][1], pathPt[refPt][2]   #reset originLL for next vector calc...
#             ctrHead = pathPt[refPt][4]                      #reset current heading
#             Kt = Kt + 1

#         pass                                                #END OF if node selected...
  
#         refPt = refPt + incr                                #process next record (incr is -1) for approach, +1 for WZ lanes

#     pass                                                    #end of while loop

#     if laneType == 1:
#         wzMapLen[0] = distVecTot
#     else:
#         wzMapLen[1] = distVecTot

#     return                                                 #end of function...

