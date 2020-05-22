# -*- coding: utf-8 -*-
"""
Created on Fri Apr 24 19:52:51 2020
@author: York_king
"""
import numpy as np
from myUtil import Dprint 
import functools
import copy
class MC(object):
    #1e6,1e6,50,1,5
    def __init__(self, _axis, _full_power=1e6, _left_power=1e6, _power_consume=50,  _v=1 ,_charge_rate=5 ,_time=0.0,_cycle = 60):
        self.time = _time
        self.axis = _axis
        self.power_consume = _power_consume
        self.left_power = _left_power
        self.v = _v
        self.charge_rate = _charge_rate
        self.full_power = _full_power
        self.cycle = _cycle
        
        
        #new code
        #self.travel_cons_rate = _travel_cons_rate

class Node(object):
    def __init__(self,_axis,_full_power,_left_power, _power_consume,_dead_time=0.0,_time = 0.0):
        self.dead_time = _dead_time
        self.axis = _axis
        self.left_power = _left_power
        self.power_consume = _power_consume
        self.full_power = _full_power
        self.time = _time
    def __str__(self):
        return "Object Node:\n" \
            + "{\ndead_time: "+str(self.dead_time)+"\n" \
            + "axis: "+str(self.axis) + "\n" \
            + "left_power: "+(str(self.left_power)) + "\n" \
            + "power_consume: " + str(self.power_consume) + "\n" \
            + "full_power: " + str(self.full_power) + "\n" \
            + "}"
    #new code
    def power_need_charge(self, time):
        #print(self.__str__())
        #这里的time是MC充完电后的时刻，之所以这样是因为假定初始时间为0
        return self.full_power - self.left_power + self.power_consume * time
    __repr__ = __str__
        
