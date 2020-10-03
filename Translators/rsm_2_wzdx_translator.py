import xml.etree.ElementTree as ET 
import json
from datetime import datetime
import uuid
import random
import string

# info = {}
# info['feed_info_id'] = feed_info_id
# info['road_name'] = roadName
# info['road_number'] = roadNumber
# info['description'] = wzDesc
# info['direction'] = direction
# info['beginning_cross_street'] = beginningCrossStreet
# info['ending_cross_street'] = endingCrossStreet
# info['beginning_milepost'] = beginningMilepost
# info['ending_milepost'] = endingMilepost
# info['issuing_organization'] = issuingOrganization
# info['creation_date'] = creationDate
# info['update_date'] = updateDate
# info['event_status'] = eventStatus
# info['beginning_accuracy'] = beginingAccuracy
# info['ending_accuracy'] = endingAccuracy
# info['start_date_accuracy'] = startDateAccuracy
# info['end_date_accuracy'] = endDateAccuracy

# info['metadata'] = {}
# info['metadata']['wz_location_method'] = wzLocationMethod
# info['metadata']['lrs_type'] = lrsType
# info['metadata']['location_verify_method'] = locationVerifyMethod
# if dataFeedFrequencyUpdate:
#     info['metadata']['datafeed_frequency_update'] = dataFeedFrequencyUpdate
# info['metadata']['timestamp_metadata_update'] = timestampMetadataUpdate
# info['metadata']['contact_name'] = contactName
# info['metadata']['contact_email'] = contactEmail
# info['metadata']['issuing_organization'] = issuingOrganization

# info['types_of_work'] = typeOfWork
# info['lanes_obj'] = lanes_obj

# Translator 
def wzdx_creator(messages, data_lane, info):
    wzd = {}
    wzd['road_event_feed_info'] = {}
    wzd['road_event_feed_info']['feed_info_id'] = info['feed_info_id']
    wzd['road_event_feed_info']['update_date'] = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    wzd['road_event_feed_info']['publisher'] = 'POC Work Zone Integrated Mapping'
    wzd['road_event_feed_info']['contact_name'] = 'Tony English'
    wzd['road_event_feed_info']['contact_email'] = 'tony@neaeraconsulting.com'
    if info['metadata'].get('datafeed_frequency_update', False):
        wzd['road_event_feed_info']['update_frequency'] = info['metadata']['datafeed_frequency_update'] # Verify data type
    wzd['road_event_feed_info']['version'] = '3.0'

    data_source = {}
    data_source['data_source_id'] = str(uuid.uuid4())
    data_source['feed_info_id'] = info['feed_info_id']
    data_source['organization_name'] = info['metadata']['issuing_organization']
    data_source['contact_name'] = info['metadata']['contact_name']
    data_source['contact_email'] = info['metadata']['contact_email']
    if info['metadata'].get('datafeed_frequency_update', False):
        data_source['update_frequency'] = info['metadata']['datafeed_frequency_update']
    data_source['update_date'] = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    data_source['location_verify_method'] = info['metadata']['location_verify_method']
    data_source['location_method'] = info['metadata']['wz_location_method']
    data_source['lrs_type'] = info['metadata']['lrs_type']
    # data_source['lrs_url'] = "basic url"

    wzd['road_event_feed_info']['data_sources'] = [data_source]

    wzd['type'] = 'FeatureCollection'
    nodes = []
    sub_identifier = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(6)) #Create random 6 character digit/letter string
    road_event_id = str(uuid.uuid4())
    ids = {}
    ids['sub_identifier'] = sub_identifier
    ids['road_event_id'] = road_event_id
    for message in messages:
        rsm = message['MessageFrame']['value']['RoadsideSafetyMessage']
        node_list = extract_nodes(rsm, wzd, ids, int(data_lane), info)
        for node in node_list:
            nodes.append(node)
    wzd['features'] = wzdx_collapser(nodes)
    wzd = add_ids(wzd, True)
    return wzd

