import xml.etree.ElementTree as ET 
import json
import xmltodict
from datetime import datetime
import uuid
#with open('rsm.json', 'r') as f:


def wzdx_creator(messages, dataLane):
    wzd = {}
    ids = False # Enables ids linking tables together within file
    wzd['road_event_feed_info'] = {}
    # if ids:
    #     wzd['road_event_feed_info']['feed_info_id'] = str(uuid.uuid4())
    wzd['road_event_feed_info']['feed_update_date'] = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    #wzd['road_event_feed_info']['metadata'] = 'https://fake-site.ltd/dummy-metadata.txt'
    wzd['road_event_feed_info']['version'] = '2.0'
    wzd['type'] = 'FeatureCollection'
    nodes = []
    for message in messages:
        RSM = message['MessageFrame']['value']['RoadsideSafetyMessage']
        node_list = extract_nodes(RSM, wzd, ids, int(dataLane))
        for node in node_list:
            nodes.append(node)
    wzd['features'] = wzdx_collapser(nodes)
    wzd = add_ids(wzd, False)
    return wzd

def add_ids(message, add_ids):
    if add_ids:
        feed_info_id = str(uuid.uuid4())
        message['road_event_feed_info']['feed_info_id'] = feed_info_id
        for feature in message['features']:
            road_event_id = str(uuid.uuid4())
            feature['properties']['road_event_id'] = road_event_id
            feature['properties']['feed_info_id'] = feed_info_id
            for lane in feature['properties']['lanes']:
                lane_id = str(uuid.uuid4())
                lane['lane_id'] = lane_id
                lane['road_event_id'] = road_event_id
                for lane_restriction in lane.get('lane_restrictions', []):
                    lane_restriction_id = str(uuid.uuid4())
                    lane_restriction['lane_restriction_id'] = lane_restriction_id
                    lane_restriction['lane_id'] = lane_id
            for types_of_work in feature['properties']['types_of_work']:
                types_of_work_id = str(uuid.uuid4())
                types_of_work['types_of_work_id'] = types_of_work_id
                types_of_work['road_event_id'] = road_event_id

    return message

def wzdx_collapser(features): #Collapse identical nodes together to reduce overall number of nodes
    #return features
    new_nodes = []
    new_nodes.append(features[0])
    #directions = []
    for i in range(1, len(features)):
        new_nodes[-1]['geometry']['coordinates'].append(features[i]['geometry']['coordinates'][0]) #Add coordinates of next node to end of previous node
        if features[i]['properties'] != features[i-1]['properties'] and i != len(features)-1: #Only add unique nodes to output list
            new_nodes.append(features[i])
        #     print('new')
        # else:
        #     print('old')

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

    # heading = int(RSM['regionInfo']['applicableHeading']['heading'])
    # tol = int(RSM['regionInfo']['applicableHeading']['tolerance'])
    # if abs(heading) + abs(tol) < 45:
    #     direction = 'northbound'
    # elif abs(heading) + 

    for i in range(len(new_nodes)):
        new_nodes[i]['properties']['direction'] = direction

    
    return new_nodes

def form_len(string):
    num = int(string)
    return format(num, '02d')

