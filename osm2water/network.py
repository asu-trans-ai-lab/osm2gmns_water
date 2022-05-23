
import os
import tempfile
import pathlib
import shutil
from .reader import *
from .classes import *

def _check_filename(filename):
    path = pathlib.Path(filename)
    for ch in filename:
        if '\u4e00' <= ch <= '\u9fff':
            tmpdir = tempfile.gettempdir()
            if path.suffix == '.pbf':
                tmpfile=os.path.join(tmpdir,'map.osm.pbf')
            else:
                tmpfile=os.path.join(tmpdir,'map.osm')
            shutil.copy(filename,tmpfile)
            return tmpfile,True
    return filename,False

def _new_link_from_way(from_node,to_node, way):
    link = Link()
    link.access = way.access
    link.boat = way.boat
    link.capacity = None
    link.dir_flag = 2
    link.from_node = from_node
    link.gnis_feature_id = way.gnis_feature_id
    link.gnis_state_id = way.gnis_state_id
    link.gnis_name = way.gnis_name
    link.intermittent = way.intermittent
    link.link_type_name = way.waterway
    link.name = way.name
    link.osm_way_id = way.osm_way_id
    link.to_node = to_node
    link.tunnel = way.tunnel
    link.calculateLength()
    link.generate_geometry()
    return link

def _create_links_from_way(network, link_way_list):
    link_id = 0
    for way in link_way_list:
        for ref_node_id in range(len(way.ref_node_list) - 1):
            from_node = way.ref_node_list[ref_node_id]
            from_node.valid = True
            to_node = way.ref_node_list[ref_node_id + 1]
            to_node.valid = True
            link=_new_link_from_way(from_node,to_node, way)
            link.link_id=link_id
            network.link_dict[link_id]=link
            link_id+=1
    network.number_of_links = link_id

def _create_pois_from_way(network,POI_way_list):
    POI_list = []
    poi_id = 0
    for way in POI_way_list:
        poi = POI()
        poi.poi_id = poi_id
        poi.name = way.name
        poi.waterway = way.waterway
        poi.osm_way_id = way.osm_way_id
        ref_node_list = []
        for ref_node in way.ref_node_list:
            # ref_node.valid=True
            ref_node_list.append(ref_node.geometry)
        if way.ref_node_list[0].osm_node_id != way.ref_node_list[-1].osm_node_id or len(way.ref_node_list)<=2:
            continue
        poi.ref_node_list = ref_node_list
        poi.generate_geometry()
        poi.area=poi.geometry.area
        lon, lat = poi.geometry.centroid.x, poi.geometry.centroid.y
        poi.centroid = geometry.Point((round(lon, lonlat_precision), round(lat, lonlat_precision)))
        POI_list.append(poi)
        poi_id += 1
        network.POI_list.append(poi)

def _create_pois_from_relation(network):
    poi_id = len(network.POI_list)+1
    for way in network.osm_relation_inter_way_list:
        poi = POI()
        poi.poi_id = poi_id
        poi.name = way.name
        poi.waterway = way.waterway
        poi.osm_way_id = way.osm_way_id
        ref_node_list = []
        for ref_node in way.ref_node_list:
            ref_node_list.append(ref_node.geometry)
        if way.ref_node_list[0].osm_node_id != way.ref_node_list[-1].osm_node_id:
            continue
        poi.ref_node_list = ref_node_list
        poi.generate_geometry()
        if poi.geometry:
            poi.area = poi.geometry.area
            lon, lat = poi.geometry.centroid.x, poi.geometry.centroid.y
            poi.centroid = geometry.Point((round(lon, lonlat_precision), round(lat, lonlat_precision)))
            network.POI_list.append(poi)
            poi_id += 1
    for way_list in network.osm_relation_outer_way_list:
        if way_list[0].ref_node_list[0] == way_list[-1].ref_node_list[-1]:
            poi = POI()
            poi.poi_id = poi_id
            poi.osm_way_id = way_list[0].osm_way_id
            poi.waterway = way_list[0].waterway
            ref_node_list = []
            for way in way_list:
                for ref_node in way.ref_node_list:
                    ref_node_list.append(ref_node.geometry)
            poi.ref_node_list = ref_node_list
            poi.generate_geometry()
            if poi.geometry:
                poi.area = poi.geometry.area
                lon, lat = poi.geometry.centroid.x, poi.geometry.centroid.y
                poi.centroid = geometry.Point((round(lon, lonlat_precision), round(lat, lonlat_precision)))
                network.POI_list.append(poi)
                poi_id += 1
        else:
            link_id = len(network.link_dict) + 1
            for way in way_list:
                for ref_node_id in range(len(way.ref_node_list) - 1):
                    from_node = way.ref_node_list[ref_node_id]
                    from_node.valid = True
                    to_node = way.ref_node_list[ref_node_id + 1]
                    to_node.valid = True
                    link = _new_link_from_way(from_node, to_node, way)
                    link.link_id = link_id
                    network.link_dict[link_id] = link
                    link_id += 1

def _createNLPs(network):
    link_way_list = []
    POI_way_list = []
    for osm_way_id,way in network.osm_way_dict.items():
        if way.way_poi :
            POI_way_list.append(way)
        else:
            link_way_list.append(way)
    if len(link_way_list):
        _create_links_from_way(network, link_way_list)
    else:
        print('railway link not found')
    if len(POI_way_list) > 0:
        _create_pois_from_way(network, POI_way_list)
    else:
        print('railway POI not found')
    _create_pois_from_relation(network)





def _filter_osm_node(network):
    node_dict = {}
    node_id = 0
    for osm_node_id, node in network.osm_node_dict.items():
        if node.valid and node.in_region:
            node.node_id = node_id
            node_dict[node_id] = node
            node_id += 1
    network.node_dict = node_dict

def _filter_osm_link(network):
    link_dict = {}
    link_id = 0
    for id, link in network.link_dict.items():
        from_node = link.from_node
        to_node = link.to_node
        if from_node.in_region and to_node.in_region:
            link_dict[link_id] = link
            link_id = link_id + 1
    network.link_dict = link_dict

def _filter_osm_poi(network):
    poi_list = []
    for poi in network.POI_list:
        if poi.geometry.within(network.bounds):
            poi_list.append(poi)
    network.POI_list = poi_list

def _buildNet(network,strict_mode=False):
    _createNLPs(network)
    _filter_osm_node(network)
    if strict_mode:
        _filter_osm_link(network)
        _filter_osm_poi(network)

def get_network_from_file(filename='map.osm',bbox=None,strict_mode=False,POIs=True):
    filename,is_tmp=_check_filename(filename)
    network=readOSMFile(filename=filename,POIs=POIs,strict_mode=strict_mode,bbox=bbox)
    _buildNet(network=network,strict_mode=strict_mode)
    if is_tmp:
        os.remove(filename)
    return network