# Add ids to message
def add_ids(message, add_ids):
    if add_ids:
        feed_info_id = message['road_event_feed_info']['feed_info_id']
        data_source_id = message['road_event_feed_info']['data_sources'][0]['data_source_id']

        road_event_length = len(message['features'])
        road_event_ids = []
        for i in range(road_event_length):
            road_event_ids.append(str(uuid.uuid4()))

        for i in range(road_event_length):
            feature = message['features'][i]
            road_event_id = road_event_ids[i]
            feature['properties']['road_event_id'] = road_event_id
            # feature['properties']['feed_info_id'] = feed_info_id
            feature['properties']['data_source_id'] = data_source_id
            # feature['properties']['relationship'] = {}
            feature['properties']['relationship']['relationship_id'] = str(uuid.uuid4())
            feature['properties']['relationship']['road_event_id'] = road_event_id
            if i == 0: feature['properties']['relationship']['first'] = road_event_ids
            else: feature['properties']['relationship']['next'] = road_event_ids
            for lane in feature['properties']['lanes']:
                lane_id = str(uuid.uuid4())
                lane['lane_id'] = lane_id
                lane['road_event_id'] = road_event_id
                for lane_restriction in lane.get('restrictions', []):
                    lane_restriction_id = str(uuid.uuid4())
                    lane_restriction['lane_restriction_id'] = lane_restriction_id
                    lane_restriction['lane_id'] = lane_id
            for types_of_work in feature['properties']['types_of_work']:
                types_of_work_id = str(uuid.uuid4())
                types_of_work['types_of_work_id'] = types_of_work_id
                types_of_work['road_event_id'] = road_event_id
    return message

# Collapse nodes into fewest number of features as possible
def wzdx_collapser(features): #Collapse identical nodes together to reduce overall number of nodes
    #return features
    new_nodes = []
    new_nodes.append(features[0])
    for i in range(1, len(features)):
        new_nodes[-1]['geometry']['coordinates'].append(features[i]['geometry']['coordinates'][0]) #Add coordinates of next node to end of previous node
        if features[i]['properties'] != features[i-1]['properties'] and i != len(features)-1: #Only add unique nodes to output list
            new_nodes.append(features[i])

    long_dif = new_nodes[-1]['geometry']['coordinates'][-1][0] - new_nodes[0]['geometry']['coordinates'][0][0]
    lat_dif = new_nodes[-1]['geometry']['coordinates'][-1][1] - new_nodes[0]['geometry']['coordinates'][0][1]
    if abs(long_dif) > abs(lat_dif):
        if long_dif > 0:
            direction = 'eastbound'
        else:
            direction = 'westbound'
    elif lat_dif > 0:
        direction = 'northbound'
    else:
        direction = 'southbound'

    # heading = int(rsm['regionInfo']['applicableHeading']['heading'])
    # tol = int(rsm['regionInfo']['applicableHeading']['tolerance'])
    # if abs(heading) + abs(tol) < 45:
    #     direction = 'northbound'
    # elif abs(heading) + 

    for i in range(len(new_nodes)):
        if not new_nodes[i]['properties']['direction']:
            new_nodes[i]['properties']['direction'] = direction

    
    return new_nodes

# 0 pad times to 2 digits (2 -> 02)
def form_len(string):
    num = int(string)
    return format(num, '02d')

