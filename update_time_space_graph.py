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
        self.update_graph.receive_messege(triple, text)


if __name__ == '__main__':
    # messege = ['刘老师:大家上午8点10分到1号会议室开会',
    #            '兰军:收到',
    #            '港晖:我8点10分要去1001教室上课，能不能换个时间？',
    #            '刘老师:那我们就换到8点40分吧',
    #            '晨峻:收到',
    #            '港晖:收到']
    m = deal()
    # for i in messege:
    # 	m.dynamic_space_time_graph(i)
    while 1:
        text = input('text:')
        m.dynamic_space_time_graph(text)
