# -*- coding: utf-8 -*-
"""
Created on Fri Apr 24 19:52:51 2020
@author: York_king
"""
import numpy as np
from myUtil import Dprint 
class MC(object):
    #1e6,1e6,50,1,5
    def __init__(self, _axis, _full_power=1e6, _left_power=1e6, _power_consume=50,  _v=1 ,_charge_rate=5 ,_time=0.0):
        self.time = _time
        self.axis = _axis
        self.power_consume = _power_consume
        self.left_power = _left_power
        self.v = _v
        self.charge_rate = _charge_rate
        self.full_power = _full_power
        
        
        #new code
        #self.travel_cons_rate = _travel_cons_rate

class Node(object):
    def __init__(self,_axis,_full_power,_left_power, _power_consume,_dead_time=0.0):
        self.dead_time = _dead_time
        self.axis = _axis
        self.left_power = _left_power
        self.power_consume = _power_consume
        self.full_power = _full_power
        
        
    #new code
    def power_need_charge(self, time):
        #这里的time是MC充完电后的时刻，之所以这样是因为假定初始时间为0
        return self.full_power - self.left_power + self.power_consume * time

class Area(object):
    def __init__(self,MCList, NodeList,_depot_site):
        self.MCsets = MCList
        self.NodeSets = NodeList
        self.ask_charge_thre = 0.3
        self.depot_site = _depot_site
        
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
        mc=self.MCsets[0]
        while counter<charge_node_num:
            ok, MC_temp, node_temp = self.charge_is_ok(mc,chargeList[counter])
            
            if not ok:#如果该节点无法救活
                del chargeList[counter]#删除该节点
                charge_node_num-=1
                node_dead_num += 1
            else:
                counter+=1
                
        Dprint("chargeList",chargeList)
        #开始为充电请求队列安排MC进行充电
        mc_num = 0
        travel_power=0
        charge_power=0
        
        MCnum=len( self.MCsets )
        
        while len(chargeList)>=1 and mc_num<MCnum:
            #选择距离当前MC最近的节点
            choose_node_index=0
            choose_node_dist=self.getDist(mc.axis, chargeList[0].axis)
            
            for i in range(1, len(chargeList) ):
                i_dist = self.getDist(mc.axis, chargeList[i].axis)
                if choose_node_dist > i_dist:
                    choose_node_index = i
                    choose_node_dist = i_dist
            
            #判断当前MC是否可以为最近的节点充电
            ok, MC_temp, node_temp = self.charge_is_ok(mc,chargeList[ choose_node_index ])
            
            if ok:
                #更新
                mc = MC_temp
                
                '''
                Dprint('aaa')
                Dprint( choose_node_dist )
                Dprint( mc.power_consume )
                
                Dprint( chargeList[ choose_node_index ].full_power )
                Dprint( chargeList[ choose_node_index ].left_power )
                Dprint( chargeList[ choose_node_index ].power_consume )
                Dprint( mc.time )
                
                Dprint( chargeList[ choose_node_index ].power_need_charge( mc.time ) )
                '''
                
                travel_power += choose_node_dist * mc.power_consume
                charge_power += chargeList[ choose_node_index ].power_need_charge( mc.time )
                chargeList[ choose_node_index ] = node_temp
                del chargeList[ choose_node_index ]
            else:
                #开始一个新的巡回
                mc_num+=1
                mc=self.MCsets[mc_num]
        
        #计算存活率
        node_dead_num += len(chargeList)
        node_num = len( self.NodeSets )
        live_rate = (node_num-node_dead_num)/node_num
        
        #计算充电效率
        '''
        Dprint( charge_power )
        Dprint( travel_power )
        '''
        
        if charge_power + travel_power > 0:
            eff_rate = charge_power / (charge_power + travel_power)
        else:
            eff_rate = -1

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
        if time_to + MC.time > node.dead_time:
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
    MC_nums = 10
    depot_site = np.array([200,200])
    MCList = []
    for i in range(MC_nums):
        #def __init__(self, _axis,_full_power,_left_power, _power_consume, _v,_charge_rate,_time=0.0):
        mc = MC(depot_site,1e6,1e6,50,1,5)
        MCList.append(mc)
    
    ## 初始化传感器节点
    node_nums = 100
    NodeList = []
    #(self,_axis,_full_power,_left_power, _power_consume,_dead_time=0.0):
    edge_size = 300
    for i in range(node_nums):
        axis = np.random.uniform(0.0,edge_size, size=(1,2)).reshape(2)
        rate = np.random.uniform(0.15,0.8)
        power_consume = 50
        node = Node(axis,1.08e4,rate*1.08e4,power_consume)
        NodeList.append(node)
    
    ## 随机运行一段时间？？？其实和之
        
    area = Area(MCList,NodeList,depot_site)
    
    print("live rate, efficiency rate: ", area.chargeAlgorithm())
