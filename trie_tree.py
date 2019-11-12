# -*- encoding:utf-8 -*-
import random
import math
from cal_can_arrive_station import cal_can_arrive

class TrieNode(object):
    def __init__(self, value=None, count=0, parent=None, level=0, local_count=0):
        # 值
        self.value = value
        # 频数统计
        self.count = count
        # 与父节点边
        self.parent = parent
        # 子节点，{value:TrieNode}
        self.children = {}
        # 原始count
        self.local_count = local_count
        # 节点所在层数
        self.level = level


class Trie(object):
    def __init__(self):
        # 创建空的根节点
        self.root = TrieNode()

    def insert(self, sequence, height):
        """
        基操，插入一个序列
        :param sequence: 列表
        :param height: 树高度
        :return:
        """
        cur_node = self.root
        for item in sequence:
            if item not in cur_node.children:
                # 插入结点
                child = TrieNode(value=item, count=1, parent=cur_node, level=cur_node.level + 1, local_count=1)
                cur_node.children[item] = child
                cur_node = child
                if child.level == height:
                    return
            else:
                # 更新结点
                cur_node = cur_node.children[item]
                cur_node.count += 1
                cur_node.local_count += 1
                if cur_node.level == height:
                    return

    # 生成有序树
    def sort(self, rootNode):
        keys = list(rootNode.children.keys())  # 取键
        # print(keys)
        before_sorted = [] #
        before_sorted_count = []
        after_sorted = []
        result_dict = {}
        for item in rootNode.children.values():
            before_sorted.append(item)
            before_sorted_count.append(item.count)
        after_sorted = list(reversed(sorted(before_sorted_count)))
        for i in range(len(after_sorted)):
            before_index = before_sorted_count.index(after_sorted[i])
            result_dict[keys[before_index]] = before_sorted[before_index]
            before_sorted_count[before_index] = -1  # 取值后赋值-1。。防止重复值报错
        rootNode.children = result_dict
        # 递归
        for item in rootNode.children.values():
            if len(item.children) > 0:
                self.sort(item)


    def printTrie(self, cur_node):
        """
        基操，打印完整字典树
        :return:
        """
        # cur_node = self.root
        for item in cur_node.children.values():
            print(item.value, '： 原始count：', item.local_count, '|| 加噪声后count：', item.count, '|| 所在level：', item.level)
            if len(item.children) == 0:
                pass
            else:
                self.printTrie(item)

# 查找第n层的所有节点
def search_level_nodes(root_node, level, ret_nodes):
    son_nodes = root_node.children
    for son_node in son_nodes.values():
        if level == son_node.level:
            ret_nodes.append(son_node)
        elif level > son_node.level:
            search_level_nodes(son_node, level, ret_nodes)
    return ret_nodes

def search_tri(r, height, now_height, search_tri_arr=[("a", 1)], level=1, ret_search=[]):
    if level > len(search_tri_arr):
        return []
    search_node = search_tri_arr[level - 1]
    for i in range(now_height, height + 1):
        leaf_nodes_i = search_level_nodes(r.root, i, [])
        for leaf in leaf_nodes_i:
            rootVal = leaf.value
            rootLoc = rootVal[0]
            rootTim = rootVal[1]
            if rootLoc == search_node[0] and rootTim == search_node[1]:
                if level == len(search_tri_arr):  # 完全找到该tr
                    ret_search.append([leaf.value, leaf.local_count, leaf.count])
                else:
                    search_tri(leaf, height, leaf.level + 1, search_tri_arr, level + 1, ret_search)        
    return ret_search


def choose_satisfies_node(root_node, level, ret_nodes, time):
    # 选择的节点的时间需小于等于time参数
    son_nodes = root_node.children
    for son_node in son_nodes.values():
        if level == son_node.level:
            if son_node.value[1]<=time:
                ret_nodes.append(son_node)
        elif level > son_node.level:
            if son_node.value[1]<=time: 
                choose_satisfies_node(son_node, level, ret_nodes, time)
    return ret_nodes

def test1(root_node, level, ret_nodes, time,location):
    # ret_nodes={}
    son_nodes = root_node.children
    for son_node in son_nodes.values():
        if level == son_node.level:
            if son_node.value[1]==time and son_node.value[0]==location:
                ret_nodes.append(son_node)
        elif level > son_node.level:
            if son_node.value[1]<=time:
                test1(son_node, level, ret_nodes, time, location)
    return ret_nodes


def search_satisfies_tri(r, height, now_height, search_tri_arr=[("a", 1)], level=1, ret_search=[]):
    if level > len(search_tri_arr):
        return []
    search_node = search_tri_arr[level - 1]
    for i in range(now_height, height + 1):
        leaf_nodes_i = test1(r, i, [], search_node[1], search_node[0])
        for leaf in leaf_nodes_i:
            if level == len(search_tri_arr):  # 完全找到该tr
                ret_search.append(leaf.count)
            else:
                search_satisfies_tri(leaf, height, leaf.level + 1, search_tri_arr, level + 1, ret_search)
    return ret_search

def signum(x):
    if x > 0:
        return 1.0
    if x < 0:
        return -1.0
    if x == 0:
        return 0

def change_time(str_time):
    # str_time = str_time.split('')
    if str_time < 10:
        str_time = '0' + str(str_time)
    else:
        str_time = str(str_time)
    minute = str_time[-1]
    if minute == '1':
        m = 0
    if minute == '2':
        m = 15
    if minute == '3':
        m = 30
    if minute == '4':
        m = 45
    str_time = str_time[:-1] + ":" + str(m)
    return str_time

