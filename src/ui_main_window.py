# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'dictionary.ui'
##
## Created by: Qt User Interface Compiler version 6.6.3
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QFrame, QGridLayout,
    QHBoxLayout, QLineEdit, QListWidget, QListWidgetItem,
    QPushButton, QSizePolicy, QSpacerItem, QVBoxLayout,
    QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(356, 374)
        Form.setStyleSheet(u"")
        self.gridLayout = QGridLayout(Form)
        self.gridLayout.setObjectName(u"gridLayout")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.content_frm = QFrame(Form)
        self.content_frm.setObjectName(u"content_frm")
        self.content_frm.setFrameShape(QFrame.StyledPanel)
        self.content_frm.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.content_frm)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.search_frm = QFrame(self.content_frm)
        self.search_frm.setObjectName(u"search_frm")
        self.horizontalLayout = QHBoxLayout(self.search_frm)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.search_item = QLineEdit(self.search_frm)
        self.search_item.setObjectName(u"search_item")
        font = QFont()
        font.setPointSize(10)
        self.search_item.setFont(font)
        self.search_item.setStyleSheet(u"")
        self.search_item.setClearButtonEnabled(True)

        self.horizontalLayout.addWidget(self.search_item)

        self.search_item_btn = QPushButton(self.search_frm)
        self.search_item_btn.setObjectName(u"search_item_btn")
        self.search_item_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.search_item_btn.setIconSize(QSize(32, 32))

        self.horizontalLayout.addWidget(self.search_item_btn)


        self.horizontalLayout_2.addWidget(self.search_frm)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)


        self.verticalLayout.addWidget(self.content_frm)

        self.listWidget = QListWidget(Form)
        self.listWidget.setObjectName(u"listWidget")
        self.listWidget.setFont(font)
        self.listWidget.setStyleSheet(u"")
        self.listWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.listWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.listWidget.setAutoScroll(False)
        self.listWidget.setAutoScrollMargin(1)
        self.listWidget.setAlternatingRowColors(True)
        self.listWidget.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.listWidget.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.listWidget.setWordWrap(True)

        self.verticalLayout.addWidget(self.listWidget)


        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Dictionary", None))
#if QT_CONFIG(tooltip)
        self.search_item.setToolTip(QCoreApplication.translate("Form", u"Search word", None))
#endif // QT_CONFIG(tooltip)
        self.search_item.setPlaceholderText(QCoreApplication.translate("Form", u"Search...", None))
#if QT_CONFIG(tooltip)
        self.search_item_btn.setToolTip(QCoreApplication.translate("Form", u"Search", None))
#endif // QT_CONFIG(tooltip)
        self.search_item_btn.setText("")
#if QT_CONFIG(shortcut)
        self.search_item_btn.setShortcut(QCoreApplication.translate("Form", u"Enter", None))
#endif // QT_CONFIG(shortcut)
#if QT_CONFIG(tooltip)
        self.listWidget.setToolTip(QCoreApplication.translate("Form", u"List of definations", None))
#endif // QT_CONFIG(tooltip)
    # retranslateUi

