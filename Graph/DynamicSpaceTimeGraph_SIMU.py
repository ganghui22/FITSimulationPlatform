# -*-coding:utf-8-*-
from concurrent.futures import thread
import multiprocessing
import random

import numpy
from scipy.stats import skewnorm
import networkx as nx

from PathPlanningAstar.astar import world_to_pixel
import cv2
import time
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg

from PIL import Image
import matplotlib
import json
import copy
import threading
import time
import jionlp as jio
import calendar
from Graph.expreiment import ground_truth2sample_table,get_acc_one_sample
location = ['room510', 'room511', 'room512', 'room513', 'room514', 'room515', 'room516']
other_location = ['1号会议室', '2号会议室', '休息室', '茶水间', '1001教室', '1002教室', '1003教室', '讨论区', '其他']
with open('/home/llj/FITSimulationPlatform/data/Location_list.json') as f:
    location_dict = json.load(f)


total_time_location=30*60
total_time_other=60*60
sigma_location=total_time_location/2
sigma_other_location=total_time_other/2


# def mark_location():
#     import numpy as np
#     location_list = {'elevator_1': (14.30, -51.42), 'elevator_2': (10.10, -3.37), '文栋': (81.05, 13.98),
#                      'meeting': (74.90, 10.18), '刘老师': (69.55, -69.32)}
#     src = cv2.imread('./PathPlanningAstar/fit4_5Dealing_draw.png')
#     for key, value in location_list.items():
#         text = key
#         cv2.putText(src, text, world_to_pixel(world_points=(value[0], value[1] - 5), image_size=(2309, 2034)),
#                     cv2.FONT_HERSHEY_COMPLEX, 1.0, (0, 0, 255), 2)
#         cv2.circle(src, world_to_pixel(world_points=(value[0], value[1]), image_size=(2309, 2034)), 5, (0, 0, 255), -1)
#     cv2.imwrite('./result_mark.png', src)


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, set):
            return list(obj)
def timetostamp(tss1):
    timeArray = time.strptime(tss1, "%Y-%m-%d %H:%M:%S")
    timeStamp = int(time.mktime(timeArray))
    return timeStamp


def stamptotime(stamp):
    timeArray = time.localtime(stamp)
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    return otherStyleTime

def cal_time(a, total_time, u, sigma, t_th):
    a = a
    x = np.linspace(0, total_time, total_time)
    u = u
    sigma = sigma
    l = skewnorm.pdf(x, a, u, sigma)
    # print(l[t_th])
    return l[t_th]

def cal_time_zheng(total_time,u,sigma,t_th):
    x=np.arange(0,total_time,1)
    pdf = np.exp(-((x - u) ** 2) / (2 * sigma ** 2)) / (sigma * np.sqrt(2 * np.pi))
    pdf=(pdf-np.min(pdf))/(np.max(pdf)-np.min(pdf))
    return pdf[t_th]
    

from scipy import stats
def cal_time_zhishu(sigma,time_go,time):
    '''
    time is s
    sigma is 参数、
    一般在sigma以后，可能性降为0.5
    '''
    r = 1 / sigma
    X = []
    Y = []
    for x in np.linspace(0, time_go, time_go):
        if x == 0:
            continue
        #   p = r*math.e**(-r*x)  #直接用公式算
        p = stats.expon.cdf(x, scale=1 / r)  # 用scipy.stats.expon工具算,注意这里scale参数是标准差
        X.append(x)
        Y.append(p)
    Y=1-(Y - np.min(Y)) / (np.max(Y) - np.min(Y))  #
    # print(Y[time])
    return Y[time]




