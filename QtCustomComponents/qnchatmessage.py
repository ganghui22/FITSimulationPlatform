import math
import time
from enum import Enum
from PyQt5.QtCore import QDateTime, Qt, QRect, QSize, QPointF, QRectF
from PyQt5.QtGui import QFontMetrics, QPixmap, QImage, QPainter, QMovie, QBrush, QColor, QPen, QTextOption
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import *
import PyQt5.QtWidgets


class QNChatMessage(QWidget):
    class User_Type(Enum):
        User_System = 1
        User_Me = 2
        User_She = 3
        User_Time = 4

    def __init__(self, parent=None):
        super(QNChatMessage, self).__init__(parent)
        te_font = self.font()
        te_font.setFamily("Arial")
        te_font.setPointSize(12)
        self.setFont(te_font)
        self.setFont(te_font)

        self.m_leftPixmap = QPixmap()
        self.m_rightPixmap = QPixmap()
        self.m_loadingMovie = QMovie(self)
        self.m_loadingMovie.setFileName("ProfilePicture/loading4.gif")
        self.m_loading = QLabel(self)
        self.m_loading.setMovie(self.m_loadingMovie)
        self.m_loading.resize(16, 16)
        self.m_loading.setAttribute(Qt.WA_TranslucentBackground, True)
        self.m_loading.setAutoFillBackground(False)
        self.m_isSending = False
        self.m_kuangRightRect = None
        self.m_iconLeftRect = QRect()
        self.m_iconRightRect = QRect()
        self.m_sanjiaoLeftRect = QRectF()
        self.m_sanjiaoRightRect = QRectF()
        self.m_kuangLeftRect = QRectF()
        self.m_kuangRightRect = QRectF()
        self.m_nameLeftRect = QRectF()
        self.m_textLeftRect = QRectF()
        self.m_textRightRect = QRectF()
        self.m_nameRightRect = QRectF()
        self.m_msg = ""
        self.m_userType = self.User_Type.User_System
        self.m_time = ""
        self.m_curTime = ""
        self.m_allSize = QSize()
        self.m_kuangWidth = 0
        self.m_textWidth = 0
        self.m_spaceWid = 0
        self.m_lineHeight = 0
        self.usrname = " "

    def setPixUser(self, q_pixmap: QPixmap):
        self.m_leftPixmap = q_pixmap

    def setTextSuccess(self):
        self.m_loading.hide()
        self.m_loadingMovie.stop()
        self.m_isSending = True

    def setText(self, text: str, t: int, name: str, allSize: QSize, userType: User_Type):
        self.m_msg = text
        self.m_userType = userType
        self.m_time = t
        self.usrname = name
        self.m_curTime = QDateTime.fromTime_t(t).toString("hh:mm")
        self.m_allSize = allSize
        if userType == self.User_Type.User_Me:
            if self.m_isSending is not True:
                self.m_loading.move(self.m_kuangRightRect.x() - self.m_loading.width() - 10,
                                    self.m_kuangRightRect.y() + self.m_kuangRightRect.height() / 2 - self.m_loading.height() / 2)
                self.m_loading.show()
                self.m_loadingMovie.start()
            else:
                self.m_loading.hide()
        self.update()

    def fontRect(self, string: str, name: str):
        self.m_msg = string
        self.usrname = name
        minHei = 60
        iconWH = 60
        iconSpaceW = 20
        iconRectW = 5
        iconTMPH = 5
        sanJiaoW = 6
        kuangTMP = 20
        textSpaceRect = 10
        nameHei = 30
        width = 441
        self.m_kuangWidth = width - kuangTMP - 2 * (iconWH + iconSpaceW + iconRectW)
        self.m_textWidth = self.m_kuangWidth - 2 * textSpaceRect
        self.m_spaceWid = width - self.m_textWidth
        # 头像框设置
        self.m_iconLeftRect = QRect(iconSpaceW, iconTMPH, iconWH, iconWH)
        self.m_iconRightRect = QRect(width - iconSpaceW - iconWH, iconTMPH, iconWH, iconWH)
        size = self.getRealString(self.m_msg)
        hei = minHei if size.height() < minHei else size.height()
        # 三角框设置
        self.m_sanjiaoLeftRect = QRect(iconWH + iconSpaceW + iconRectW, self.m_lineHeight / 2 + nameHei + 10, sanJiaoW,
                                       hei -
                                       self.m_lineHeight)
        self.m_sanjiaoRightRect = QRect(width - iconRectW - iconWH - iconSpaceW - sanJiaoW,
                                        self.m_lineHeight / 2 + nameHei + 10, sanJiaoW, hei - self.m_lineHeight)
        # 昵称框设置
        self.m_nameLeftRect.setRect(self.m_sanjiaoLeftRect.x() + self.m_sanjiaoLeftRect.width(),
                                    self.m_lineHeight / 4 * 3,
                                    self.getNameWidth() + 5,
                                    nameHei)
        self.m_nameRightRect.setRect(width - iconRectW - iconWH - iconSpaceW - sanJiaoW- self.getNameWidth(),
                                    self.m_lineHeight / 4 * 3,
                                    self.getNameWidth() + 5,
                                    nameHei)
        # 气泡框设置
        if size.width() < (self.m_textWidth + self.m_spaceWid):
            self.m_kuangLeftRect.setRect(self.m_sanjiaoLeftRect.x() + self.m_sanjiaoLeftRect.width(),
                                         self.m_lineHeight / 4 * 3 + nameHei,
                                         size.width() - self.m_spaceWid + 2 * textSpaceRect + 5,
                                         hei - self.m_lineHeight - 2 * iconTMPH)
            self.m_kuangRightRect.setRect(
                width - size.width() + self.m_spaceWid - 2 * textSpaceRect - iconWH - iconSpaceW - iconRectW - sanJiaoW,
                self.m_lineHeight / 4 * 3 + nameHei,
                size.width() - self.m_spaceWid + 2 * textSpaceRect + 5,
                hei - self.m_lineHeight - 2 * iconTMPH)
        else:
            self.m_kuangLeftRect.setRect(self.m_sanjiaoLeftRect.x() + self.m_sanjiaoLeftRect.width(),
                                         self.m_lineHeight / 4 * 3 + nameHei,
                                         self.m_kuangWidth + 1, hei - self.m_lineHeight - 2 * iconTMPH)
            self.m_kuangRightRect.setRect(iconWH + kuangTMP + iconSpaceW + iconRectW - sanJiaoW,
                                          self.m_lineHeight / 4 * 3 + nameHei,
                                          self.m_kuangWidth + 1, hei - self.m_lineHeight - 2 * iconTMPH)
        # 字体框设置
        self.m_textLeftRect.setRect(self.m_kuangLeftRect.x() + textSpaceRect, self.m_kuangLeftRect.y() + iconTMPH,
                                    self.m_kuangLeftRect.width() - 2 * textSpaceRect,
                                    self.m_kuangLeftRect.height() - 2 * iconTMPH)
        self.m_textRightRect.setRect(self.m_kuangRightRect.x() + textSpaceRect, self.m_kuangRightRect.y() + iconTMPH,
                                     self.m_kuangRightRect.width() - 2 * textSpaceRect,
                                     self.m_kuangRightRect.height() - 2 * iconTMPH)
        return QSize(size.width(), hei + 20)

    def getNameWidth(self):
        fm = QFontMetrics(self.font())
        namewidth = fm.horizontalAdvance(self.usrname)
        return namewidth

    def getRealString(self, src: str) -> QSize:
        fm = QFontMetrics(self.font())
        self.m_lineHeight = fm.lineSpacing()
        nCount = src.count("\n")
        nMaxWidth = 0
        if nCount == 0:
            nMaxWidth = fm.horizontalAdvance(src)
            if nMaxWidth > self.m_textWidth:
                num = math.ceil(nMaxWidth / self.m_textWidth)
                nMaxWidth = self.m_textWidth
                nCount += num
        else:
            for i in range(nCount + 1):
                value = src.split("\n")[i]
                nMaxWidth = fm.width(value) if fm.width(value) > nMaxWidth else nMaxWidth
                if nMaxWidth > self.m_textWidth:
                    num = math.ceil(nMaxWidth / self.m_textWidth)
                    nMaxWidth = self.m_textWidth
                    nCount += num
            if src[-1] != "\n":
                nCount = nCount + 1
        return QSize(nMaxWidth + self.m_spaceWid, ((nCount + 2) * self.m_lineHeight))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(Qt.gray))

        if self.m_userType == self.User_Type.User_She:
            painter.drawPixmap(self.m_iconLeftRect, self.m_leftPixmap)
            col_KuangB = QColor(234, 234, 234)
            painter.setBrush(QBrush(col_KuangB))
            painter.drawRoundedRect(self.m_kuangLeftRect.x() - 1, self.m_kuangLeftRect.y() - 1,
                                    self.m_kuangLeftRect.width() + 2, self.m_kuangLeftRect.height() + 2, 4, 4)
            col_Kuang = QColor(255, 255, 255)
            painter.setBrush(QBrush(col_Kuang))
            painter.drawRoundedRect(self.m_kuangLeftRect, 4, 4)
            # 三角
            points = [QPointF(self.m_sanjiaoLeftRect.x(), self.m_sanjiaoLeftRect.y()),
                      QPointF(self.m_sanjiaoLeftRect.x() + self.m_sanjiaoLeftRect.width(), self.m_sanjiaoLeftRect.y()),
                      QPointF(self.m_sanjiaoLeftRect.x() + self.m_sanjiaoLeftRect.width(),
                              self.m_sanjiaoLeftRect.y() + 10)]
            pen = QPen()
            pen.setColor(col_Kuang)
            painter.setPen(pen)
            painter.drawPolygon(points[0], points[1], points[2])
            # 三角加边
            penSanJiaoBian = QPen()
            penSanJiaoBian.setColor(col_KuangB)
            painter.setPen(penSanJiaoBian)
            painter.drawLine(QPointF(self.m_sanjiaoLeftRect.x() - 1, self.m_sanjiaoLeftRect.y()),
                             QPointF(self.m_sanjiaoLeftRect.x() + self.m_sanjiaoLeftRect.width(),
                                     self.m_sanjiaoLeftRect.y()))
            painter.drawLine(QPointF(self.m_sanjiaoLeftRect.x() - 1, self.m_sanjiaoLeftRect.y()),
                             QPointF(self.m_sanjiaoLeftRect.x() + self.m_sanjiaoLeftRect.width(),
                                     self.m_sanjiaoLeftRect.y() + 11))
            # 名称框内容
            penText = QPen()
            penText.setColor(QColor(153, 153, 153))
            painter.setPen(penText)
            option = QTextOption(Qt.AlignLeft)
            option.setWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
            painter.setFont(self.font())
            painter.drawText(self.m_nameLeftRect, self.usrname, option)
            # 内容
            penText = QPen()
            penText.setColor(QColor(51, 51, 51))
            painter.setPen(penText)
            option = QTextOption(Qt.AlignLeft)
            option.setWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
            painter.setFont(self.font())
            painter.drawText(self.m_textLeftRect, self.m_msg, option)
        # 自己
        if self.m_userType == self.User_Type.User_Me:
            # 头像
            painter.drawPixmap(self.m_iconRightRect, self.m_rightPixmap)
            # 框
            col_Kuang = QColor(75, 164, 242)
            painter.setBrush(QBrush(col_Kuang))
            painter.drawRoundedRect(self.m_kuangRightRect, 4, 4)

            # 三角
            points = [
                QPointF(self.m_sanjiaoRightRect.x() + self.m_sanjiaoRightRect.width() + 5, self.m_sanjiaoRightRect.y()),
                QPointF(self.m_sanjiaoRightRect.x(), self.m_sanjiaoRightRect.y()),
                QPointF(self.m_sanjiaoRightRect.x(), self.m_sanjiaoRightRect.y()+11),
            ]

            pen = QPen()
            pen.setColor(col_Kuang)
            painter.setPen(pen)
            painter.drawPolygon(points[0], points[1], points[2])

            # 名称框内容
            penText = QPen()
            penText.setColor(QColor(153, 153, 153))
            painter.setPen(penText)
            option = QTextOption(Qt.AlignLeft)
            option.setWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
            painter.setFont(self.font())
            painter.drawText(self.m_nameRightRect, self.usrname, option)

            # 内容
            penText = QPen()
            penText.setColor(QColor(255, 255, 255))
            painter.setPen(penText)
            option = QTextOption(Qt.AlignLeft)
            option.setWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
            painter.setFont(self.font())
            painter.drawText(self.m_textRightRect, self.m_msg, option)
        if self.m_userType == self.User_Type.User_Time:
            penText = QPen()
            penText.setColor(QColor(153, 153, 153))
            painter.setPen(penText)
            option = QTextOption(Qt.AlignCenter)
            option.setWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
            te_font = self.font()
            te_font.setFamily("Arial")
            te_font.setPointSize(10)
            painter.setFont(te_font)
            rect = self.rect()
            rect.setRect(rect.x(), rect.y(), 441, rect.height())

            painter.drawText(rect, Qt.AlignCenter, self.m_curTime)