# Create feature for every node from rsm message
def extract_nodes(rsm, wzd, ids, data_lane, info):
    lanes = rsm['rszContainer']['rszRegion']['roadwayGeometry']['rsmLanes']['RSMLane']
    num_lanes = len(lanes)
    nodes = lanes[0]['laneGeometry']['nodeSet']['NodeLLE']
    nodes_wzdx = []
    prev_attr_list = []
    reduced_speed_limit = int(rsm['rszContainer'].get('speedLimit').get('speed', 0))

    if rsm['rszContainer']['speedLimit'].get('kph', {}) == None: #If kph, convert to mph
        reduced_speed_limit = round(reduced_speed_limit*0.6214)
    prev_attributes_general = {'peoplePresent': False, 'reducedSpeedLimit': reduced_speed_limit}

    for k in range(len(lanes)):
        prev_attributes_lane = {'laneClosed': False, 'merge-left': False, 'merge-right': False}
        prev_attr_list.append(prev_attributes_lane)
    
    for i in range(len(nodes)):
        # lanes_obj = {}
        lanes_wzdx = []
        restrictions = []
        
        people_present = False #initialization
        geometry = {}
        geometry['type'] = 'LineString'
        for j in range(len(lanes)):
            lane = {}
            lane['lane_id'] = ''
            lane['road_event_id'] = ''
            # Lane Number
            lane['order'] = int(lanes[j]['lanePosition'])
            lane['lane_number'] = int(lanes[j]['lanePosition'])

            # Lane Edge Reference
            # lane['lane_edge_reference'] = 'left' #This is an assumed value

            # Generically set lane type
            # lane, lane_type = get_lane_type(lane, num_lanes)

            
            node_contents = lanes[j]['laneGeometry']['nodeSet']['NodeLLE'][i]

            # Lane Status
            lane_status = get_lane_status(node_contents, j, prev_attr_list)
            lane['status'] = lane_status

            lane['type'] = ''

            # Lane Restrictions
            lane, lane_type, restrictions = get_lane_restrictions(info, lane, restrictions)

            # Lane Type
            if not lane_type: #Generally set lane type (right, middle or left)
                lane, lane_type = get_lane_type(lane, num_lanes)
            lane['type'] = lane_type


            # Geometry
            point = lanes[j]['laneGeometry']['nodeSet']['NodeLLE'][i]['nodePoint']
            geometry = get_geometry(lane, point, data_lane, geometry)

            # Reduced Speed Limit
            reduced_speed_limit, prev_attributes_general = get_reduced_speed_limit(node_contents, prev_attributes_general)

            # Workers Present
            people_present, prev_attributes_general = get_worker_presence(node_contents, prev_attributes_general)

            # Add Lane
            lanes_wzdx.append(lane)

        # feed_info_id
        # lanes_obj['feed_info_id'] = wzd['road_event_feed_info']['feed_info_id']

        lanes_obj = set_lane_properties(ids, info, rsm)

        # total_num_lanes
        lanes_obj['total_num_lanes'] = num_lanes

        # vehicle_impact
        num_closed_lanes = 0
        for lane in lanes_wzdx:
            if lane['status'] == 'closed' or lane['status'] == 'merge-left' or lane['status'] == 'merge-right':
                num_closed_lanes = num_closed_lanes + 1
        if num_closed_lanes == 0:
            lanes_obj['vehicle_impact'] = 'all-lanes-open'
        elif num_closed_lanes == num_lanes:
            lanes_obj['vehicle_impact'] = 'all-lanes-closed'
        else:
            lanes_obj['vehicle_impact'] = 'some-lanes-closed'

        # workser_present
        lanes_obj['workers_present'] = people_present

        # reduced_speed_limit
        lanes_obj['reduced_speed_limit'] = reduced_speed_limit #Will either be set to the reference value or a lower value if found

        # description
        lanes_obj['description'] = info['description']

        # restrictions
        if restrictions:
            lanes_obj['restrictions'] = restrictions

        # Lanes object
        lanes_obj['lanes'] = lanes_wzdx

        # properties
        lanes_obj_properties = {}
        lanes_obj_properties['type'] = 'Feature'
        lanes_obj_properties['properties'] = lanes_obj
        lanes_obj_properties['geometry'] = geometry

        nodes_wzdx.append(lanes_obj_properties)
    return nodes_wzdx

def get_lane_restrictions(info, lane, restrictions):
    lane_type = ''
    lane['restrictions'] = []#no-trucks, travel-peak-hours-only, hov-3, hov-2, no-parking
        #reduced-width, reduced-height, reduced-length, reduced-weight, axle-load-limit, gross-weight-limit, towing-prohibited, permitted-oversize-loads-prohibited

    # Overwrite lane_type if present in configuration file
    for lane_obj in info['lanes_obj']:
        if lane_obj['LaneNumber'] == lane['lane_number']:
            lane_type = lane_obj['LaneType']
            for lane_restriction_info in lane_obj['LaneRestrictions']:
                lane_restriction = {}
                lane_restriction['lane_restriction_id'] = ''
                lane_restriction['lane_id'] = ''
                lane_restriction['restriction_type'] = lane_restriction_info['RestrictionType']
                if not lane_restriction_info['RestrictionType'] in restrictions: restrictions.append(lane_restriction_info['RestrictionType'])
                if lane_restriction['restriction_type'] in ['reduced-width', 'reduced-height', 'reduced-length', 'reduced-weight', 'axle-load-limit', 'gross-weight-limit']:
                    lane_restriction['restriction_value'] = lane_restriction_info['RestrictionValue']
                    lane_restriction['restriction_units'] = lane_restriction_info['RestrictionUnits']
                lane['restrictions'].append(lane_restriction)

    return lane, lane_type, restrictions


