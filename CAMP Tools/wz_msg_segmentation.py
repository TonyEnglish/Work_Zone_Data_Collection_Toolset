#!/usr/bin/env python3
###
#   Python module to determine number of message segments required for the message builder:
###
### ------------------------------------------------------------------------------------------------------------------
###
#
#   Following function determines required number of RSM (WZ) map message segmentations 
#	The RSM message is split in number of segments to support very long and complex work zone map where it is likely that the
#       message payload would be either greater than PDU requirement or number of nodes (waypoints) to represent lane is greater than 63.
#       It is required in the ASN.1 definition that the number of nodes to represent lane geometry must be between 2..63
###     _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
###
#       Under following conditions, the generated wzLane map nodes are split to generate multiple message segments:
#       1.  When number of nodes generated per lane exceeds 63 (2..63)
#       2.  When expected UPER encoded message size exceeds 1100 octets (PDU Upper limit is 1500) +
#           space for header, security and other stuff for about 400 octets
#
#       The point of segmentation is based on:
#       1.  1 node is equivalent to approx. 11 octets when nodes are represented as xyz_offset,
#             therefore total 100 nodes per message segment makes map data approx. 1100 octets
#       2.  1 node is equivalent to approx. 15 octets when nodes are represented as 3d_absolute of lat, lon, alt,
#             therefore total 73 nodes per message segment
#
#   The message segmentation is carried out as follows:
#       All approach lane nodes per lane PLUS at least 2 nodes (as per J2735, nodes must be between 2..63)
#       from the WZ lane must fit in the first segment.
#       IF NOT, alternative action is taken as outlined below...
#
###

###
#	Created by J. Parikh @ CAMP
#	May, 2018
#       Updated - Jan. 2019 to address when approach lane nodes/lane is >= max nodes/lane
#
###

###
#   Import math library for computation
###

import  math                                            #math library for math functions

def buildMsgSegNodeList (appNodesPerLane,wzNodesPerLane,totLanes):

###
#       Data elements passed from the caller for determining message segmentation...
###
#       appNodesPerLane = Approach lane nodes per lane - len(appMapPt)
#       wzNodesPerLane  = wz lane nodes per lane - len(wzMapPt)
#       totLanes        = Total number of lanes
###
#
#       The function builds a list as follows and returns to the caller...
#
#   NOTE: First node for all lanes of the the message segment is the same as the last node for all lanes of the
#         previous segment thus provides node overlaps to maintain continuity in map matching.
#
#       Added: June 18, 2018  
#
#       nplList[0]  = (totMsgSeg, maxNPL)
#       nplList[1]  = (1,startNode for appLane,endNode of appLane)    --- NOTE --- approach lane nodes ARE NOT SPLIT in multiple msg Seg.
#       nplList[2]  = (segNum,startNode for wzLane(same as endNode of previous segment),endNode of wzLane)
#               ...
#               ...
#       nplList[n]  = (segNum,startNode for wzLane(same as endNode of previous segment),endNode of wzLane)
#       
###
#       Following assumes that the nodes are represented in xyz_offset and NOT in 3d_absolute format
#
#	Local variables...
###

    nplList     = []                                            #list to contain constructed message segments   
    msgSizeOct  = 1100                                          #msg size in octets
    nodeSizeOct = 11                                            #node size in octets
    maxNodesPerMsg  = int(msgSizeOct / nodeSizeOct)             #max nodes per message
    maxNodesPerLane = int(maxNodesPerMsg / totLanes)            #max nodes per lane based on xyz_offset for node representation

###
#   Address following three possibilities...
#   1. maxNodesPerLane > appNodesPerLane        CONTINUE PROCESSING....
#   2. maxNodesPerLane = appNodesPerLane        add 2 (bet 2..63) to maxNodesPerLane so that the first seg has at least 2 WZ node...
#   3. maxNodesPerLane < appNodesPerLane        STOP with WARNING... MESSAGE SEGMENTATION is Failed...
#                                               reduce mapped approach lane length to generate nodes below maxNodePerLane
###
#   Approach lane nodes are always in the msg segment #1.
#   It is assumed that total number of nodes per lane for approach will be less than maxNodesPerLane and fit in the first msg segment 
###

    if appNodesPerLane > maxNodesPerLane:
       # print ("*** ERROR ***")
       # print ("*** ERROR *** approach lane nodes:",appNodesPerLane,"must be less than",maxNodesPerLane," Max nodes per lane for a message segment")
       # print ("*** ERROR *** the s/w will place all approach lane nodes in the first segment...")
       # print ("*** ERROR *** this may exceed message PDU size of 1500 octets...\n")

