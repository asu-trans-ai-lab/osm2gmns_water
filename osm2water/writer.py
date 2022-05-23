
import csv
import os

def saveNetwork(network, output_folder='csvfile', enconding=None):
    if output_folder:
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        node_filepath = os.path.join(output_folder, 'node.csv')
        link_filepath = os.path.join(output_folder, 'link.csv')
        poi_filepath = os.path.join(output_folder, 'poi.csv')
    else:
        node_filepath = 'node.csv'
        link_filepath = 'link.csv'
        poi_filepath = 'poi.csv'

    try:
        if enconding is None:
            outfile = open(node_filepath, 'w', newline='', errors='ignore')
        else:
            outfile = open(node_filepath, 'w', newline='', errors='ignore', encoding=enconding)

        write = csv.writer(outfile)
        write.writerow(['name', 'node_id', 'osm_node_id','x_coord', 'y_coord', 'geometry'])

        for node_id, node in network.node_dict.items():
            name = node.name if node.name else ''
            geometry = node.geometry.wkt
            line = [name, node.node_id, node.osm_node_id, node.x_coord, node.y_coord, geometry]
            write.writerow(line)
        outfile.close()
    except PermissionError:
        print('node.csv may be locked by other programs. please release it then try again')

    try:
        if enconding is None:
            outfile = open(link_filepath, 'w', newline='', errors='ignore')
        else:
            outfile = open(link_filepath, 'w', newline='', errors='ignore', encoding=enconding)

        write = csv.writer(outfile)
        write.writerow(['name', 'link_id', 'osm_way_id', 'from_node_id', 'to_node_id', 'link_type_name','dir_flag',
                        'access','boat','capacity', 'gnis_feature_id', 'gnis_state_id', 'gnis_name', 'intermittent',
                        'tunnel','lanes','length', 'free_speed','geometry'])
        for link_id, link in network.link_dict.items():
            name = link.name if link.name else ''
            link_type_name = link.link_type_name if link.link_type_name else ''
            access = link.access if link.access else ''
            boat=link.boat if link.boat else ''
            capacity=link.capacity if link.capacity else ''
            gnis_feature_id = link.gnis_feature_id if link.gnis_feature_id else ''
            gnis_state_id = link.gnis_state_id if link.gnis_state_id else ''
            gnis_name = link.gnis_name if link.gnis_name else ''
            intermittent = link.intermittent if link.intermittent else ''
            tunnel = link.tunnel if link.tunnel else ''
            free_speed = link.free_speed if link.free_speed else ''
            line = [name, link.link_id, link.osm_way_id, link.from_node.node_id, link.to_node.node_id,link_type_name,
                    link.dir_flag,access,boat,capacity,gnis_feature_id,gnis_state_id,gnis_name,intermittent,
                    tunnel,link.lanes,link.length,free_speed,link.geometry.wkt]
            write.writerow(line)
        outfile.close()
    except PermissionError:
        print('link.csv may be locked by other programs. please release it then try again')

    try:
        if len(network.POI_list):
            if enconding is None:
                outfile = open(poi_filepath, 'w', newline='', errors='ignore')
            else:
                outfile = open(poi_filepath, 'w', newline='', errors='ignore', encoding=enconding)

            write = csv.writer(outfile)
            write.writerow(['name', 'poi_id', 'osm_way_id', 'waterway','barrier','area','centroid', 'geometry'])

            for poi in network.POI_list:
                name = ' ' + poi.name if poi.name else ''
                barrier=poi.barrier if poi.barrier else ''
                line = [name, poi.poi_id, poi.osm_way_id, poi.waterway,barrier,poi.area,poi.centroid.wkt, poi.geometry.wkt]
                write.writerow(line)
            outfile.close()
    except PermissionError:
        print('poi.csv may be locked by other programs. please release it then try again')

