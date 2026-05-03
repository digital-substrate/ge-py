# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'render.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QSizePolicy, QWidget)

class Ui_RenderComponent(object):
    def setupUi(self, RenderComponent):
        if not RenderComponent.objectName():
            RenderComponent.setObjectName(u"RenderComponent")
        RenderComponent.resize(400, 300)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(RenderComponent.sizePolicy().hasHeightForWidth())
        RenderComponent.setSizePolicy(sizePolicy)

        self.retranslateUi(RenderComponent)

        QMetaObject.connectSlotsByName(RenderComponent)
    # setupUi

    def retranslateUi(self, RenderComponent):
        RenderComponent.setWindowTitle(QCoreApplication.translate("RenderComponent", u"Frame", None))
    # retranslateUi

