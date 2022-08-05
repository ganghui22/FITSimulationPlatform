# -*-coding:utf-8-*-
import json

import NlpToolKit.Chinese.DialoguePrediction as extract_triple
import Graph.DynamicSpaceTimeGraph_SIMU as graph
import numpy as np
import time
from Graph.expreiment import get_acc_one_sample


class deal():
    def __init__(self):
        self.triple = extract_triple.DialoguePrediction()

    def caluate(self,stride,begin,end,messege,label):
        self.update_graph = graph.update(stride)
        for i in messege:
            # print(i)
            m.dynamic_space_time_graph(i,label)
            # print(m.person_get_location('港晖'))

        pre,truth=self.update_graph.simulate_time(begin=begin,end=end,stride=stride)
        res=get_acc_one_sample(pre,truth)
        print(res)
        return res



    def dynamic_space_time_graph(self, text,label):
        triple = self.triple(text)
        # print(triple)
        self.update_graph.receive_messege(triple, text,label)
        self.if_need_change = 0

    def person_get_location(self, person_name):
        if person_name in self.update_graph.graph_rel:
            person_message = self.update_graph.graph_rel[person_name]
            # print(person_message)
            a=person_message['rel_now']
            max_loc_id=np.where(a==np.max(a))[0][0]
            # print(self.update_graph.location_total[max_loc_id])
            return self.update_graph.location_total[max_loc_id]
        else:
            return None
    def get_graph(self):
        return self.update_graph.image
    def get_now_time(self):
        now_time=stamptotime(self.update_graph.now_time)
        return now_time


def stamptotime(stamp):
    timeArray = time.localtime(stamp)
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    return otherStyleTime


if __name__ == '__main__':
    m = deal()
    with open('/home/llj/FITSimulationPlatform/experiment.json','r') as f:
        dataset=json.load(f)
    # messege = ['兰军:大家12点到到讨论区讨论一下',
    #            '卞港晖:我参加不了，我12点要在516开个线上会议',
    #            '兰军:行，其他人呢',
    #            '小飞:收到',
    #            '晨峻:我没问题',
    #            '姚峰:我也可以',
    #
    #            ]
    sum=0
    nums=len(dataset)
    for i in dataset:
        messege=i['dialogue']
        label=i['label']
        sum+=m.caluate(720,0,0,messege,label)
        print()
        # time.sleep(5)
    print(sum/nums)
    # m.caluate(720, 0, 0, messege)

    # print(m.person_get_location('港晖'), '\n')
    # print(m.person_get_location('兰军'), '\n')
    # print('need_update:', m.update_graph.need_update, '\n')
    # print('tmp_graph:', m.update_graph.tmp_graph, '\n')
    # print('event:', m.update_graph.event, '\n')
    # print('vitual_event:', m.get_sample())
    #
