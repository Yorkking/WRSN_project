# -*- coding: utf-8 -*-
"""
Created on Fri Apr 24 19:52:51 2020

@author: York_king
"""
import numpy as np

class MC(object):
    def __init__(self,_time, _axis,_left_power, _power_consume, _v,_charge_rate,_full_power):
        self.time = _time
        self.axis = _axis
        self.power_consume = _power_consume
        self.left_power = _left_power
        self.v = _v
        self.charge_rate = _charge_rate
        self.full_power = _full_power
        
        
        #new code
        self.travel_cons_rate = travel_cons_rate

class Node(object):
    def __init__(self,_dead_time,_axis,_left_power, _power_consume,_full_power,depot_site):
        self.dead_time = _dead_time
        self.axis = _axis
        self.left_power = _left_power
        self.power_consume = _power_consume
        self.full_power = _full_power
        self.depot_site
        
    #new code
    def power_need_charge(self, time):
        #这里的time是MC充完电后的时刻，之所以这样是因为假定初始时间为0
        return self.full_power - self.left_power - self.power_consume * time

class Area(object):
    def __init__(self,MCList, NodeList):
        self.MCsets = MCList
        self.NodeSets = NodeList
        self.ask_charge_thre = 0.3
        
    def getDist(self,axis1,axis2):
        return ((axis1[0]-axis2[0])**2 + (axis1[1]-axis2[1])**2)**0.5
    
    def chargeAlgorithm(self):
        
        ## 存活率，充电效率
        live_rate, eff_rate = 0.0, 0.0
        
        ## 设置NodeSets的死亡时间
        for index,node in enumerate(self.NodeSets):
            self.NodeSets[index].dead_time = (node.left_power)/node.power_consume
        
        
        ## 警戒线以下的节点进入充电队列,保存了node
        chargeList = []
        for index,node in enumerate(self.NodeSets):
            if node.left_power <= 0.3*node.full_power:
                chargeList.append(node)
        
        ## 剔除那些无法救活的节点
        ## Your codes are here
        node_dead_num = 0
        
        charge_node_num=len(chargeList)
        counter=0
        mc=MC()
        while counter<charge_node_num:
            ok, MC_temp, node_temp = self.charge_is_ok(mc,chargeList[counter])
            
            if not ok:#如果该节点无法救活
                del chargeList[counter]#删除该节点
                charge_node_num-=1
                node_dead_num += 1
            else:
                counter+=1
                
        #开始为充电请求队列安排MC进行充电
        mc_num = 0
        travel_power=0
        charge_power=0
        
        while len(chargeList)!=0 or mc_num<self.MCnum:
            #选择距离当前MC最近的节点
            choose_node_index=0
            choose_node_dist=dist(mc.axis, chargeList[0].axis)
            
            for i in range(1, len(chargeList) ):
                i_dist = dist(mc.axis, chargeList[i].axis)
                if choose_node_dist > i_dist:
                    choose_node_index = i
                    choose_node_dist = i_dist
            
            #判断当前MC是否可以为最近的节点充电
            ok, MC_temp, node_temp = self.charge_is_ok(mc,chargeList[ choose_node_index ])
            
            if ok:
                #更新
                mc = MC_temp
                travel_power += choose_node_dist * mc.travel_cons_rate
                charge_power += chargeList[ choose_node_index ].power_need_charge( mc.time )
                chargeList[ choose_node_index ] = node_temp
                del chargeList[ choose_node_index ]
            else:
                #开始一个新的巡回
                mc_num+=1
                mc=MC()
        
        #计算存活率
        node_dead_num += len(chargeList)
        node_num = len( self.NodeList )
        live_rate = (node_num-node_dead_num)/node_num
        
        #计算充电效率
        eff_rate = charge_power / (charge_power + travel_power)

        return live_rate, eff_rate
    
    def charge_is_ok(self, MC, node):
        '''
            MC: MC class
            node: Node class
            
            returns: True, MC, node
            该函数判断当前状态的MC从当前位置出发给node节点充电，是否满足条件;
            如果满足，返回True, MC到达那里后给node充完电的状态，包括更新自身时间、能量、坐标，同时也更新了node的状态
            建议调用的时候这样写:
            ok, MC_temp, node_temp = self.charge_is_ok(MC,node)
            if ok: 
                # 这样便把MC的状态和node充完电状态更新了
                MC = MC_temp
                node = node_temp
                
        '''
        
        ## MC从当前位置出发去node的时间
        dist = self.getDist(MC.axis, node.axis)
        time_to = dist/MC.v
        if time_to + MC.time > node.deadtime:
            return False,None,None
        ## 去的能量消耗
        MC_travel_power = time_to * MC.power_consume
        MC.left_power -=  MC_travel_power
        MC.time += time_to
        if MC.left_power <= 0:
            return False,None,None
        
        ## 无法充满电
        if node.full_power - node.left_power > MC.left_power:
            return False,None,None
        
        ## 充电的时间消耗和能量消耗
        time_charge = (node.full_power - node.left_power)/MC.charge_rate
        MC.time += time_charge
        MC.left_power -= node.full_power - node.left_power
        dist_depot = self.getDist(MC.axis,self.depot_site)
        
        ## 如果直接回depot的能量都没有了，也返回False
        back_depot_power = dist_depot/MC.v * MC.power_consume
        if MC.left_power - back_depot_power <= 0:
            return False,None,None
        
        ## 如果成功，更新MC的坐标，以及node的剩余电量
        MC.axis = node.axis       
        node.left_power = node.full_power
        
        return True, MC, node
        
        
        
        
        
        
        
        
if __name__ == '__main__':
    
    
    ## 这部分的初始化得利用之前我们聚类等算法的结果，先不初始化
    ## todo by shuitang
    ## 初始化MCList
    MCList = []
    ## 初始化传感器节点
    NodeList = []
    
    area = Area(MCList,NodeList)
    
    print(area.chargeAlgorithm())
    
    
    
    
    
    
    
    
    
