# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'QtNLP'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_dialog(object):
    def setupUi(self, dialog):
        dialog.setObjectName("dialog")
        dialog.resize(2038, 1253)
        dialog.setAutoFillBackground(False)
        self.chat_interface = QtWidgets.QTextBrowser(dialog)
        self.chat_interface.setGeometry(QtCore.QRect(10, 10, 571, 1161))
        self.chat_interface.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.chat_interface.setAutoFillBackground(False)
        self.chat_interface.setFrameShape(QtWidgets.QFrame.Box)
        self.chat_interface.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.chat_interface.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.chat_interface.setTabChangesFocus(False)
        self.chat_interface.setObjectName("chat_interface")
        self.chat_text = QtWidgets.QTextEdit(dialog)
        self.chat_text.setGeometry(QtCore.QRect(10, 1180, 471, 70))
        self.chat_text.setObjectName("chat_text")
        self.Send_Button = QtWidgets.QPushButton(dialog)
        self.Send_Button.setGeometry(QtCore.QRect(490, 1180, 91, 71))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.Send_Button.setFont(font)
        self.Send_Button.setObjectName("Send_Button")
        self.map = QtWidgets.QLabel(dialog)
        self.map.setGeometry(QtCore.QRect(590, 10, 1431, 1221))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.map.sizePolicy().hasHeightForWidth())
        self.map.setSizePolicy(sizePolicy)
        self.map.setAutoFillBackground(False)
        self.map.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.map.setFrameShadow(QtWidgets.QFrame.Plain)
        self.map.setText("")
        self.map.setTextFormat(QtCore.Qt.PlainText)
        self.map.setObjectName("map")

        self.retranslateUi(dialog)
        QtCore.QMetaObject.connectSlotsByName(dialog)

    def retranslateUi(self, dialog):
        _translate = QtCore.QCoreApplication.translate
        dialog.setWindowTitle(_translate("dialog", "FIT4-5仿真平台"))
        self.Send_Button.setText(_translate("dialog", "Send"))
