import cv2
import sys
import time
from PyQt5 import QtCore
from PyQt5.QtCore import QTimer, QSize, QDateTime
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from MainWindow import Ui_MainWindow
from PathPlanningAstar.astar import world_to_pixel, Map, smooth_path2
from PathPlanningAstar.Simulator_llj import search
from CoreNLP.CoreNLP import CorenNLP
from QtCustomComponents.qnchatmessage import QNChatMessage
HeadWidth = 80
HeadHight = 80

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

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.Send_Button.clicked.connect(self.sendbutton_fuction)
        self.UserComboBox.currentIndexChanged.connect(self.userchanged)
        self.cleartrackbutton.clicked.connect(self.cleartrackbutton_function)
        self.map.setScaledContents(True)
        self.userhead.setScaledContents(True)
        self.movetimer = QTimer(self)
        self.count = 0
        self.pointnumber = 0
        self.Im = cv2.imread('PathPlanningAstar/fit4_5Dealing.png')
        self.RobotCurrentPoint_pix, self.RobotCurrentPoint = get_random_agent_location()
        self.RobotTargetPoint_pix = None
        cv2.circle(self.Im, (self.RobotCurrentPoint_pix[0], self.RobotCurrentPoint_pix[1]), 10, (0, 0, 255), -1)
        self.show_pic(self.Im)
        self.path = []
        self.corenlp = CorenNLP()
        self.Currentuser = Person['WenDong']
        self.RobotHead = "robot.jpeg"
        self.path_map = Map()
        self.userhead.setPixmap(QPixmap("ProfilePicture/" + self.Currentuser['head']))


    def dealMessage(self, messageW: QNChatMessage, item: QListWidgetItem,
                    text: str, name: str, time: int, usertype: QNChatMessage.User_Type):
        messageW.setFixedWidth(self.width())
        size = messageW.fontRect(text, name)
        item.setSizeHint(size)
        messageW.setText(text, time, name, size, usertype)
        self.listWidget.setItemWidget(item, messageW)

    def dealMessageTime(self, curMsgTime: int):
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

    def show_pic(self, cv2image) -> None:
        cv2image = cv2.resize(cv2image, (2300, 2000), interpolation=cv2.INTER_CUBIC)
        showImage = QImage(cv2image.data, cv2image.shape[1], cv2image.shape[0], QImage.Format_RGB888)
        self.map.setPixmap(QPixmap.fromImage(showImage))

    def UserTalk(self, message: str):
        t = QDateTime.currentDateTime().toTime_t()
        self.dealMessageTime(t)
        messageW = QNChatMessage(self.listWidget.parentWidget())
        messageW.setPixUser("ProfilePicture/" + self.Currentuser['head'])
        item = QListWidgetItem(self.listWidget)
        self.dealMessage(messageW, item, message, self.Currentuser['name'], t, QNChatMessage.User_Type.User_She)
        self.listWidget.setCurrentRow(self.listWidget.count() - 1)

    def Robotalk(self, message: str):
        t = QDateTime.currentDateTime().toTime_t()
        self.dealMessageTime(t)
        messageW = QNChatMessage(self.listWidget.parentWidget())
        print(self.listWidget.parentWidget().width())
        item = QListWidgetItem(self.listWidget)
        self.dealMessage(messageW, item, message, "Robot", t, QNChatMessage.User_Type.User_Me)
        self.listWidget.setCurrentRow(self.listWidget.count() - 1)
    def userchanged(self):
        currentuser = self.UserComboBox.currentText()
        for key in Person:
            if currentuser == key:
                self.Currentuser = Person[key]
                break
        self.userhead.setPixmap(QPixmap("ProfilePicture/" + self.Currentuser['head']))

    def cleartrackbutton_function(self):
        self.Im = cv2.imread('PathPlanningAstar/fit4_5Dealing.png')
        cv2.circle(self.Im, (self.RobotCurrentPoint_pix[0], self.RobotCurrentPoint_pix[1]), 10, (0, 0, 255), -1)
        self.show_pic(self.Im)

    def sendbutton_fuction(self):
        sendtext = self.chat_text.toPlainText()
        self.chat_text.setText("")
        if sendtext != "":
            self.UserTalk(sendtext)
            most_subject, relations, objects = self.corenlp.annotate_message_en(sendtext, "Wendong", "Jiqiren")
            if most_subject is not None:
                if most_subject == "Robot" and len(relations) != 0:
                    robotreply = "Who:{}, Doing:{}, What:{}".format(most_subject, relations[0], objects)
                else:
                    robotreply = "Sorry,I dont know what you say."
            else:
                robotreply = "Sorry,I dont know what you say."
            self.Robotalk(robotreply)

            if sendtext == "4":
                path_search = search(start=(self.RobotCurrentPoint_pix[0], self.RobotCurrentPoint_pix[1]),
                                     goal=(1470, 1821), map=self.path_map)
                path = path_search.make_path()
                self.path = smooth_path2(path)
                self.RobotTargetPoint_pix = [self.path[-1][0], self.path[-1][1]]
                cv2.circle(self.Im, (self.RobotTargetPoint_pix[0], self.RobotTargetPoint_pix[1]), 10, (255, 0, 0), -1)
                self.movetimer.start(2)
                self.movetimer.timeout.connect(self.timeout_slot)
                print(len(self.path))
                self.pointnumber = len(self.path)

    def timeout_slot(self):
        if self.count >= self.pointnumber:
            self.movetimer.stop()
            self.count = 0
            self.pointnumber = 0
        else:
            self.RobotCurrentPoint_pix[0], self.RobotCurrentPoint_pix[1] = self.path[self.count][0], \
                                                                           self.path[self.count][1]
            cv2.circle(self.Im, (self.RobotCurrentPoint_pix[0], self.RobotCurrentPoint_pix[1]), 2, (0, 0, 213), -1)
            self.show_pic(self.Im)
            self.count = self.count + 1


def get_random_agent_location():
    import random
    map = Map().grid_map
    while True:
        point = (random.choice(range(-80, 80)), random.choice(range(-80, 80)))
        pixle_point = world_to_pixel(world_points=point, image_size=(2309, 2034))
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
