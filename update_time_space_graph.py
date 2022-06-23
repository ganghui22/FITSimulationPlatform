# -*-coding:utf-8-*-
import NlpToolKit.Chinese.DialoguePrediction as extract_triple
import Graph.DynamicSpaceTimeGraph as graph
import threading


class deal():
    def __init__(self):
        self.triple = extract_triple.DialoguePrediction()
        self.update_graph = graph.update()
        thread1 = threading.Thread(target=self.update_graph.update_auto)
        # thread2 = threading.Thread(target=self.update_graph.receive_messege)
        #
        # thread2.start()
        thread1.start()

    def dynamic_space_time_graph(self, text):
        triple = self.triple(text)
        print(triple)
        self.update_graph.receive_messege(triple, text)
        self.if_need_change = 0

    def person_get_location(self, person_name):
        if person_name in self.update_graph.graph_rel:
            person_message = self.update_graph.graph_rel[person_name]
            if person_message['rel_now'] != None:
                return person_message['rel_now'][1]
            else:
                return person_message['rel_base'][1]
        else:
            return None


if __name__ == '__main__':
    import time

    messege = ['刘老师:大家上午8点15分到1号会议室开会',
               '兰军:收到',
               '港晖:老师，我8点15分要去1001教室上课，能不能换个时间？',
               '刘老师:那我们就换到9点吧',
               '晨峻:收到',
               '港晖:收到',
               '伟华:收到',
               '姚峰:收到',
               '港晖:收到',
               '刘毅:收到',
               '侯煊:收到',
               '小飞:收到',
               '郝伟:收到',
               '海洋:收到',
               '春秋:收到',
               '靖宇:收到',
               '兴航:收到',
               '文栋:收到',
               '李老师:收到',
               '馨竹:收到'
               ]
    m = deal()
    for i in messege:
        print(i)
        m.dynamic_space_time_graph(i)
        print(m.person_get_location('港晖'))
        time.sleep(1)
    while 1:
        print(m.person_get_location('港晖'))
# while 1:
# 	text=input('text:')
# 	m.dynamic_space_time_graph(text)