def extract_nodes(RSM, wzd, ids, dataLane):
    lanes = RSM['rszContainer']['rszRegion']['roadwayGeometry']['rsmLanes']['RSMLane']
    num_lanes = len(lanes)
    nodes = lanes[0]['laneGeometry']['nodeSet']['NodeLLE']
    nodes_wzdx = []
    prev_attr_list = []
    for k in range(len(lanes)):
        prev_attributes = {'laneClosed': False, 'peoplePresent': False}
        prev_attr_list.append(prev_attributes)
    for i in range(len(nodes)):
        lanes_obj = {}
        lanes_wzdx = []
        reduced_speed_limit = int(RSM['rszContainer'].get('speedLimit').get('speed', 0))
        if RSM['rszContainer']['speedLimit'].get('kph', {}) == None: #If kph, convert to mph
            reduced_speed_limit = round(reduced_speed_limit*0.6214)
        people_present = False #initialization
        geometry = {}
        geometry['type'] = 'LineString'
        road_event_id = str(uuid.uuid4())
        for j in range(len(lanes)):
            lane = {}
            # if ids:
            #     lane['lane_id'] = str(uuid.uuid4())

            #     lane['road_event_id'] = road_event_id

            lane['lane_number'] = int(lanes[j]['lanePosition'])

            lane['lane_edge_reference'] = 'left' #This is an assumed value

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
            lane['lane_type'] = lane_type

            node_contents = lanes[j]['laneGeometry']['nodeSet']['NodeLLE'][i]
            lane_status = 'open' #Can be open, closed, shift-left, shift-right, merge-right, merge-left, alternating-one-way

            if node_contents.get('nodeAttributes', {}).get('taperLeft', {}).get('true', {}) == None:
                lane_status = 'merge-left'
            elif node_contents.get('nodeAttributes', {}).get('taperRight', {}).get('true', {}) == None:
                lane_status = 'merge-right'

            if node_contents.get('nodeAttributes', {}).get('laneClosed', {}).get('true', {}) == None: #laneClosed set to true, set lane_status to closed and previous value
                lane_status = 'closed'
                prev_attr_list[j]['laneClosed'] = True
            elif node_contents.get('nodeAttributes', {}).get('laneClosed', {}).get('false', {}) == None: #laneClosed set to false, leave lane_status alone and set previous value
                prev_attr_list[j]['laneClosed'] = False
            elif prev_attr_list[j]['laneClosed']: #No info in current node, use previous value
                lane_status = 'closed'


            lane['lane_status'] = lane_status
            point = lanes[j]['laneGeometry']['nodeSet']['NodeLLE'][i]['nodePoint']
            if lane['lane_number'] == dataLane:
                lane_coordinate = []
                if point.get('node-3Dabsolute') is not None: #Store coordinates of node for use later
                    lane_coordinate.append(int(point['node-3Dabsolute']['long'])/10000000)
                    lane_coordinate.append(int(point['node-3Dabsolute']['lat'])/10000000)
                else: #Node is defined as offset (node-3Doffset), this is not yet supported
                    lane_coordinate.append(0)
                    lane_coordinate.append(0)
                geometry['coordinates'] = []
                geometry['coordinates'].append(lane_coordinate)
            
            #lane['lane_restrictions'] = []#no-trucks, travel-peak-hours-only, hov-3, hov-2, no-parking
                #reduced-width, reduced-height, reduced-length, reduced-weight, axle-load-limit, gross-weight-limit, towing-prohibited, permitted-oversize-loads-prohibited
            # Restrictions will be added later
            # for lane_restriction in lane_restrictions
                # if restr['restriction_type'] in ['reduced-width', 'reduced-height', 'reduced-length', 'reduced-weight', 'axle-load-limit', 'gross-weight-limit']:
                    # lane_restriction = {}
                    # if ids:
                        # lane_restriction['lane_restriction_id'] = str(uuid.uuid4())
                        # lane_restriction['lane_id'] = lane['lane_id']
                    # lane_restriction['restriction_type'] = 
                    # lane_restriction['restriction_value'] = 
                    # lane_restriction['restriction_units'] = 
                    # lane['lane_restrictions'].append(lane_restriction)

            # Reduced Speed Limit
            if node_contents.get('nodeAttributes', {}).get('speedLimit', {}).get('type', {}).get('vehicleMaxSpeed', {}) == None:
                reduced_speed_limit = int(node_contents['nodeAttributes']['speedLimit']['speed'])
                units = node_contents['nodeAttributes']['speedLimit']['speedUnits']
                if units.get('kph', {}) == None:
                    reduced_speed_limit = round(reduced_speed_limit*0.6214)

            if node_contents.get('nodeAttributes', {}).get('peoplePresent', {}).get('true', {}) == None: #People present
                people_present = True
            elif node_contents.get('nodeAttributes', {}).get('peoplePresent', {}).get('false', {}) == None: #No people present
                people_present = False
            else:
                people_present = prev_attr_list[j]['peoplePresent']
            prev_attr_list[j]['peoplePresent'] = people_present #Set previous value

            lanes_wzdx.append(lane)

        # if ids:
        #     # road_event_id
        #     lanes_obj['road_event_id'] = road_event_id

        #     # feed_info_id
        #     lanes_obj['feed_info_id'] = wzd['road_event_feed_info']['feed_info_id']

        # road_name
        lanes_obj['road_name'] = 'unknown'

        # direction
        lanes_obj['direction'] = 'unknown'

        # beginning_accuracy
        lanes_obj['beginning_accuracy'] = 'estimated'

        # ending_accuracy
        lanes_obj['ending_accuracy'] = 'estimated'

        # start_date_accuracy
        lanes_obj['start_date_accuracy'] = 'estimated'

        # end_date_accuracy
        lanes_obj['end_date_accuracy'] = 'estimated'

        # total_num_lanes
        lanes_obj['total_num_lanes'] = num_lanes

        # reduced_speed_limit
        if reduced_speed_limit != -1:
            lanes_obj['reduced_speed_limit'] = reduced_speed_limit #Will either be set to the reference value or a lower value if found

        # workser_present
        lanes_obj['workers_present'] = people_present

        # vehicle_impact
        num_closed_lanes = 0
        for lane in lanes_wzdx:
            if lane['lane_status'] == 'closed':
                num_closed_lanes = num_closed_lanes + 1
        if num_closed_lanes == 0:
            lanes_obj['vehicle_impact'] = 'all_lanes_open'
        elif num_closed_lanes == num_lanes:
            lanes_obj['vehicle_impact'] = 'all_lanes_closed'
        else:
            lanes_obj['vehicle_impact'] = 'some_lanes_closed'

        # start_date
        start_date = RSM['commonContainer']['eventInfo']['startDateTime'] #Offset is in minutes from UTC (-5 hours, ET), unused
        lanes_obj['start_date'] = str(start_date['year']+'-'+form_len(start_date['month'])+'-'+form_len(start_date['day'])+'T'+form_len(start_date['hour'])+':'+form_len(start_date['minute'])+':00Z')
        
        # end_date
        end_date = RSM['commonContainer']['eventInfo']['endDateTime']
        lanes_obj['end_date'] = str(end_date['year']+'-'+form_len(end_date['month'])+'-'+form_len(end_date['day'])+'T'+form_len(end_date['hour'])+':'+form_len(end_date['minute'])+':00Z')
        
        #type_of_work
        #maintenance, minor-road-defect-repair, roadside-work, overhead-work, below-road-work, barrier-work, surface-work, painting, roadway-relocation, roadway-creation
        #Maybe use cause code??
        lanes_obj['types_of_work'] = []
        #if cause_code == 3: #No other options are available
        types_of_work = {}
        # if ids:
        #     types_of_work['types_of_work_id'] = str(uuid.uuid4())
        #     types_of_work['road_event_id'] = road_event_id
        types_of_work['type_name'] = 'roadside-work'
        types_of_work['is_architectual_change'] = False
        lanes_obj['types_of_work'].append(types_of_work)

        lanes_obj['lanes'] = lanes_wzdx

        # properties
        lanes_obj_properties = {}
        lanes_obj_properties['type'] = 'Feature'
        lanes_obj_properties['properties'] = lanes_obj
        lanes_obj_properties['geometry'] = geometry

        nodes_wzdx.append(lanes_obj_properties)
    return nodes_wzdx

# with open('C:/Users/rando/OneDrive/Documents/GitHub/V2X-manual-data-collection/CAMP Tools/WZ_MapMsg/RSZW_MAP_xml_File-20200330-102959-1_of_1.exer', 'r') as frsm:
#     #rsm = rsm_creator('heh')
#     #f.write(json2xml.Json2xml(rsm).to_xml())
#     #rsm_xml = xmltodict.unparse(rsm, pretty=True)
#     xmlSTRING = frsm.read()
#     rsm_obj = xmltodict.parse(xmlSTRING)
#     #with open('RSM_example.json', 'w') as frsm_json:
#     #    frsm_json.write(json.dumps(rsm_obj, indent=2))
#     wzdx = wzdx_creator(rsm_obj)
#     with open('wzdx_test.geojson', 'w') as fwzdx:
#         fwzdx.write(json.dumps(wzdx, indent=2))