# WRSN_project
这是WRSN课题组的项目。主要研究多智能体充电的问题。

代码文件说明：

>- `__init__.py`: 不用管
>- `myUtil.py`: 封装一些配置函数，比如debug函数
>- `test.py`: 测试函数，我们先让我们的算法跑起来，写的一个测试函数, 即我们**只需要运行该文件来跑我们的算法！**
>- `depots_deployment.py`: 算法的主要代码：包括 shuitang 和 baiyun 写的算法部分的代码
>- `my_depots_deployment.py`: baiyun 那部分的代码，先已经把该部分代码全部加入到 `depots_deployment.py`
>- `参数笔记.txt`: 白云的参数

现在正在测试，我重写了`WRSNEnv`部分代码，在`depots_deployment.py`已写注释(搜索 By shuitang)。具体而言：重写了 `__init__`部分，只初始化了部分目前用得上的变量。

### 实验结果

目前的结果如下：

![聚类结果](./image/%E8%81%9A%E7%B1%BB%E7%BB%93%E6%9E%9C.png)



## 算法性能评估指标
1. predicted survival rate of sensor nodes (mininum charging duration: charging time of MC + maintainance; if a sensor owns enough energy till the end of mininum charging duration, we say it survives.)
2. predicted charging utility of MCs (charged_energy / (moving_energy + charged_energy)
