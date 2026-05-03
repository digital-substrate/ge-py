# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'comments.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel,
    QLineEdit, QListWidget, QListWidgetItem, QSizePolicy,
    QToolButton, QVBoxLayout, QWidget)

class Ui_CommentsComponent(object):
    def setupUi(self, CommentsComponent):
        if not CommentsComponent.objectName():
            CommentsComponent.setObjectName(u"CommentsComponent")
        CommentsComponent.resize(280, 274)
        self.verticalLayout = QVBoxLayout(CommentsComponent)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.w_label = QLabel(CommentsComponent)
        self.w_label.setObjectName(u"w_label")
        font = QFont()
        font.setBold(True)
        self.w_label.setFont(font)

        self.verticalLayout.addWidget(self.w_label)

        self.w_list_widget = QListWidget(CommentsComponent)
        self.w_list_widget.setObjectName(u"w_list_widget")
        self.w_list_widget.setAlternatingRowColors(True)

        self.verticalLayout.addWidget(self.w_list_widget)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.w_element_line_edit = QLineEdit(CommentsComponent)
        self.w_element_line_edit.setObjectName(u"w_element_line_edit")

        self.horizontalLayout.addWidget(self.w_element_line_edit)

        self.w_add_button = QToolButton(CommentsComponent)
        self.w_add_button.setObjectName(u"w_add_button")

        self.horizontalLayout.addWidget(self.w_add_button)

        self.w_assign_button = QToolButton(CommentsComponent)
        self.w_assign_button.setObjectName(u"w_assign_button")

        self.horizontalLayout.addWidget(self.w_assign_button)

        self.w_remove_button = QToolButton(CommentsComponent)
        self.w_remove_button.setObjectName(u"w_remove_button")

        self.horizontalLayout.addWidget(self.w_remove_button)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.retranslateUi(CommentsComponent)

        QMetaObject.connectSlotsByName(CommentsComponent)
    # setupUi

    def retranslateUi(self, CommentsComponent):
        CommentsComponent.setWindowTitle(QCoreApplication.translate("CommentsComponent", u"Frame", None))
        self.w_label.setText(QCoreApplication.translate("CommentsComponent", u"Comments", None))
        self.w_add_button.setText(QCoreApplication.translate("CommentsComponent", u"+", None))
        self.w_assign_button.setText(QCoreApplication.translate("CommentsComponent", u"=", None))
        self.w_remove_button.setText(QCoreApplication.translate("CommentsComponent", u"-", None))
    # retranslateUi

