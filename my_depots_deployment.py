# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 08:42:44 2020
@author: DELL
"""
import numpy as np
import copy

############################下面两个函数是功能函数，无需加入类。。。吧？


def dist(loc_i, loc_j):
    #计算i和j的距离，i和j的位置是np.array类型
    loc = loc_i-loc_j
    loc = loc * loc
    
    return np.sqrt( loc.sum() )


def get_span_tree_and_leaves( node_list ):
    '''
    输入：
        node_list：类型为list，是节点列表，其中第一个节点是充电桩，里面的元素是np.array([x,y])
    输出：
        tree_dict：最小生成树相关的字典，键是子节点，值是父节点（元素是节点的索引1）
        leaf_node_list：叶节点列表（元素是节点的索引1）
    '''
    #输入是节点列表，其中第一个节点是充电桩；输出是树的字典和叶子集合（）
    
    #得到距离数组，并存储起来
    size=len(node_list)
    dist_array=np.zeros((size, size))#第一个位置是充电桩，然后第二个位置是node_list第一个节点。。。
    not_leaf_list=[0 for i in range(1,size)]#判断不是叶节点的列表，若为1，则不是叶节点
    remain_node_list=[i for i in range(1,size)]#未加入树的节点列表
    tree_node_list=[0]#加入树的节点列表
    
    for i in range(size):
        for j in range(i):
            dist_array[i][j]=dist( node_list[i] , node_list[j] )
            dist_array[j][i]=dist_array[i][j]
    
    
    tree_dict={}#字典，键是子节点，值是父节点
    
    for counter in range(size-1):
        node=remain_node_list[0]
        f_node=0#根
        lowcost=dist_array[ 0 ][ node ]
        
        for i in remain_node_list:#存留的节点集合
            for j in tree_node_list:
                if dist_array[i][j] < lowcost:
                    #更新选择的节点
                    node=i
                    f_node=j
                    lowcost=dist_array[i][j]
        
        #更新
        not_leaf_list[f_node]=1
        tree_node_list.append( node )
        remain_node_list.remove(node)
        tree_dict[node]=f_node
        
    
    leaf_node_list=[]
    #得到叶节点集合作为候选节点集合
    for i in range(not_leaf_list):
        if not_leaf_list[i]==0:
            leaf_node_list.append(i)
    
    return tree_dict, leaf_node_list
                
    


    
    
#############################加入类里去作函数
def algorithm_5(self, depot_list, area_list):
    mc_num_list=[]
    
    span_tree=[]#该树的表达用列表形式，里面的元素是[父亲节点的id，子节点的id]，充电桩（即根节点）的id为-1
    
    list_size=len(depot_list)
    
    #self.capacity_mc
    for i in range(list_size):
        #得到节点集合(这些集合的索引定义为索引1）
        node_loc_list=[ depot_list[i] ]#节点位置集合
        for j in range( len(area_list[i]) ):
            node_loc_list.append( self.loc_nodes[ area_list[i][j] ] )
        
        node_id_list=[-1]+area_list[i]#节点id集合
        
        node_choosen_list=[0 for j in range( len(area_list[i])+1 )]#节点是否被选择加入候选节点列表，若是，则为1
        node_choosen_list[0]=1#充电桩为1，因为巡回初始化便会将其加入


        #node_list = [ depot_list[i] ] + area_list[i]#
        #得到的结果里装的索引均为索引1
        span_tree_dict, candidate_node_list =get_span_tree_and_leaves( node_loc_list )
        
        
        
        
        
        #更新node_choosen_list
        for j in range( len(candidate_node_list) ):
            node_choosen_list[ candidate_node_list[j] ]=1
        
        
        mc_num=0#所需MC数量
        node_in_route_num=1#巡回中节点数量
        route_centre_loc=copy.deepcopy( depot_list[i] )#巡回的中心位置
        route_power=0#巡回所需的大致能量
        while( len(candidate_node_list)>0 ):
            choosen_node=candidate_node_list[0]#candidate_node_list的第一位,这里记录的是索引1
            
            #计算该节点能耗
            choosen_node_id=node_id_list[ choosen_node ]#节点id
            choosen_node_loc=node_loc_list[ choosen_node ]#节点位置
            choosen_node_power=self.charge_power_for_node( choosen_node_id )+self.move_power*dist( route_centre_loc , choosen_node_loc )
            
            #选择加入巡回路径能耗最小的节点
            for j in range( 1,len(candidate_node_list) ):
                node_j=candidate_node_list[j]
                
                #计算节点能耗
                node_j_id=node_id_list[ node_j ]#节点id
                node_j_loc=node_loc_list[ node_j ]#节点位置
                node_j_power=self.charge_power_for_node( node_j_id )+self.move_power*dist( route_centre_loc , node_j_loc )
                
                #能耗比较
                if choosen_node_power > node_j_power:
                    #更换选择节点及相关信息
                    choosen_node=node_j
                    choosen_node_power=node_j_power
            
            #如果可以加入巡回
            if choosen_node_power+route_power < self.capacity_mc:
                #进行更新
                route_power+=choosen_node_power
                route_centre_loc = ( node_in_route_num*route_centre_loc + node_loc_list[ choosen_node ] )/(node_in_route_num+1)
                node_in_route_num+=1
                
                #删除被选择的节点
                candidate_node_list.remove( choosen_node )
                
                #尝试将被选择的节点的父节点加入候选节点列表
                f_node=span_tree_dict[ choosen_node ]#得到父节点的索引1
                #若父节点未加入过候选节点列表
                if node_choosen_list[ f_node ]==0:
                    node_choosen_list[ f_node ]=1
                    candidate_node_list.append( f_node )
            else:
                mc_num+=1
                
                #重置巡回
                node_in_route_num=1#巡回中节点数量
                route_centre_loc=copy.deepcopy( depot_list[i] )#巡回的中心位置
                route_power=0#巡回所需的大致能量
        
        
        #最后，将结果放入列表
        mc_num_list.append(mc_num)
        
	
	return mc_num_list