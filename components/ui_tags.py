# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'tags.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QFrame, QHBoxLayout,
    QHeaderView, QLabel, QLineEdit, QSizePolicy,
    QSpacerItem, QToolButton, QTreeWidget, QTreeWidgetItem,
    QVBoxLayout, QWidget)

class Ui_TagsComponent(object):
    def setupUi(self, TagsComponent):
        if not TagsComponent.objectName():
            TagsComponent.setObjectName(u"TagsComponent")
        TagsComponent.resize(286, 307)
        self.verticalLayout = QVBoxLayout(TagsComponent)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.w_label = QLabel(TagsComponent)
        self.w_label.setObjectName(u"w_label")
        font = QFont()
        font.setBold(True)
        self.w_label.setFont(font)

        self.verticalLayout.addWidget(self.w_label)

        self.w_tree_widget = QTreeWidget(TagsComponent)
        self.w_tree_widget.setObjectName(u"w_tree_widget")
        self.w_tree_widget.setAlternatingRowColors(True)
        self.w_tree_widget.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

        self.verticalLayout.addWidget(self.w_tree_widget)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.w_key_line_edit = QLineEdit(TagsComponent)
        self.w_key_line_edit.setObjectName(u"w_key_line_edit")

        self.horizontalLayout_2.addWidget(self.w_key_line_edit)

        self.w_value_line_edit = QLineEdit(TagsComponent)
        self.w_value_line_edit.setObjectName(u"w_value_line_edit")

        self.horizontalLayout_2.addWidget(self.w_value_line_edit)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.w_set_button = QToolButton(TagsComponent)
        self.w_set_button.setObjectName(u"w_set_button")

        self.horizontalLayout.addWidget(self.w_set_button)

        self.w_update_button = QToolButton(TagsComponent)
        self.w_update_button.setObjectName(u"w_update_button")

        self.horizontalLayout.addWidget(self.w_update_button)

        self.w_unset_button = QToolButton(TagsComponent)
        self.w_unset_button.setObjectName(u"w_unset_button")

        self.horizontalLayout.addWidget(self.w_unset_button)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.retranslateUi(TagsComponent)

        QMetaObject.connectSlotsByName(TagsComponent)
    # setupUi

    def retranslateUi(self, TagsComponent):
        TagsComponent.setWindowTitle(QCoreApplication.translate("TagsComponent", u"Frame", None))
        self.w_label.setText(QCoreApplication.translate("TagsComponent", u"Tags", None))
        ___qtreewidgetitem = self.w_tree_widget.headerItem()
        ___qtreewidgetitem.setText(1, QCoreApplication.translate("TagsComponent", u"Value", None));
        ___qtreewidgetitem.setText(0, QCoreApplication.translate("TagsComponent", u"Key", None));
        self.w_set_button.setText(QCoreApplication.translate("TagsComponent", u"+", None))
        self.w_update_button.setText(QCoreApplication.translate("TagsComponent", u"=", None))
        self.w_unset_button.setText(QCoreApplication.translate("TagsComponent", u"-", None))
    # retranslateUi

