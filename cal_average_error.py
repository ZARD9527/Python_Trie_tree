# -*- coding: utf-8 -*-
"""
Created on Mon Nov 11 20:42:04 2019

@author: y1881
"""

# -*- coding: utf-8 -*-
"""
Created on Sun Apr 14 20:10:11 2019

@author: y1881
"""

import time
from trie_tree import search_satisfies_tri, search_level_nodes
import random
import pickle as pkl
import os

# [1.0,1],[1.5,1],[2.0,1],[2.0,2],[2.0,3]
name = './20191029/h3/'
lap_file = name + 'lap_tree_data_height_14_1.0_1.5_1_.txt'  # 不同数据集记得改393
raw_file = name + 'raw_tree_data_height_14_.txt'
lapname = '1'

def read_location_time(location_file, time_file):
    if not os.path.exists(location_file) or not os.path.exists(time_file):
        print("loc或time文件不存在！")
        return 
    # 读取的地点、时间文件用于构造轨迹 不是索引文件
    with open(location_file, 'rb') as f:
        location = pkl.load(f)
    with open(time_file, 'rb') as f:
        timestamp = pkl.load(f)
    return list(set(location)), timestamp

def construct_test_track(location_file, time_file, num, length):
    test_trajectory = []
    locations, timestamp = read_location_time(location_file, time_file)
    for i in range(num):
        single_trajectory = []
        start_t_index = 0
        for j in range(length):
            loc_index = random.randint(0, len(locations) - 1)
            time_index = random.randint(start_t_index, len(timestamp) - 1)
            start_t_index = time_index
            node = (locations[loc_index], timestamp[time_index])
            single_trajectory.append(node)
        test_trajectory.append(single_trajectory)
    return test_trajectory

def calculate_loc_frequency(raw_file, lap_file, height):
    '''
    统计地点频率，返回原始树和噪声树地点的频率 数据格式{(loc,time):count}
    '''
    if not os.path.exists(raw_file) or not os.path.exists(lap_file):
        print(">>>raw_tree_file或lap_tree_file不存在！")
        return 
    with open(lap_file, 'rb') as f:
        laptree = pkl.load(f)
    with open(raw_file, 'rb') as f:
        rawtree = pkl.load(f)
    
    lapdata = {}
    rawdata = {}
    for i in range(1,height+1):
        nodes = search_level_nodes(laptree.root, i, [])
        for n in nodes:
            if n.value not in lapdata.keys():
                lapdata[n.value] = round(n.count,4)  # 0:value
            else:
                lapdata[n.value] += round(n.count,4) 
    
    for i in range(1,height+1):
        nodes = search_level_nodes(rawtree.root, i, [])
        for n in nodes:
            if n.value not in rawdata.keys():
                rawdata[n.value] = round(n.count,4)  # 0:value
            else:
                rawdata[n.value] += round(n.count,4) 
    
    print('lapdata keys:',len(lapdata.keys()))
    print('rawdata keys:',len(rawdata.keys()))
    return rawdata, lapdata

def cal_relative_error(raw_trajectory, lap_trajectory, test_trajectory, s):
    # raw_trajectory lap_trajectory 保存的是长度为1轨迹的频率{(loc, time):count}
    raw_result = []
    lap_result = []
    for test in test_trajectory:
        if test[0] in raw_trajectory.keys():
            raw_result.append(raw_trajectory[test[0]])  # 保存真实的计数
        if test[0] in lap_trajectory.keys():
            lap_result.append(lap_trajectory[test[0]])
    
    real_count = sum(raw_result)  # 真实计数
    lap_count = sum(lap_result)  # 添加噪声的计数
    raw_query_count = len(raw_result)
    lap_query_count = len(lap_result)
    relative_error = abs(lap_count - real_count) / max(real_count, s)  # s为
    print(len(test_trajectory), "条长度为1的测试轨迹在噪声轨迹和原始轨迹中查到的数量为:", \
          lap_query_count,'、',raw_query_count, "条")
    return round(relative_error,5)


