# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MainWindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1643, 1021)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.widget = QtWidgets.QWidget(self.centralwidget)
        self.widget.setGeometry(QtCore.QRect(10, 810, 451, 161))
        self.widget.setObjectName("widget")
        self.UserComboBox = QtWidgets.QComboBox(self.widget)
        self.UserComboBox.setGeometry(QtCore.QRect(0, 0, 115, 35))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.UserComboBox.setFont(font)
        self.UserComboBox.setAutoFillBackground(False)
        self.UserComboBox.setStyleSheet("border-radius:6px;\n"
"padding:2px 4px;\n"
"border-style: outset;\n"
"border:2px groove gray;\n"
"")
        self.UserComboBox.setObjectName("UserComboBox")
        self.UserComboBox.addItem("")
        self.UserComboBox.addItem("")
        self.UserComboBox.addItem("")
        self.UserComboBox.addItem("")
        self.userhead = QtWidgets.QLabel(self.widget)
        self.userhead.setGeometry(QtCore.QRect(0, 40, 110, 110))
        self.userhead.setAutoFillBackground(False)
        self.userhead.setStyleSheet("border-radius:6px;\n"
"padding:2px 4px;\n"
"border-style: outset;\n"
"border:2px groove gray;")
        self.userhead.setText("")
        self.userhead.setObjectName("userhead")
        self.chat_text = QtWidgets.QTextEdit(self.widget)
        self.chat_text.setGeometry(QtCore.QRect(120, 0, 321, 150))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.chat_text.sizePolicy().hasHeightForWidth())
        self.chat_text.setSizePolicy(sizePolicy)
        self.chat_text.setStyleSheet("border-radius:6px;\n"
"padding:2px 4px;\n"
"border-style: outset;\n"
"border:2px groove gray;\n"
"background-color: rgb(251, 251, 251);\n"
"border-top-color:rgb(186, 189, 182);\n"
"border:none;")
        self.chat_text.setObjectName("chat_text")
        self.Send_Button = QtWidgets.QPushButton(self.widget)
        self.Send_Button.setGeometry(QtCore.QRect(350, 110, 75, 35))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Send_Button.sizePolicy().hasHeightForWidth())
        self.Send_Button.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.Send_Button.setFont(font)
        self.Send_Button.setAutoFillBackground(False)
        self.Send_Button.setStyleSheet("border-radius:6px;\n"
"padding:2px 4px;\n"
"border-style: outset;\n"
"border:2px groove gray;\n"
"border:none;\n"
"background-color: rgb(229, 234, 233);\n"
"color: rgb(37, 194, 118);\n"
"")
        self.Send_Button.setIconSize(QtCore.QSize(16, 16))
        self.Send_Button.setAutoDefault(True)
        self.Send_Button.setDefault(False)
        self.Send_Button.setFlat(False)
        self.Send_Button.setObjectName("Send_Button")
        self.widget_2 = QtWidgets.QWidget(self.centralwidget)
        self.widget_2.setGeometry(QtCore.QRect(460, 0, 911, 971))
        self.widget_2.setObjectName("widget_2")
        self.map = QtWidgets.QLabel(self.widget_2)
        self.map.setGeometry(QtCore.QRect(0, 10, 910, 891))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.map.sizePolicy().hasHeightForWidth())
        self.map.setSizePolicy(sizePolicy)
        self.map.setAutoFillBackground(False)
        self.map.setStyleSheet("border-radius:6px;\n"
"padding:2px 4px;\n"
"border-style: outset;\n"
"border:2px groove gray;")
        self.map.setLocale(QtCore.QLocale(QtCore.QLocale.Chinese, QtCore.QLocale.China))
        self.map.setFrameShadow(QtWidgets.QFrame.Plain)
        self.map.setText("")
        self.map.setTextFormat(QtCore.Qt.PlainText)
        self.map.setObjectName("map")
        self.cleartrackbutton = QtWidgets.QPushButton(self.widget_2)
        self.cleartrackbutton.setGeometry(QtCore.QRect(0, 910, 910, 35))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.cleartrackbutton.setFont(font)
        self.cleartrackbutton.setAutoFillBackground(False)
        self.cleartrackbutton.setStyleSheet("border-radius:6px;\n"
"padding:2px 4px;\n"
"border-style: outset;\n"
"border:2px groove gray;\n"
"background-color: rgb(229, 234, 233);\n"
"color: rgb(37, 194, 118);")
        self.cleartrackbutton.setObjectName("cleartrackbutton")
        self.widget_3 = QtWidgets.QWidget(self.centralwidget)
        self.widget_3.setGeometry(QtCore.QRect(1370, 10, 271, 961))
        self.widget_3.setObjectName("widget_3")
        self.chat_interface = QtWidgets.QTextBrowser(self.widget_3)
        self.chat_interface.setGeometry(QtCore.QRect(10, -10, 251, 961))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.chat_interface.sizePolicy().hasHeightForWidth())
        self.chat_interface.setSizePolicy(sizePolicy)
        self.chat_interface.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.chat_interface.setAutoFillBackground(False)
        self.chat_interface.setFrameShape(QtWidgets.QFrame.Box)
        self.chat_interface.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.chat_interface.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.chat_interface.setTabChangesFocus(False)
        self.chat_interface.setObjectName("chat_interface")
        self.widget_4 = QtWidgets.QWidget(self.centralwidget)
        self.widget_4.setGeometry(QtCore.QRect(10, 10, 441, 791))
        self.widget_4.setObjectName("widget_4")
        self.listWidget = QtWidgets.QListWidget(self.widget_4)
        self.listWidget.setGeometry(QtCore.QRect(0, 0, 441, 791))
        self.listWidget.setStyleSheet("QListWidget{background-color: rgb(247, 247, 247); color:rgb(51,51,51); border: 1px solid  rgb(247, 247, 247);outline:0px;}\n"
"QListWidget::Item{background-color: rgb(247, 247, 247);}\n"
"QListWidget::Item:hover{background-color: rgb(247, 247, 247); }\n"
"QListWidget::item:selected{\n"
"    background-color: rgb(247, 247, 247);\n"
"    color:black; \n"
"    border: 1px solid  rgb(247, 247, 247);\n"
"}\n"
"QListWidget::item:selected:!active{border: 1px solid  rgb(247, 247, 247); background-color: rgb(247, 247, 247); color:rgb(51,51,51); } ")
        self.listWidget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.listWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.listWidget.setObjectName("listWidget")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1643, 28))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "FIT4-5仿真平台"))
        self.UserComboBox.setItemText(0, _translate("MainWindow", "WenDong"))
        self.UserComboBox.setItemText(1, _translate("MainWindow", "Mr.Liu"))
        self.UserComboBox.setItemText(2, _translate("MainWindow", "GangHui"))
        self.UserComboBox.setItemText(3, _translate("MainWindow", "LanJun"))
        self.Send_Button.setText(_translate("MainWindow", "发送(↵)"))
        self.cleartrackbutton.setText(_translate("MainWindow", "Clear the Track"))
