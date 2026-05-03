# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'statistics.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QLabel,
    QSizePolicy, QVBoxLayout, QWidget)

class Ui_StatisticsComponent(object):
    def setupUi(self, StatisticsComponent):
        if not StatisticsComponent.objectName():
            StatisticsComponent.setObjectName(u"StatisticsComponent")
        StatisticsComponent.resize(141, 116)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(StatisticsComponent.sizePolicy().hasHeightForWidth())
        StatisticsComponent.setSizePolicy(sizePolicy)
        self.verticalLayout = QVBoxLayout(StatisticsComponent)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.w_label = QLabel(StatisticsComponent)
        self.w_label.setObjectName(u"w_label")
        font = QFont()
        font.setBold(True)
        self.w_label.setFont(font)

        self.verticalLayout.addWidget(self.w_label)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.label_2 = QLabel(StatisticsComponent)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)

        self.w_vertices_label = QLabel(StatisticsComponent)
        self.w_vertices_label.setObjectName(u"w_vertices_label")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.w_vertices_label.sizePolicy().hasHeightForWidth())
        self.w_vertices_label.setSizePolicy(sizePolicy1)

        self.gridLayout.addWidget(self.w_vertices_label, 0, 1, 1, 1)

        self.label_3 = QLabel(StatisticsComponent)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)

        self.w_edges_label = QLabel(StatisticsComponent)
        self.w_edges_label.setObjectName(u"w_edges_label")

        self.gridLayout.addWidget(self.w_edges_label, 1, 1, 1, 1)

        self.label_4 = QLabel(StatisticsComponent)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout.addWidget(self.label_4, 2, 0, 1, 1)

        self.w_min_max_label = QLabel(StatisticsComponent)
        self.w_min_max_label.setObjectName(u"w_min_max_label")

        self.gridLayout.addWidget(self.w_min_max_label, 2, 1, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout)


        self.retranslateUi(StatisticsComponent)

        QMetaObject.connectSlotsByName(StatisticsComponent)
    # setupUi

    def retranslateUi(self, StatisticsComponent):
        StatisticsComponent.setWindowTitle(QCoreApplication.translate("StatisticsComponent", u"Frame", None))
        self.w_label.setText(QCoreApplication.translate("StatisticsComponent", u"Statistics", None))
        self.label_2.setText(QCoreApplication.translate("StatisticsComponent", u"Vertices:", None))
        self.w_vertices_label.setText(QCoreApplication.translate("StatisticsComponent", u"999/999", None))
        self.label_3.setText(QCoreApplication.translate("StatisticsComponent", u"Edges:", None))
        self.w_edges_label.setText(QCoreApplication.translate("StatisticsComponent", u"999/999", None))
        self.label_4.setText(QCoreApplication.translate("StatisticsComponent", u"Min/Max:", None))
        self.w_min_max_label.setText(QCoreApplication.translate("StatisticsComponent", u"999/999", None))
    # retranslateUi

