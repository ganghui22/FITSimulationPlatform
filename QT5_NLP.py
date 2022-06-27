import json
import multiprocessing
import threading

import cv2
import time
import random
from multiprocessing import Process, Queue
from PyQt5.QtCore import QTimer, QSize, QDateTime, Qt, QPoint, QThread, pyqtSignal
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from QtCustomComponents.MainWindow import Ui_MainWindow
from PathPlanningAstar.astar import world_to_pixel, Map
from PathPlanningAstar.Simulator_llj import search
from NlpToolKit.Chinese.InstructionPrediction import InstructionPrediction as InstructionPrediction
from QtCustomComponents.qnchatmessage import QNChatMessage
from PathPlanningAstar.util_llj.AStar import *
from update_time_space_graph import deal
import itertools

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self,
                 InstructionPrediction_InQueue: multiprocessing.Queue,
                 InstructionPrediction_OutQueue: multiprocessing.Queue,
                 TimeSpaceGraph_InQueue: multiprocessing.Queue,
                 TimeSpaceGraph_OutQueue: multiprocessing.Queue,
                 PathPlanningProcess_InQueue: multiprocessing.Queue,
                 PathPlanningProcess_OutQueue: multiprocessing.Queue,
                 dialogue_list: list = None,
                 parent=None):
        super(MainWindow, self).__init__(parent)

        self.setupUi(self)

        self.actionTag_location.triggered.connect(self._Tag_location)
        # 读入地图
        self.Im = cv2.imread('PathPlanningAstar/map.png')
        self.__path_map = Map("PathPlanningAstar/middle.png")
        self.statuLabel = QLabel()
        self.statusbar.addWidget(self.statuLabel)
        Im_W, Im_H, map_W, map_H = self.Im.shape[1], self.Im.shape[0], self.map.width(), self.map.height()
        self.map.setGeometry(self.map.x(), self.map.y(), map_W, int(map_W * (Im_H / Im_W)))
        self.map.setMouseTracking(True)
        self.map.mouseMoveEvent = self.map_mouseMoveEvent

        # 加载地点列表
        with open('data/Location_list.json', 'r', encoding='utf-8') as f:
            self._location_list = json.load(f)

        # 生成不同颜色的未知头像
        unk_head = cv2.imread("ProfilePicture/Unk.png", cv2.IMREAD_UNCHANGED)
        r, g, b, a = cv2.split(unk_head)
        unk_head_rgb_permutation = list(itertools.permutations([r, g, b], 3))
        unk_head_permutation = []
        for u in unk_head_rgb_permutation:
            first, second, third = u
            uu = cv2.merge([first, second, third, a])
            unk_head_permutation.append(uu)

        # 加载人物列表及生成图像
        with open('data/Person.json', 'r', encoding='utf-8') as f:
            self._Person = json.load(f)

        for person in self._Person:
            if 'head' in self._Person[person]:
                h = cv2.imread("ProfilePicture/" + self._Person[person]["head"], cv2.IMREAD_UNCHANGED)
                h_q = cv2.imread("ProfilePicture/" + self._Person[person]["head"])

                # h 用于地图人物位置标记
                h = cv2.resize(h, (50, 50), interpolation=cv2.INTER_CUBIC)

                # h_q用于qt界面头像显示
                h_q = cv2.resize(h_q, (200, 200), interpolation=cv2.INTER_CUBIC)
                h_q = QImage(h_q.data, h_q.shape[1], h_q.shape[0], h_q.shape[1] * 3,
                           QImage.Format.Format_BGR888)

                self._Person[person]["head_QImage"] = h_q
                self._Person[person]["head"] = h
            else:
                # h 用于地图人物位置标记
                h = unk_head_permutation.pop()
                b, g, r, _ = cv2.split(h)
                h_q = cv2.merge([b, g, r])
                h = cv2.resize(h, (200, 200), interpolation=cv2.INTER_CUBIC)

                self._Person[person]["head"] = h
                h_q = cv2.resize(h_q, (200, 200), interpolation=cv2.INTER_CUBIC)
                h_q = QImage(h_q.data, h_q.shape[1], h_q.shape[0], h_q.shape[1] * 3,
                             QImage.Format.Format_BGR888)
                self._Person[person]["head_QImage"] = h_q

        # 一些槽函数的连接
        self.Send_Button.clicked.connect(self.sendButtonFunction)
        self.UserComboBox.currentIndexChanged.connect(self.__userChanged)
        self.cleartrackbutton.clicked.connect(self.__clearTrackFunction)

        # 一些Qt组件的属性设置
        self.map.setScaledContents(True)
        self.userhead.setScaledContents(True)
        self.RobotTargetPoint_pix = None

        # 初始化一些参数
        self.__moveSequence = []
        self.__currentMovePath = []
        self.__path = []
        self.__currentWaitCont = 0
        self.count = 0
        self.__pointNumber = 0

        # 导入自然语言处理工具
        # 创建对话分析工具Queue队列
        self._InstructionPrediction_InQueue = InstructionPrediction_InQueue
        self._InstructionPrediction_OutQueue = InstructionPrediction_OutQueue

        # self._instruction_deal = InstructionPrediction()  # 指令处理工具

        # 初始化动态时空图谱
        # 创建动态时空图谱进程的Queue队列
        self._TimeSpaceGraph_InQueue = TimeSpaceGraph_InQueue
        self._TimeSpaceGraph_OutQueue = TimeSpaceGraph_OutQueue

        # 初始化路径规划模块
        # 创建路径规划进程的Queue队列
        self.__search = search(map=self.__path_map)
        self.PathPlanningProcess_InQueue = PathPlanningProcess_InQueue
        self.PathPlanningProcess_OutQueue = PathPlanningProcess_OutQueue

        # 生成机器人随机位置
        self.RobotCurrentPoint_pix, self.RobotCurrentPoint = self.__getRandomAgentLocation()
        cv2.circle(self.Im, (self.RobotCurrentPoint_pix[0], self.RobotCurrentPoint_pix[1]), 10, (0, 0, 255), -1)
        self.__show_pic(self.Im)

        # 初始化当前用户
        self.CurrentUser = self._Person['晨峻']
        self.__RobotHead = "robot.png"
        self.userhead.setPixmap(QPixmap.fromImage(self.CurrentUser['head_QImage']))

        # 初始化动作扫描服务
        self.__moveTimer = QTimer(self)
        self.__moveTimer.timeout.connect(self.__moveScanf)
        self.__moveSpeed = 5
        self.__waitForPathPlanning = False
        self.__moveTimer.start(self.__moveSpeed)

        # map事件的用到的一些参数的初始化
        self.map.start_pos = QPoint()
        self.map.end_pos = QPoint()

        self.map.mouseDown = False
        # self.map_view = QGraphicsView(self.map)

        # 列表扫描服务
        if dialogue_list is not None:
            self.dialogue_list = dialogue_list
            self.dialogue_list_deal_timer = QTimer(self)
            self.dialogue_list_deal_timer.timeout.connect(self._dialogue_list_deal)
            self.dialogue_list_deal_timer.start(2000)

    def _Tag_location(self):
        self.window().setCursor(Qt.CrossCursor)
        # self.window().mousePressEvent = self.window()._Tag_action_location_mousePressEvent
        # self.window().map.mouseMoveEvent = self.window()._Tag_action_location_mousePressEvent
        self.map_view.mouseMoveEvent = self._Tag_action_location_mouseMoveEvent
    def _dialogue_list_deal(self):
        if self.dialogue_list:
            dialogue = self.dialogue_list.pop(0)
            self.dealMessage(dialogue)
        else:
            self.dialogue_list_deal_timer.stop()

    def _Tag_action_location_mousePressEvent(self, event: QMouseEvent):
        """
        位置标注动作触发时的鼠标按压事件
        """
        if event.button() == Qt.LeftButton:
            self.window().map.start_pos = event.pos()
            self.map.mouseDown = True
        # x = event.pos().x()
        # self.window()

    def _Tag_action_location_mouseMoveEvent(self, event: QMouseEvent):
        """
        位置标注动作触发时的鼠标移动事件
        """
        if event.button() == Qt.LeftButton:
            if self.window().map.mouseDown:
                self.window().map.end_pos = event.pos()
                self.paint()

    def _Tag_action_location_mouseReleaseEvent(self, event: QMouseEvent):
        """
        位置标注动作触发时的鼠标释放事件
        """
        if self.window().map.mouseDown:
            self.window().map.end_pos = event.pos()
            self.self.window().map.mouseDown = False

    def paint(self):
        """
        位置标注动作框选时的画框函数
        """


    def __dealMessageShow(self, messageW: QNChatMessage, item: QListWidgetItem,
                          text: str, name: str, time: int, usertype: QNChatMessage.User_Type):
        """
        处理消息气泡显示效果的函数
        """
        messageW.setFixedWidth(self.width())
        size = messageW.fontRect(text, name)
        item.setSizeHint(size)
        messageW.setText(text, time, name, size, usertype)
        self.listWidget.setItemWidget(item, messageW)

    def map_mouseMoveEvent(self, event: QMouseEvent):
        x, y = event.pos().x(), event.pos().y()
        self.window().statuLabel.setText("<font color='red'>X</font>:<font color='blue'>{}</font>, "
                                         "<font color='red'>Y</font>:<font color='blue'>{}</font>".format(x, y))

    def __dealMessageTime(self, curMsgTime: int):
        """
        处理对话时时间显示函数
        """
        isShowTime = False
        if self.listWidget.count() > 0:
            lastItem = self.listWidget.item(self.listWidget.count() - 1)
            messageW = self.listWidget.itemWidget(lastItem)
            lastTime = messageW.m_time
            curTime = curMsgTime
            isShowTime = ((curTime - lastTime) > 60)  # 两个消息相差一分钟
        else:
            isShowTime = True
        if isShowTime:
            messageTime = QNChatMessage(self.listWidget.parentWidget())
            itemTime = QListWidgetItem(self.listWidget)
            size = QSize(self.width(), 40)
            messageTime.resize(size)
            itemTime.setSizeHint(size)
            messageTime.setText(str(curMsgTime), curMsgTime, "", size, QNChatMessage.User_Type.User_Time)
            self.listWidget.setItemWidget(itemTime, messageTime)

    def __show_pic(self, cv2image) -> None:
        """
        私有化函数，进行地图图片的刷新
        """
        cv2image = cv2.resize(cv2image, (int(cv2image.shape[1] / 4) * 4, int(cv2image.shape[0] / 4) * 4),
                              interpolation=cv2.INTER_CUBIC)
        showImage = QImage(cv2image.data, cv2image.shape[1], cv2image.shape[0], cv2image.shape[1] * 3,
                           QImage.Format.Format_RGB888)
        self.map.setPixmap(QPixmap.fromImage(showImage))

    def UserTalk(self, message: str) -> None:
        """
        用户说话

        :param message: 消息文本
        :return:
        """
        t = QDateTime.currentDateTime().toTime_t()
        self.__dealMessageTime(t)
        messageW = QNChatMessage(self.listWidget.parentWidget())
        userHead = self.CurrentUser['head_QImage']
        messageW.setPixUser(userHead)
        item = QListWidgetItem(self.listWidget)
        self.__dealMessageShow(messageW, item, message, self.CurrentUser['name'], t, QNChatMessage.User_Type.User_She)
        self.listWidget.setCurrentRow(self.listWidget.count() - 1)

    def RobotTalk(self, message: str) -> None:
        """
        机器人说话

        :param message: 消息文本
        :return:
        """
        t = QDateTime.currentDateTime().toTime_t()
        self.__dealMessageTime(t)
        messageW = QNChatMessage(self.listWidget.parentWidget())
        item = QListWidgetItem(self.listWidget)
        self.__dealMessageShow(messageW, item, message, "Robot", t, QNChatMessage.User_Type.User_Me)
        self.listWidget.setCurrentRow(self.listWidget.count() - 1)

    def logInfo(self, logText: str):
        """
        打印信息
        """
        self.chat_interface.append("<style type='text/css'>.background span{"
                                   "display:inline-block;background:#28FF28;border:2px "
                                   "solid;color:#000;text-align:left;}</style>" +
                                   "<font class='background'><span>[Info]</span></font>" + "<font color='blue'>" +
                                   str(time.strftime("%Y-%m-%d %H:%M:%S")) + ":</font>\n" +
                                   logText + "\n")

    def logWarn(self, logText: str):
        """
        打印警告
        """
        self.chat_interface.append("<style type='text/css'>.background span{"
                                   "display:inline-block;background:#FFD306;border:2px "
                                   "solid;color:#000;text-align:left;}</style>" +
                                   "<font background-color='yellow'>[Warn]</font>" + "<font color='blue'>" +
                                   str(time.strftime("%Y-%m-%d %H:%M:%S")) + ":</font>\n" +
                                   logText + "\n")

    def logError(self, logText: str):
        """
        打印错误
        """
        self.chat_interface.append("<style type='text/css'>.background span{"
                                   "display:inline-block;background:#EA0000;border:2px "
                                   "solid;color:#000;text-align:left;}</style>" +
                                   "<font background-color='red'>[Error]</font>" + "<font color='blue'>" +
                                   str(time.strftime("%Y-%m-%d %H:%M:%S")) + ":</font>\n" +
                                   logText + "\n")

    def __userChanged(self, signal, user: str = None):
        if user is None:
            currentUser = self.UserComboBox.currentText()
            for key in self._Person:
                if currentUser == key:
                    self.CurrentUser = self._Person[key]
                    break
            self.userhead.setPixmap(QPixmap.fromImage(self.CurrentUser['head_QImage']))
        else:
            self.CurrentUser = user
            self.UserComboBox.setCurrentText(user['name'])
            for key in self._Person:
                if user['name'] == key:
                    self.CurrentUser = self._Person[key]
                    break
            self.userhead.setPixmap(QPixmap.fromImage(self.CurrentUser['head_QImage']))

    def __clearTrackFunction(self):
        """
        清除轨迹
        """
        self.Im = cv2.imread('PathPlanningAstar/map.png')
        cv2.circle(self.Im, (self.RobotCurrentPoint_pix[0], self.RobotCurrentPoint_pix[1]), 10, (0, 0, 255), -1)
        self.__show_pic(self.Im)

    def sendButtonFunction(self):
        """
        用户消息发送按钮点击事件
        """

        sendText = self.chat_text.toPlainText()
        self.chat_text.setText("")
        if sendText != '':
            self.UserTalk(sendText)
            if self.CurrentUser['name'] != "Robot":
                t = self.CurrentUser['name'] + ":" + sendText
                self.dealMessage(t)

    def dealMessage(self, sentence: str):
        """
        消息处理函数，主要对消息进行一些简单的处理
        """
        if sentence == "":
            return
        else:
            speak_person = sentence.split(":")[0]
            speak_person = self._Person[speak_person]
            self.__userChanged(None, speak_person)
            t = sentence.split(":")[1]
            self.UserTalk(t)
            if '@ Robot' not in sentence:
                # 提取时间、地点、人物三元组并更新动态时空图谱
                self._TimeSpaceGraph_InQueue.put([True, sentence])
            else:
                # 指令处理
                sentence = sentence[sentence.index('@ Robot') + 7:]
                self.dealInstruction(sentence)

    # def _personCheck(self, input_item):

    def dealInstruction(self, sentence):
        """
        指令处理，将指令解析成动作，并压入动作的序列
        """
        self._InstructionPrediction_InQueue.put(sentence)
        while self._InstructionPrediction_OutQueue.empty():
            pass
        frame = self._InstructionPrediction_OutQueue.get()

        path = []
        if 'bring' not in frame:
            return
        for frameElement in frame['bring']:
            fe = frame['bring'][frameElement]
            if len(fe) > 1:
                frame['bring'][frameElement] = ''.join(fe)
            else:
                frame['bring'][frameElement] = frame['bring'][frameElement][0]
        bringFrame = frame['bring']
        # 判断beneficiary是否存在
        # 不存在时
        if 'beneficiary' not in bringFrame:
            # 判断source 和 goal是同时存在
            if ('source' in bringFrame) and ('goal' in bringFrame):
                path.append(bringFrame['source'])
                path.append(bringFrame['goal'])
            elif ('goal' in bringFrame) and ('source' not in bringFrame):
                path.append(bringFrame['goal'])
        # 存在时
        else:
            if 'goal' in bringFrame and 'source' not in bringFrame:
                path.append(bringFrame['goal'])
            elif 'goal' in bringFrame and 'source' in bringFrame:
                path.append(bringFrame['goal'])
                path.append(bringFrame['source'])

        path_l = self.listPersonOrLocation_diff(path)
        path = [[2000, p, path[i]] for i, p in enumerate(path_l)]
        for p in path:
            self.addMoveSequence(p)

        # 路径地点都能找到时,将地点按顺序导入动作序列
        self.logInfo(str(path))

    def listPersonOrLocation_diff(self, lii):
        li = lii[:]
        for idx, item in enumerate(li):
            # 带有固定位置的词出现时,代表固定地点
            if "位置" in item or "工位" in item or "办公室":
                for p in self._Person:
                    if p in item:
                        li[idx] = self._location_list[self._Person[p]['position']]
                        break
            else:
                # 当路径是人物时，需要查询人物当前的位置
                for p in self._Person:
                    if p in item:
                        self._TimeSpaceGraph_InQueue.put(p)
                        while self._TimeSpaceGraph_OutQueue.empty():
                            pass
                        l = self._TimeSpaceGraph_OutQueue.get()
                        li[idx] = self._location_list[l]
                        self.logInfo("path append: " + l)
                        break
                # 当是地点时
                for loc in self._location_list:
                    if loc in item:
                        li[idx] = self._location_list[loc]
                        self.logInfo("path append: " + loc)
                        break
        return li

    def addMoveSequence(self, sequence: [int, [int, int], str]):
        """
        添加动作序列，传入动作序列Sequence，Sequence格式为[waitTime,
        [goalX, goalY]], waitTime表示机器人在执行动作序列之前要等待的时间
        ，单位ms. goalX，goalY分别表示该动作序列要到达的点

        :param: Sequence: 动作序列
        :return: None
        """
        self.__moveSequence.append(sequence)

    def StartActionSequence(self):
        """
        启动动作序列的依次执行

        """
        self.__moveTimer.start(self.__moveSpeed)

    def StopActionSequence(self):
        """
        停止动作序列的执行和

        """
        self.__moveTimer.stop()

    def __moveScanf(self):
        """
        动作序列的扫描函数

        """
        if self.__currentMovePath:  # 当路径序列不为空时执行当前路径
            self.RobotCurrentPoint_pix = self.__currentMovePath.pop(0)  # 读出路径序列第一个元素
            print(self.RobotCurrentPoint_pix)
            self.RobotCurrentPoint_pix = [self.RobotCurrentPoint_pix[0], self.RobotCurrentPoint_pix[1]]  # 更新当前位置
            cv2.circle(self.Im, (self.RobotCurrentPoint_pix[0],  # 画点
                                 self.RobotCurrentPoint_pix[1]), 2, (0, 0, 213), -1)
            self.__show_pic(self.Im)  # 刷新显示
        elif self.__waitForPathPlanning:
            if not self.PathPlanningProcess_OutQueue.empty():
                self.__currentMovePath = self.PathPlanningProcess_OutQueue.get()
                self.__clearTrackFunction()
                # QThread.msleep(waitTime)  # 等待时间
                self.RobotTargetPoint_pix = [self.__currentMovePath[-1][0], self.__currentMovePath[-1][1]]  # 更新当前目标点
                cv2.circle(self.Im, (self.RobotTargetPoint_pix[0], self.RobotTargetPoint_pix[1]),  # 在地图上标出目标点
                           10, (255, 0, 0), -1)
                self.__show_pic(self.Im)  # 刷新显示
                self.__waitForPathPlanning = False
        else:  # 当路径列表读空之后，扫描动作序列
            if self.__moveSequence:  # 当动作序列不为空时
                # self.__moveTimer.stop()  # 先暂停扫描函数的触发
                # print("MoveSequence pop")
                waitTime, [goalX, goalY], name = self.__moveSequence.pop(0)  # 读出动作序列第一个元素
                goalX, goalY = world_to_pixel((goalX, goalY))
                self.PathPlanningProcess_InQueue.put([self.RobotCurrentPoint_pix[0],
                                                      self.RobotCurrentPoint_pix[1],
                                                      goalX,
                                                      goalY])
                self.logInfo("Current goal: " + name)
                self.__waitForPathPlanning = True
                # self.__moveTimer.start(self.__moveSpeed)  # 重启扫描

    def __getRandomAgentLocation(self) -> [[int, int], [int, int]]:
        """
        随机生成机器人位置

        :return: pixle_point-像素坐标，point-世界坐标
        """
        map = self.__path_map.grid_map
        while True:
            point = (random.choice(range(-80, 80)), random.choice(range(-80, 80)))
            pixle_point = world_to_pixel(world_points=point)
            if 0 <= pixle_point[0] < 1883 and 0 <= pixle_point[1] < 533:
                false_flag = False
                for i in range(-2, 2, 2):
                    for j in range(-2, 2, 2):
                        if map[pixle_point[0] + i][pixle_point[1] + j]:
                            false_flag = True
                            break
                    if false_flag:
                        break
                if map[pixle_point[0]][pixle_point[1]]:
                    break
        return pixle_point, point


