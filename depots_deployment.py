import numpy as np
import copy
from myUtil import Dprint
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
    
    not_leaf_list=[0 for i in range(size)]#判断不是叶节点的列表，若为1，则不是叶节点
    
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
    for i in range(size):
        if not_leaf_list[i]==0:
            leaf_node_list.append(i)
    
    return tree_dict, leaf_node_list

class WRSNEnv(object):
    def __init__(self):
        node_nums = 50
        self.loc_nodes = [ np.random.uniform(0.0,100, size=(1,2)).reshape(2)  for _ in range(node_nums)]
        self.capacity_mc = 30000
        self.move_power = 1
    
    def Unused__init__(self, **kwargs):
        '''
        By shuitang:
            先不用这个init
        '''
        
        self.net_shape = net_shape # int, net_shape * net_shape square network
        self.num_node = num_node # int, number of sensor nodes
        self.loc_nodes = np.random.uniform(0, net_shape, (num_node, 2)).astype('i') # locations of sensor nodes
  #node is what?      # int, the battery capacity of a node can be any number within [min_capacity_node, max_capacity_node]
        self.min_capacity_node, self.max_capacity_node = min_capacity_node, max_capacity_node # ???
        # float, the power of sensor node can be any float number within [min_power_node, max_power_node]
        self.min_power_node, self.max_power_node = min_power_node, max_power_node
        self.loc_bs = (net_shape // 2, net_shape // 2) # the base station locates at the center by default
        self.capacity_mc = capacity_mc # int, the battery capaccity of any Mobile Charger ## 
        self.speed_mc = speed_mc # int, moving speed of MC
        self.charge_power = charge_power # int, the charging power of MC ???
        
        ###
        self.move_power = move_power # int, the moving power of MC  ???  #####
        ### 
        
        self.maintainance = maintainance # int, minimum time needed to fully recharge a MC ??? why
        self.requests = [] # list, the global queue saving all charging requests  ??? id, timestamp
        self.max_request_len = max_request_len # int, the maximum length of self.requests 

        self.loc_depots, self.sub_nets, self.num_mc = self.optimal_deployment()

    def _init_energy(self, min_ratio=0.5):
        return np.random.uniform(low=min_ratio, high=1., size=self.num_node)

    def optimal_deployment(self, thre=5):
        ''' Return the optimal deployment of depots and MCs. '''

        num_depot = 1
        depot_pos_set, sensors_depart_set, num_mc_set = self._optimal_deployment(num_depot)
        while True:
            num_depot += 1
            depot_pos_set1, sensors_depart_set1, num_mc_set1 = self._optimal_deployment(num_depot)

            if num_mc_set - num_mc_set1 < thre:
                return depot_pos_set, sensors_depart_set, num_mc_set

            depot_pos_set, sensors_depart_set, num_mc_set = depot_pos_set1, sensors_depart_set1, num_mc_set1

    def Unused_optimal_deployment(self, num_depot):
        '''
            By shuitang:
                先不用这部分代码
        '''
        # you may initialize the residual energy of sensor nodes as below

        num_simulation = 50
        for idx in range(num_simulation):
            self.capacity_nodes = np.random.uniform(low=self.min_capacity_node, high=self.max_capacity_node,
                                                    size=self.num_node).astype('i')
            self.energy_nodes = self._init_energy() * self.capacity_nodes
            # depot_pos_set, sensors_depart_set, num_mc_set = [], [], []

        # 约束条件：因为每个MC外出一次回来后，需要至少 self.maintaince 的时间充满电才可以重新出发，所以 opt_depot_pos_set,
        # opt_sensors_depart_set, opt_num_mc_set 需要保证在 (1-a)*100% 的情况下，下一充电周期开始时的 sum(self.energy_nodes)
        # 不小于当前充电周期开始时的 sum(self.energy_nodes) ??? 标注
        # （如取 a=0.05，则相应地在上面的 simulations 中至少有 50*0.95=48 个 simulation 满足约束条件）
        #opt_depot_pos_set, opt_sensors_depart_set, opt_num_mc_set = ???
        return opt_depot_pos_set, opt_sensors_depart_set, opt_num_mc_set

    
    def _optimal_deployment(self, num_depot):
        '''
            By shuitang:
                我重写了这部分来作为我们初始模拟实验
                call the self.charge_power_for_node @ baiyun
        '''
        
        ## 每个区域能量的上限考虑为总能量/num_depot
        U = 0.0
        for index,_ in enumerate(self.loc_nodes):
            U += self.charge_power_for_node(index)
        
        A, DL = self.area_depart(num_depot,U)
        num_list = self.algorithm_5(DL, A)
        
        total_MC_nums = sum([sum(x) for x in num_list])
    
        return DL, A, total_MC_nums

    '''
    Algm5: min_dispatch
    
    Algm3+Algm4 VS Algm5: 前者是通过给定WRSN中节点的个数与功率，决定一开始的时候要建造多少个充电桩、以及各个充电桩要配备多少个
    MC，使得长期来看可以保证在 (1-a)*100% 的概率下不会出现节点耗完电的情况，只在初始化的时候运行一次并保存部署结果；后者是在每个
    充电周期开始的时候决定在各个充电桩处要派出多少个MC以满足当前的充电需求，在强化学习的部分，每个 episode 都会运行该算法一次。
    Algm5似乎可以直接用Algm4大部分的代码？
    '''

    def min_dispatch(self):
        '''
        Return the mininum number of dispatched MCs during a charging cycle.
        E.g.:
        suppose self.num_mc = [3, 2, 3], then obtain self.loc_mcs = [0, 0, 0, 1, 1, 2, 2, 2];
        if return [0, 3, 4, 5, 6], it indicates that 1, 2, 2 MCs are dispatched from each depot
        '''
        pass
    
    
    '''
        我觉得需要定义一个节点类吧，不如搞index真的麻烦？
    '''  
    def calculate_center_axi(self,K,A):
        '''
            By shuitang
        
        '''
        #print(A)
        A = [[self.loc_nodes[i] for i in area] for area in A]
        DL = [[] for _ in range(K)]
        for index, area in enumerate(A):
            if(len(area) == 0):
                continue
            x = 0.0
            y = 0.0
            for node in area:
                x += node[0]
                y += node[1]
            x = x/len(node)
            y = y/len(node)
            
            DL[index] = np.array([x,y])
            
        return DL
    def energy_consume(self, area):
        '''
        By shuitang:
            area 这个类有些麻烦
            这里能量的估计，简单地把这个区域内传感器的能耗加了起来
            注: 这里调用了self.charge_power_for_node() @ baiyun
        '''
        ans = 0.0
        for i in area:
            ans += self.charge_power_for_node(i)
        
        return ans
            
        
    def argmin_i(self,e,DL):
        '''
        By shuitang:
        
        '''
        dist_i = [ ((e-d)**2,index)  for index,d in enumerate(DL)]
        
        dist_i.sort()
        
        return [i for _,i in dist_i]
        
        
    def area_depart(self,K, U, err0 = 10,loc_nodes = None):
        '''
        By shuitang:
        args:
            K : int
            U : 每个depot负责的充电能量上限
            loc_nodes: 节点列表,list[np.array(2),...]
        returns:
            A :  [[id1,id2,...,],[id1,id2,...],...] 对应的depot负责的传感器的id的列表的列表
            DL : [np.array([x,y]),...,], depot的位置列表
            
        这个算法，用来初始确定depot的位置，以及每个depot负责的传感器的id集合
        所用到信息有:
            self.loc_nodes: 传感器的位置列表
            
        '''
        
       
        if loc_nodes is None:
            loc_nodes = self.loc_nodes
        
        ## 初始化，但是需要保证，每一类都必须要有元素
        ## 
        A = [[i] for i in range(K)]    
        for index in range(K,len(loc_nodes)):
            i = np.random.randint(0,K)
            A[i].append(index)
        
        DL = self.calculate_center_axi(K,A)
        
        epoch = 0
        while epoch < 100:
            A1 = A+[]
            A = [[] for i in range(K)]
            
            for index,e in enumerate(loc_nodes):
                j_list = self.argmin_i(e,DL)
                for j in j_list:
                    if self.energy_consume(A[j]+[index]) <= U:
                        A[j].append(index)
                        break
                    elif j == len(j_list)-1:
                        A[j].append(index)
                        break
                    
            #A_axi = [self.loc_nodes[i] for i in A]
            DL1 = self.calculate_center_axi(K,A)
            
            diff = np.sum([ (d1-d2)**2 for d1,d2 in zip(DL,DL1)])/len(DL)
            
            if diff < err0:
                return A, DL1
            DL = DL1 + []
            
            epoch += 1
        
        return A,DL
     
        
    def charge_power_for_node(self, node_j_id):
        return 50
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
