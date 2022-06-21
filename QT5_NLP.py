import cv2
import time
import random
from PyQt5.QtCore import QTimer, QSize, QDateTime, QThread
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from QtCustomComponents.MainWindow import Ui_MainWindow
from PathPlanningAstar.astar import world_to_pixel, Map
from PathPlanningAstar.Simulator_llj import search
from NlpToolKit.CoreNLP import CorenNLP
from NlpToolKit.Chinese.DialoguePrediction import DialoguePrediction as DialoguePrediction
from NlpToolKit.Chinese.InstructionPrediction import InstructionPrediction as InstructionPrediction
from QtCustomComponents.qnchatmessage import QNChatMessage
from transformers import pipeline
import re
from PathPlanningAstar.util_llj.AStar import *
from update_time_space_graph import deal

location_list = {
    '休息室': [-19.7, 3.7],
    '2号会议室': [-16.4, 4.1],
    '讨论区': [-6.2, 2.3],
    '1号会议室': [5.8, -2.3],
    'Room510': [22.8, 4.1],
    'Room511': [22.7, -4.2],
    'Room512': [17.5, 4.2],
    'Room513': [19.6, -4.2],
    'Room514': [15, -4.3],
    'Room515': [11.2, 2.4],
    'Room516': [5.8, -2.3],
}
Person = {
    "港晖": {
        "name": "GangHui",
        "position": [74.90, 10.18],
        "head": "GangHui.jpeg"
    },
    "兰军": {
        "name": "LanJun",
        "position": [10.10, -3.37],
        "head": "LanJun.jpeg"
    },
    "文栋": {
        "name": "WenDong",
        "position": [81.05, 13.98],
        "head": "WenDong.jpeg"
    },
    "刘老师": {
        "name": "Mr.Liu",
        "position": [69.55, -69.32],
        "head": "Mr.Liu.jpeg"
    },
    "晨峻": {
        "name": "ChenJun",
        "position": []
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
        self._dialog_deal = DialoguePrediction() # 对话分析工具
        self._instruction_deal = InstructionPrediction() # 指令处理工具

        # 初始化动态时空图谱
        self._tp_graph = deal()

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
        self.__dealMessage(messageW, item, message, "Robot", t, QNChatMessage.User_Type.User_Me)
        self.listWidget.setCurrentRow(self.listWidget.count() - 1)

    def logInfo(self, logText: str):
        """
        打印信息
        """
        self.chat_interface.append("<style type='text/css'>.background span{"
                                   "display:inline-block;background:#28FF28;border:2px "
                                   "solid;color:#000;text-align:left;}</style>" +
                                   "<font class='background'><span>[Info]</span></font>" + "<font color='blue'>" +
                                   time.strftime("%Y-%m-%d %H:%M:%S") + ":</font>\n" +
                                   logText + "\n")

    def logWarn(self, logText: str):
        """
        打印警告
        """
        self.chat_interface.append("<style type='text/css'>.background span{"
                                   "display:inline-block;background:#FFD306;border:2px "
                                   "solid;color:#000;text-align:left;}</style>" +
                                   "<font background-color='yellow'>[Warn]</font>" + "<font color='blue'>" +
                                   time.strftime("%Y-%m-%d %H:%M:%S") + ":</font>\n" +
                                   logText + "\n")

    def logError(self, logText: str):
        """
        打印错误
        """
        self.chat_interface.append("<style type='text/css'>.background span{"
                                   "display:inline-block;background:#EA0000;border:2px "
                                   "solid;color:#000;text-align:left;}</style>" +
                                   "<font background-color='red'>[Error]</font>" + "<font color='blue'>" +
                                   time.strftime("%Y-%m-%d %H:%M:%S") + ":</font>\n" +
                                   logText + "\n")

    def __userChanged(self):
        currentUser = self.UserComboBox.currentText()
        for key in Person:
            if currentUser == key:
                self.CurrentUser = Person[key]
                break
        self.userhead.setPixmap(QPixmap("ProfilePicture/" + self.CurrentUser['head']))

    def __clearTrackFunction(self):
        """
        清除轨迹
        """
        self.Im = cv2.imread('PathPlanningAstar/fit4_5Dealing.png')
        cv2.circle(self.Im, (self.RobotCurrentPoint_pix[0], self.RobotCurrentPoint_pix[1]), 10, (0, 0, 255), -1)
        self.__show_pic(self.Im)

    def sendButtonFuction(self):
        """
        用户消息发送按钮点击事件
        """
        sendText = self.chat_text.toPlainText()
        if sendText != '':
            self.chat_text.setText("")
            self.UserTalk(sendText)
            if self.CurrentUser != "Robot":
                self.dealMessage(sendText, self.CurrentUser)

    def dealMessage(self, sentence: str, current_user: str):

        if sentence == "":
            return
        else:
            if '@ Robot' not in sentence:
                 # 提取时间、地点、人物三元组并更新动态时空图谱
                self._tp_graph.dynamic_space_time_graph(sentence)
            else:
                # 指令处理
                self.dealInstruction(sentence)

    def dealInstruction(self, sentence):
        frame = self._instruction_deal(sentence)
        path = []
        if 'bring' not in frame:
            return
        for frameElement in frame['bring']:
            fe = frame['bring'][frameElement]
            if len(fe) > 1:
                frame['bring'][frameElement] = ''.join(fe)
        bringFrame = frame['bring']

        # 判断beneficiary是否存在
        # 不存在时
        if 'beneficiary' not in bringFrame:
            # 判断source 和 goal是同时存在
            if 'source' in frame and 'goal' in frame:
                path.append(bringFrame['source'])
                path.append(bringFrame['goal'])
            elif 'goal' in frame:
                path.append(bringFrame['goal'])
        else:
            if 'goal' in frame and 'source' not in frame:
                path.append(bringFrame['goal'])
            elif 'goal' not in frame and 'source' in frame:
                path.append(bringFrame['source'])
        if path is not None:
            for loc in path:
                if loc in location_list:
                    pass

    def addMoveSequence(self, Sequence: [int, [int, int], str]):
        """
        添加动作序列，传入动作序列Sequence，Sequence格式为[waitTime,
        [goalX, goalY]], waitTime表示机器人在执行动作序列之前要等待的时间
        ，单位ms. goalX，goalY分别表示该动作序列要到达的点

        :param Sequence: 动作序列
        :return: None
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
                waitTime, [goalX, goalY], name = self.__moveSequence.pop(0)  # 读出动作序列第一个元素
                self.__currentMovePath = self.__search.make_path(  # 路径规划，并把路径加入路径序列
                    start=(self.RobotCurrentPoint_pix[0],
                           self.RobotCurrentPoint_pix[1]),
                    goal=(goalX, goalY))
                self.__clearTrackFunction()
                QThread.msleep(waitTime)  # 等待时间
                self.logInfo("Current goal: " + name)
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
