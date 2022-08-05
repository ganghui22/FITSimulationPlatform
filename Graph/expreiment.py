import time
import jionlp as jio
import calendar
import numpy as np
import torch
import json
def object_time2real_time(tiem_object:str, qurey_time:float)->list:
    """
    时间object映射到实际时间.当时间实体是时间点时，则返回具体时间，列表长度为1.当时间实体是时间段时，怎返回起始时间和终止时间，返回列表长度为2.当无法分析时间时，返回空列表
    :param tiem_object: 输入时间实体
    :param query_time: 请求时间，时间戳格式
    :return: 返回时间戳
    """
    ret = []
    if "会" in tiem_object:
        return [qurey_time + 10*60]
    if tiem_object == "现在":
        return [qurey_time]
    try:
        prase_time = jio.parse_time(tiem_object, qurey_time)
        if prase_time['type'] is "time_span":
            ret = [calendar.timegm(time.strptime(prase_time['time'][0], "%Y-%m-%d %H:%M:%S"))-28800,
                   calendar.timegm(time.strptime(prase_time['time'][1], "%Y-%m-%d %H:%M:%S"))-28800]
        if prase_time['type'] is "time_point":
            ret = [calendar.timegm(time.strptime(prase_time['time'][0], "%Y-%m-%d %H:%M:%S"))-28800]
    except ValueError as e:
        pass
    return ret
def ground_truth2sample_table(label:list,now_time:float, person_dict:dict, localtion_dict:dict,
                              start_time=0, end_time=12*60*60, sample_step=720):
    """
    
    :param label: 测试样本标签,要求是三元组列表，格式-[subject, loction, time]
    :param now_time: 当天时间
    :param person_dict: 人物地点的字典，需要给定每个人物的常驻位置
    :param localtion_dict: 地点列表
    :param start_time: 仿真的起始时间戳 默认为0 即早上8点
    :param end_time: 仿真的结束时间戳 默认为12*60*60 即晚上8点
    :param sample_step: 采样步数
    :return: 返回采样后的每个人位置的真实分布
    """

    real_person_table = dict.fromkeys(list(person_dict.keys()))
    localtion_list = list(localtion_dict.keys())
    that_day_8_o_clock = (now_time//(60*60*24))*60*60*24 # 当天8点的时间戳
    sample_interval = (end_time-start_time) // sample_step 
    # 初始化每个人的位置表
    for person_name in real_person_table:
        sample_time_list = np.zeros((len(localtion_list) + 1,sample_step))
        idx = localtion_list.index(person_dict[person_name]['position'])
        sample_time_list[idx] = [1]*sample_step
        real_person_table[person_name] = sample_time_list
        
    # 根据所给label采样
    for idx, one_sentence_lable_list in enumerate(label):
        if not one_sentence_lable_list:
            continue
        for tuple_hlt in one_sentence_lable_list:
            try:
                subject, location, t  = tuple_hlt
            except:
                continue
            estimated_arrival_time = object_time2real_time(t, that_day_8_o_clock)  # 预计到达时间戳或时间段
            if not estimated_arrival_time:
                print(label[idx])
                print(tuple_hlt, t)
                raise ValueError("object_time error")
            early_time = np.random.normal(loc=0, scale=60*60*(0.5 if "room" in location else 1))      # 采样实际提前了多长时间(可为负数)
            arrival_time = estimated_arrival_time[0] - early_time                                      # 实际到达的时间
            over_stay_time = np.random.normal(loc=0, scale=60*60*(0.5 if "room" in location else 1)) # 采样实际晚走了多长时间(可为负数)
            stay_time = 60*60*2 if len(estimated_arrival_time)==1 else estimated_arrival_time[1] - estimated_arrival_time[0]
            leave_time = estimated_arrival_time[0] + over_stay_time +stay_time   # 实际离开的时间
            # 计算到达和离开的步数
            arrival_step = int((arrival_time - that_day_8_o_clock) // sample_interval)
            leave_step = int((leave_time - that_day_8_o_clock) // sample_interval)

            if subject in ["全体员工","大家", "所有人", "我们"]:
                for p in real_person_table:
                    real_person_table[p][0:][arrival_step:leave_step] = 0
                    real_person_table[p][-1][arrival_step:leave_step] = 1 
            else:
                idx_loc = localtion_list.index(location) if location in localtion_list else -1
                if subject in real_person_table:
                    sample_array = real_person_table[subject]
                    sample_array[0:,arrival_step:leave_step+1] = 0
                    sample_array[idx_loc][arrival_step:leave_step+1] = 1 
                    real_person_table[subject] = sample_array
                else:
                    pass
            
    return real_person_table

def get_acc_one_sample(pre_table, truth_table):
    sum_acc = 0
    for p in pre_table:
        pre = torch.tensor(pre_table[p])
        label = torch.tensor(truth_table[p])
        sum_acc += torch.sum((pre>0.5)==(label==1))/(pre.shape[0]*pre.shape[1])
    return sum_acc/len(pre_table)