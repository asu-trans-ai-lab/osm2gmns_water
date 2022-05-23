
import sys
import osmium
from .classes import *
from .setting import *
from shapely import geometry

def _getBounds(filename, bbox):
    try:
        f = osmium.io.Reader(filename)
    except:
        sys.exit(f'Error: filepath {filename} contains invalid characters. Please use english characters only')

    if bbox is None:
        header = f.header()
        box = header.box()
        bottom_left = box.bottom_left
        top_right = box.top_right
        try:
            minlat, minlon = bottom_left.lat, bottom_left.lon
            maxlat, maxlon = top_right.lat, top_right.lon
        except:
            minlat, minlon, maxlat, maxlon = default_bounds['minlat'], default_bounds['minlon'], default_bounds['maxlat'], default_bounds['maxlon']
    else:
        minlat, minlon, maxlat, maxlon = bbox

    bounds = geometry.Polygon([(minlon, maxlat), (maxlon, maxlat), (maxlon, minlat), (minlon, minlat)])
    return bounds

class NWRHandler(osmium.SimpleHandler):
    def __init__(self):
        osmium.SimpleHandler.__init__(self)

        self.strict_mode = True
        self.bounds = None
        self.POIs = False

        self.osm_node_dict = {}
        self.osm_node_id_list = []
        self.osm_node_coord_list = []

        self.osm_way_dict = {}
        self.osm_relation_outer_way_list=[]
        self.osm_relation_inter_way_list = []


    def node(self, n):
        node = Node()
        node.osm_node_id = str(n.id)
        lon, lat = n.location.lon, n.location.lat
        node.geometry = geometry.Point((round(lon, lonlat_precision), round(lat, lonlat_precision)))
        node.x_coord=lon
        node.y_coord=lat
        if self.strict_mode:
            if not node.geometry.within(self.bounds):
                node.in_region = False
        self.osm_node_id_list.append(node.osm_node_id)
        self.osm_node_coord_list.append((lon, lat))

        self.osm_node_dict[node.osm_node_id] = node
        del n

    def way(self, w):
        way = Way()
        way.osm_way_id = str(w.id)
        way.ref_node_id_list = [str(node.ref) for node in w.nodes]
        if w.tags.get('waterway') or w.tags.get('water'):
            way.waterway=w.tags.get('waterway') if w.tags.get('waterway') else w.tags.get('water')
            way.access = w.tags.get('access')
            way.boat = w.tags.get('boat')
            way.barrier = w.tags.get('barrier')
            way.gnis_feature_id = w.tags.get('gnis:feature_id')
            way.gnis_state_id = w.tags.get('gnis:state_id')
            way.gnis_name = w.tags.get('gnis:name')
            way.intermittent = w.tags.get('intermittent')
            way.name = w.tags.get('name')
            way.natural = w.tags.get('natural')
            way.tunnel = w.tags.get('tunnel')
        if w.tags.get('man_made') in default_man_mades:
            way.waterway = w.tags.get('man_made')
            way.access = w.tags.get('access')
            way.boat = w.tags.get('boat')
            way.barrier = w.tags.get('barrier')
            way.gnis_feature_id = w.tags.get('gnis:feature_id')
            way.gnis_state_id = w.tags.get('gnis:state_id')
            way.gnis_name = w.tags.get('gnis:name')
            way.intermittent = w.tags.get('intermittent')
            way.name = w.tags.get('name')
            way.natural = w.tags.get('natural')
            way.tunnel = w.tags.get('tunnel')
        if w.tags.get('waterway:type'):
            way.waterway = w.tags.get('waterway:type')
            way.access = w.tags.get('access')
            way.boat = w.tags.get('boat')
            way.barrier = w.tags.get('barrier')
            way.gnis_feature_id = w.tags.get('gnis:feature_id')
            way.gnis_state_id = w.tags.get('gnis:state_id')
            way.gnis_name = w.tags.get('gnis:name')
            way.intermittent = w.tags.get('intermittent')
            way.name = w.tags.get('name')
            way.natural = w.tags.get('natural')
            way.tunnel = w.tags.get('tunnel')
        if not w.tags.get('waterway') and not w.tags.get('water'):
            if w.tags.get('natural'):
                way.waterway = w.tags.get('natural')
                way.access = w.tags.get('access')
                way.boat = w.tags.get('boat')
                way.barrier = w.tags.get('barrier')
                way.gnis_feature_id = w.tags.get('gnis:feature_id')
                way.gnis_state_id = w.tags.get('gnis:state_id')
                way.gnis_name = w.tags.get('gnis:name')
                way.intermittent = w.tags.get('intermittent')
                way.name = w.tags.get('name')
                way.natural = w.tags.get('natural')
                way.tunnel = w.tags.get('tunnel')
        self.osm_way_dict[way.osm_way_id] = way

        del w


    def relation(self, r):
        relation = Relation()
        relation.osm_relation_id = str(r.id)
        relation.name = r.tags.get('name')
        outer_ways=[]
        is_close = True
        if r.tags.get('water') or r.tags.get('waterway'):
            if r.tags.get('type') == 'multipolygon':
                try:
                    for member in r.members:
                        member_id, member_type, member_role = member.ref, member.type, member.role
                        member_id_str = str(member_id)
                        member_type_lc = member_type.lower()
                        osm_way = self.osm_way_dict[member_id_str]
                        if not osm_way.waterway:
                            osm_way.waterway = r.tags.get('water') if r.tags.get('water') else r.tags.get('waterway')
                        if member_role == 'inner' and member_type_lc == 'w':
                            self.osm_relation_inter_way_list.append(osm_way)
                        elif member_role == 'outer' and member_type_lc == 'w':
                            outer_ways.append(osm_way)
                        else:
                            if osm_way.ref_node_id_list[0] == osm_way.ref_node_id_list[-1]:
                                self.osm_relation_inter_way_list.append(osm_way)
                except:
                    is_close=False
        elif  r.tags.get('natural') and r.tags.get('natural') == 'water':
            if r.tags.get('type') == 'multipolygon':
                try:
                    for member in r.members:
                        member_id, member_type, member_role = member.ref, member.type, member.role
                        member_id_str = str(member_id)
                        member_type_lc = member_type.lower()
                        osm_way = self.osm_way_dict[member_id_str]
                        if not osm_way.waterway:
                            osm_way.waterway = r.tags.get('water') if r.tags.get('water') else r.tags.get('waterway')
                        if member_role == 'inner' and member_type_lc == 'w':
                            self.osm_relation_inter_way_list.append(osm_way)
                        elif member_role == 'outer' and member_type_lc == 'w':
                            outer_ways.append(osm_way)
                        else:
                            if osm_way.ref_node_id_list[0] == osm_way.ref_node_id_list[-1]:
                                self.osm_relation_inter_way_list.append(osm_way)
                except:
                    is_close=False
        if is_close and len(outer_ways)>0:
            outer_ways_ = [outer_ways[0]]
            outer_ways.remove(outer_ways[0])
            epochs = 0
            max_epochs = len(outer_ways) * len(outer_ways)
            while True:
                for way in outer_ways:
                    for i in range(len(outer_ways_)):
                        if way.ref_node_id_list[0] == outer_ways_[i].ref_node_id_list[-1]:
                            outer_ways_.insert(i + 1, way)
                            outer_ways.remove(way)
                            break
                        elif way.ref_node_id_list[-1] == outer_ways_[i].ref_node_id_list[-1]:
                            way.ref_node_id_list = way.ref_node_id_list[::-1]
                            outer_ways_.insert(i + 1, way)
                            outer_ways.remove(way)
                            break
                        elif way.ref_node_id_list[0] == outer_ways_[i].ref_node_id_list[0]:
                            way.ref_node_id_list = way.ref_node_id_list[::-1]
                            outer_ways_.insert(i, way)
                            outer_ways.remove(way)
                            break
                        elif way.ref_node_id_list[-1] == outer_ways_[i].ref_node_id_list[0]:
                            outer_ways_.insert(i, way)
                            outer_ways.remove(way)
                            break
                epochs += 1
                if len(outer_ways) == 0 or epochs > max_epochs:
                    break
            self.osm_relation_outer_way_list.append(outer_ways_)
        else:
            if len(outer_ways) > 0:
                self.osm_relation_outer_way_list.append(outer_ways)
        del r

