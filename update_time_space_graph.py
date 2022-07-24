# -*-coding:utf-8-*-
import NlpToolKit.Chinese.DialoguePrediction as extract_triple
import Graph.DynamicSpaceTimeGraph as graph
import threading


class deal():
    def __init__(self):
        self.triple = extract_triple.DialoguePrediction()
        self.update_graph = graph.update()
        thread1 = threading.Thread(target=self.update_graph.update_auto)

        thread2=threading.Thread(target=self.update_graph.simulate_time,args=(False,))#True denote using real time.
        thread2.start()
        thread1.start()

    def dynamic_space_time_graph(self, text):
        triple = self.triple(text)
        print(triple)
        self.update_graph.receive_messege(triple, text)
        self.if_need_change = 0

    def person_get_location(self, person_name):
        if person_name in self.update_graph.graph_rel:
            person_message = self.update_graph.graph_rel[person_name]
            print(person_message)
            if person_message['rel_now'] != None:
                return person_message['rel_now'][1]
            else:
                return person_message['rel_base'][1]
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
    import time

    # messege = ['刘华平:我们该赶进度了,大家12点到1号会议室碰一下',
    #            '兰军:收到',
    #            '卞港晖:老师，我参加不了，我8点15分要在Room511开个线上会议',
    #            '刘老师:那我们就换到12点15分吧',
    #            '晨峻:收到',
    #            '港晖:收到',
    #            '姚峰:收到',
    #            '港晖:收到',
    #            '小飞:收到',
    #            '兴航:收到',
    #            ]
    messege=['兰军:老师您在哪呢？','刘老师:我现在在Room516','兰军：好的老师，一会儿我去找你。']
    # messege = ['刘老师:大家上午8点30分到1号会议室开会',
    #            '兰军:收到',
    #            '港晖:1号会议室有人，换个地方吧？',
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
        pass
# while 1:
# 	text=input('text:')
# 	m.dynamic_space_time_graph(text)