def test_result(pre_tree, tree, epsilon, test_trajectory, height):
#    name = './20191029/d3/'
    query_count1 = 0
    query_count2 = 0
    # 构造查询轨迹
    q_time = time.time()
    temp_error = 0
    for test_tr in test_trajectory:
        # tree是添加噪声的树  pre_tree无噪声树
        if len(test_tr) == 1:
            with open(name + lapname + '.txt','rb') as f:
                lapdata = pkl.load(f)
            if test_tr[0] not in lapdata.keys():
                result1 = []
            else:
                result1=[lapdata[test_tr[0]]]  # 保存有噪声的数据
        else:
            result1 = search_satisfies_tri(tree, height, 1, search_tri_arr=test_tr, ret_search=[])
        if len(test_tr) == 1:
            with open(name + 'rawdata'+ '.txt','rb') as f:
                data = pkl.load(f)
            if test_tr[0] not in data.keys():
                result2 = []
            else:
                result2=[data[test_tr[0]]]
        else:
            result2 = search_satisfies_tri(pre_tree, height, 1, search_tri_arr=test_tr, ret_search=[])
        all_count = 0  # 添加噪声的计数
        all_tr_id = 0  # 真实计数
        for item in result1:
            all_count += item
        if result1:
            query_count1 += 1
        for item2 in result2:
            all_tr_id += item2
        if result2:
            query_count2 +=1
        temp_error += abs(all_tr_id - all_count) / max(all_tr_id, 824)  # len(tr_id)  848 394 690 572 824
    error = temp_error
    print("查询时间:", round((time.time() - q_time) / 60,4), "分钟")
    print(len(test_trajectory), "条轨迹中在噪声轨迹和原始轨迹查到数量各为:", query_count1,'、',query_count2, "条")
    # error_1 = error / query_count  # 除查到的数据量
    error_2 = error / len(test_trajectory)  #
    if query_count2 != 0:
        err = error/query_count2
    else:
        err = 0
    print("相对误差:", round(error_2,10))
    print('除以在噪声轨迹中查中的条数的误差:',round(err,10))
    print('-'*50)
    return round(error_2,10)

def load(height, epsilon, L, num, tree, pre_tree):
    # L 构造的轨迹长度
#    random.seed(L*123)  # 1223415
    test_trajectory = []
    len_tra = L # 查询轨迹长度
    pre_location, pre_timer = read_location_time(height)
    for i in range(num):
        single_trajectory = []
        start_t_index = 0
        for j in range(len_tra):
            l_index = random.randint(0, len(pre_location) - 1)
            t_index = random.randint(start_t_index, len(pre_timer) - 1)
            start_t_index = t_index
            node = (pre_location[l_index], pre_timer[t_index])
            single_trajectory.append(node)
        test_trajectory.append(single_trajectory)
#    test_trajectory=[[('木棉湾',124),('丹竹头',214)],[('华新',133),('水贝',134)]] # ('科学馆站',132),
    print('轨迹长度{}构造完毕!'.format(L))
    err = test_result(pre_tree.root, tree.root,epsilon, test_trajectory, height)
    return err

def main(height=0, epsilon=1.0, maxq=0):
    with open(lap_file, 'rb') as f:
        laptree = pkl.load(f)
    with open(raw_file, 'rb') as f:
        rawtree = pkl.load(f)  
    for q in [3]:
        err = 0
        for l in range(1,2): # q
            err += load(height=height, epsilon=epsilon, L=l, num=20000//(q-1), tree=laptree, pre_tree=rawtree)
        print('maxq=', maxq ,'时误差为:',round(err/maxq,5)+0.00)  # err/3 3表示max|Q|=3
if __name__ == '__main__':
    location_file = './location_time_index/locations.txt'
    time_file = './location_time_index/time_ds1.txt'  # 全时间 不同数据集时间不同
    raw_file = './raw_tree/raw_tree_data_height_6_.txt'
    lap_file = './lap_tree/ds1/lap_tree_data_height_6_1.0_1.5_1.0_.txt'
    height = 6
    s = 393  # 数据集的tr_idx0.001结果
    test_trajectory = construct_test_track(location_file, time_file, num=1000, length=1)
    rawdata, lapdata = calculate_loc_frequency(raw_file, lap_file, height)
    
    relative_error = cal_relative_error(rawdata, lapdata, test_trajectory, s)
    print(relative_error)
    