def _processWays(net, h):
    for osm_way_id, osm_way in h.osm_way_dict.items():
        if osm_way.waterway:
            try:
                osm_way.ref_node_list = [net.osm_node_dict[ref_node_id] for ref_node_id in osm_way.ref_node_id_list]
                if osm_way.ref_node_list[0] == osm_way.ref_node_list[-1]:
                    osm_way.way_poi=True
                net.osm_way_dict[osm_way_id] = osm_way
            except KeyError as e:
                print(f'  warning: ref node {e} in way {osm_way_id} is not defined, way {osm_way_id} will not be imported')


def _processRelations(net, h):
    for osm_way in h.osm_relation_inter_way_list:
        try:
            osm_way.ref_node_list = [net.osm_node_dict[ref_node_id] for ref_node_id in osm_way.ref_node_id_list]
            if osm_way.ref_node_list[0] == osm_way.ref_node_list[-1]:
                osm_way.way_poi = True
            net.osm_relation_inter_way_list.append(osm_way)
        except KeyError as e:
            print(f'  warning: ref node {e} in way {osm_way.osm_way_id} is not defined, way {osm_way.osm_way_id} will not be imported')
    for osm_ways in h.osm_relation_outer_way_list:
        try:
            for osm_way in osm_ways:
                    osm_way.ref_node_list = [net.osm_node_dict[ref_node_id] for ref_node_id in osm_way.ref_node_id_list]
                    if osm_way.ref_node_list[0] == osm_way.ref_node_list[-1]:
                        osm_way.way_poi = True
            net.osm_relation_outer_way_list.append(osm_ways)
        except KeyError as e:
                print(
                    f'  warning: ref node {e} in way {osm_way.osm_way_id} is not defined, way {osm_way.osm_way_id} will not be imported')



def readOSMFile(filename,POIs,strict_mode, bbox):
    net = Network()

    net.bounds = _getBounds(filename, bbox)

    h = NWRHandler()
    h.strict_mode = strict_mode
    h.bounds = net.bounds
    h.POIs = POIs
    h.apply_file(filename)

    net.osm_node_dict=h.osm_node_dict

    _processWays(net, h)
    _processRelations(net, h)

    return net
