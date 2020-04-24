构建一个区域类：
```python
class MC:
    time #时间是指，从MC被派出去时刻为0开始计时的时刻
    axis #坐标
    capacity #携带电量
    power_consume # 能耗
    v #速度
class Node:
    dead_time #死亡时间是指，从MC被派出去时刻为0开始计时的时刻
    axis
    capacity
    power_consume
    

class Area:
    def __init__(self):
        self.MCsets = MCList
        self.NodeSets = NodeList
        ## 这里需要随机初始
        
        ## 然后调用充电过程
        live_rate, eff_rate = self.chargeAlgorithm
        
        
    def chargeAlgorithm:
    
        pass
```
初始化传感器的电量（随机50%到100%）

随机一段时间，然后停下，接着观察传感器里有多少传感器的电量下到警戒值。将到了警戒值的传感器的id放入充电传感器队列q（用list）。


初始化时间，计算传感器的时间并保存在字典中（字典的键是节点id，字典的值是时间）

判断充电请求队列里的节点是否有无法救活的（即一个满电量MC在初始时间从depot出发前往该节点，无法给它充满电或者在抵达该传感器之前已死亡），踢出充电请求队列，并增加放弃节点数量

初始化MC（包括电量和位置）。选择q中距离该MC最近的传感器a，判断是否可以在a死亡之前MC抵达其位置并给它充满电（MC有足够电量前往该传感器，充满电并可以回去depot），如果可以，更新MC的信息并更新时间；

如果不行，则新启动一个MC，然后重复上一步骤，直到MC的数量超过depot的限定数量或传感器充电请求队列为空

将充电请求队列中的数量加至放弃节点数量，然后输出


函数charge_is_ok（MC_location, MC_power, 节点id）：
    判断MC能否给该节点充电，返回true或false
