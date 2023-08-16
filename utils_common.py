# -*- coding: utf-8 -*-
"""
Created on Sun Jan 15 14:34:34 2023

@author: yulun
"""


import pickle as pk


def read_pkl(fn):
    with open(str(fn),'rb')as f:
        D = pk.load(f)
    return D


def dump_pkl(D, fn):
    with open(str(fn), 'ab') as f:
        pk.dump(D, f)