def PathPlanningProcess(qi: multiprocessing.Queue, qo: multiprocessing.Queue):
    path_map = Map("PathPlanningAstar/middle.png")
    s = search(map=path_map)
    while True:
        if not qi.empty():
            start_x, start_y, goal_x, goal_y = qi.get()
            print((start_x, start_y), (goal_x, goal_y))
            path = s.make_path((start_x, start_y), (goal_x, goal_y))
            qo.put(path)


def TimeSpaceGraph_process(qi: multiprocessing.Queue, qo: multiprocessing.Queue):
    tp_graph = deal()
    while True:
        if not qi.empty():
            query = qi.get()
            if query[0]:
                tp_graph.dynamic_space_time_graph(query[1])
            else:
                reply = tp_graph.person_get_location(query[1])
                qo.put(reply)


def InstructionPrediction_process(qi: multiprocessing.Queue, qo: multiprocessing.Queue):
    deal_instruction = InstructionPrediction()
    while True:
        if not qi.empty():
            query = qi.get()
            reply = deal_instruction(query)
            qo.put(reply)


def main():
    dialogue_list = None
    dialogue_list = ['刘老师:大家上午8点15分到1号会议室开会',
                     '兰军:收到',
                     '港晖:老师，我8点15分要去1001教室上课，能不能换个时间？',
                     '刘老师:那我们就换到9点吧',
                     '晨峻:收到',
                     '兴航:收到',
                     '姚峰:收到',
                     '港晖:收到',
                     '小飞:收到',
                     '晨峻:@ Robot从港晖那拿份文件给兰军'
                     ]

    # 指令解析服务的进程通信队列
    InstructionPrediction_InQueue, InstructionPrediction_OutQueue = multiprocessing.Queue(), multiprocessing.Queue()

    # 时空图谱服务的进程通信队列
    TimeSpaceGraph_InQueue, TimeSpaceGraph_OutQueue = multiprocessing.Queue(), multiprocessing.Queue()

    # 地图路径规划的进程通信队列
    PathPlanningProcess_InQueue, PathPlanningProcess_OutQueue = multiprocessing.Queue(), multiprocessing.Queue()

    # 指令解析服务的进程启动
    _InstructionPrediction_process = Process(target=InstructionPrediction_process, args=(
        InstructionPrediction_InQueue,
        InstructionPrediction_OutQueue))
    _InstructionPrediction_process.start()

    # 时空图谱服务的进程启动
    _TimeSpaceGraph_process = Process(target=TimeSpaceGraph_process, args=(
        TimeSpaceGraph_InQueue,
        TimeSpaceGraph_OutQueue))
    _TimeSpaceGraph_process.start()

    # 地图路径规划进程启动
    _PathPlanning_process = Process(target=PathPlanningProcess, args=(
        PathPlanningProcess_InQueue,
        PathPlanningProcess_OutQueue))
    _PathPlanning_process.start()

    app = QApplication(sys.argv)
    window = MainWindow(InstructionPrediction_InQueue,
                        InstructionPrediction_OutQueue,
                        TimeSpaceGraph_InQueue,
                        TimeSpaceGraph_OutQueue,
                        PathPlanningProcess_InQueue,
                        PathPlanningProcess_OutQueue,
                        dialogue_list=dialogue_list)
    window.show()

    sys.exit([app.exec_(), _TimeSpaceGraph_process.terminate(), _InstructionPrediction_process.terminate(),
              _PathPlanning_process.terminate()])


if __name__ == '__main__':
    main()
