# -*- coding: utf-8 -*-
"""
Created on Sat Apr 11 09:40:56 2020

@author: York_king
"""
import numpy as np
import depots_deployment
import first_test_performance as fp
from myUtil import Dprint
import os
#import json
np.random.seed(0)
if __name__ == '__main__':
    ## 传感器节点的配置
    node_full_power = 1.08e4
    rate = np.random.uniform(0.3,0.8)
    node_left_power = rate*node_full_power # 初始的能量配置为0.3-0.8之间的一个均匀分布
    node_power_consume = np.random.uniform(1e-3,1e-2) # 传感器消耗的能量在这之间随机分布
    ## MC的配置
    MC_full_power = 1e6
    MC_left_power = MC_full_power
    MC_power_consume = 50  # 50 J/m or 50 J/s
    MC_v = 1
    MC_charge_rate = 5 # 给传感器充电的效率为 5J/s
    
    
    wrsn = depots_deployment.WRSNEnv()
    try:
       #a = 1/0
       with open('./data/first_algorithm.data','r') as f:
           from numpy import array
           result = eval(f.read())
           #print(result)
           mc_nums = result['mc_nums']
           depot_pos_set = result['depot_pos_set']
           sensors_depart_set = result['sensors_depart_set']
           num_mc_set = result['num_mc_set']
    except:
        mc_nums, depot_pos_set, num_mc_set, sensors_depart_set = wrsn.optimal_deployment()
        result = {'mc_nums':mc_nums, 'depot_pos_set':depot_pos_set, \
                  'sensors_depart_set':sensors_depart_set, 'num_mc_set':num_mc_set}
        with open('./data/first_algorithm.data','w') as f:
            f.write(str(result))
    
    cycle = 60
    for index in range(len(depot_pos_set)):
        
        depot_site = depot_pos_set[index]
        MCList = []
        for i in range(num_mc_set[index]):
            #def __init__(self, _axis,_full_power,_left_power, _power_consume, _v,_charge_rate,_time=0.0):
            mc = fp.MC(depot_site,MC_full_power,MC_left_power,MC_power_consume,MC_v,MC_charge_rate,cycle)
            MCList.append(mc)
        
        ## 初始化传感器节点
        NodeList = []
        #(self,_axis,_full_power,_left_power, _power_consume,_dead_time=0.0):
        #edge_size = 300
        node_nums = len(sensors_depart_set[index])
        for i in range(node_nums):
            axis = wrsn.loc_nodes[sensors_depart_set[index][i]]
            #Dprint(axis)
            rate = np.random.uniform(0.3,0.8)
            power_consume = np.random.uniform(1e-3,1e-2)
            # def __init__(self,_axis,_full_power,_left_power, _power_consume,_dead_time=0.0):
            node = fp.Node(axis,node_full_power,rate*node_full_power,power_consume)
            NodeList.append(node)
            
        
            
            
        area = fp.Area(MCList,NodeList,depot_site)
        #print("for the "+str(index)+" area")
        
        epochs = 1000
        for epoch in range(epochs):
            charge_sum_before = 0
            # print(MCList[0].)
            total_sum = len(area.NodeSets)*area.NodeSets[0].full_power
            for i in area.NodeSets:
                charge_sum_before += i.left_power
            node_dead_num, node_lived_num, charge_power, travel_power= area.chargeAlgorithm('dist')
            
            
            charge_sum_after = 0
            for i in area.NodeSets:
                
                charge_sum_after += i.left_power
            
            
           
            if charge_power+travel_power == 0:
                eff_rate = 1
            else:
                print(area)
                print("depot_pos_set_index:%d"%index)
                print("the %d rounds"%(epoch))
                print("node_dead_num:",node_dead_num," node_lived_num:",node_lived_num)
                print("charge_power:",charge_power,"travel_power:",travel_power)
                eff_rate =  charge_power/(charge_power+travel_power)
                print("efficiency rate:", eff_rate)
                print("charge_sum_before_precent:",charge_sum_before/total_sum)
                print("charge_sum_after_precent:",charge_sum_after/total_sum)
                print("-------------------------------------------------\n")
            
            
            for i in area.NodeSets:
                i.left_power-=i.power_consume*cycle
            for i in area.MCsets:
                if i.cycle<=0:
                    i.cycle+=cycle
                else:
                    i.cycle=cycle
          
        
        
