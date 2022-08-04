# -*-coding:utf-8-*-
import NlpToolKit.Chinese.DialoguePrediction as extract_triple
import Graph.DynamicSpaceTimeGraph as graph
import threading
import numpy as np


class deal():
    def __init__(self):
        self.triple = extract_triple.DialoguePrediction()
        self.update_graph = graph.update(12)
        thread1 = threading.Thread(target=self.update_graph.update_auto)
        thread2=threading.Thread(target=self.update_graph.simulate_time,args=(True,))#True denote using real time.
        thread2.start()
        thread1.start()

    def dynamic_space_time_graph(self, text):
        triple = self.triple(text)
        print(triple)
        if triple!=[]:
            self.update_graph.receive_messege(triple, text)
        else:
            pass
        # self.if_need_change = 0

    def person_get_location(self, person_name):
        if person_name in self.update_graph.graph_rel:
            person_message = self.update_graph.graph_rel[person_name]
            print(person_message)
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
    def get_sample(self):
        return self.update_graph.vitual_envent

def stamptotime(stamp):
    timeArray = time.localtime(stamp)
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    return otherStyleTime

if __name__ == '__main__':
    import time
    '''
    1、第一种情况：验证指令解析模块
    直接@机器人渠去到指定的地点：
    @机器人 到511去
    3、验证语义解析模块的有序性：
        3-1:兰军：@机器人 从港晖那拿份文件给我
        3-2:兰军：@机器人 帮我给港晖送一份文件
    2、验证动态场景图谱的有效性：
        2-1:群里还没有说话的时候：兰军：@机器人 从港晖那拿份文件给我
        2-2:群里说话：港晖没有去参加会议
            messege = [
                '兰军:大家下午16:00到516碰一下',
                '姚峰:收到',
                '卞港晖:我参加不了，我下午4点要在511开个线上会议',
                '兰军:行，其他人呢',
                '小飞:收到',
                '晨峻:收到',
                ]
            到了下午4点以后，兰军：@机器人 从港晖那拿份文件给我
        2-3:两个个小时以后，预测港晖已经回到自己办公室里了
            此时：兰军：@机器人 从港晖那拿份文件给我
    3、验证语义解析模块的有序性：
        3-1:兰军：@机器人 从港晖那拿份文件给我
        3-2:兰军：@机器人 帮我给港晖送一份文件

    '''

    messege = ['兰军:大家下午5点10分到讨论区讨论一下',
                '卞港晖:我参加不了，我下午5点10分要在516开个线上会议',
                '兰军:行，其他人呢',
                '小飞:收到',
                '晨峻:我没问题',
                '姚峰:我也可以',
               # '兰军:大家下午6点到511讨论一下',
               # '卞港晖:好的',
               # '兰军:行，其他人呢',
               # '小飞:收到',
               # '晨峻:我没问题',
               # '姚峰:我也可以',

               ]
    # messege = ['刘老师:大家上午8点30分到1号会议室开会',
    #            '兰军:收到',
    #            '港晖:1号会议室有人用了，换个地方吧？',
    #            '刘老师:那我们就换到2号会议室吧',
    #            '晨峻:收到',
    #            '港晖:收到',
    #            '姚峰:收到',
    #            '港晖:收到',
    #            '小飞:收到',
    #            '兴航:收到',
    #            ]
    # messege = ['刘老师:你们上午有什么安排吗？要不去公园爬山吧？',
    #            '兰军:我上午8点10分要去1001教室。',
    #            '港晖:我上午8点15分要去找姚峰'
    #            ]
    m = deal()
    for i in messege:
        # print(i)
        m.dynamic_space_time_graph(i)
        # print(m.person_get_location('港晖'))
        # time.sleep(1)

    while 1:
        print(m.get_now_time())
        print(m.person_get_location('港晖'),'\n')
        print(m.person_get_location('兰军'), '\n')
        print('need_update:',m.update_graph.need_update,'\n')
        print('tmp_graph:',m.update_graph.tmp_graph,'\n')
        print('event:',m.update_graph.event,'\n')
        print('vitual_event:',m.get_sample())
        # print('table',m.update_graph.virtual_person_location_table)
        # print()
        time.sleep(5)
# while 1:
# 	text=input('text:')
# 	m.dynamic_space_time_graph(text)