def get_lane_type(lane, num_lanes):
    # Lane Type
    lane_type = 'middle-lane' #left-lane, right-lane, middle-lane, right-exit-lane, left-exit-lane, ... (exit lanes, merging lanes, turning lanes)
    if lane['lane_edge_reference'] == 'left':
        if lane['lane_number'] == 1:
            lane_type = 'left-lane'
        elif lane['lane_number'] == num_lanes:
            lane_type = 'right-lane'
    elif lane['lane_edge_reference'] == 'right':
        if lane['lane_number'] == 1:
            lane_type = 'right-lane'
        elif lane['lane_number'] == num_lanes:
            lane_type = 'left-lane'

    return lane, lane_type

def get_lane_status(node_contents, j, prev_attr_list):
    # Lane Status
    lane_status = 'open' #Can be open, closed, shift-left, shift-right, merge-right, merge-left, alternating-one-way
    if node_contents.get('nodeAttributes', {}).get('laneClosed', {}).get('true', {}) == None: #laneClosed set to true, set lane_status to closed and previous value
        lane_status = 'closed'
        prev_attr_list[j]['laneClosed'] = True
    elif node_contents.get('nodeAttributes', {}).get('laneClosed', {}).get('false', {}) == None: #laneClosed set to false, leave lane_status alone and set previous value
        prev_attr_list[j]['laneClosed'] = False
    elif prev_attr_list[j]['laneClosed']: #No info in current node, use previous value
        lane_status = 'closed'

    if node_contents.get('nodeAttributes', {}).get('taperLeft', {}).get('true', {}) == None:
        lane_status = 'merge-left'
        prev_attr_list[j]['merge-left'] = True
    elif node_contents.get('nodeAttributes', {}).get('taperLeft', {}).get('false', {}) == None:
        prev_attr_list[j]['merge-left'] = False
    elif prev_attr_list[j]['merge-left']:
        lane_status = 'merge-left'

    if node_contents.get('nodeAttributes', {}).get('taperRight', {}).get('true', {}) == None:
        lane_status = 'merge-right'
        prev_attr_list[j]['merge-right'] = True
    elif node_contents.get('nodeAttributes', {}).get('taperRight', {}).get('false', {}) == None:
        prev_attr_list[j]['merge-right'] = False
    elif prev_attr_list[j]['merge-right']:
        lane_status = 'merge-right'

    return lane_status

def get_geometry(lane, point, data_lane, geometry):
    # Geometry
    if lane['lane_number'] == data_lane:
        lane_coordinate = []
        if point.get('node-3Dabsolute') is not None: #Store coordinates of node for use later
            lane_coordinate.append(int(point['node-3Dabsolute']['long'])/10000000)
            lane_coordinate.append(int(point['node-3Dabsolute']['lat'])/10000000)
            lane_coordinate.append(int(point['node-3Dabsolute']['elevation']))
        else: #Node is defined as offset (node-3Doffset), this is not yet supported
            lane_coordinate.append(0)
            lane_coordinate.append(0)
        geometry['coordinates'] = []
        geometry['coordinates'].append(lane_coordinate)
    return geometry

def get_reduced_speed_limit(node_contents, prev_attributes_general):
    # Reduced Speed Limit
    if node_contents.get('nodeAttributes', {}).get('speedLimit', {}).get('type', {}).get('vehicleMaxSpeed', {}) == None:
        reduced_speed_limit = int(node_contents['nodeAttributes']['speedLimit']['speed'])
        units = node_contents['nodeAttributes']['speedLimit']['speedUnits']
        if units.get('kph', {}) == None:
            reduced_speed_limit = round(reduced_speed_limit*0.6214)
    else:
        reduced_speed_limit = prev_attributes_general['reducedSpeedLimit']
    prev_attributes_general['reducedSpeedLimit'] = reduced_speed_limit
    return reduced_speed_limit, prev_attributes_general

