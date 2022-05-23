
from .utils import get_distance_from_coord
from shapely import geometry

class Node():
    def __init__(self):
        self.name = None
        self.node_id = 0
        self.osm_node_id = None

        self.x_coord=None
        self.y_coord=None
        self.geometry = None


        self.in_region=True

        self.valid = False

        self.incoming_link_list = []
        self.outgoing_link_list = []

class Link():
    def __init__(self):
        self.access=None
        self.boat=None
        self.capacity=None
        self.dir_flag = 2
        self.lanes=1
        self.from_node = None
        self.gnis_feature_id=None
        self.gnis_state_id=None
        self.gnis_name=None
        self.geometry_str=None
        self.geometry = None
        self.intermittent=None
        self.link_id = 0
        self.link_type_name = None
        self.length=None
        self.free_speed= None
        self.name = ''
        self.osm_way_id = None
        self.to_node = None
        self.tunnel=None


    def calculateLength(self):
        self.length=get_distance_from_coord(self.from_node.x_coord,self.from_node.y_coord,
                                              self.to_node.x_coord,self.to_node.y_coord) * 1000
    def generate_geometry(self):
        self.geometry=geometry.LineString([self.from_node.geometry,self.to_node.geometry])

class POI():
    def __init__(self):
        self.area=None
        self.barrier=None
        self.geometry = None
        self.name=None
        self.osm_way_id=None
        self.poi_id=0
        self.waterway=None
        self.centroid=None
        self.ref_node_list=[]

    def generate_geometry(self):
        try:
            self.geometry = geometry.Polygon(self.ref_node_list)
        except:
            self.geometry=None

class Way():
    def __init__(self):
        self.access=None
        self.boat=None

        self.barrier=None

        self.gnis_feature_id=None
        self.gnis_state_id=None
        self.gnis_name=None

        self.geometry_str=None
        self.geometry = None

        self.intermittent=None
        self.name = ''
        self.natural=None
        self.osm_way_id = None
        self.ref_node_list=[]
        self.tunnel=None

        self.waterway=None
        self.way_poi=None
        self.man_made=None
        self.ref_node_list = []

class Relation:
    def __init__(self):
        self.osm_relation_id = None
        self.member_list = []
        self.node_dict = {}
        self.way_dict = {}
        self.name = ''
        self.waterway = None


class Network():
    def __init__(self):
        self.bounds = None

        self.osm_node_dict = {}
        self.osm_way_dict = {}
        self.osm_relation_inter_way_list =[]
        self.osm_relation_outer_way_list = []

        self.node_dict = {}
        self.link_dict = {}
        self.POI_list = []


        self.central_lon=None

        self.number_of_links=0