class Graph():
    def __init__(self):
        self.person = ['港晖', '晨峻', '伟华', '刘老师', '袁老师', '刘毅', '姚峰', '侯煊', '小飞', '郝伟', '海洋', '春秋', '靖宇', '兴航', '文栋', '兰军',
                       '李老师', '馨竹']
        self.location = ['Room510', 'Room511', 'Room512', 'Room513', 'Room514', 'Room515', 'Room516']
        self.other_location = ['1号会议室', '2号会议室', '讨论区', '休息室']
        self.outdoor = ['超市', '电影院', '上海', '公园', '机场', '食堂', '1001教室', '1002教室', '1003教室']
        self.pos_1 = {
            '港晖': [-0.06590949, -0.98459114], 'Room516': [-0.11786665, -0.85143201], '晨峻':
                [-0.00480235, 0.65759833], 'Room510': [-0.11290646, 0.68940615], '伟华':
                [-0.05434, 0.45155499], '刘老师': [-0.63341604, -0.76072163], 'Room511':
                [-0.52784206, -0.63116621], '袁老师': [0.38728818, -0.72880871], 'Room512':
                [0.38210208, -0.86613776], '刘毅': [-0.20869839, -0.98553632], '姚峰':
                [-0.08793546, 0.85471983], '侯煊': [0.47539044, 0.69069804], 'Room515':
                [0.38868173, 0.56584303], '小飞': [-0.22183974, 0.82653035], '郝伟':
                [0.89141278, 0.33221307], 'Room513': [0.7212116, 0.32303753], '海洋':
                [-0.36248728, 0.10174334], 'Room514': [-0.55537919, 0.20630467], '春秋':
                [-0.64660707, 0.3322593], '靖宇': [0.33638749, 0.69034494], '兴航':
                [0.35578187, 0.39735446], '文栋': [-0.72049126, 0.23389377], '兰军':
                [0.65899121, 0.41378254], '李老师': [0.2501025, -0.81441738], '馨竹':
                [-0.07180646, -0.6593223], ' ': [-0.81032829, 0.01610876], '  ': [-0.81032829, 0.01610876], '1号会议室':
                [-0.81032829, 0.01610876], '茶水间':
                [-0.64787042, 0.60134683], '讨论区':
                [1., 0.02354849], '休息室': [-0.74027552, -0.46807695], '其他': [0.074027552, -0.46807695],
            '2号会议室': [0.84768565, -0.59677]}
        # '1001教室': [0.89010407, -0.27253654], '1002教室':
        # [-0.92707715, -0.29802952], '1003教室': [0.80476599, 0.56320228],'2号会议室': [0.84768565, -0.59677],
        self.man_anotate = {'Room511': [-0.58564247, 0.25416477], 'Room512': [-0.38256115, -0.57270125],
                            'Room513': [0.33214105, -0.87734133], 'Room515': [0.57428342, -0.38469979],
                            'Room514': [0.22919887, 0.65937288], 'Room510': [-0.5283078, 0.56331821],
                            'Room516': [0.43335628, 0.92137264]}

    def draw(self, graph_rel):

        plt.rcParams['font.sans-serif'] = ['SimHei']

        self.G = nx.Graph()
        self.graph_rel = graph_rel
        self.node_colors = []
        self.edge_colors = []
        for personName, all_rel in self.graph_rel.items():
            if all_rel['rel_now'] != None:
                for other in self.outdoor:
                    if all_rel['rel_now'][1] == other:
                        all_rel['rel_now'][1] = '其他'
                        break
                self.G.add_edge(all_rel['rel_now'][0], all_rel['rel_now'][1], edge_color=all_rel['rel_now'][2] * 1000)
            else:
                self.G.add_edge(all_rel['rel_base'][0], all_rel['rel_base'][1],
                                edge_color=all_rel['rel_base'][2] * 1000)
        self.G.add_edge(' ', '1号会议室', edge_color=0)
        self.G.add_edge('  ', '1号会议室', edge_color=1000)

        '''添加orther_location的node'''
        self.G.add_nodes_from(self.other_location)
        self.G.add_nodes_from(self.location)
        self.G.add_nodes_from(self.person)
        self.G.add_node('其他')

        '''设置排列的形式'''
        plt.rcParams['figure.figsize'] = (16, 8)
        self.pos = self.pos_1
        '''删掉某一个节点'''
        # self.G.remove_edge(' 港晖', 'Room511')
        for i in self.G.nodes():
            if i in self.other_location:
                self.node_colors.append('pink')
            elif i in self.location:
                self.node_colors.append('#9370db')  # 浅紫色
            else:
                self.node_colors.append('#1f78b4')

        eee = nx.get_edge_attributes(self.G, 'edge_color')
        for edge in self.G.edges():
            self.edge_colors.append(eee[edge])
        # print(self.edge_colors)
        nx.draw_networkx_labels(self.G, self.pos, horizontalalignment='center', verticalalignment="top")
        nx.draw_networkx(self.G, with_labels=False, width=2, pos=self.pos, node_color=self.node_colors,
                         edge_color=self.edge_colors, edge_cmap=plt.cm.Blues)  # add colors
        plt.savefig('Graph/graph_update.png')
        canvas=FigureCanvasAgg(plt.gcf())
        # 绘制图像
        canvas.draw()
        # 获取图像尺寸
        w, h = canvas.get_width_height()
        # 解码string 得到argb图像
        buf = np.fromstring(canvas.tostring_argb(), dtype=np.uint8)
        # 重构成w h 4(argb)图像
        buf.shape = (w, h, 4)
        # 转换为 RGBA
        buf = np.roll(buf, 3, axis=2)
        # 得到 Image RGBA图像对象 (需要Image对象的同学到此为止就可以了)
        image = Image.frombytes("RGBA", (w, h), buf.tostring())
        # 转换为numpy array rgba四通道数组
        image = np.asarray(image)
        # 转换为rgb图像
        rgb_image = image[:, :, :3]
        # print(rgb_image)
        img=cv2.cvtColor(rgb_image,cv2.COLOR_BGR2RGBA)

        plt.close()
        self.G.clear()
        return img


