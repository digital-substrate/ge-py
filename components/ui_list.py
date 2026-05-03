# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'list.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QFrame, QLabel,
    QListWidget, QListWidgetItem, QSizePolicy, QVBoxLayout,
    QWidget)

class Ui_ListComponent(object):
    def setupUi(self, ListComponent):
        if not ListComponent.objectName():
            ListComponent.setObjectName(u"ListComponent")
        ListComponent.resize(239, 300)
        self.verticalLayout = QVBoxLayout(ListComponent)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.w_label = QLabel(ListComponent)
        self.w_label.setObjectName(u"w_label")
        font = QFont()
        font.setBold(True)
        self.w_label.setFont(font)

        self.verticalLayout.addWidget(self.w_label)

        self.w_list_widget = QListWidget(ListComponent)
        self.w_list_widget.setObjectName(u"w_list_widget")
        self.w_list_widget.setAlternatingRowColors(True)
        self.w_list_widget.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

        self.verticalLayout.addWidget(self.w_list_widget)


        self.retranslateUi(ListComponent)

        QMetaObject.connectSlotsByName(ListComponent)
    # setupUi

    def retranslateUi(self, ListComponent):
        ListComponent.setWindowTitle(QCoreApplication.translate("ListComponent", u"Frame", None))
        self.w_label.setText(QCoreApplication.translate("ListComponent", u"Elements", None))
    # retranslateUi

