# -*- coding: utf-8 -*-
"""
Created on Tue Nov 12 16:30:16 2019

@author: y1881
"""

sanitized_data = [([('华侨城站', 64, 16.008), ('深圳北站', 73, 6.023)], 6.023), 
 ([('华侨城站', 64, 16.008), ('深圳北站', 73, 6.023), ('红树湾', 71, 4.682), 
   ('世界之窗站', 73, 4.682)], 4.682)]

res = []  # 保存轨中地点迹索引的数组 [[1,2,3],[2,3],[4,5,6,7]]  长度可能不一样
for data in sanitized_data:
    # data ([(l,t,count),()], count)
    trajectory = data[0]  # trajectory [(l,t,count),(l,t,count)]
    count = data[1]
    tmp = []
#    while trajectory:
    for tra in trajectory:
        l, t, c = tra
        c = round(c-count,3)
        if c>=0:
            tmp.append((l,t,c))
        print(tmp)

