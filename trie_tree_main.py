# -*- coding: utf-8 -*-
"""
Created on Mon Nov 11 13:20:53 2019

@author: y1881
"""

# -*- encoding:utf-8 -*-
import pandas as pd
import numpy as np
import time
from trie_tree import Trie, search_level_nodes, addNoise, output
from lapnoise import lap_noise
import math
import pickle as pkl
import os
import collections
#from tqdm import tqdm
#import prefixspan_demo

def summary_statics(path="./data/dataset.csv"):
    # 打印原始数据集基本信息
    if not os.path.exists(path):
        print(">>>文件不存在,请检查文件路径是否正确!<<<")
        return 
    data = pd.read_csv(path)
    data1 = data[['card_number', 'count']]
    data1 = data1.drop_duplicates(subset=['card_number', 'count'])
    c = collections.Counter(data1["count"])
    print('长度分布:\n',c,'\n数据集基本信息:')
    print("length", len(data), "\n",
          "Location:", len(set(data["route_station"])), "\n",
          "timestamp:", len(set(data["timestamp"])), "\n",
          "max|tr|:", max(data["count"]), "\n",
          "mean|tr|:", round(data["count"].mean(), 2), "\n",
          "user num:", len(set(data["card_number"])))

def cal_time(start_time, end_time):
    total_time = end_time - start_time
    return round(total_time, 4)

def other_dataset(file):
    # 读取其他格式的数据集函数
    if not os.path.exists(file):
        print("文件不存在！")
        return 
    pre_timer = []
    pre_location = []
    information = dict({})
    with open(file, 'r') as f_file:
        T_all = []
        tr_id_index = 0
        for line in f_file:
            tr_id_index += 1
            tr_id_name = 'tr' + str(tr_id_index)
            T = []
            for item in line.strip().split('(')[1:]:
                item2 = item.split(')')[0].split(',')
                locat = str(item2[0].strip())
                timer = int(item2[1].strip()[1:-1])
                if locat not in pre_location:
                    pre_location.append(locat)
                if timer not in pre_timer:
                    pre_timer.append(timer)
                T.append((locat, timer))
            T_all.append(T)
            information[tr_id_name] = T

    pre_timer.sort()
    pre_location.sort()
    return pre_timer, pre_location

def assign_privacy_budget_and_thresholds(height, total_budget, k, b, delta):  #
    # 隐私预算、阈值分配  height为树高  k,b 是阈值公式的系数  delta是隐私预算公式系数
    epsilons = []
    thresholds = []
    for i in range(height + 1):
        epsilons.append(math.log(i + delta, 10))  # 1.6**(0.5*i)  delta=1.5 默认值是1.1  math.log(i + 1.1, 10)
    sum_epsilons = sum(epsilons)
    for i in range(height + 1):
        epsilons[i] = round(total_budget*(epsilons[i] / sum_epsilons), 4)
        thresholds.append(round(k/(i+1)+b, 4)) # 默认1.5/i+1  i=1,2,3,...  1.5/(i+1) 阈值函数 线性 kx+b
#        thred.append(round(k/(i+1)**2+b, 6))  # 阈值公式2
#        thred.append(round(k/(2.718**(i+1))+b, 6))  # e=2.718  阈值公式3
    # 隐私预算归一化
    epsilons = sorted(epsilons, reverse=True)
    thresholds = sorted(thresholds, reverse=True)
    return epsilons, thresholds

