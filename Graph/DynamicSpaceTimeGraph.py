# -*-coding:utf-8-*-
import random

from scipy.stats import skewnorm
import networkx as nx

from PathPlanningAstar.astar import world_to_pixel
import cv2
import time
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib
import json

location = ['Room510', 'Room511', 'Room512', 'Room513', 'Room514', 'Room515', 'Room516']
other_location = ['1号会议室', '2号会议室', '休息室', '茶水间', '1001教室', '1002教室', '1003教室', '讨论区', '其他']


def mark_location():
    import numpy as np
    location_list = {'elevator_1': (14.30, -51.42), 'elevator_2': (10.10, -3.37), '文栋': (81.05, 13.98),
                     'meeting': (74.90, 10.18), '刘老师': (69.55, -69.32)}
    src = cv2.imread('./PathPlanningAstar/fit4_5Dealing_draw.png')
    for key, value in location_list.items():
        text = key
        cv2.putText(src, text, world_to_pixel(world_points=(value[0], value[1] - 5), image_size=(2309, 2034)),
                    cv2.FONT_HERSHEY_COMPLEX, 1.0, (0, 0, 255), 2)
        cv2.circle(src, world_to_pixel(world_points=(value[0], value[1]), image_size=(2309, 2034)), 5, (0, 0, 255), -1)
    cv2.imwrite('./result_mark.png', src)


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
        plt.close()
        self.G.clear()