###     Above message is in log file... Set totMsgSeg to -1 indicating error in segmentation...

        totMsgSeg = -1
        nplList.insert(0,list((totMsgSeg,maxNodesPerLane)))
        nplList.insert(1,list((1,1,appNodesPerLane)))           #Seg number, start node number, end node number for the seg

        return nplList                                          #no further processing, return to caller..
    pass


###
#   If nodes per approach lane is same as the computed max nodes per lane, do following...
###

    if (maxNodesPerLane == appNodesPerLane):
        maxNodesPerLane += 2;                                   #Two Additional node per lane will not bust the msgSize
        maxNodesPerMsg = maxNodesPerMsg + totLanes*2            #add two additional node per lane
    pass
    
###
#   Compute total number of nodes per msg segment comprising of starting with approach followed by wz lanes
#
#   ALL computations below is based on max number of nodes/lane for each message segment.
#   Max nodes/lane is derived above from number of lanes in wz mapping
###

    totNodes    = (appNodesPerLane + wzNodesPerLane) * totLanes
    totMsgSeg   = math.ceil(totNodes/maxNodesPerMsg)


    ####print ("nodes per lane and per meg: ", maxNodesPerLane, maxNodesPerMsg)

###
#   Add a segment to support overlapping nodes in the message
#
   #-# if (totMsgSeg*maxNodesPerMsg) == totNodes:                  #add an additional segment for overlap nodes
   #-#     totMsgSeg = totMsgSeg+1                                 #add one more seg due to overlap...
    
        
    nplList.insert(0,list((totMsgSeg,maxNodesPerLane)))         #total number of msg segments, max nodes per lane



###
#   Continue on...
###

    nplList.insert(1,list((1,1,appNodesPerLane)))               #Seg number, start node number, end node number for the seg

###
#   Determine wzLane nodes per msg segment
#   The 1st messgae to hold ALL approach lane (appLane) nodes
#   The 1st message segment to also hold nodes for the work zone lane up to the maxNodesPerLane
#   The last message segment to have the remainder nodes for wzLanes = wzNPL - wzNodes in 1st seg + wzNPSeg*(totMsgSeg-2)
#   wzNPSeg = wz nodes per segment per lane...
###

    wzNodesPerMsgSeg = int(maxNodesPerLane - appNodesPerLane)    
    wzNodesRemain = wzNodesPerLane - wzNodesPerMsgSeg           #no of wz node remaining

    if wzNodesRemain <= 0:
        wzNodesPerMsgSeg = wzNodesPerLane                       #all wz nodes for a lane
    pass
    
    nplList.insert(2,list((1,1,wzNodesPerMsgSeg)))          #Seg #, No of wz lane nodes, starting node number

    ##print ("wz Remaining nodes after 1st seg:",wzNodesPerMsgSeg,wzNodesRemain)

    idx = 3                                                     #First 2 locations in nplList has 1) #of segments and 2)max nodes per lane
    wzStartNode = wzNodesPerMsgSeg
    
    if wzNodesRemain < maxNodesPerLane:                         
        wzEndNode = wzStartNode + wzNodesRemain - 1             #compute the end node
        ##print (wzNodesRemain, maxNodesPerLane, wzEndNode)
    else:
        wzEndNode = wzStartNode + maxNodesPerLane - 1
        ##print (wzEndNode)
    pass
        
   

    while idx <= totMsgSeg+1:

        ##print ("start & End node:", wzStartNode, wzEndNode)

        if wzNodesRemain > maxNodesPerLane:
            ##nplList.insert(idx,list((idx-1,wzStartNode+1,wzEndNode))) #seg #, wz nodes per lane, wz start node #
            nplList.insert(idx,list((idx-1,wzStartNode,wzEndNode)))     #seg #, wz nodes per lane, wz start node #
            wzStartNode = wzStartNode + maxNodesPerLane - 1             #next start node overlaps with previous end node
            wzEndNode   = wzStartNode + maxNodesPerLane - 1             #end node will be 1 less due to overlap
            wzNodesRemain = wzNodesRemain - maxNodesPerLane + 1         #node remains nodes
        else:
            wzEndNode = wzStartNode + wzNodesRemain
            ##nplList.insert(idx,list((idx-1,wzStartNode+1,wzEndNode))) #seg #, wz nodes per lane, wz start node #
            nplList.insert(idx,list((idx-1,wzStartNode,wzEndNode)))     #seg #, wz nodes per lane, wz start node #
        pass
    
        idx = idx+1
    pass

    ##print ("App and WZ nodes per lane and total lanes",appNodesPerLane,wzNodesPerLane,totLanes)
    ##print ("totNodes, totMsgSeg, nodesPerLane",totNodes,totMsgSeg,maxNodesPerLane)

    return nplList


