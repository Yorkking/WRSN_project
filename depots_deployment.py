#coding:utf-8
import numpy as np
import copy
from myUtil import Dprint
import myUtil
import matplotlib.pyplot as plt
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
        '''
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
        '''
        node_nums = 1000
        edge_size = 1e4
        self.loc_nodes = [ np.random.uniform(0.0,edge_size, size=(1,2)).reshape(2)  for _ in range(node_nums)]
        self.node_nums = node_nums
        
        self.capacity_mc = 1e6

        self.move_power = 50
        
        self.node_full_power = 1.08e4
    
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

    def optimal_deployment(self, thre=3):
        ''' Return the optimal deployment of depots and MCs. '''
        
        ans_mc_nums = 0xfffff
        ans_depot_pos_set = []
        ans_num_mc_set = []
        ans_sensors_depart_set = []
        
        
        num_depot = 1
        depot_pos_set, sensors_depart_set, mc_set_list = self._optimal_deployment(num_depot)
        num_mc_set = len(mc_set_list)
        print("set depot num = ",num_depot)
        print("K:",len(depot_pos_set))
        #print("depot_pos_set:",depot_pos_set)
        #print("sensors_depart_set",sensors_depart_set)
        print("mc_lsit",mc_set_list)
        print("num_mc_set",num_mc_set)
        print("************************************************************")
        
        if sum(mc_set_list) < ans_mc_nums:
            ans_mc_nums = sum(mc_set_list)
            ans_depot_pos_set = depot_pos_set
            ans_num_mc_set = mc_set_list
            ans_sensors_depart_set = sensors_depart_set
        
        
        while num_depot < min(self.node_nums,10):
            num_depot += 1
            depot_pos_set1, sensors_depart_set1, mc_set_list1 = self._optimal_deployment(num_depot)
            num_mc_set1 = len(mc_set_list1)
            if num_mc_set1 < 0:
                continue
            
            '''
            if num_mc_set - num_mc_set1 >= thre: #一个depot换超过 thre 个MC
                print("************************************************************")
                print("K:",len(depot_pos_set1))
                #print("depot_pos_set:",depot_pos_set)
                #print("sensors_depart_set",sensors_depart_set)
                print("mc_lsit",mc_set_list1)
                print("num_mc_set",num_mc_set1)

                #return depot_pos_set, sensors_depart_set, num_mc_set
            '''
            # 目前先不考虑最优depot个数，先看看这个算法根据不同个k得出的结果：       
            #print("************************************************************")
            print("set depot num = ",num_depot)
            print("K:",len(depot_pos_set1))
            #print("depot_pos_set:",depot_pos_set)
            #print("sensors_depart_set",sensors_depart_set)
            print("mc_lsit",mc_set_list1)
            print("num_mc_set",num_mc_set1)
            print("************************************************************")
            depot_pos_set, sensors_depart_set, num_mc_set = depot_pos_set1, sensors_depart_set1, num_mc_set1
            mc_set_list = mc_set_list1
            if sum(mc_set_list) < ans_mc_nums:
                ans_mc_nums = sum(mc_set_list)
                ans_depot_pos_set = depot_pos_set
                ans_num_mc_set = mc_set_list
                ans_sensors_depart_set = sensors_depart_set
            
       
        return ans_mc_nums, ans_depot_pos_set, ans_num_mc_set, ans_sensors_depart_set

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
        
        A, DL = self.area_depart(num_depot,U/num_depot)
        area_list = []
        DL_list = []
        for index,area in enumerate(A):
            if len(area) != 0:
                area_list.append(area)
                DL_list.append(DL[index])
        self.showClusterResult(area_list,num_depot,DL_list)
        #Dprint("191 *** is ok! cluster ok!")        
        num_list = self.algorithm_5(DL_list, area_list)
        
        #print(num_list)
       
        #total_MC_nums = sum(num_list)
    
        return DL_list, area_list, num_list

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
        我觉得需要定义一个节点类吧，不然搞index真的麻烦？   
    '''  
    def calculate_center_axi(self,K,A):
        '''
            By shuitang
        '''
        nodes_locs = [[self.loc_nodes[i] for i in area] for area in A]   
        DL = [[] for _ in range(K)]
        for index, area in enumerate(nodes_locs):
            if(len(area) == 0):
                continue
            x = 0.0
            y = 0.0
            for node in area:
                x += node[0]
                y += node[1]
            x = x/len(area)
            y = y/len(area)
            
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
    

    def getClusterCentre(self, cluster):
        if(len(cluster) == 0):
            return []
        
        x = 0.0
        y = 0.0
        cluster_nodes = [self.loc_nodes[node_id]  for node_id in cluster]
        for node in cluster_nodes:
            x += node[0]
            y += node[1]
        x = x/len(cluster_nodes)
        y = y/len(cluster_nodes)
        
        return np.array([x,y])
        
    def argmin_i(self,e,DL):
        '''
        By shuitang:
        
        '''
        dist_i = [ (sum((e-d)**2)**0.5,index)  for index,d in enumerate(DL)]
        
        #Dprint("dist_i",dist_i)
        
        dist_i.sort()
        #Dprint("dist_i",dist_i)
        
        return [i for _,i in dist_i]
    
    
    def showClusterResult(self,clusterSets,K,centres):
        plt.figure()
        x_list = [nodes[0]  for nodes in self.loc_nodes]
        y_list = [nodes[1]  for nodes in self.loc_nodes]
        plt.plot(x_list, y_list, 'o')
        Colors = [val  for key,val in myUtil.cnames.items()]
        cnt = 0
        for index, cluster in enumerate(clusterSets):
            x_temp = [self.loc_nodes[i][0] for i in cluster]
            y_temp = [self.loc_nodes[i][1] for i in cluster]
            plt.plot(x_temp, y_temp, 'o', color=Colors[7*cnt+10])
            plt.plot(centres[index][0],centres[index][1],'+',color=Colors[7*cnt+10])
            cnt +=  1
        plt.xlabel("clusters nums="+str(len(clusterSets)))
        #plt.legend()
        plt.show()
        
        pass
    
    def processNullCluster(self,clusterSets, K, centres):
        '''
            用于处理聚类过程中某一类为空的情况
            哎，发现个坑: 我们使用的节点竟然是节点的id!!!不是坐标啊！！！好麻烦啊！
        
        '''
        def getDist(pointA, pointB):
            #print("2877777777777*****",pointA,pointB)
            return ((pointA[0]-pointB[0])**2 + (pointA[1]-pointB[1])**2)**0.5
        
        for cluster_id, cluster in enumerate(clusterSets):         
            if len(cluster) == 0:
                ## 从其他类选出一个最远的来，而且不能使得原本的类为空，所以要对距离加权
                select_cluster_id = -1
                d_furthest = -1
                select_point_id = -1
                for index, clu in enumerate(clusterSets):
                    if(len(clu) > 1):
                        ## 寻找该cluster中离该聚类中心最远的点，保留它的距离和下标
                        dmax = -1
                        imax = -1
                        cent = centres[index]
                        for i,point in enumerate(clu):
                            if getDist(self.loc_nodes[point],cent)>dmax:
                                dmax = getDist(self.loc_nodes[point],cent)
                                imax = i
                        if d_furthest < dmax:
                            d_furthest = dmax
                            select_cluster_id = index
                            select_point_id = imax
                
                clusterSets[cluster_id].append(clusterSets[select_cluster_id][select_point_id])
                del clusterSets[select_cluster_id][select_point_id]
                
                centres[select_cluster_id] = self.getClusterCentre(clusterSets[select_cluster_id])
                centres[cluster_id] = self.getClusterCentre(clusterSets[cluster_id])
        #return clusterSets
        
    def area_depart(self,K, U, err0 = 1e-2,loc_nodes = None, epoch0 = 2000):
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
        while epoch < epoch0:
            A1 = A+[]
            A = [[] for i in range(K)]
            
            for index,e in enumerate(loc_nodes):
                j_list = self.argmin_i(e,DL)
                
                ## 感觉这里限制负载均衡的话，应该这样做：如果某一cluster超出的话，应该先把该cluster最大的替换出去
                for index1,j in enumerate(j_list):
                    if self.energy_consume(A[j]+[index]) <= 1000*U:
                        A[j].append(index)
                        break
                    elif index1 == len(j_list)-1:
                        A[j_list[0]].append(index)
                        break
                    
            #A_axi = [self.loc_nodes[i] for i in A]           
            ## 处理空聚类
            ## 采取的措施是：选取其他类中选取一个距离它们自身中心最远的点加入到该集合中，目的在于消除方差
            DL1 = self.calculate_center_axi(K,A)
            self.processNullCluster(A,K,DL1)         
            DL1 = self.calculate_center_axi(K,A)
            #Dprint(DL1,DL)
            
            '''
            ## 聚类会导致某一类为空！！！！
            ## 强行聚类？？？
            diff = 0.0
            for d1,d2 in zip(DL,DL1):
                try:
                    diff +=  sum((d1-d2)**2)
                except:
                    return A,DL            
            '''
            diff = np.sum([ sum((d1-d2)**2) for d1,d2 in zip(DL,DL1)])/len(DL)
            if diff < err0:    
                return A, DL1
            DL = DL1 + []   
            epoch += 1
        
        return A,DL
     
        
    def charge_power_for_node(self, node_j_id):
        return self.node_full_power * 0.5
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
            
            
            mc_num=1#所需MC数量（至少要一个巡回）
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
    
if __name__ == '__main__':
    
    wrsn = depots_deployment.WRSNEnv()
    
    wrsn.optimal_deployment()