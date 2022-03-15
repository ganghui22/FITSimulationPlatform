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
from PathPlanningAstar.astar import world_to_pixel, PathPlanner, Node, Map
from CoreNLP.CoreNLP import CorenNLP

location_list = {
    'elevator_1': (14.30, -51.42),
    'elevator_2': (10.10, -3.37),
    'Wendong': (81.05, 13.98),
    'meeting': (74.90, 10.18),
    'Mr.Liu': (69.55, -69.32)
}


class MainWindow(QMainWindow, Ui_dialog):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.Send_Button.clicked.connect(self.sendbutton_fuction)
        self.map.setScaledContents(True)
        self.timer = QTimer(self)
        self.count = 0
        self.pointnumber = 0
        self.Im = cv2.imread('./PathPlanningAstar/fit4_5Dealing.png')
        self.startlocal_pix, self.startlocal = get_random_agent_location()
        self.startlocal_pix = (self.startlocal_pix[0], self.startlocal_pix[1])
        print(self.startlocal_pix)
        cv2.circle(self.Im, self.startlocal_pix, 10, (0, 0, 255), -1)
        self.show_pic(self.Im)
        self.path = []
        self.corenlp = CorenNLP()
        self.GanghuiHead = "<img src='./headportrait.jpeg' width='80' height='80'> "
        self.RobotHead = "<img src='./robot.jpeg' width='80' height='80'>"

    def show_pic(self, cv2image) -> None:
        cv2image = cv2.resize(cv2image, (2300, 2000), interpolation=cv2.INTER_CUBIC)
        showImage = QImage(cv2image.data, cv2image.shape[1], cv2image.shape[0], QImage.Format_RGB888)
        self.map.setPixmap(QPixmap.fromImage(showImage))

    def UserTalk(self, user: str, message: str):
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
                  + self.GanghuiHead + \
                  "<font color='green'>" \
                  + user + \
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
                  + self.RobotHead + \
                  "<font color='green'>" \
                  + "Robot" + \
                  "      </font>" \
                  "<font color='blue'>" \
                  + time.strftime("%Y-%m-%d %H:%M:%S") + \
                  "</font>" \
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

    def sendbutton_fuction(self):
        sendtext = self.chat_text.toPlainText()
        if sendtext != "":
            self.UserTalk("WenDong", sendtext)
            most_subject, relations, objects = self.corenlp.annotate_message_en(sendtext, "Wendong", "Jiqiren")
            if most_subject is not None:
                if most_subject == "Robot" and len(relations) != 0:
                    robotreply = "Who:{}, Doing:{}, What:{}".format(most_subject, relations[0], objects)
                else:
                    robotreply = "Sorry,I dont know what you say."
            else:
                robotreply = "Sorry,I dont know what you say."
            self.Robotalk(robotreply)

            if sendtext == "帮我给刘老师送一份文件":
                start1 = Node(self.startlocal[0], self.startlocal[1], math.pi)
                goal1 = Node(81.050, 13.979)
                planner1 = PathPlanner(goal1, math.pi, start1)
                start2 = Node(81.050, 13.979, math.pi)
                goal2 = Node(69.550, -69.322, math.pi)
                planner2 = PathPlanner(goal2, math.pi, start2)
                self.path = planner1.plan()
                self.timer.start(20)
                self.timer.timeout.connect(self.timeout_slot)
                self.pointnumber = len(self.path)

    def timeout_slot(self):
        if self.count >= self.pointnumber:
            self.timer.stop()
            self.count = 0
            self.pointnumber = 0
        else:
            x, y = world_to_pixel(world_points=(self.path[self.count].x, self.path[self.count].y),
                                  image_size=(2309, 2034))
            cv2.circle(self.Im, (x, y), 2, (0, 0, 213), -1)
            self.show_pic(self.Im)
            self.count = self.count + 1


def get_random_agent_location():
    import random
    map = Map().grid_map
    while True:
        point = (random.choice(range(-80, 80)), random.choice(range(-80, 80)))
        pixle_point = world_to_pixel(world_points=point, image_size=(2309, 2034))
        if 0 <= pixle_point[0] < 2309 and 0 <= pixle_point[1] < 2034:
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
