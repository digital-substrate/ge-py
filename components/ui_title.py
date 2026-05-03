# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'title.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QLabel, QLineEdit,
    QSizePolicy, QVBoxLayout, QWidget)

class Ui_TitleComponent(object):
    def setupUi(self, TitleComponent):
        if not TitleComponent.objectName():
            TitleComponent.setObjectName(u"TitleComponent")
        TitleComponent.resize(215, 69)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(TitleComponent.sizePolicy().hasHeightForWidth())
        TitleComponent.setSizePolicy(sizePolicy)
        self.verticalLayout = QVBoxLayout(TitleComponent)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.w_label = QLabel(TitleComponent)
        self.w_label.setObjectName(u"w_label")
        font = QFont()
        font.setBold(True)
        self.w_label.setFont(font)

        self.verticalLayout.addWidget(self.w_label)

        self.w_title_line_edit = QLineEdit(TitleComponent)
        self.w_title_line_edit.setObjectName(u"w_title_line_edit")

        self.verticalLayout.addWidget(self.w_title_line_edit)


        self.retranslateUi(TitleComponent)

        QMetaObject.connectSlotsByName(TitleComponent)
    # setupUi

    def retranslateUi(self, TitleComponent):
        TitleComponent.setWindowTitle(QCoreApplication.translate("TitleComponent", u"Frame", None))
        self.w_label.setText(QCoreApplication.translate("TitleComponent", u"Title", None))
    # retranslateUi

