import cv2
import time
import random
from PyQt5.QtCore import QTimer, QSize, QDateTime, QThread
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from QtCustomComponents.MainWindow import Ui_MainWindow
from PathPlanningAstar.astar import world_to_pixel, Map
from PathPlanningAstar.Simulator_llj import search
from CoreNLP.CoreNLP import CorenNLP
from QtCustomComponents.qnchatmessage import QNChatMessage
from transformers import pipeline
from PathPlanningAstar.util_llj.AStar import *

location_list = {
    'elevator_1': (14.30, -51.42),
    'elevator_2': (10.10, -3.37),
    'WenDong': (81.05, 13.98),
    'meeting': (74.90, 10.18),
    'Mr.Liu': (69.55, -69.32)
}
Person = {
    "GangHui": {
        "name": "GangHui",
        "position": (),
        "head": "Ganghui.jpeg"
    },
    "LanJun": {
        "name": "LanJun",
        "position": (),
        "head": "Lanjun.jpeg"
    },
    "WenDong": {
        "name": "WenDong",
        "position": (81.05, 13.98),
        "head": "WenDong.jpeg"
    },
    "Mr.Liu": {
        "name": "Mr.Liu",
        "position": (69.55, -69.32),
        "head": "Mr.Liu.jpeg"
    },
    "WangYi": {

    }
}
actions_lu = {
    "bring": ["bring", "fetch", "take", "deliver", "offer", "get", "obtain", "send", "mail", "offer"],
    "go": ["go", "come"]
}
persons = ["Ganghui", "LanJun", "ChenJun", "WeiHua", "Mr.Liu", "Mr.Yuan", "LiuYi", "YaoFeng", "HouXuan",
           "XiaoFei", "HaoWei", "HaiYang", "ChunQiu", "JingYu", "XingHang", "WenDong", "QingZhu", "Ms.Li"]


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        # 一些槽函数的连接
        self.Send_Button.clicked.connect(self.sendButtonFuction)
        self.UserComboBox.currentIndexChanged.connect(self.__userChanged)
        self.cleartrackbutton.clicked.connect(self.__clearTrackButtonFunction)

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

        # 启动CoreNLP服务，这里我设置的是使用远端的CoreNLP Sever，如果你想更改这一部分设置请去 CoreNLP/CoreNLP.py文件更改
        self.__corenlp = CorenNLP()

        # 初始化transformers question-answering模型
        self.__question_answerer = pipeline('question-answering')

        # 读入地图
        self.Im = cv2.imread('PathPlanningAstar/fit4_5Dealing.png')
        self.__path_map = Map("PathPlanningAstar/middle.png")

        # 初始化路径规划模块
        self.__search = search(map=self.__path_map)

        # 生成机器人随机位置
        self.RobotCurrentPoint_pix, self.RobotCurrentPoint = self.__getRandomAgentLocation()
        cv2.circle(self.Im, (self.RobotCurrentPoint_pix[0], self.RobotCurrentPoint_pix[1]), 10, (0, 0, 255), -1)
        self.__show_pic(self.Im)

        # 初始化当前用户
        self.CurrentUser = Person['WenDong']
        self.__RobotHead = "robot.jpeg"
        self.userhead.setPixmap(QPixmap("ProfilePicture/" + self.CurrentUser['head']))

        # 初始化动作扫描服务
        self.__moveTimer = QTimer(self)
        self.__moveTimer.timeout.connect(self.__moveScanf)
        self.__moveSpeed = 5
        self.__moveTimer.start(self.__moveSpeed)

    def __dealMessage(self, messageW: QNChatMessage, item: QListWidgetItem,
                      text: str, name: str, time: int, usertype: QNChatMessage.User_Type):
        """
        处理消息气泡显示效果的函数
        """
        messageW.setFixedWidth(self.width())
        size = messageW.fontRect(text, name)
        item.setSizeHint(size)
        messageW.setText(text, time, name, size, usertype)
        self.listWidget.setItemWidget(item, messageW)

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
        cv2image = cv2.resize(cv2image, (2300, 2000), interpolation=cv2.INTER_CUBIC)
        showImage = QImage(cv2image.data, cv2image.shape[1], cv2image.shape[0], QImage.Format_RGB888)
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
        messageW.setPixUser("ProfilePicture/" + self.CurrentUser['head'])
        item = QListWidgetItem(self.listWidget)
        self.__dealMessage(messageW, item, message, self.CurrentUser['name'], t, QNChatMessage.User_Type.User_She)
        self.listWidget.setCurrentRow(self.listWidget.count() - 1)

    def Robotalk(self, message: str) -> None:
        """
        机器人说话

        :param message: 消息文本
        :return:
        """
        t = QDateTime.currentDateTime().toTime_t()
        self.__dealMessageTime(t)
        messageW = QNChatMessage(self.listWidget.parentWidget())
        print(self.listWidget.parentWidget().width())
        item = QListWidgetItem(self.listWidget)
        self.__dealMessage(messageW, item, message, "Robot", t, QNChatMessage.User_Type.User_Me)
        self.listWidget.setCurrentRow(self.listWidget.count() - 1)

    def logInfo(self, logText: str):
        """
        打印信息
        """
        self.chat_interface.append("<font background-color='green'>[Info]</font>" + "<font color='blue'>" +
                                   time.strftime("%Y-%m-%d %H:%M:%S") + ":</font>\n" +
                                   logText + "\n")

    def logWarn(self, logText: str):
        """
        打印警告
        """
        self.chat_interface.append("<font background-color='yellow'>[Warn]</font>" + "<font color='blue'>" +
                                   time.strftime("%Y-%m-%d %H:%M:%S") + ":</font>\n" +
                                   logText + "\n")

    def logError(self, logText: str):
        """
        打印错误
        """
        self.chat_interface.append("<font background-color='red'>[Error]</font>" + "<font color='blue'>" +
                                   time.strftime("%Y-%m-%d %H:%M:%S") + ":</font>\n" +
                                   logText + "\n")

    def __userChanged(self):
        currentUser = self.UserComboBox.currentText()
        for key in Person:
            if currentUser == key:
                self.CurrentUser = Person[key]
                break
        self.userhead.setPixmap(QPixmap("ProfilePicture/" + self.CurrentUser['head']))

    def __clearTrackButtonFunction(self):
        """
        清除轨迹
        """
        self.Im = cv2.imread('PathPlanningAstar/fit4_5Dealing.png')
        cv2.circle(self.Im, (self.RobotCurrentPoint_pix[0], self.RobotCurrentPoint_pix[1]), 10, (0, 0, 255), -1)
        self.__show_pic(self.Im)

    def sendButtonFuction(self):
        """
        用户消息发送
        """
        sendText = self.chat_text.toPlainText()
        self.chat_text.setText("")
        if sendText != "":
            self.UserTalk(sendText)
            most_subject, relations, objects, process_sentence = self.__corenlp.annotate_message_en(
                sendText, self.CurrentUser['name'], "Jiqiren")
            robotReply = "ok"
            if most_subject is not None:
                if most_subject == "Robot" and len(relations) != 0:
                    self.logInfo("Who:{}, Doing:{}, What:{}".format(most_subject, relations[0], objects))
                    objectNum = 0
                    _object = []
                    for object_ in objects:
                        if object_ in Person.keys():
                            _object.append(object_)
                    if len(_object) == 2:
                        answer = self.__question_answerer({'question': 'Where should the Robot go first?',
                                                           'context': process_sentence})
                        answer = answer['answer']
                        self.logInfo("answer:" + answer)
                        if answer in _object and _object[0] in Person.keys() and _object[1] in Person.keys():
                            if answer in Person.keys():
                                if Person[answer]['position']:
                                    goalX, goalY = world_to_pixel([Person[answer]['position'][0],
                                                                   Person[answer]['position'][1]])
                                    self.addMoveSequence([0, [goalX, goalY]])
                                    self.logInfo("add move sequence: " + answer)
                                else:
                                    self.logError("{} is not position".format(answer))
                                    robotReply = "Sorry,I dont know what you say."
                                nextGoalName = ""
                                if _object[0] == answer:
                                    nextGoalName = _object[1]
                                else:
                                    nextGoalName = _object[0]
                                if Person[nextGoalName]['position']:
                                    goalX, goalY = world_to_pixel([Person[nextGoalName]['position'][0],
                                                                   Person[nextGoalName]['position'][1]])
                                    self.addMoveSequence([15000, [goalX, goalY]])
                                    self.logInfo("add move sequence: " + nextGoalName)
                                    robotReply = "ok"
                                else:
                                    self.logError("{} is not position".format(nextGoalName))
                                    robotReply = "Sorry,I dont know what you say."
                        else:
                            robotReply = "Sorry,I dont know what you say."
                            self.logWarn("Can't tell where to go first.")
                else:
                    robotReply = "Sorry,I dont know what you say."
            else:
                robotReply = "Sorry,I dont know what you say."
            self.Robotalk(robotReply)

    def addMoveSequence(self, Sequence: [int, [int, int]]):
        """
        添加动作序列，传入动作序列Sequence，Sequence格式为[waitTime,
        [goalX, goalY]], waitTime表示机器人在执行动作序列之前要等待的时间
        ，单位ms. goalX，goalY分别表示该动作序列要到达的点

        :param Sequence: 动作序列
        :return:
        """
        self.__moveSequence.append(Sequence)

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
            self.RobotCurrentPoint_pix = [self.RobotCurrentPoint_pix[0], self.RobotCurrentPoint_pix[1]]  # 更新当前位置
            cv2.circle(self.Im, (self.RobotCurrentPoint_pix[0],  # 画点
                                 self.RobotCurrentPoint_pix[1]), 2, (0, 0, 213), -1)
            self.__show_pic(self.Im)  # 刷新显示
        else:  # 当路径列表读空之后，扫描动作序列
            if self.__moveSequence:  # 当动作序列不为空时
                self.__moveTimer.stop()  # 先暂停扫描函数的触发
                waitTime, [goalX, goalY] = self.__moveSequence.pop(0)  # 读出动作序列第一个元素
                self.__currentMovePath = self.__search.make_path(  # 路径规划，并把路径加入路径序列
                    start=(self.RobotCurrentPoint_pix[0],
                           self.RobotCurrentPoint_pix[1]),
                    goal=(goalX, goalY))
                QThread.msleep(waitTime)  # 等待时间
                self.RobotTargetPoint_pix = [self.__currentMovePath[-1][0], self.__currentMovePath[-1][1]]  # 更新当前目标点
                cv2.circle(self.Im, (self.RobotTargetPoint_pix[0], self.RobotTargetPoint_pix[1]),  # 在地图上标出目标点
                           10, (255, 0, 0), -1)
                self.__show_pic(self.Im)  # 刷新显示
                self.__moveTimer.start(self.__moveSpeed)  # 重启扫描

    def __getRandomAgentLocation(self) -> [[int, int], [int, int]]:
        """
        随机生成机器人位置

        :return: pixle_point-像素坐标，point-世界坐标
        """
        map = self.__path_map.grid_map
        while True:
            point = (random.choice(range(-80, 80)), random.choice(range(-80, 80)))
            pixle_point = world_to_pixel(world_points=point)
            if 0 <= pixle_point[0] < 2309 and 0 <= pixle_point[1] < 2034:
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


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