def addNoise(par_node, pre_timer, pre_location, epsilon, sensitivity, thred):
    """
    添加噪声
    :param par_node: 父节点
    :param pre_timer: 时间域列表
    :param pre_location: 地点域列表
    :param epsilon: 隐私预算
    :param sensitivity: 敏感度
    :param thred: 阈值
    :return:
    """

    par_node_count = par_node.count  # 父节点count
    new_children_dict = {}   # 新孩子字典
    children_nodes = par_node.children  # 遍历原子节点
    for key in children_nodes.keys():
        item = children_nodes[key]
        # 添加噪声
        randomDouble = random.random() - 0.5
        noise = - (sensitivity / epsilon) * signum(randomDouble) * math.log(1 - 2 * abs(randomDouble))
        item.count = item.count + noise
        # 判断是否满足阈值
        if item.count < thred:
            continue
        # 满足阈值，父节点count减去对应count，并将子节点加入新的孩子字典中
        par_node_count = par_node_count - item.count
        new_children_dict[key] = item

        # 根据父节点剩余count判断是否终止
        if par_node_count < 0:
            item.count = item.count + par_node_count
            par_node_count = 0
            break
        elif par_node_count == 0:
            break
        else:
            continue

    # 排除最后一个时间戳节点的干扰
    if par_node.value is not None:
        par_node_timer = par_node.value[1]
        timer_index = pre_timer.index(par_node_timer)
        if timer_index == len(pre_timer) - 1:
            return
    # 还有count多，需要选择新节点，直到count为0为止
    while par_node_count > 0:
        # 直到选择成功为止
        temp = extraAdd(par_node, pre_timer, pre_location, epsilon, 1, thred)
        while temp is None:
            temp = extraAdd(par_node, pre_timer, pre_location, epsilon, 1, thred)

        par_node_count = par_node_count - temp.count
        new_children_dict[temp.value] = temp
        # 保持一致性
        if par_node_count < 0:
            temp.count = temp.count + par_node_count
            par_node_count = 0

    par_node.children = new_children_dict

def extraAdd(par_node, pre_timer, pre_location, epsilon, sensitivity, thred):
    # 输入:
    # 排除根节点、最后一个时间戳节点的干扰
    if par_node.value is not None:
        par_node_locat = par_node.value[0]
        par_node_timer = par_node.value[1]
        timer_index = pre_timer.index(par_node_timer)
        if timer_index == len(pre_timer) - 1:
            return -1
    else:
        par_node_timer = -1
        timer_index = -1
    # 随机取时间戳
    # print("len(pre_timer):",len(pre_timer))
    random_index = random.randint(timer_index + 1, len(pre_timer) - 1)
    t = pre_timer[random_index]
    while t == par_node_timer:
        random_index = random.randint(timer_index + 1, len(pre_timer) - 1)
        t = pre_timer[random_index]

    children_nodes_keys = list(par_node.children.keys())
    par_t = change_time(par_node_timer)
    son_t = change_time(t)
    select_nodes = []
    # 返回可用地点域
    if par_node.value is not None:
        temp_limit_locations = cal_can_arrive(par_node_locat, par_t, son_t)
#        temp_limit_locations=pre_location

    else:
        temp_limit_locations = pre_location
    # 建立可用(地点.时间)节点, 保证跟同层的孩子节点不同
    for temp in temp_limit_locations:
        node = (temp, t)
        if node not in children_nodes_keys:
            select_nodes.append(node)
    # 无可用地点时间对情况，返回None
    if len(select_nodes) == 0:
        return None

    # 对该时间段所有可用节点加噪声
    can_nodes = []
    
    for select_node in select_nodes:
        # 加噪声
        randomDouble = random.random() - 0.5
        noise = - (sensitivity / epsilon) * signum(randomDouble) * math.log(1 - 2 * abs(randomDouble))
        # 不从阈值基础上添加噪声、从0上添加
        node_count = 0 + noise
        # 满足时，加入can_nodes  ,调小阈值thred/2,3,4,5
        if node_count >= thred:
            can_node = TrieNode(value=select_node, count=node_count,\
             parent=par_node, level=par_node.level + 1, local_count=0)
            can_nodes.append(can_node)
    if len(can_nodes) == 0:
        return None
    # 随机取一个can_node加入
    random_select_index = random.randint(0, len(can_nodes) - 1)
    node = can_nodes[random_select_index]
    return node

def output(par_tra, now_node, ret_d):
    """
    par_tra:
    """
    if par_tra is None:
        par_tra = []
    son_nodes = now_node.children.values()
    add_node = (now_node.value[0], now_node.value[1], round(now_node.count,3))  # 地点 时间
    par_tra.append(add_node)
    new_tra = par_tra.copy()  # 格式['地点']
    sons_count = 0

    for son_node in son_nodes:
        sons_count += son_node.count
#    ret_count = int(now_node.count - sons_count)  # 有剩余,表示有用户在now_node结束
    ret_count = now_node.count - sons_count
    ret_count = round(ret_count,3)
    ret_row = (new_tra, ret_count)  # (['地点',...], count)
    # ret_row = ((now_node.value[0], now_node.value[1]), ret_count)
    if ret_count > 0:
        ret_d.append(ret_row)  # ret_d 格式:[(['地点',...], count),(['地点',...], count)]
    for son_node in son_nodes:
        output(new_tra, son_node, ret_d)
    return ret_d


    

