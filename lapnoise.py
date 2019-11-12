# -*- coding: utf-8 -*-
"""
Created on Mon Nov 11 14:07:47 2019

@author: y1881
"""

import random
import math

def signum(x):
    if x > 0:
        return 1.0
    if x < 0:
        return -1.0
    if x == 0:
        return 0

def lap_noise(epsilon, sensitivity=1.0):
    # 产生噪声
    randomDouble = random.random() - 0.5
    noise = - (sensitivity / epsilon) * signum(randomDouble) * math.log(1 - 2 * abs(randomDouble))
    return round(noise, 4)