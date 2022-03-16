import PyQt5.QtCore
import cv2
import math
import sys
import time
import os
from PyQt5 import QtCore
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from QtNLP import Ui_dialog
from PathPlanningAstar.astar import world_to_pixel, Map, smooth_path2
from PathPlanningAstar.Simulator_llj import search
from CoreNLP.CoreNLP import CorenNLP

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
    }
}

class MainWindow(QMainWindow, Ui_dialog):
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
        userhead = cv2.imread(self.Currentuser['head'])
        userhead = cv2.resize(userhead, (80, 80), interpolation=cv2.INTER_CUBIC)
        userhead = QImage(userhead.data, userhead.shape[1], userhead.shape[0], QImage.Format_RGB888)
        self.userhead.setPixmap(QPixmap.fromImage(userhead))

    def show_pic(self, cv2image) -> None:
        cv2image = cv2.resize(cv2image, (2300, 2000), interpolation=cv2.INTER_CUBIC)
        showImage = QImage(cv2image.data, cv2image.shape[1], cv2image.shape[0], QImage.Format_RGB888)
        self.map.setPixmap(QPixmap.fromImage(showImage))

    def UserTalk(self, message: str):
        self.chat_interface.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        strHTML = "<html>" \
                  "<head>" \
                  "<style type='text/css'>" \
                  ".atalk{margin:10px}" \
                  ".atalk span{display:inline-block;background:#dcdcdc;border:2px solid;color:#000;text-align:left;}" \
                  ".myMsg{max-height:300px;max-width:300px;position:relative;float:lift;}" \
                  ".divMyHead{position: relative;float: right;margin:5px 0px 5px 0px;right: 1px;border-radius: 5px;}" \
                  "" \
                  "font-size:3px;font-family:'微软雅黑';text-align:center;color:#fff;}.clear{clear:both;}" \
                  "</style>" \
                  "</head>" \
                  "<body>" \
                  "<li class='myMsg'>" \
                  "<div>" \
                  "<div class='divMyHead'>" \
                  "<img src='" + self.Currentuser['head'] + "' width=" + str(HeadWidth) + " height=" + ">" + \
                  "<font color='green'>" \
                  + self.Currentuser['name'] + \
                  "      </font>" \
                  "<font color='blue'>" \
                  + time.strftime("%Y-%m-%d %H:%M:%S") + \
                  "</font>" \
                  "</div>" \
                  "<div class='atalk'>" \
                  "<font class='atalk' size=5><span>" + message + "</span>" \
                                                                  "</font>" \
                                                                  "</div>" \
                                                                  "</div>" \
                                                                  "</li>" \
                                                                  "<body>" \
                                                                  "</html>"
        self.chat_interface.insertHtml(strHTML)

    def Robotalk(self, message: str):
        self.chat_interface.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        strHTML = "<html>" \
                  "<head>" \
                  "<style type='text/css'>" \
                  ".atalk{margin:10px}" \
                  ".atalk span{background:#dcdcdc;border:2px solid;color:#000;text-align:right;}" \
                  ".myMsg{max-height:300px;max-width:300px;position:right;float:lift;}" \
                  ".divMyHead{position: relative;float: right;margin:5px 0px 5px 0px;right: 1px;border-radius: 5px;}" \
                  "" \
                  "font-size:3px;font-family:'微软雅黑';text-align:center;color:#fff;}.clear{clear:both;}" \
                  "</style>" \
                  "</head>" \
                  "<body>" \
                  "<li class='myMsg'>" \
                  "<div>" \
                  "<div class='divMyHead'>" \
                  "<font color='green'>" \
                  + "Robot" + \
                  "      </font>" \
                  "<font color='blue'>" \
                  + time.strftime("%Y-%m-%d %H:%M:%S") + \
                  "</font>" \
                  + "<img src='" + self.RobotHead + "' width=" + str(HeadWidth) + " height=" + ">" \
                                                                                               "</div>" \
                                                                                               "<div class='atalk'>" \
                                                                                               "<font class='atalk' size=5><span>" + message + \
                  "</span>" \
                  "</font>" \
                  "</div>" \
                  "</div>" \
                  "</li>" \
                  "<body>" \
                  "</html>"
        self.chat_interface.insertHtml(strHTML)

    def userchanged(self):
        currentuser = self.UserComboBox.currentText()
        for key in Person:
            if currentuser == key:
                self.Currentuser = Person[key]
                break
        userhead = cv2.imread(self.Currentuser['head'])
        userhead = cv2.resize(userhead, (80, 80), interpolation=cv2.INTER_CUBIC)
        userhead = QImage(userhead.data, userhead.shape[1], userhead.shape[0], QImage.Format_RGB888)
        self.userhead.setPixmap(QPixmap.fromImage(userhead))

    def cleartrackbutton_function(self):
        self.Im = cv2.imread('PathPlanningAstar/fit4_5Dealing.png')
        cv2.circle(self.Im, (self.RobotCurrentPoint_pix[0],self.RobotCurrentPoint_pix[1]), 10, (0, 0, 255), -1)
        self.show_pic(self.Im)
    def sendbutton_fuction(self):
        sendtext = self.chat_text.toPlainText()
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
            # x, y = world_to_pixel(world_points=(self.path[self.count][0], self.path[self.count][1]),
            #                       image_size=(2309, 2034))
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
                    if map[pixle_point[0] + i][pixle_point[1] + j] == False:
                        false_flag = True
                        break
                if false_flag == True:
                    break
            if map[pixle_point[0]][pixle_point[1]] == True:
                break
    return pixle_point, point


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