class update():
    def __init__(self):
        self.total_time_o = 0
        self.time = time.asctime(time.localtime(time.time()))
        self.time_propity = {'1号会议室': 30, '休息室': 50, '其他': 30}
        self.messege = None
        self.waiting_update = []
        with open('Graph/Graph.json', 'r', encoding='utf-8') as load_f:
            self.graph_rel = json.load(load_f)
        self.need_update = {}
        today_time = time.localtime(time.time())
        self.now_time = timetostamp(f"{today_time.tm_year}-{today_time.tm_mon}-{today_time.tm_mday} 08:00:00")
        '''设置时间函数的参数'''
        self.sigma = 100  # 影响最大的可能性---可能性可以乘上sigma
        self.u = 100  # 影响最左边的值
        self.a_time = 10  # 影响左边下降的梯度
        self.person = ['港晖', '晨峻', '伟华', '刘老师', '袁老师', '刘毅', '姚峰', '侯煊', '小飞', '郝伟', '海洋', '春秋', '靖宇', '兴航', '文栋', '兰军',
                       '李老师', '馨竹']
        self.if_need_change = 0
        self.tmp_graph = {}
        self.event = {}

    def receive_messege(self, triple, text):
        # for i in messege:
        # 	self.triple=i['label']
        # 	self.text=i['dialogue']
        # 	self.tmp_dynamic_time_graph()
        # messege=[{'dialogue':'刘老师:大家上午8点10分到1号会议室开会','label':[['大家','1号会议室','8点10分']]},
        #          {'dialogue':'兰军:收到','label':[]},
        #          {'dialogue':'港晖:8点10分我要去1001教室上课，能不能换个时间？','label':[['港晖','1001教室','8点10分']]},
        #          {'dialogue':'刘老师:那我们就换到8点40分吧','label':[['我们','','8点40分']]},
        #          {'dialogue':'晨峻:收到','label':[]},
        #          {'dialogue':'港晖:收到','label':[]}]
        # for i in messege:
        # 	self.triple = i['label']
        # 	self.text=i['dialogue']
        # 	self.tmp_dynamic_time_graph()
        self.triple = triple
        self.text = text
        self.tmp_dynamic_time_graph()

    def del_messege(self):
        self.messege = None

    def update_rel(self):
        '''-------------------------------根据json格式更改-接收消息时候的改变--------------------------------'''

        tmp_graph = self.tmp_graph.copy()
        for time_dy, messege in tmp_graph.items():
            if self.now_time >= timetostamp(time_dy):
                time.sleep(0.0001)
                # print(stamptotime(self.now_time),time_dy)
                for per_event in messege:
                    # print(per_event)
                    for p in per_event:
                        ch_person = p[0]
                        ch_location = p[1]
                        # location发生了变化
                        if self.graph_rel[ch_person]['rel_base'][1] != ch_location:
                            self.graph_rel[ch_person]['rel_now'] = [ch_person, ch_location, 1]
                            self.need_update[ch_person] = [ch_person, ch_location, time_dy]
                        else:
                            self.graph_rel[ch_person]['rel_now'] = None
                del self.tmp_graph[time_dy]
            # time.sleep(5)
        tmp = self.event.copy()
        tmp1 = self.event.copy()  # 防止在接受消息的时候被删掉
        for person_name, p in tmp.items():
            for num, person_event in enumerate(p):  # 取出事件
                if self.now_time < timetostamp(person_event[0][2]):
                    continue
                else:
                    for per in person_event:
                        ch_person = per[0]
                        ch_location = per[1]
                        if self.graph_rel[ch_person]['rel_base'][1] != ch_location:
                            self.graph_rel[ch_person]['rel_now'] = [ch_person, ch_location, 1]
                            self.need_update[ch_person] = [ch_person, ch_location, person_event[0][2]]
                    del tmp1[person_name][num]
                    self.event = tmp1
        # print('============rel====================\n',self.graph_rel['港晖'])

    def tmp_dynamic_time_graph(self):  # single text
        self.need_update = {}  # 指的是需要进一步继续时空概率推断的关系
        for i in ['那我们就换', '那我们换',
                  '那咱们就换', '那咱们换',
                  '那咱们改', '那我们就改',
                  '那我们改', '那咱们就改']:
            if i in self.text:
                self.if_need_change = 1
                break
        else:
            self.if_need_change = 0
        self.initiator = self.text.split(':')
        self.initiator = self.initiator[0]  # 事件的发起者
        if self.initiator not in self.event:
            self.event[self.initiator] = []
        self.per_event = []

        if self.if_need_change == 0:  # 发起者发起的新事件，进行事件记录
            if self.event[self.initiator] != []:
                time_signal = self.event[self.initiator][0][0][2]
                # print(self.event[self.initiator][0])
                if time_signal not in self.tmp_graph:
                    self.tmp_graph[time_signal] = []
                self.tmp_graph[time_signal].append(self.event[self.initiator][0])
                del self.event[self.initiator][0]
            total_person_flag = 0

            for value in self.triple:
                if value[1] != '' and value[1] in self.person:  # 当地点是人的时候，对应这个人的办公室
                    value[1] = self.graph_rel[value[1]]['rel_base'][1]

                if value[1] != '' and '的办公室' in value[1]:
                    value[1] = value[1].split('的办公室')[0]
                    value[1] = self.graph_rel[value[1]]['rel_base'][1]

                if value[2] != '':
                    value[2] = get_time(value[2])
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
            if self.triple != []:
                self.event[self.initiator].append(self.per_event)

        # 由于是新的时间，所以把之前的存在的事件就默认已经确定不变，放在self.tmp_graph中，


        elif self.if_need_change == 1:  # 那就xxx
            for value in self.triple:
                self.per_event = []
                if value[1] != '' and value[1] in self.person:  # 当地点是人的时候，对应这个人的办公室
                    value[1] = self.graph_rel[value[1]]['rel_base'][1]

                if value[1] != '' and '的办公室' in value[1]:
                    value[1] = value[1].split('的办公室')[0]
                    value[1] = self.graph_rel[value[1]]['rel_base'][1]

                if value[2] is not None:
                    value[2] = get_time(value[2])

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
            time_signal = self.event[self.initiator][0][0][2]
            if time_signal not in self.tmp_graph:
                self.tmp_graph[time_signal] = []
            self.tmp_graph[time_signal].append(self.event[self.initiator][0])
            del self.event[self.initiator][0]
        time.sleep(0.01)

    # print('===tmp_graph======',self.tmp_graph)
    # print('====event=========',self.event)

    def update_auto(self):  # 自动的改变
        self.a = Graph()
        while 1:
            time.sleep(1)
            self.update_rel()
            '''按照时间函数更新'''
            # img = cv2.imread('Graph/graph_update.png')
            m = self.need_update.copy()
            for k, info in self.need_update.items():
                '''设置时间函数的计算参数'''
                if info[1] in location:
                    self.sigma = 500
                    self.total_time_o = 30 * 60
                elif info[1] in other_location:
                    self.sigma = 1000
                    self.total_time_o = 60 * 60
                # 更新可能性
                time_err = self.now_time - timetostamp(info[2])
                if time_err < self.total_time_o:
                    tmp_possibillity = cal_time(self.a_time, self.total_time_o, self.u, self.sigma,
                                                time_err) * self.sigma
                    self.graph_rel[info[0]]['rel_now'][2] = tmp_possibillity  # 更新可能性
                # print(stamptotime(self.now_time),self.graph_rel[info[0]]['rel_now'])
                # 小于阈值的时候，相当于不再存在
                if time_err > self.total_time_o or (
                        time_err > 100 and self.graph_rel[info[0]]['rel_now'][2] < 0.07):  # 这里加上time——err的
                    self.graph_rel[info[0]]['rel_now'] = None
                    del m[k]
                    info_detail = '{} come back to office!!!'.format(info[0])
                # print(info_detail,tmp_possibillity)
                # cv2.putText(img, info_detail, (600, 90), cv2.FONT_HERSHEY_COMPLEX, 1.0,(255,255,0),2)
            self.need_update = m
            # print(self.graph_rel)
            self.a.draw(self.graph_rel)
            time.sleep(0.1)
            # cv2.putText(img, stamptotime(self.now_time), (200, 90), cv2.FONT_HERSHEY_COMPLEX, 2.0, (100, 200, 200),
            #             2)
            # cv2.imshow('graph', img)
            self.now_time += 60
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        # 	break
        # return