class update():
    def __init__(self,stride):
        self.id = 0
        self.location_total=[]
        # print(location_dict)
        for i,xy in location_dict.items():
            self.location_total.append(i.lower())
        self.location_id = {}
        for i in self.location_total:
            self.location_id[i] = self.id
            self.id += 1
            print(self.id)
        self.stride=stride#采样步数
        self.distribute = [0] * (self.id + 1)
        # print(self.distribute)
        self.lock=threading.Lock()
        # self.condition = threading.Condition()
        self.total_time_o = 0
        self.time = time.asctime(time.localtime(time.time()))
        self.messege = None
        self.waiting_update = []
        with open('/home/llj/FITSimulationPlatform/data/Person.json', 'r', encoding='utf-8') as f:
            self.ppp = json.load(f)
        # with open('Graph/Graph.json', 'r', encoding='utf-8') as load_f:
        #     self.graph_rel = json.load(load_f)
        self.teacher=['刘华平','刘老师']
        self.graph_rel = {}
        self.need_update={}
        self.virtual_person_location_table = {}
        for p in self.ppp:
            self.graph_rel[p] = {}
            self.graph_rel[p]["rel_base"] = [self.ppp[p]["name"], self.ppp[p]["position"], 1]
            self.graph_rel[p]["rel_now"] =self.distribute.copy()
            # print(self.graph_rel[p]["rel_base"][1].lower())
            # print(self.location_id[self.graph_rel[p]["rel_base"][1].lower()])
            self.graph_rel[p]['rel_now'][self.location_id[self.graph_rel[p]["rel_base"][1].lower()]]=1
            self.need_update[p]={}
            self.virtual_person_location_table[p] = [[0]*self.stride for i in range(self.id+1)]

        self.today_time = time.localtime(time.time())
        self.now_time = timetostamp(f"{self.today_time.tm_year}-{self.today_time.tm_mon}-{self.today_time.tm_mday} 08:00:00")

        self.today = timetostamp(f"{self.today_time.tm_year}-{self.today_time.tm_mon}-{self.today_time.tm_mday} 00:00:00")
        '''设置时间函数的参数'''
        self.sigma = 100  # 影响最大的可能性---可能性可以乘上sigma
        self.u = 100  # 影响最左边的值
        self.a_time = 10  # 影响左边下降的梯度
        self.person = [p for p in self.ppp]

        self.if_need_change = 0
        self.tmp_graph = {}
        self.event = {}
        self.image=None
        self.mohu=['一会儿','一会','过会']
        self.vitual_envent={}


    def receive_messege(self, triple, text,label):
        # print(triple)
        # triple[2]=self.object_time2real_time(triple[2],time.time())
        self.triple = triple
        for k,lll in enumerate(self.triple):
            if lll[2]!='':
                self.triple[k][2]=self.object_time2real_time(lll[2],time.time())
        self.text = text
        self.tmp_dynamic_time_graph()
        self.label=label


    def del_messege(self):
        self.messege = None

    def update_rel(self):
        '''-------------------------------根据json格式更改-接收消息时候的改变--------------------------------'''
        # print('---------go in updat rel--------------')
        # tmp_graph = self.tmp_graph.copy()
        delete_list=[]
        for time_dy, messege in self.tmp_graph.items():
            if self.now_time >= timetostamp(time_dy[0]):
                # print('---------go in updat rel del!!!--------------')
                # time.sleep(0.0001)
                # print(stamptotime(self.now_time),time_dy)
                for per_event in messege:
                    # print(per_event)
                    for p in per_event:
                        ch_person = p[0]
                        ch_location = p[1]
                        # location发生了变化
                        # if self.graph_rel[ch_person]['rel_base'][1] != ch_location:
                        self.graph_rel[ch_person]['rel_now'][self.location_id[ch_location.lower()]] = 1
                        for i in enumerate(self.graph_rel[ch_person]['rel_now'][:self.location_id[ch_location]]):
                            self.graph_rel[ch_person]['rel_now'][i[0]] = 0
                        for j in enumerate(self.graph_rel[ch_person]['rel_now'][self.location_id[ch_location] + 1:]):
                            self.graph_rel[ch_person]['rel_now'][self.location_id[ch_location] + 1+j[0]] = 0
                        self.need_update[ch_person][time_dy[0]]=[ch_person, ch_location, time_dy]
                        # else:
                        #     self.graph_rel[ch_person]['rel_now'] = None
                        #     self.need_update[ch_person]=[ch_person, ch_location, time_dy]
                # del self.tmp_graph[time_dy[0]]
                delete_list.append(time_dy[0])
        for o in delete_list:
            del self.tmp_graph[o]
            # time.sleep(5)
        # tmp =self.event.copy()
        # tmp1 = self.event.copy()  # 防止在接受消息的时候被删掉
        dele_event=[]
        for person_name, p in self.event.items():
            for num, person_event in enumerate(p):  # 取出事件
                if self.now_time < timetostamp(person_event[0][2][0]):
                    continue
                else:
                    for per in person_event:
                        ch_person = per[0]
                        ch_location = per[1]
                        # if self.graph_rel[ch_person]['rel_base'][1] != ch_location:

                        for i in enumerate(self.graph_rel[ch_person]['rel_now'][:self.location_id[ch_location]]):
                            self.graph_rel[ch_person]['rel_now'][i[0]] = 0
                        for j in enumerate(self.graph_rel[ch_person]['rel_now'][self.location_id[ch_location] + 1:]):
                            ind=self.location_id[ch_location]+1+j[0]
                            self.graph_rel[ch_person]['rel_now'][ind] = 0
                        self.graph_rel[ch_person]['rel_now'][self.location_id[ch_location]] = 1
                        self.need_update[ch_person][person_event[0][2][0]] = [ch_person, ch_location, person_event[0][2]]
                    # del tmp1[person_name]
                    dele_event.append(person_name)
        for op in dele_event:
            del self.event[op]
        # '--------------模拟人离开的--------------------'
        # # print(self.need_update)
        # if self.need_update:
        #     for k,i in self.need_update.items():#k表示人
        #         for t,e in i.items():
        #             '''
        #             {港晖：{到到达地点的时间1：[地点，离开的时间]，到到达地点的时间2：[地点，离开的时间],,,,,}},{兰军：{时间1：【地点，离开时间】}}
        #             '''
        #             if k not in self.vitual_envent:
        #                 self.vitual_envent[k] = {}
        #             # print('===============================================',i[2])
        #             # if i[2] not in self.vitual_envent[k]:
        #             #     self.vitual_envent[k][i[2]]=[]
        #             if t not in self.vitual_envent[k]:
        #                 self.vitual_envent[k][t]=[e[1],stamptotime(timetostamp(t)+sample(e[1]))]
        #             else:
        #                 if e[1]==self.vitual_envent[k][t][0]:#防止重新采样
        #                     pass
        #                 else:
        #                     self.vitual_envent[k][t] = [e[1], stamptotime(timetostamp(t) + sample(e[1]))]


        # print('============rel====================\n',self.need_update)

    def nomalize_triple(self,value):
        if value[1] == '你':  # 处理'找你'的情况
            value[1] = self.old_initiator

        value[0] = self.normalize_name(value[0])
        value[1] = self.normalize_location(value[1])
        if value[1] !=[] and value[1] not in self.location_total:
            value[1]='其他'
        if value[1] != '' and value[1] in self.person:  # 当地点是人的时候，对应这个人的办公室
            if self.graph_rel[value[1]]['rel_now'] != None:
                value[1] = self.graph_rel[value[1]]['rel_now'][1]
            else:
                value[1] = self.graph_rel[value[1]]['rel_base'][1]

        if value[1] != '' and '的办公室' in value[1]:
            value[1] = value[1].split('的办公室')[0]
            value[1] = self.graph_rel[value[1]]['rel_base'][1]

        # if value[2] != '':
        #     value[2] = self.get_time(value[2])
        if value[1] != '' and value[2] != '':
            self.per_event.append([value[0], value[1], value[2]])
            # print(self.per_event)
            if value[0] in ['我们', '大家', '咱们', '全体员工', '所有人']:
                self.total_person_flag = 1
        return value
    def normalize_location(self,l):
        for j in location:
            if l in j :
                l=j
                break
        return l
    def normalize_name(self, m):
        for p in self.ppp:
            if p in m:
                m = p
                break
        for t in self.teacher:
            if t == m:
                m = '刘老师'
                break
        return m

    def tmp_dynamic_time_graph(self):  # single text
        # self.need_update = {}  # 指的是需要进一步继续时空概率推断的关系
        self.if_need_change = 0
        for i in ['那我们就换', '那我们换',
                  '那咱们就换', '那咱们换',
                  '那咱们改', '那我们就改',
                  '那我们改', '那咱们就改']:
            if i in self.text:
                self.if_need_change = 1
                break
        self.initiator = self.text.split(':')
        self.initiator = self.initiator[0]  # 事件的发起者
        #修改名字不一样的地方，
        self.initiator=self.normalize_name(self.initiator)


        if self.initiator not in self.event:
            self.event[self.initiator] = []
        self.per_event = []

        if self.if_need_change == 0:  # 发起者发起的新事件，进行事件记录
            try:
                if self.event[self.initiator] != []:
                    time_signal = self.event[self.initiator][0][0][2]
                    # print(self.event[self.initiator][0])
                    if time_signal not in self.tmp_graph:
                        self.tmp_graph[time_signal] = []
                    self.tmp_graph[time_signal].append(self.event[self.initiator][0])
                    del self.event[self.initiator][0]
                self.total_person_flag = 0

                for value in self.triple:
                    value=self.nomalize_triple(value)
                    if self.total_person_flag == 1:  # 把我们更换成人名
                        event_time = value[2]
                        event_location = value[1]
                        self.per_event = []
                        for i in self.person:
                            self.per_event.append([i, event_location, event_time])
                if self.triple != [] and self.per_event!=[]:
                    self.event[self.initiator].append(self.per_event)
            except:
                print('-------can not record the triple, drop out----1!!!!--------')

        # 由于是新的时间，所以把之前的存在的事件就默认已经确定不变，放在self.tmp_graph中，


        elif self.if_need_change == 1:  # 那就xxx
            try:
                for value in self.triple:
                    value=self.nomalize_triple(value)

                    # 时间地点都有
                    if value[2] != '' and value[1] != '':
                        for per in self.event[self.initiator][0]:
                            per[1] = value[1]
                            per[2] = value[2]
                            self.per_event.append(per)
                    # 地点需要更新
                    if value[2] == '' and value[1] != '':
                        for per in self.event[self.initiator][0]:
                            per[1] = value[1]
                            self.per_event.append(per)

                    # 时间需要更新
                    if value[2] != '' and value[1] == '':
                        for per in self.event[self.initiator][0]:
                            per[2] = value[2]
                            self.per_event.append(per)
                self.event[self.initiator].append(self.per_event)
                time_signal = self.event[self.initiator][0][0][2][0]
                if time_signal not in self.tmp_graph:
                    self.tmp_graph[time_signal] = []
                self.tmp_graph[time_signal].append(self.event[self.initiator][0])
                del self.event[self.initiator][0]
            except:
                print('---------------can not change the time or location----2!!!!!---------------------')
        elif self.if_need_change==2:
            try:
                if self.event[self.initiator] != []:
                    time_signal = self.event[self.initiator][0][0][2][0]
                    # print(self.event[self.initiator][0])
                    if time_signal not in self.tmp_graph:
                        self.tmp_graph[time_signal] = []
                    self.tmp_graph[time_signal].append(self.event[self.initiator][0])
                    del self.event[self.initiator][0]
                total_person_flag = 0
                for value in self.triple:
                    value[0] = self.normalize_name(value[0])
                    value[1] = self.normalize_location(value[1])
                    value[1]=self.old_initiator
                    if value[1] != '' and value[1] in self.person:  # 当地点是人的时候，对应这个人的办公室
                        if self.graph_rel[value[1]]['rel_now'] != None:
                            value[1]=self.graph_rel[value[1]]['rel_base'][1]
                        else:
                            value[1] = self.graph_rel[value[1]]['rel_base'][1]
                    if value[1] != '' and '的办公室' in value[1]:
                        value[1] = value[1].split('的办公室')[0]
                        value[1] = self.graph_rel[value[1]]['rel_base'][1]

                    # if value[2] != '':
                    #     value[2] = self.get_time(value[2])

                    if value[1] != '' and value[2] != '':
                        self.per_event.append([value[0], value[1], value[2]])
                        # print(self.per_event)
                        if value[0] in ['我们', '大家', '咱们', '全体员工', '所有人']:
                            total_person_flag = 1

                if total_person_flag == 1:  # 把我们更换成人名
                    event_time = value[2]
                    event_location = value[1]
                    self.per_event = []
                    for i in self.person:
                        self.per_event.append([i, event_location, event_time])
                if self.triple != [] and self.per_event!=[]:
                    self.event[self.initiator].append(self.per_event)
            except:
                print('-------can not record the triple, drop out----3!!!!--------')

        time.sleep(0.01)
        self.old_initiator=self.initiator



    # print('====event=========',self.event)

    def update_auto(self):  # 自动的改变
        # self.a = Graph()
        # img = cv2.imread('Graph/graph_update.png')
        # while 1:
        # self.lock.acquire()
        try:
            self.update_rel()
            '''按照时间函数更新'''
            # img = plt.imread('Graph/graph_update.png')
            # m = self.need_update.copy()
            # mm=self.need_update.copy()
            # m = self.need_update
            # mm = m
            # print(stamptotime(self.now_time))
            # print('for 之前',self.need_update)
            need_delete_list = []
            for k, info in self.need_update.items():
                for t, e in info.items():
                    # print('for 之后', self.need_update)
                    if len(e[2])==1:
                        '''设置时间函数的计算参数'''
                        if e[1] in location:
                            self.sigma = sigma_location
                            self.total_time_o = total_time_location
                        elif e[1] in other_location:
                            self.sigma = sigma_other_location
                            self.total_time_o = total_time_other
                        # 更新可能性

                        time_err = self.now_time - timetostamp(e[2][0])

                        if 0 < time_err < self.total_time_o - 1:
                            # tmp_possibillity = cal_time(self.a_time, self.total_time_o, self.u, self.sigma,
                            #                             time_err) * self.sigma
                            # tmp_possibillity=cal_time_zhishu(self.sigma,self.total_time_o,time_err)
                            tmp_possibillity = cal_time_zheng(self.total_time_o, 0, self.sigma, time_err)
                            self.graph_rel[k]['rel_now'][self.location_id[e[1]]] = tmp_possibillity  # 更新可能性
                            self.graph_rel[k]['rel_now'][
                                self.location_id[self.graph_rel[k]['rel_base'][1].lower()]] = 1 - tmp_possibillity
                        # print(stamptotime(self.now_time),self.graph_rel[info[0]]['rel_now'])

                        # 小于阈值的时候，相当于不再存在
                        if time_err > self.total_time_o:  # 这里加上time——err的

                            self.graph_rel[k]['rel_now'][self.location_id[self.graph_rel[k]['rel_base'][1].lower()]] = 1
                            self.graph_rel[k]['rel_now'][self.location_id[e[1]]] = 0
                            # del m[k][t]
                            need_delete_list.append((k, t))

                            # info_detail = '{} come back to office!!!'.format(info[0])

                    else:
                        if timetostamp(e[2][0])<self.now_time<timetostamp(e[2][1]):
                            self.graph_rel[k]['rel_now'][self.location_id[e[1]]] =1
                            for i in enumerate(self.graph_rel[k]['rel_now'][:self.location_id[e[1]]]):
                                self.graph_rel[k]['rel_now'][i[0]] = 0
                            for j in enumerate(
                                    self.graph_rel[k]['rel_now'][self.location_id[e[1]] + 1:]):
                                self.graph_rel[k]['rel_now'][self.location_id[e[1]] + 1 + j[0]] = 0
                        elif self.now_time>timetostamp(e[2][1]):
                            self.graph_rel[k]['rel_now'][self.location_id[self.graph_rel[k]['rel_base'][1].lower()]] = 1
                            self.graph_rel[k]['rel_now'][self.location_id[e[1]]] = 0
                            # del m[k][t]
                            need_delete_list.append((k,t))

            for a, b in need_delete_list:
                del self.need_update[a][b]
        # self.need_update = m
        except Exception as e:
            print(str(e))
        # self.lock.release()
            # print(self.graph_rel['港晖'])

            # print(self.graph_rel)
            # self.image=self.a.draw(self.graph_rel)
            # time.sleep(0.1)
            # cv2.putText(image, stamptotime(self.now_time), (200, 90), cv2.FONT_HERSHEY_COMPLEX, 2.0, (100, 200, 200),
            #             2)
            # cv2.imshow('graph', image)
            #
            # if cv2.waitKey(1) & 0xFF == ord('q'):
            #     break
            # self.now_time += 60s

    def simulate_time(self,begin=0,end=0,stride=12):
        s_begin = self.now_time + begin * 60*60
        s_end = self.now_time + (12 + end) * 60*60
        diff_time = (s_end-s_begin)//self.stride
        # print(diff_time)
        nums=0#第num次采样
        time_copy = s_begin
        total_days=1
        result={}
        truth=ground_truth2sample_table(self.label, self.now_time,self.ppp,localtion_dict=location_dict,start_time=begin,sample_step=stride)
        while total_days>0:
            # time.sleep(1)
            # self.lock.acquire()
            result=[]
            self.now_time+=diff_time
            # print(stamptotime(self.now_time))
            self.update_auto()
            # print(self.graph_rel['港晖'])
            for pp,table in self.virtual_person_location_table.items():
                for cloumn in range(self.id+1):#地点
                    # print(cloumn,nums)
                    self.virtual_person_location_table[pp][cloumn][nums]=self.graph_rel[pp]['rel_now'][cloumn]
            result.append(self.virtual_person_location_table)
            nums+=1
            if nums==self.stride:
                time_copy+=24*60*60
                self.now_time=time_copy
                nums=0
                total_days -= 1
            # print('-----------------------------------',self.virtual_person_location_table)
            # with open('./experiment_result.json', 'w',encoding='utf-8') as f:
            #     f.write(json.dumps(result,ensure_ascii=False))

            # time.sleep(2)
            # self.lock.release()
        return self.virtual_person_location_table,truth


    def object_time2real_time(self,tiem_object: str, qurey_time: float) -> list:
        """
        时间object映射到实际时间.当时间实体是时间点时，则返回具体时间，列表长度为1.当时间实体是时间段时，怎返回起始时间和终止时间，返回列表长度为2.当无法分析时间时，返回空列表
        :param tiem_object: 输入时间实体
        :param query_time: 请求时间，时间戳格式
        :return: 返回时间戳
        """
        # print(tiem_object)
        ret = []
        result = []
        if "会" in tiem_object:
            return [stamptotime(qurey_time + 10 * 60)]
        if tiem_object == "现在":
            return [stamptotime(qurey_time)]
        try:
            prase_time = jio.parse_time(tiem_object, qurey_time)
            if prase_time['type'] is "time_span":
                ret = [calendar.timegm(time.strptime(prase_time['time'][0], "%Y-%m-%d %H:%M:%S")) - 28800,
                       calendar.timegm(time.strptime(prase_time['time'][1], "%Y-%m-%d %H:%M:%S")) - 28800]
            if prase_time['type'] is "time_point":
                ret = [calendar.timegm(time.strptime(prase_time['time'][0], "%Y-%m-%d %H:%M:%S")) - 28800]
            for i in ret:
                result.append(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(i)))

        except ValueError as e:
            pass
        return result

    # def get_time(self,detail):
    #     if '分钟后' in detail:
    #         detail_time=detail.split('分',1)
    #         start_time=stamptotime(self.now_time+detail_time[0]*60)
    #     elif detail == '现在':
    #         start_time = stamptotime(self.now_time)
    #     elif ':' in detail:
    #         evening=0
    #         add_flag=0
    #         if '明天' in detail:
    #             detail = detail[2:]
    #             add_flag = 1
    #         if '下午' in detail:
    #             evening = 1
    #             detail = detail[2:]
    #         if '上午' in detail:
    #             detail = detail[2:]
    #         if '晚上' in detail:
    #             detail=detail[2:]
    #             evening=1
    #         split_time = detail.split(':', 1)
    #         hours = int(split_time[0])
    #
    #         if evening == 1 and hours <= 12:
    #             hours += 12
    #         minutes = split_time[1]
    #         if '0' in minutes:
    #             if minutes[0]=='0':
    #                 minutes=int(minutes[1])
    #             else:
    #                 minutes=int(minutes[0])*10+int(minutes[1])
    #         else:
    #             minutes=int(split_time[1])
    #         stamp_time = add_flag * 24 * 60 * 60 + hours * 60 * 60 + minutes * 60
    #         start_time_stamp = stamp_time + self.today
    #         start_time = stamptotime(start_time_stamp)
    #     elif '：' in detail:
    #         evening=0
    #         add_flag=0
    #         if '明天' in detail:
    #             detail = detail[2:]
    #             add_flag = 1
    #         if '下午' in detail:
    #             evening = 1
    #             detail = detail[2:]
    #         if '上午' in detail:
    #             detail = detail[2:]
    #         if '晚上' in detail:
    #             detail=detail[2:]
    #             evening=1
    #         split_time = detail.split(':', 1)
    #         hours = int(split_time[0])
    #
    #         if evening == 1 and hours <= 12:
    #             hours += 12
    #         minutes = split_time[1]
    #         if '0' in minutes:
    #             if minutes[0]=='0':
    #                 minutes=int(minutes[1])
    #             else:
    #                 minutes=int(minutes[0])*10+int(minutes[1])
    #
    #         else:
    #             minutes=int(split_time[1])
    #         stamp_time = add_flag * 24 * 60 * 60 + hours * 60 * 60 + minutes * 60
    #         start_time_stamp = stamp_time + self.today
    #         start_time = stamptotime(start_time_stamp)
    #     else:
    #         for i in self.mohu:
    #             if i in detail:
    #                 start_time=stamptotime(self.now_time+10*60)
    #                 return start_time
    #         today_time = time.localtime(time.time())
    #         today = f"{today_time.tm_year}-{today_time.tm_mon}-{today_time.tm_mday} 00:00:00"
    #         today = timetostamp(today)
    #         add_flag = 0
    #         evening = 0
    #         if '半' in detail:
    #             detail = detail.replace('半', '30分')
    #         if '明天' in detail:
    #             detail = detail[2:]
    #             add_flag = 1
    #         if '下午' in detail:
    #             evening = 1
    #             detail = detail[2:]
    #         if '上午' in detail:
    #             detail = detail[2:]
    #         if '晚上' in detail:
    #             detail=detail[2:]
    #             evening=1
    #         split_time = detail.split('点', 1)
    #         hours = int(split_time[0])
    #         if evening == 1 and hours <= 12:
    #             hours += 12
    #         if '分' in split_time[1]:
    #             minutes = int(split_time[1].split('分', 1)[0])
    #         else:
    #             minutes = 0
    #
    #         stamp_time = add_flag * 24 * 60 * 60 + hours * 60 * 60 + minutes * 60
    #         start_time_stamp = stamp_time + today
    #         start_time = stamptotime(start_time_stamp)
    #     # print(start_time)
    #     return start_time

