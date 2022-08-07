import json
import multiprocessing
import os
import threading

import cv2
import time
import random
import numpy as np
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
import pickle


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

        # 加载当前屏幕的分辨率
        current_screenNumber = qApp.desktop().screenNumber()
        desktop_w, desktop_h = qApp.desktop().screenGeometry(current_screenNumber).width(), \
                               qApp.desktop().screenGeometry(current_screenNumber).height()

        # 加载地图
        self._map = QPixmap("data/map/fit4_5/fit4_5.png")
        self._map_cv2 = cv2.imread("PathPlanningAstar/fit4_5.png")
        self._map_w, self._map_h = self._map.width(), self._map.height()

        # 加载机器人头像
        self._robot = QPixmap("ProfilePicture/robot.png") \
            .scaled(50, 50, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)

        # 设置全屏显示
        self.setGeometry(self.centralwidget.x() + 0, self.centralwidget.height() + 0, desktop_w, desktop_h)
        self.centralwidget.setGeometry(0, 0,
                                       self.width(), self.height() - self.menubar.height() - self.statusbar.height())

        # map scene 设置, 长宽为map的分辨率
        self.map_scene = QGraphicsScene(0, 0, self._map_w, self._map_h)
        # 向map scene中添加地图
        self.map_scene_map_item = self.map_scene.addPixmap(self._map)
        # 向map scene中添加机器人
        self.map_scene_robot_item = self.map_scene.addPixmap(self._robot)
        # 设置机器人的图层为2
        self.map_scene_robot_item.setZValue(2)
        # 生成机器人随机位置
        self.RobotCurrentPoint_pix, self.RobotCurrentPoint = self.__getRandomAgentLocation()
        # 设置机器人位置
        self.map_scene_robot_item.setPos(int((self.RobotCurrentPoint_pix[0] - self._robot.width() / 2)),
                                         int(self.RobotCurrentPoint_pix[1] - self._robot.height() / 2))

        # map_scene real view 即局部地图的view设置
        self.map_view_real.setScene(self.map_scene)

        # map_scene real view 即全局小地图的view设置
        self.map_view_mini.setScene(self.map_scene)

        # 路径画笔定义
        path_pen = QPen()
        path_pen.setColor(QColor(255, 0, 0))
        path_pen.setStyle(Qt.DotLine)
        path_pen.setWidth(5)
        self._map_scene_path = QPainterPath()
        self._map_scene_path.moveTo(self.RobotCurrentPoint_pix[0], self.RobotCurrentPoint_pix[1])
        self._map_scene_path_item = self.map_scene.addPath(self._map_scene_path, path_pen)
        self._map_scene_path_item.setPen(path_pen)
        # 设置路径的图层为1
        self._map_scene_path_item.setZValue(1)

        # 布局设计
        # 全局小地图大小和位置设置
        self.map_view_mini.setGeometry(self.centralwidget.x() + int(self.centralwidget.width() / 4),
                                       self.centralwidget.y() + 10,
                                       int(self.centralwidget.width() / 4), int(self.centralwidget.width() / 4))
        self.map_view_mini.scale(0.99 * self.map_view_mini.width() / self._map_w,
                                 0.99 * self.map_view_mini.height() / self._map_h * (self._map_h / self._map_w))
        # 局部地图的view大小和位置设置,以及聚焦机器人
        self.map_view_real.setGeometry(self.centralwidget.x() + 2 * int(self.centralwidget.width() / 4),
                                       self.centralwidget.y() + 10,
                                       2 * int(self.centralwidget.width() / 4),
                                       int(self.centralwidget.width() / 4))
        self.map_view_real.centerOn(self.map_scene_robot_item)
        # 聊天框大小及位置设置
        self.listWidget.setGeometry(self.centralwidget.x() + 10,
                                    self.centralwidget.y() + 10,
                                    int(self.centralwidget.width() / 4) - 10,
                                    int(4 * self.centralwidget.height() / 5))
        # 用户选择框大小及位置设置
        self.UserComboBox.move(self.listWidget.x(), self.listWidget.y() + self.listWidget.height() + 10)
        self.UserComboBox.setFixedWidth(int(self.listWidget.width() / 4) - 10)  # 聊天框的五分之一减去10
        self.UserComboBox.setFixedHeight(self.centralwidget.height() - self.listWidget.height() -\
                                         self.UserComboBox.width() - 10 - 10 - 10)
        # 用户头像框大小及位置设置
        self.userhead.setGeometry(self.UserComboBox.x(),
                                  self.UserComboBox.y() + self.UserComboBox.height() + 10,
                                  self.UserComboBox.width(),
                                  self.UserComboBox.width())
        # 文本框大小及位置设置
        self.chat_text.setGeometry(self.UserComboBox.x() + self.UserComboBox.width() + 10,
                                   self.UserComboBox.y(),
                                   self.listWidget.width() - 10 - self.UserComboBox.width(),
                                   self.UserComboBox.height() + 10 + self.userhead.height())
        # 发送按钮位置设置
        self.Send_Button.move(self.chat_text.x() + self.chat_text.width() - self.Send_Button.width() - 5,
                              self.chat_text.y() + self.chat_text.height() - self.Send_Button.height() - 5)
        # 清空按钮的大小及位置设置
        self.cleartrackbutton.move(self.map_view_mini.x(), self.map_view_mini.y() + self.map_view_mini.height() + 10)
        self.cleartrackbutton.setFixedWidth(self.map_view_mini.width() + self.map_view_real.width())

        # 信息打印窗口大小及位置设置
        self.chat_interface.setFixedHeight(int(self.centralwidget.height() - self.map_view_real.height() - 20))
        self.chat_interface.setFixedWidth(int(self.centralwidget.width() / 4 - 20))
        self.chat_interface.move(self.map_view_real.x() + self.map_view_real.width() + 10,
                                 self.map_view_real.y())

        # 加载地点列表
        with open('data/Location_list.json', 'r', encoding='utf-8') as f:
            self._location_list: dict = json.load(f)

        # 生成不同颜色的未知头像
        unk_head = cv2.imread("ProfilePicture/Unk.png", cv2.IMREAD_UNCHANGED)
        r, g, b, a = cv2.split(unk_head)
        unk_head_rgb_permutation = list(itertools.permutations([r, g, b], 3))
        unk_head_permutation = []
        for u in unk_head_rgb_permutation:
            first, second, third = u
            uu = cv2.merge([first, second, third, a])
            q_uu = QPixmap.fromImage(QImage(uu.data, uu.shape[1], uu.shape[0], uu.shape[1] * 4,
                                            QImage.Format.Format_RGBA8888))
            unk_head_permutation.append(q_uu)

        # 加载人物列表及生成图像
        with open('data/Person.json', 'r', encoding='utf-8') as f:
            self._Person = json.load(f)
        for person in self._Person:
            if 'head' in self._Person[person]:
                self._Person[person]["head_QPixmap"] = QPixmap("ProfilePicture/" + self._Person[person]["head"])
            else:
                self._Person[person]["head_QPixmap"] = unk_head_permutation.pop()

        # 一些槽函数的连接
        self.Send_Button.clicked.connect(self.sendButtonFunction)
        self.UserComboBox.currentIndexChanged.connect(self.__userChanged)
        self.cleartrackbutton.clicked.connect(self.__clearTrackFunction)

        # 向statusbar添加map_view_real的信息打印
        self.map_view_real_status = QLabel()
        self.map_view_real_status.setMinimumWidth(150)
        self.statusbar.addWidget(self.map_view_real_status)

        # 重写map_view_real 的mouseMoveEvent函数
        self.map_view_real.mouseMoveEvent = self._map_view_real_mouseMoveEvent
        # 打开map_view_real 的鼠标跟踪功能
        self.map_view_real.setMouseTracking(True)

        # 一些Qt组件的属性设置
        self.userhead.setScaledContents(True)
        self.RobotTargetPoint_pix = None

        # 初始化一些参数
        self.__moveSequence = []
        self.__currentMovePath = []
        self.__path = []
        self.__currentWaitCont = 0
        self.count = 0
        self.__pointNumber = 0

        # 接入自然语言处理工具
        # 创建对话分析工具Queue队列
        self._InstructionPrediction_InQueue = InstructionPrediction_InQueue
        self._InstructionPrediction_OutQueue = InstructionPrediction_OutQueue

        # 初始化动态时空图谱
        # 创建动态时空图谱进程的Queue队列
        self._TimeSpaceGraph_InQueue = TimeSpaceGraph_InQueue
        self._TimeSpaceGraph_OutQueue = TimeSpaceGraph_OutQueue

        # 初始化路径规划模块
        # 创建路径规划进程的Queue队列
        self.PathPlanningProcess_InQueue = PathPlanningProcess_InQueue
        self.PathPlanningProcess_OutQueue = PathPlanningProcess_OutQueue

        # 初始化当前用户
        self.CurrentUser = self._Person['晨峻']
        self.userhead.setPixmap(self.CurrentUser['head_QPixmap'])

        # 初始化动作扫描服务
        self.__moveTimer = QTimer(self)
        self.__moveTimer.timeout.connect(self.__moveScanf)
        self.__moveSpeed = 10
        self.__waitForPathPlanning = False
        self.__moveTimer.start(self.__moveSpeed)

        # 画框标志位
        self.isDragRect = False
        self.dragStartPt = QPoint()
        self.dragRectPressFlag = False

        # 列表扫描服务
        if dialogue_list is not None:
            self.dialogue_list = dialogue_list
            self.dialogue_list_deal_timer = QTimer(self)
            self.dialogue_list_deal_timer.timeout.connect(self._dialogue_list_deal)
            self.dialogue_list_deal_timer.start(2000)

        self.actionTag_location.setCheckable(True)
        self.actionTag_location.triggered.connect(self._Tag_location_fun)
        self.action_exit.triggered.connect(self.action_exit_fun)

        # 初始化标注的房间item列表
        self.room_item_list = []
        self.map_scene_room_item_dict = {}
        self._load_map_room_item()

        # tag location槽函数连接
        self.map_view_real.mouseReleaseEvent = self._map_view_real_ReleaseEvent
        self.map_view_real.mousePressEvent = self._map_view_real_PressEvent

        # save TagLocation槽函数连接
        self.actionsave_Tag_Location = self.save_map_scene_room_item_dict

        # open map事件
        self.action_open_map = self._action_open_map

    def keyPressEvent(self, a0: QKeyEvent) -> None:
        """
        重写按键Press事件
        """
        if a0.key() == Qt.Key.Key_Escape:
            self.close()
        if a0.key() == Qt.Key.Key_Delete:
            QGraphicsItemList = self.map_scene.selectedItems()
            if QGraphicsItemList:
                for item in QGraphicsItemList:
                    if isinstance(item, QGraphicsPixmapItem):
                        name = item.data(0)
                        self.map_scene.removeItem(item)
                        self.map_scene.removeItem(self.map_scene_room_item_dict[name]["name_label"])
                        self.map_scene_room_item_dict.pop(name)
                        self.actionTag_location.setVisible(True)

        return QMainWindow.keyPressEvent(self, a0)

    def save_map_scene_room_item_dict(self):
        """
        room信息保存功能的实现
        """
        d = {}
        for name in self.map_scene_room_item_dict:
            d[name] = {}
            d[name]['argument'] = {}
            d[name]['argument']['color'] =self.map_scene_room_item_dict[name]["argument"]["color"]
            self.map_scene_room_item_dict[name]["argument"]["label_pos"] = \
                [int(self.map_scene_room_item_dict[name]['name_label'].x()),
                 int(self.map_scene_room_item_dict[name]['name_label'].y())]
            room_name_label_pos = self.map_scene_room_item_dict[name]["argument"]["label_pos"]
            d[name][name]["argument"]["label_pos"] = room_name_label_pos
            d[name]['argument']['name'] = self.map_scene_room_item_dict[name]['argument']["name"]
            d[name]['argument']['rect'] = self.map_scene_room_item_dict[name]['argument']["rect"]
            d[name]['argument']['room'] = self.map_scene_room_item_dict[name]['argument']["room"]
        with open("data/fit4_5Dealing.pkl", 'wb') as f:
            pickle.dump(d, f)

    def _load_map_room_item(self):
        """
        加载保存的房间标注信息
        """
        if os.path.exists("data/fit4_5Dealing.pkl"):
            with open("data/fit4_5Dealing.pkl", 'rb') as f:
                d = pickle.load(f)
            for r in d:
                # 加载room信息
                rect = d[r]['argument']['rect']
                room = d[r]['argument']['room']
                room_color = d[r]['argument']['color']
                color = (255 - room_color).tolist() + [200]
                room_name_label_pos = d[r]['argument']['label_pos']

                name = d[r]['argument']['name']
                # room标签设置
                room_name_label: QGraphicsTextItem = self.map_scene.addText(name)
                room_name_label.setDefaultTextColor(QColor(color[0], color[1], color[2], color[3]))
                font = QFont("Times", 36)
                room_name_label.setFont(font)
                room_name_label.setPos(room_name_label_pos[0], room_name_label_pos[1])
                room_name_label.setFlags(QGraphicsItem.ItemIsSelectable |
                                         QGraphicsItem.ItemIsMovable |
                                         QGraphicsItem.ItemIsFocusable)
                room_name_label.setZValue(4)

                Q_room_Image = QImage(room.data, room.shape[1], room.shape[0], room.shape[1] * 4,
                                      QImage.Format_RGBA8888)
                Q_room = QPixmap().fromImage(Q_room_Image)
                map_room_item: QGraphicsPixmapItem = self.map_scene.addPixmap(Q_room)
                map_room_item.setPos(rect[0], rect[1])
                map_room_item.setZValue(1)
                map_room_item.setShapeMode(QGraphicsPixmapItem.MaskShape)
                map_room_item.setFlags(QGraphicsItem.ItemIsSelectable |
                                       QGraphicsItem.ItemIsFocusable |
                                       QGraphicsItem.ItemClipsToShape
                                       )
                map_room_item.setData(0, name)  # 自定义map_room_item的值
                map_room_item.setCacheMode(QGraphicsItem.DeviceCoordinateCache)
                self.map_scene_room_item_dict[r] = d[r]
                self.map_scene_room_item_dict[r]['item'] = map_room_item
                self.map_scene_room_item_dict[r]['name_label'] = room_name_label
            items = []
            for room_name in self._location_list:
                if room_name not in self.map_scene_room_item_dict:
                    items.append(room_name)
            if items:
                pass
            else:
                self.actionTag_location.setCheckable(False)
                self.actionTag_location.setVisible(False)

    def action_exit_fun(self):
        """
        程序退出时调用的函数
        """
        if QMessageBox(QMessageBox.Icon.Question, "确认退出", "是否退应用程序？",
                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) \
                .exec_() == QMessageBox.StandardButton.Yes:
            self.close()

    def _map_view_real_ReleaseEvent(self, e: QMouseEvent):
        """
        重写 map_view_real的鼠标释放事件。
        释放时若是DragRec模式读取 RubberBandDrag所选中区域进行区域内房间选择，该功能待优化，效果不是太好。
        """
        if self.dragRectPressFlag & self.actionTag_location.isChecked():
            # 获取roi 区域
            r = self.map_view_real.mapToScene(self.map_view_real.rubberBandRect())  # [0左上角，1右上角，2右下角，3左下角]

            # 原图mask
            mask = np.zeros(self._map_cv2.shape[:2], dtype=np.uint8)

            # 矩形roi
            rect = (int(r[0].x()), int(r[0].y()), int(r[2].x() - r[0].x()), int(r[2].y() - r[0].y()))
            bgdmodel = np.zeros((1, 65), np.float64)  # bg模型的临时数组
            fgdmodel = np.zeros((1, 65), np.float64)  # fg模型的临时数组

            # 提取区域
            cv2.grabCut(self._map_cv2, mask, rect, bgdmodel, fgdmodel, 3, mode=cv2.GC_INIT_WITH_RECT)

            # 提取前景和可能的前景区域
            room_mask = np.array(mask[int(r[0].y()):int(r[2].y()),
                                 int(r[0].x()):int(r[2].x())], dtype='uint8')
            room_mask = np.where((room_mask == 1) + (room_mask == 3),
                                 125, 0).reshape(room_mask.shape[0], room_mask.shape[1], 1)
            room_color = np.random.randint(0, 255, 3)
            room = room_color * np.ones((room_mask.shape[0], room_mask.shape[1], 1), np.uint8)
            room = np.concatenate((room, room_mask), axis=2).astype(np.uint8)
            Q_room_Image = QImage(room.data, room.shape[1], room.shape[0], room.shape[1] * 4,
                                  QImage.Format_RGBA8888)
            Q_room = QPixmap().fromImage(Q_room_Image)

            # 记录当前房间item
            map_room_item: QGraphicsPixmapItem = self.map_scene.addPixmap(Q_room)
            map_room_item.setPos(r[0])
            map_room_item.setZValue(1)
            map_room_item.setShapeMode(QGraphicsPixmapItem.MaskShape)
            map_room_item.setFlags(QGraphicsItem.ItemIsSelectable |
                                   QGraphicsItem.ItemIsFocusable |
                                   QGraphicsItem.ItemClipsToShape)

            items = []
            for room_name in self._location_list:
                if room_name not in self.map_scene_room_item_dict:
                    items.append(room_name)
            name, boolAction = QInputDialog.getItem(self.window(), "指定房间", "房间:", items, 0, False)
            if boolAction and name != '':
                self.map_scene_room_item_dict[name] = {}
                room_name_label: QGraphicsTextItem = self.map_scene.addText(name)
                color = (255 - room_color).tolist() + [200]
                room_name_label.setDefaultTextColor(QColor(color[0], color[1], color[2], color[3]))
                font = QFont("Times", 28)
                room_name_label.setFont(font)
                room_name_label.setFlags(QGraphicsItem.ItemIsSelectable |
                                         QGraphicsItem.ItemIsFocusable)
                room_name_label.setZValue(4)
                room_name_label_pos = [int(rect[0] + rect[2] / 2), int(rect[1] + rect[3] / 2 - 36)]
                room_name_label.setPos(room_name_label_pos[0], room_name_label_pos[1])
                map_room_item.setData(0, name)  # 自定义map_room_item的值
                self.map_scene_room_item_dict[name]["item"] = map_room_item
                self.map_scene_room_item_dict[name]["name_label"] = room_name_label
                self.map_scene_room_item_dict[name]["argument"] = {}
                self.map_scene_room_item_dict[name]["argument"]["color"] = room_color
                self.map_scene_room_item_dict[name]["argument"]["label_pos"] = room_name_label_pos
                self.map_scene_room_item_dict[name]["argument"]["name"] = name
                self.map_scene_room_item_dict[name]["argument"]["rect"] = rect
                self.map_scene_room_item_dict[name]["argument"]["room"] = room
                if len(items) == 1 and name == items[0]:  # 最后一个房间已被选择完成，将该模式隐藏
                    self.map_view_real.setDragMode(QGraphicsView.NoDrag)
                    self.map_view_real.setCursor(Qt.ArrowCursor)
                    self.actionTag_location.setCheckable(False)
                    self.actionTag_location.setDisabled(True)
            else:
                self.map_scene.removeItem(map_room_item)
            # drag模式选择Flag
            self.dragRectPressFlag = False
        return QGraphicsView.mouseReleaseEvent(self.map_view_real, e)

    def _map_view_real_mouseMoveEvent(self, event: QMouseEvent):
        """
        重写map_view_real的鼠标移动事件，打印鼠标指向的地图像素点
        """
        view_pos = event.pos()
        scene_pos = self.map_view_real.mapToScene(view_pos)
        self.window().map_view_real_status.setText("<font color='red'>X</font>:<font color='blue'>{}</font>, "
                                                   "<font color='red'>Y</font>:<font color='blue'>{}</font>"
                                                   .format(scene_pos.x(), scene_pos.y()))
        return QGraphicsView.mouseMoveEvent(self.map_view_real, event)

    def _map_view_real_PressEvent(self, e: QMouseEvent):
        """
        重写map_view_real的鼠标按压事件，若是dragRect的模式则置位dragRectPressFlag标记位
        """
        if self.actionTag_location.isChecked():
            self.dragRectPressFlag = True
        return QGraphicsView.mousePressEvent(self.map_view_real, e)

    def _Tag_location_fun(self, check: bool):
        """
        Tag_location动作调用的函数
        """
        if check:
            self.map_view_real.setDragMode(QGraphicsView.RubberBandDrag)
            self.map_view_real.setCursor(Qt.CrossCursor)
        else:
            self.map_view_real.setCursor(Qt.ArrowCursor)
            self.map_view_real.setDragMode(QGraphicsView.NoDrag)

    def _dialogue_list_deal(self):
        """
        对话列表的处理函数
        """
        if self.dialogue_list:
            dialogue = self.dialogue_list.pop(0)
            self.dealMessage(dialogue)
        else:
            self.dialogue_list_deal_timer.stop()

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
            size = QSize(self.listWidget.width(), 40)
            messageTime.resize(size)
            itemTime.setSizeHint(size)
            messageTime.setText(str(curMsgTime), curMsgTime, "", size, QNChatMessage.User_Type.User_Time)
            self.listWidget.setItemWidget(itemTime, messageTime)

    def UserTalk(self, message: str) -> None:
        """
        用户说话

        :param message: 消息文本
        :return:
        """
        t = QDateTime.currentDateTime().toTime_t()
        self.__dealMessageTime(t)
        messageW = QNChatMessage(self.listWidget.parentWidget())
        userHead = self.CurrentUser['head_QPixmap']
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
        """
        用户改变的槽函数
        :param user: 当传入user为None时，则选取UserComboBox当前指定的用户
        :return:
        """
        if user is None:
            currentUser = self.UserComboBox.currentText()
            for key in self._Person:
                if currentUser == key:
                    self.CurrentUser = self._Person[key]
                    break
            self.userhead.setPixmap(self.CurrentUser['head_QPixmap'])
        else:
            self.CurrentUser = user
            self.UserComboBox.setCurrentText(user['name'])
            for key in self._Person:
                if user['name'] == key:
                    self.CurrentUser = self._Person[key]
                    break
            self.userhead.setPixmap(self.CurrentUser['head_QPixmap'])

    def __clearTrackFunction(self):
        """
        清除轨迹
        """
        self._map_scene_path.clear()
        self._map_scene_path_item.setPath(self._map_scene_path)
        self._map_scene_path.moveTo(self.RobotCurrentPoint_pix[0], self.RobotCurrentPoint_pix[1])

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
            self.RobotCurrentPoint_pix = [self.RobotCurrentPoint_pix[0], self.RobotCurrentPoint_pix[1]]  # 更新当前位置
            self._map_scene_path.lineTo(self.RobotCurrentPoint_pix[0], self.RobotCurrentPoint_pix[1])
            self._map_scene_path_item.setPath(self._map_scene_path)
            self.map_scene_robot_item.setPos(self.RobotCurrentPoint_pix[0] - int(self._robot.width() / 2),
                                             self.RobotCurrentPoint_pix[1] - int(self._robot.height() / 2))
            self.map_view_real.centerOn(self.map_scene_robot_item)
        elif self.__waitForPathPlanning:
            self.__moveTimer.setInterval(self.__moveSpeed)
            if not self.PathPlanningProcess_OutQueue.empty():
                self.__currentMovePath = self.PathPlanningProcess_OutQueue.get()
                self.__clearTrackFunction()
                self.RobotTargetPoint_pix = [self.__currentMovePath[-1][0], self.__currentMovePath[-1][1]]  # 更新当前目标点
                self.__waitForPathPlanning = False
        else:  # 当路径列表读空之后，扫描动作序列
            if self.__moveSequence:  # 当动作序列不为空时
                waitTime, [goalX, goalY], name = self.__moveSequence.pop(0)  # 读出动作序列第一个元素
                goalX, goalY = world_to_pixel((goalX, goalY))
                self.PathPlanningProcess_InQueue.put([self.RobotCurrentPoint_pix[0],
                                                      self.RobotCurrentPoint_pix[1],
                                                      goalX,
                                                      goalY])
                self.logInfo("Current goal: " + name)
                self.__waitForPathPlanning = True
                self.__moveTimer.setInterval(waitTime)

    def __getRandomAgentLocation(self) -> [[int, int], [int, int]]:
        """
        随机生成机器人位置

        :return: pixle_point-像素坐标，point-世界坐标
        """
        map = Map("PathPlanningAstar/middle.png").grid_map
        while True:
            point = (random.choice(range(-80, 80)), random.choice(range(-80, 80)))
            pixle_point = world_to_pixel(world_points=point)
            if 0 <= pixle_point[0] < len(map) and 0 <= pixle_point[1] < len(map[0]):
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
    # dialogue_list = ['刘老师:该赶我们的进度了，下午2点钟在1号会议室碰一下怎么样？',
    #                  '港晖:抱歉，老师，我参加不了，我下午2点要在Room511开个线上的会议',
    #                  '刘老师:好，其他人呢？',
    #                  '兰军:我准时到',
    #                  '小飞:我没问题'
    #                  ]

    # 指令解析服务的进程通信队列
    InstructionPrediction_InQueue, InstructionPrediction_OutQueue = multiprocessing.Queue(), multiprocessing.Queue()

    # 时空图谱服务的进程通信队列
    TimeSpaceGraph_InQueue, TimeSpaceGraph_OutQueue = multiprocessing.Queue(), multiprocessing.Queue()

    # 地图路径规划的进程通信队列
    PathPlanningProcess_InQueue, PathPlanningProcess_OutQueue = multiprocessing.Queue(), multiprocessing.Queue()

    # 指令解析服务的进程启动
    _InstructionPrediction_process = Process(target=InstructionPrediction_process, args=(
        InstructionPrediction_InQueue,
        InstructionPrediction_OutQueue), daemon=True)
    _InstructionPrediction_process.start()

    # 时空图谱服务的进程启动
    _TimeSpaceGraph_process = Process(target=TimeSpaceGraph_process, args=(
        TimeSpaceGraph_InQueue,
        TimeSpaceGraph_OutQueue), daemon=True)
    _TimeSpaceGraph_process.start()

    # 地图路径规划进程启动
    _PathPlanning_process = Process(target=PathPlanningProcess, args=(
        PathPlanningProcess_InQueue,
        PathPlanningProcess_OutQueue), daemon=True)
    _PathPlanning_process.start()

    app = QApplication(sys.argv)  # app应用程序对象,在Qt中，应用程序对象有且仅有一个
    window = MainWindow(InstructionPrediction_InQueue,
                        InstructionPrediction_OutQueue,
                        TimeSpaceGraph_InQueue,
                        TimeSpaceGraph_OutQueue,
                        PathPlanningProcess_InQueue,
                        PathPlanningProcess_OutQueue,
                        dialogue_list=dialogue_list)

    window.showFullScreen()  # 窗口对象默认不会显示，必须调用show方法显示窗口

    sys.exit(app.exec_())  # 让应用程序对象进入消息死循环, 让代码阻塞到此行


if __name__ == '__main__':
    main()