def building_noise_tree(height, total_budget, k, b, delta, data_file, trajectory_file, save_path):
    if not os.path.exists(data_file):
        print("原始数据集文件不存在！")
        return 
    if not os.path.exists(trajectory_file):
        print("轨迹数据集文件不存在！")
        return
    print('>>>开始构建树' + '>' * 40)
    read_data_start_time = time.time()
    data = pd.read_csv(data_file)
    information = np.load(trajectory_file).item()  # {id:轨迹} Tractory_dataset_40_170
    read_data_end_time = time.time()
    pre_location = list(set(data["route_station"]))  # 地点域
    pre_timer = sorted(set(data["timestamp"]))  # 时间域
    read_data_time = cal_time(read_data_start_time, read_data_end_time)
    # 字典树高度，除根节点
    budget, thresholds = assign_privacy_budget_and_thresholds(height, total_budget, k, b, delta) # allcation_ep(height)  t是阈值list
    print('每层树节点阈值划分:', thresholds) 
    print('每层树隐私预算划分:', budget) 
    trie = Trie()  # 建立字典树
    root_epsilon = budget[0]  # 根节点隐私预算
    epsilonL = budget[1] # 每层隐私预算
    thred = thresholds[0]  # 阈值
    sensitivity = 1  # 敏感度
    # 插入每条轨迹，建立字典树
    for item in information.values():
        trie.insert(item, height)
        trie.root.count += 1
    build_rawtree_start_time = time.time()  
    build_rawtree_time = cal_time(read_data_end_time, build_rawtree_start_time)
    
    # 保存文件存放路径
    raw_path = './raw_tree/'
    if not os.path.exists(raw_path):
        os.mkdir(raw_path)
    filename = raw_path + 'raw_tree_data_height_' + str(height)+'_.txt'
    if os.path.isfile(filename) == False:
        with open(filename, 'wb') as f:
            pkl.dump(trie, f)  
        print(">>>成功保存原轨迹树文件！")
    else:
        print(">>>原轨迹树文件已经存在，不需要重复保存！")
    # 给根节点加噪声
    build_noise_tree_start_time = time.time()
    noise = lap_noise(root_epsilon, sensitivity)
    trie.root.local_count = trie.root.count  # 保存根节点原始count
    trie.root.count = trie.root.count + noise  # 根节点count加噪声
    # 对树节点加噪声
    addNoise(trie.root, pre_timer, pre_location, epsilonL, sensitivity, thred)
    thred2 = thresholds[1] # 阈值
    for i in range(1, height):
        next_epsilon = budget[i+1] # 下一层树节点的隐私预算
        thred2 = thresholds[i]
        for item in search_level_nodes(trie.root, i, []):
            if pre_timer.index(item.value[1]) >= len(pre_timer) - height:
                continue
            addNoise(item, pre_timer, pre_location, next_epsilon, sensitivity, thred2)
    build_noise_tree_end_time = time.time()
    build_noise_tree_time = cal_time(build_noise_tree_start_time, build_noise_tree_end_time)
    
    sanitized_data = []  # 保存净化的轨迹
    for son_node in trie.root.children.values():
        sanitized_data.extend(output([], son_node, []))
    print('轨迹预览:',sanitized_data[:2])
    print('不重复的轨迹数量:',len(sanitized_data))
    sanitized_data_endtime = time.time()
    sanitized_data_time = cal_time(build_noise_tree_end_time, sanitized_data_endtime)
    
    lap_path = './lap_tree/' + save_path
    if not os.path.exists(lap_path):
        os.mkdir(lap_path)
    prefix_path = lap_path + '/lap_tree_data_height_' 
    suffix = str(height) + '_' + str(total_budget) + '_' + \
                str(k) + '_' + str(b) + '_.txt'
    lap_name = prefix_path + suffix
    if os.path.isfile(lap_name) == False:
        with open(lap_name, 'wb') as f:
            pkl.dump(trie, f)
        print(">>>成功保存噪声树文件！")
    else:
        print(">>>原噪声树文件已经存在，不需要重复保存！")
    total_time = build_rawtree_time + build_noise_tree_time + sanitized_data_time
    print('=' * 50)
    print("读数据时间[秒]:", read_data_time)
    print("建原始树时间[秒](Read time):", build_rawtree_time)
    print('建噪声树时间[秒](saniztion time):', build_noise_tree_time)
    print('生成数据集时间[秒](writing time):', sanitized_data_time)
    print('total time[秒]:', round(total_time,4))
    print('=' * 50)
#    res = syn_data(ret_D)
#    prefixspan_demo.main(res, 'db_80w.txt')  # 第2个参数为原始轨迹文件路径

def syn_data(sanitized_data, file):
    # 将地点转为索引的形式，用于频繁模式挖掘
    if not os.path.exists(file):
        print(">>>location2id文件不存在,请检查文件路径是否正确!<<<")
        return 
    with open(file,'rb') as f:
        location2id = pkl.load(f)
    res = []  # 保存轨中地点迹索引的数组 [[1,2,3],[2,3],[4,5,6,7]]  长度可能不一样
    for data in sanitized_data:
        # data ([(l,t,count),()], count)
        trajectory = data[0]  # trajectory [(l,t,count),(l,t,count)]
        count = data[1]
        
        if len(trajectory)>5:
            last_tra = trajectory[5:]
            trajectory = trajectory[:5]
            tmp_tra = []
            for lo in last_tra:
                l2id = location2id[lo]
                tmp_tra.append(l2id)
            res += [tmp_tra] * count
        tmp_tra = []
        for lo in trajectory:
            l2id = location2id[lo]
            tmp_tra.append(l2id)
        res += [tmp_tra] * count
    return res
if __name__ == '__main__':
    height = 6
    total_budget = 1.0
    k, b = 1.5, 1.0
    delta = 1.1
    data_file = './raw_data/sub_dataset_40_90.csv'
    trajectory_file = './raw_trajectory/Tractory_dataset_40_90.npy'
    save_path = 'ds1'  # 保存噪声树文件的目录
    summary_statics(data_file)
    building_noise_tree(height, total_budget, k, b, delta, 
                        data_file, trajectory_file, save_path)
    
    
    