class Area(object):
    def __init__(self,MCList, NodeList,_depot_site):
        self.MCsets = MCList
        self.NodeSets = NodeList
        self.ask_charge_thre = 0.3
        self.depot_site = _depot_site
    def __str__(self):
        return "Area object:\n " + \
        "{\n" + \
        "depots nums:" + "1" +"\n" + \
        "MC nums:" + str(len(self.MCsets)) + "\n" + \
        "node nums:" + str(len(self.NodeSets)) + "\n" + \
        "}" 
        
    
    def getDist(self,axis1,axis2):
        return ((axis1[0]-axis2[0])**2 + (axis1[1]-axis2[1])**2)**0.5
    
    def get_priority_value(self, node, mc, choose_way):
        #得到节点关于MC的优先值（用于选择充电节点）
        if choose_way=='dist':
            return self.getDist(mc.axis, node.axis)
        elif choose_way=='electricity':
            return node.left_power
        
    
    def chargeAlgorithm(self, choose_way):
        
        ## NodeSets时间的初始化, MCsets的初始化
        
        for index,node in enumerate(self.NodeSets):
            self.NodeSets[index].time = 0
        
        for index,mc in enumerate(self.MCsets):
            self.MCsets[index].time = 0
            self.MCsets[index].left_power = self.MCsets[index].full_power
        
        
        ## 当存在一个节点电量小于30%以下时，调用该函数，将60%以下的节点进入充电队列,保存了node
        chargeList = []
        for index,node in enumerate(self.NodeSets):
            if node.left_power <= 0.6*node.full_power:
                chargeList.append([node,index])
                #node_to_index[node] = index
        
        Dprint("chargeList1",len(chargeList))
        ## 剔除那些无法救活的节点
        ## Your codes are here
        node_dead_num = 0
        print("chargeList_len:",len(chargeList))
        charge_node_num=len(chargeList)
        counter=0
        mc=self.MCsets[0]
        while counter<charge_node_num:
            ok, MC_temp, node_temp = self.charge_is_ok(mc,chargeList[counter][0])
            
            if not ok:#如果该节点无法救活
                del chargeList[counter]#删除该节点
                charge_node_num-=1
                node_dead_num += 1
            else:
                counter+=1
                
        Dprint("chargeList2",chargeList)
        
        print("del_after_chargeList_len:",len(chargeList))
        '''
        充电算法：遍历MC列表，每个MC选择最优先的节点进行充电，当充电请求队列被处理完或者遍历一遍MClist后
        无充电节点被处理则跳出循环
        '''
        #开始为充电请求队列安排MC进行充电
        travel_power=0
        total_consume = 0.0
        charge_power=0
        #初始化被充电的节点数量
        charged_node_num = 0
        
        while len(chargeList)>=1:
            solve_node_num = 0 # 本次循环解决充电请求的节点数量计数
            
            #遍历MC列表（这里是self里的，因此是引用，可以通过mc直接改变MC列表里的mc）
            for index0, mc in enumerate(self.MCsets):
                if (len(chargeList)==0):
                    break
                #初始化对于当前MC最优先的节点index
                choose_node_index=0
                #选中节点的优先值
                choose_node_priority = self.get_priority_value( chargeList[0][0], mc, choose_way)
                
                #遍历充电请求队列来选择最优先的节点index
                for i in range(1, len(chargeList) ):
                    i_priority = self.get_priority_value( chargeList[i][0], mc, choose_way)
                    if choose_node_priority > i_priority:#比较节点之间的优先值
                        choose_node_index = i
                        choose_node_priority = i_priority
                        
                Dprint("mc.axis",mc.axis)
                Dprint("chargeList[ choose_node_index ].axis",chargeList[ choose_node_index ][0].axis)
                #判断当前MC是否可以为最近的节点充电
                ok, MC_temp, node_temp = self.charge_is_ok(mc,chargeList[ choose_node_index ][0])
                
                if ok:
                    # print("OK")
                    self.NodeSets[chargeList[ choose_node_index ][1]].time = MC_temp.time
                    charged_node_num += 1#被充电的节点数量加一
                    solve_node_num += 1#该循环中被充电的节点数量加一
                    
                    Dprint("update")
                    #更新

                    #计算选中节点的距离
                    choose_node_dist = self.getDist(mc.axis, chargeList[ choose_node_index ][0].axis)
                    # mc = MC_temp
                    Dprint("mc.axis",mc.axis)
                    Dprint("chargeList[ choose_node_index ].axis",chargeList[ choose_node_index ][0].axis)
                    Dprint("choose_node_dist",choose_node_dist)
                    
                    #计算本次充电所花费的旅程电量和充电电量
                    #travel_power += choose_node_dist * mc.power_consume
                    # print(travel_power)
                    # print(choose_node_dist * mc.power_consume)
                    charge_power += node_temp.left_power - chargeList[ choose_node_index ][0].left_power
                    
                    #更新节点和MC
                    self.NodeSets[ chargeList[ choose_node_index ][1]] = node_temp
                    self.MCsets[index0] = MC_temp
                    #print("169***")
                    del chargeList[ choose_node_index ]
                    mc = copy.deepcopy(MC_temp)
                
                    
                
            
            if solve_node_num == 0:
                Dprint("MC charge is over.")
                break
        
        ## 节点和MC的时间同步
        After_time = 0
        for i in self.MCsets:
            After_time = max(After_time,i.time)
            
        for index, node in enumerate(self.NodeSets):
            self.NodeSets[index].left_power -= (After_time - self.NodeSets[index].time)*self.NodeSets[index].power_consume
            self.NodeSets[index].time = After_time
            
        for index,MC in enumerate(self.MCsets):
            self.MCsets[index].time = After_time
        
        ## by the way
        travelpower,chargepower= self.bytheway()
        
        ## 再次同步
        After_time = 0
        for i in self.MCsets:
            After_time = max(After_time,i.time)
            
        for index, node in enumerate(self.NodeSets):
            self.NodeSets[index].left_power -= (After_time - self.NodeSets[index].time)*self.NodeSets[index].power_consume
            self.NodeSets[index].time = After_time
            
        for index,MC in enumerate(self.MCsets):
            total_consume += (MC.full_power-MC.left_power)
            self.MCsets[index].time = After_time
        
        
        # print(travelpower)
        # print(travel_power)
        travel_power += travelpower
        charge_power += chargepower
        
        #print("16 charge_power:",charge_power)
        #计算死亡节点
        node_dead_num += len(chargeList)
        #计算存活节点
        node_num = len( self.NodeSets )
        node_lived_num = node_num-node_dead_num
        
        '''
        Dprint( charge_power )
        Dprint( travel_power )
        '''
        Dprint("travel_power",travel_power)
        return node_dead_num, node_lived_num, charge_power, total_consume, charged_node_num,After_time
    
    def charge_is_ok(self, mc, Node):
        '''
            MC: MC class
            node: Node class
            
            returns: True, MC, node,cycle
            该函数判断当前状态的MC从当前位置出发给node节点充电，是否满足条件;
            cycle用来判断MC是因为周期时间到了还是因为电量原因而无法充电
            如果满足，返回True, MC到达那里后给node充完电的状态，包括更新自身时间、能量、坐标，同时也更新了node的状态
            建议调用的时候这样写:
            ok, MC_temp, node_temp,cycle = self.charge_is_ok(MC,node)
            if ok: 
                # 这样便把MC的状态和node充完电状态更新了
                MC = MC_temp
                node = node_temp
        '''
        '''
        5.2日更新
        此处mc应该使用深拷贝，否则会导致对原有数据进行改变
        '''
        MC = copy.deepcopy(mc)
        node = copy.deepcopy(Node)
        ## MC从当前位置出发去node的时间
        dist = self.getDist(MC.axis, node.axis)
        Dprint("dist",dist)
        time_to = dist/MC.v
        
        ## 去的能量消耗
        MC_travel_power = time_to * MC.power_consume
        MC.left_power -=  MC_travel_power
        MC.time += time_to
        if MC.left_power <= 0:
            return False,None,None
        
        ## 这段时间node的消耗
        node.left_power = node.left_power - node.power_consume * (MC.time-node.time)
        if(node.left_power<0):
            return False, None, None
        
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
        node.time = MC.time
        
        return True, MC, node

    def bytheway(self):
        ##将80%以下的节点进入充电队列,保存了node
        chargeList = []
        for index,node in enumerate(self.NodeSets):
            if node.left_power <= 0.8*node.full_power:
                chargeList.append([node,index])
                #node_to_index[node] = index
        
        Dprint("chargeList1",len(chargeList))
        ## 剔除那些无法救活的节点
        ## Your codes are here
        node_dead_num = 0
        # dispose_list = []
        # Dis_MAX = -1
        # Charge_MAX = -1
        # for i in chargeList:
        #     Dis_MAX = max(Dis_MAX,self.getDist(MC.axis, i_node.axis))
        
        charge_node_num=len(chargeList)
        counter=0
        mc=self.MCsets[0]
        while counter<charge_node_num:
            ok, MC_temp, node_temp = self.charge_is_ok(mc,chargeList[counter][0])
            
            if not ok:#如果该节点无法救活
                del chargeList[counter]#删除该节点
                charge_node_num-=1
                node_dead_num += 1
            else:
                counter+=1
                
        Dprint("chargeList2",chargeList)
        
        
        
        
        
        '''
        充电算法：遍历MC列表，每个MC选择最优先的节点进行充电，当充电请求队列被处理完或者遍历一遍MClist后
        无充电节点被处理则跳出循环
        '''
        #开始为充电请求队列安排MC进行充电
        travel_power=0
        charge_power=0
        #初始化被充电的节点数量
        charged_node_num = 0
        
        while len(chargeList)>=1:
            solve_node_num = 0 # 本次循环解决充电请求的节点数量计数
            
            #遍历MC列表（这里是self里的，因此是引用，可以通过mc直接改变MC列表里的mc）
            for index0, mc in enumerate(self.MCsets):
                if (len(chargeList)==0):
                    break
                #初始化对于当前MC最优先的节点index
                choose_node_index=-1
                choose_node_priority = 1e10
                dispose_list = []
                Dis_MAX = -1
                Charge_MAX = -1
                for i in chargeList:
                    Dis_MAX = max(Dis_MAX,self.getDist(mc.axis, i[0].axis))
                    Charge_MAX = max(Charge_MAX,i[0].left_power)
                #遍历充电请求队列来选择最优先的节点index
                for i in range(len(chargeList)):
                    if self.getDist(chargeList[i][0].axis,mc.axis)==0:
                        continue
                    i_priority = chargeList[i][0].left_power*Charge_MAX/(self.getDist(chargeList[i][0].axis,mc.axis)*Dis_MAX)
                    if choose_node_priority < i_priority:#比较节点之间的优先值
                        choose_node_index = i
                        choose_node_priority = i_priority
                        
                Dprint("mc.axis",mc.axis)
                Dprint("chargeList[ choose_node_index ].axis",chargeList[ choose_node_index ][0].axis)
                #判断当前MC是否可以为最近的节点充电
                ok, MC_temp, node_temp = self.charge_is_ok(mc,chargeList[ choose_node_index ][0])
                
                if ok:
                    charged_node_num += 1#被充电的节点数量加一
                    solve_node_num += 1#该循环中被充电的节点数量加一
                    
                    Dprint("update")
                    #更新

                    #计算选中节点的距离
                    choose_node_dist = self.getDist(mc.axis, chargeList[ choose_node_index ][0].axis)
                    # mc = MC_temp
                    Dprint("mc.axis",mc.axis)
                    Dprint("chargeList[ choose_node_index ].axis",chargeList[ choose_node_index ][0].axis)
                    Dprint("choose_node_dist",choose_node_dist)
                    
                    #计算本次充电所花费的旅程电量和充电电量
                    travel_power += choose_node_dist * mc.power_consume
                    charge_power += node_temp.left_power - chargeList[ choose_node_index ][0].left_power
                    
                    #更新节点和MC
                    self.NodeSets[ chargeList[ choose_node_index ][1]] = node_temp
                    self.MCsets[index0] = MC_temp
                    #print("169***")
                    del chargeList[ choose_node_index ]
                    mc = copy.deepcopy(MC_temp)
                    
                
            
            if solve_node_num == 0:
                Dprint("MC charge is over.")
                break
        
        return travel_power,charge_power

            
            
            
        
    __repr__ = __str__  
            
        
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
        rate = np.random.uniform(0.3,0.8)
        power_consume = np.random.uniform(1e-3,1e-2)
        node = Node(axis,1.08e4,rate*1.08e4,power_consume)
        NodeList.append(node)
    
    ## 随机运行一段时间？？？其实和之
        
    area = Area(MCList,NodeList,depot_site)
    
    print("electricity node_dead_num, node_lived_num, charge_power, travel_power: ", area.chargeAlgorithm('electricity'))
    print("dist node_dead_num, node_lived_num, charge_power, travel_power: ", area.chargeAlgorithm('dist'))
