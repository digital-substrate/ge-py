# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'select_graph_dialog.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QHBoxLayout, QLabel,
    QListWidget, QListWidgetItem, QPushButton, QSizePolicy,
    QSpacerItem, QVBoxLayout, QWidget)

class Ui_SelectGraphDialog(object):
    def setupUi(self, SelectGraphDialog):
        if not SelectGraphDialog.objectName():
            SelectGraphDialog.setObjectName(u"SelectGraphDialog")
        SelectGraphDialog.resize(280, 183)
        self.verticalLayout = QVBoxLayout(SelectGraphDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.w_label = QLabel(SelectGraphDialog)
        self.w_label.setObjectName(u"w_label")
        font = QFont()
        font.setBold(True)
        self.w_label.setFont(font)

        self.horizontalLayout.addWidget(self.w_label)

        self.w_count_label = QLabel(SelectGraphDialog)
        self.w_count_label.setObjectName(u"w_count_label")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.w_count_label.sizePolicy().hasHeightForWidth())
        self.w_count_label.setSizePolicy(sizePolicy)

        self.horizontalLayout.addWidget(self.w_count_label)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.w_list_widget = QListWidget(SelectGraphDialog)
        self.w_list_widget.setObjectName(u"w_list_widget")

        self.verticalLayout.addWidget(self.w_list_widget)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.w_cancel_button = QPushButton(SelectGraphDialog)
        self.w_cancel_button.setObjectName(u"w_cancel_button")

        self.horizontalLayout_2.addWidget(self.w_cancel_button)

        self.w_select_button = QPushButton(SelectGraphDialog)
        self.w_select_button.setObjectName(u"w_select_button")

        self.horizontalLayout_2.addWidget(self.w_select_button)


        self.verticalLayout.addLayout(self.horizontalLayout_2)


        self.retranslateUi(SelectGraphDialog)

        QMetaObject.connectSlotsByName(SelectGraphDialog)
    # setupUi

    def retranslateUi(self, SelectGraphDialog):
        SelectGraphDialog.setWindowTitle(QCoreApplication.translate("SelectGraphDialog", u"Dialog", None))
        self.w_label.setText(QCoreApplication.translate("SelectGraphDialog", u"Graphs", None))
        self.w_count_label.setText(QCoreApplication.translate("SelectGraphDialog", u"0", None))
        self.w_cancel_button.setText(QCoreApplication.translate("SelectGraphDialog", u"Cancel", None))
        self.w_select_button.setText(QCoreApplication.translate("SelectGraphDialog", u"Select", None))
    # retranslateUi