def get_worker_presence(node_contents, prev_attributes_general):
    # Workers Present
    if node_contents.get('nodeAttributes', {}).get('peoplePresent', {}).get('true', {}) == None: #People present
        people_present = True
    elif node_contents.get('nodeAttributes', {}).get('peoplePresent', {}).get('false', {}) == None: #No people present
        people_present = False
    else:
        people_present = prev_attributes_general['peoplePresent']
    prev_attributes_general['peoplePresent'] = people_present #Set previous value
    return people_present, prev_attributes_general

def set_lane_properties(ids, info, rsm):
    lanes_obj = {}
    lanes_obj['road_event_id'] = ''
    lanes_obj['data_source_id'] = ''

    # Event Type ['work-zone', 'detour']
    lanes_obj['event_type'] = 'work-zone'

    # Relationship
    lanes_obj['relationship'] = {}

    # Subidentifier
    # lanes_obj['sub_identifier'] = ids['sub_identifier']

    # road_name
    lanes_obj['road_name'] = info['road_name']

    # road_name
    lanes_obj['road_number'] = info['road_number']

    # direction
    lanes_obj['direction'] = info['direction']

    # beginning_cross_street
    if info['beginning_cross_street']:
        lanes_obj['beginning_cross_street'] = info['beginning_cross_street']

    # beginning_cross_street
    if info['ending_cross_street']:
        lanes_obj['ending_cross_street'] = info['ending_cross_street']

    # beginning_milepost
    if info['beginning_milepost']:
        lanes_obj['beginning_milepost'] = info['beginning_milepost']

    # ending_milepost
    if info['ending_milepost']:
        lanes_obj['ending_milepost'] = info['ending_milepost']

    # beginning_accuracy
    lanes_obj['beginning_accuracy'] = info['beginning_accuracy']

    # ending_accuracy
    lanes_obj['ending_accuracy'] = info['ending_accuracy']

    # start_date
    start_date = rsm['commonContainer']['eventInfo']['startDateTime'] #Offset is in minutes from UTC (-5 hours, ET), unused
    lanes_obj['start_date'] = str(start_date['year']+'-'+form_len(start_date['month'])+'-'+form_len(start_date['day'])+'T'+form_len(start_date['hour'])+':'+form_len(start_date['minute'])+':00Z')
    
    # end_date
    end_date = rsm['commonContainer']['eventInfo']['endDateTime']
    lanes_obj['end_date'] = str(end_date['year']+'-'+form_len(end_date['month'])+'-'+form_len(end_date['day'])+'T'+form_len(end_date['hour'])+':'+form_len(end_date['minute'])+':00Z')
    
    # start_date_accuracy
    lanes_obj['start_date_accuracy'] = info['start_date_accuracy']

    # end_date_accuracy
    lanes_obj['end_date_accuracy'] = info['end_date_accuracy']

    # event status
    if info['event_status']:
        lanes_obj['event_status'] = info['event_status']
        if info['event_status'] == 'planned':
            lanes_obj['start_date_accuracy'] = 'estimated'
            lanes_obj['end_date_accuracy'] = 'estimated'

    # other stuffs was here

    # issuing_organization
    if info['issuing_organization']:
        lanes_obj['issuing_organization'] = info['issuing_organization']
    
    # creation_date
    if info['creation_date']:
        lanes_obj['creation_date'] = info['creation_date']
    
    # update_date
    lanes_obj['update_date'] = info['update_date']

    # creation_date
    lanes_obj['creation_date'] = info['update_date']

    #type_of_work
    #maintenance, minor-road-defect-repair, roadside-work, overhead-work, below-road-work, barrier-work, surface-work, painting, roadway-relocation, roadway-creation
    lanes_obj['types_of_work'] = []
    for types_of_work in info['types_of_work']:
        type_of_work = {}
        type_of_work['types_of_work_id'] = ''
        type_of_work['road_event_id'] = ''
        type_of_work['type_name'] = types_of_work['WorkType']
        if types_of_work.get('Is_Architectural_Change', '') != '': type_of_work['is_architectural_change'] = types_of_work['Is_Architectural_Change']
        lanes_obj['types_of_work'].append(type_of_work)

    return lanes_obj