def init_graph(Person, Location):
    graph = {}
    for k, person in enumerate(Person):
        m = random.randint(0, len(Location) - 1)
        person_relashionship = {}
        person_relashionship['rel_base'] = [person, Location[m], 1]
        person_relashionship['rel_now'] = None
        graph[person] = person_relashionship

    with open('Graph/graph.json', "w", encoding='utf-8') as f:
        json.dump(graph, f, cls=MyEncoder, ensure_ascii=False)
    return graph


def sample(location):
    per_location=location
    if per_location in location:
        sigma=sigma_location
        total=total_time_location
    else:
        sigma=sigma_other_location
        total=total_time_other
    gfg=np.random.exponential(sigma,total)
    m=total-gfg[random.randint(0,total-1)]
    while m<0:
        m=total-gfg[random.randint(0,total-1)]
    # print(m)
    return m


if __name__ == '__main__':
    # import threading
    #
    # '''-------------初始化他们的办公室--------------'''
    # # Person = ['港晖', '晨峻', '伟华', '刘老师', '袁老师', '刘毅', '姚峰', '侯煊', '小飞',
    # #                '郝伟', '海洋', '春秋', '靖宇', '兴航', '文栋', '兰军', '李老师', '馨竹']
    # # Location = ['Room510', 'Room511', 'Room512', 'Room513', 'Room514', 'Room515', 'Room516']
    # # other_location = ['1号会议室', '2号会议室', '休息室', '茶水间', 'Toilet']
    # # init_graph(Person,Location)
    #
    # # g=Graph()
    # # g.draw(base_graph_rel)
    #
    # m = update()
    # thread1 = threading.Thread(target=m.update_auto)
    # thread2 = threading.Thread(target=m.receive_messege)
    # #
    # thread2.start()
    # thread1.start()
    m=update(12)
    m.simulate_time(False,0,0)