def cal_time(a, total_time, u, sigma, t_th):
    a = a
    x = np.linspace(0, total_time, total_time)
    u = u
    sigma = sigma
    l = skewnorm.pdf(x, a, u, sigma)
    # print(l[t_th])
    return l[t_th]


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


def timetostamp(tss1):
    timeArray = time.strptime(tss1, "%Y-%m-%d %H:%M:%S")
    timeStamp = int(time.mktime(timeArray))
    return timeStamp


def stamptotime(stamp):
    timeArray = time.localtime(stamp)
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    return otherStyleTime


def get_time(detail):
    today_time = time.localtime(time.time())
    today = f"{today_time.tm_year}-{today_time.tm_mon}-{today_time.tm_mday} 00:00:00"
    today = timetostamp(today)
    add_flag = 0
    evening = 0
    if '半' in detail:
        detail = detail.replace('半', '30分')
    if '明天' in detail:
        detail = detail[2:]
        add_flag = 1
    if '下午' in detail:
        evening = 1
        detail = detail[2:]
    if '上午' in detail:
        detail = detail[2:]
    split_time = detail.split('点', 1)
    hours = int(split_time[0])
    if evening == 1 and hours <= 12:
        hours += 12
    if '分' in split_time[1]:
        minutes = int(split_time[1].split('分', 1)[0])
    else:
        minutes = 0

    stamp_time = add_flag * 24 * 60 * 60 + hours * 60 * 60 + minutes * 60
    start_time_stamp = stamp_time + today
    start_time = stamptotime(start_time_stamp)
    # print(start_time)
    return start_time


if __name__ == '__main__':
    import threading

    '''-------------初始化他们的办公室--------------'''
    # Person = ['港晖', '晨峻', '伟华', '刘老师', '袁老师', '刘毅', '姚峰', '侯煊', '小飞',
    #                '郝伟', '海洋', '春秋', '靖宇', '兴航', '文栋', '兰军', '李老师', '馨竹']
    # Location = ['Room510', 'Room511', 'Room512', 'Room513', 'Room514', 'Room515', 'Room516']
    # other_location = ['1号会议室', '2号会议室', '休息室', '茶水间', 'Toilet']
    # init_graph(Person,Location)

    # g=Graph()
    # g.draw(base_graph_rel)

    m = update()
    thread1 = threading.Thread(target=m.update_auto)
    thread2 = threading.Thread(target=m.receive_messege)
    #
    thread2.start()
    thread1.start()
