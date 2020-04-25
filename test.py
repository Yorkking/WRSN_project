# -*- coding: utf-8 -*-
"""
Created on Sat Apr 11 09:40:56 2020

@author: York_king
"""
import numpy as np
import depots_deployment
import first_test_performance as fp
from myUtil import Dprint
#import json

if __name__ == '__main__':
    
    
    try:
       with open('./data/first_algorithm.data','r') as f:
           from numpy import array
           result = eval(f.read())
           #print(result)
           mc_nums = result['mc_nums']
           depot_pos_set = result['depot_pos_set']
           sensors_depart_set = result['sensors_depart_set']
           num_mc_set = result['num_mc_set']
    except:
    
        wrsn = depots_deployment.WRSNEnv()
        
        mc_nums, depot_pos_set, num_mc_set, sensors_depart_set = wrsn.optimal_deployment()
        result = {'mc_nums':mc_nums, 'depot_pos_set':depot_pos_set, \
                  'sensors_depart_set':sensors_depart_set, 'num_mc_set':num_mc_set}
        with open('./data/first_algorithm.data','w') as f:
            f.write(str(result))
    
    
    for index in range(len(depot_pos_set)):
        
        depot_site = depot_pos_set[index]
        MCList = []
        for i in range(num_mc_set[index]):
            #def __init__(self, _axis,_full_power,_left_power, _power_consume, _v,_charge_rate,_time=0.0):
            mc = fp.MC(depot_site,1e6,1e6,50,1,5)
            MCList.append(mc)
        
        ## 初始化传感器节点
        NodeList = []
        #(self,_axis,_full_power,_left_power, _power_consume,_dead_time=0.0):
        #edge_size = 300
        node_nums = len(sensors_depart_set[index])
        for i in range(node_nums):
            axis = wrsn.loc_nodes[sensors_depart_set[index][i]]
            #Dprint(axis)
            rate = np.random.uniform(0.15,0.8)
            power_consume = 50
            node = fp.Node(axis,1.08e4,rate*1.08e4,power_consume)
            NodeList.append(node)
            
        area = fp.Area(MCList,NodeList,depot_site)
        live_rate, eff_rate = area.chargeAlgorithm()
        
        print("live rate",live_rate,"efficiency rate:", eff_rate)
        