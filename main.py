# -*- coding: utf-8 -*-
# @Time    : 2022/1/6 10:45
# @Author  : Praise
# @File    : main.py
# obj:
import osm2water as o2w

net=o2w.get_network_from_file(filename='../osm/salt river.osm')
o2w.showNetwork(net,savefig=True,output_folder='salt river')
o2w.saveNetwork(net,output_folder='salt river')