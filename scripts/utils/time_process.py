import numpy as np
import os

def time_str2sec_list(time_str_list):
    #transfer time string list to time second float
    time_sec_list = []
    for time_str in time_str_list:
        h,m,s,ms = time_str.split(":")
        time_sec = float(h)*3600+float(m)*60+float(s)+float(ms)/30
        time_sec_list.append(time_sec)
    return time_sec_list

def time_str2sec(time_str):
    #transfer time string to time second float
    h,m,s,ms = time_str.split(":")
    time_sec = float(h)*3600+float(m)*60+float(s)+float(ms)/30
    return time_sec