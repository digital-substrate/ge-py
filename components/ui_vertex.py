# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'vertex.ui'
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
    QLineEdit, QSizePolicy, QSlider, QToolButton,
    QWidget)

class Ui_VertexComponent(object):
    def setupUi(self, VertexComponent):
        if not VertexComponent.objectName():
            VertexComponent.setObjectName(u"VertexComponent")
        VertexComponent.resize(213, 177)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(VertexComponent.sizePolicy().hasHeightForWidth())
        VertexComponent.setSizePolicy(sizePolicy)
        self.gridLayout = QGridLayout(VertexComponent)
        self.gridLayout.setObjectName(u"gridLayout")
        self.label = QLabel(VertexComponent)
        self.label.setObjectName(u"label")
        font = QFont()
        font.setBold(True)
        self.label.setFont(font)

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.label_2 = QLabel(VertexComponent)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)

        self.w_value_line_edit = QLineEdit(VertexComponent)
        self.w_value_line_edit.setObjectName(u"w_value_line_edit")
        self.w_value_line_edit.setMaximumSize(QSize(50, 16777215))

        self.gridLayout.addWidget(self.w_value_line_edit, 1, 1, 1, 1)

        self.label_3 = QLabel(VertexComponent)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)

        self.w_color_button = QToolButton(VertexComponent)
        self.w_color_button.setObjectName(u"w_color_button")

        self.gridLayout.addWidget(self.w_color_button, 2, 1, 1, 1)

        self.label_4 = QLabel(VertexComponent)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout.addWidget(self.label_4, 3, 0, 1, 1)

        self.w_x_line_edit = QLineEdit(VertexComponent)
        self.w_x_line_edit.setObjectName(u"w_x_line_edit")
        self.w_x_line_edit.setMaximumSize(QSize(50, 16777215))

        self.gridLayout.addWidget(self.w_x_line_edit, 3, 1, 1, 1)

        self.w_x_slider = QSlider(VertexComponent)
        self.w_x_slider.setObjectName(u"w_x_slider")
        self.w_x_slider.setMaximum(1000)
        self.w_x_slider.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout.addWidget(self.w_x_slider, 3, 2, 1, 1)

        self.label_5 = QLabel(VertexComponent)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout.addWidget(self.label_5, 4, 0, 1, 1)

        self.w_y_line_edit = QLineEdit(VertexComponent)
        self.w_y_line_edit.setObjectName(u"w_y_line_edit")
        self.w_y_line_edit.setMaximumSize(QSize(50, 16777215))

        self.gridLayout.addWidget(self.w_y_line_edit, 4, 1, 1, 1)

        self.w_y_slider = QSlider(VertexComponent)
        self.w_y_slider.setObjectName(u"w_y_slider")
        self.w_y_slider.setMaximum(1000)
        self.w_y_slider.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout.addWidget(self.w_y_slider, 4, 2, 1, 1)


        self.retranslateUi(VertexComponent)

        QMetaObject.connectSlotsByName(VertexComponent)
    # setupUi

    def retranslateUi(self, VertexComponent):
        VertexComponent.setWindowTitle(QCoreApplication.translate("VertexComponent", u"Frame", None))
        self.label.setText(QCoreApplication.translate("VertexComponent", u"Vertex", None))
        self.label_2.setText(QCoreApplication.translate("VertexComponent", u"Value:", None))
        self.w_value_line_edit.setText(QCoreApplication.translate("VertexComponent", u"1000", None))
        self.label_3.setText(QCoreApplication.translate("VertexComponent", u"Color:", None))
        self.w_color_button.setText(QCoreApplication.translate("VertexComponent", u"...", None))
        self.label_4.setText(QCoreApplication.translate("VertexComponent", u"X:", None))
        self.label_5.setText(QCoreApplication.translate("VertexComponent", u"Y:", None))
        self.w_y_line_edit.setText(QCoreApplication.translate("VertexComponent", u"1000", None))
    # retranslateUi

