# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'e:\MCSLCode\MCSL2\Plugins\ModPlaza_Plugin\ui_src\singleModWidget.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_singleModWidget(object):
    def setupUi(self, self):
        self.setObjectName("singleModWidget")
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setMinimumSize(QtCore.QSize(655, 0))
        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")
        self.infoWidget = QtWidgets.QWidget(self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.infoWidget.sizePolicy().hasHeightForWidth())
        self.infoWidget.setSizePolicy(sizePolicy)
        self.infoWidget.setMinimumSize(QtCore.QSize(0, 105))
        self.infoWidget.setMaximumSize(QtCore.QSize(16777215, 105))
        self.infoWidget.setObjectName("infoWidget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.infoWidget)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.modName = StrongBodyLabel(self.infoWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.modName.sizePolicy().hasHeightForWidth())
        self.modName.setSizePolicy(sizePolicy)
        self.modName.setObjectName("modName")
        self.gridLayout_2.addWidget(self.modName, 0, 0, 1, 2)
        self.tagLayout = QtWidgets.QHBoxLayout()
        self.tagLayout.setObjectName("tagLayout")
        self.gridLayout_2.addLayout(self.tagLayout, 2, 0, 1, 1)
        self.modDescription = BodyLabel(self.infoWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.modDescription.sizePolicy().hasHeightForWidth())
        self.modDescription.setSizePolicy(sizePolicy)
        self.modDescription.setObjectName("modDescription")
        self.gridLayout_2.addWidget(self.modDescription, 2, 1, 1, 1)
        self.extraInfoLayout = QtWidgets.QHBoxLayout()
        self.extraInfoLayout.setObjectName("extraInfoLayout")
        self.versionWidget = QtWidgets.QWidget(self.infoWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.versionWidget.sizePolicy().hasHeightForWidth())
        self.versionWidget.setSizePolicy(sizePolicy)
        self.versionWidget.setObjectName("versionWidget")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.versionWidget)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.versionTag = BodyLabel(self.versionWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.versionTag.sizePolicy().hasHeightForWidth())
        self.versionTag.setSizePolicy(sizePolicy)
        self.versionTag.setMinimumSize(QtCore.QSize(0, 20))
        self.versionTag.setMaximumSize(QtCore.QSize(16777215, 20))
        self.versionTag.setStyleSheet("BodyLabel {\n"
"    background-color: rgba(199, 199, 199, 50%);\n"
"    border-radius: 4px;\n"
"    padding-left: 3px solid rgba(223, 239, 232, 80%);\n"
"    padding-right: 3px solid rgba(223, 239, 232, 80%);\n"
"}")
        self.versionTag.setAlignment(QtCore.Qt.AlignCenter)
        self.versionTag.setObjectName("versionTag")
        self.horizontalLayout_2.addWidget(self.versionTag)
        self.version = CaptionLabel(self.versionWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.version.sizePolicy().hasHeightForWidth())
        self.version.setSizePolicy(sizePolicy)
        self.version.setObjectName("version")
        self.horizontalLayout_2.addWidget(self.version)
        self.extraInfoLayout.addWidget(self.versionWidget)
        self.downloadWidget = QtWidgets.QWidget(self.infoWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.downloadWidget.sizePolicy().hasHeightForWidth())
        self.downloadWidget.setSizePolicy(sizePolicy)
        self.downloadWidget.setObjectName("downloadWidget")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.downloadWidget)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.downloadTag = BodyLabel(self.downloadWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.downloadTag.sizePolicy().hasHeightForWidth())
        self.downloadTag.setSizePolicy(sizePolicy)
        self.downloadTag.setMinimumSize(QtCore.QSize(0, 20))
        self.downloadTag.setMaximumSize(QtCore.QSize(16777215, 20))
        self.downloadTag.setStyleSheet("BodyLabel {\n"
"    background-color: rgba(199, 199, 199, 50%);\n"
"    border-radius: 4px;\n"
"    padding-left: 3px solid rgba(223, 239, 232, 80%);\n"
"    padding-right: 3px solid rgba(223, 239, 232, 80%);\n"
"}")
        self.downloadTag.setAlignment(QtCore.Qt.AlignCenter)
        self.downloadTag.setObjectName("downloadTag")
        self.horizontalLayout_3.addWidget(self.downloadTag)
        self.download = CaptionLabel(self.downloadWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.download.sizePolicy().hasHeightForWidth())
        self.download.setSizePolicy(sizePolicy)
        self.download.setObjectName("download")
        self.horizontalLayout_3.addWidget(self.download)
        self.extraInfoLayout.addWidget(self.downloadWidget)
        self.lastUpdateWidget = QtWidgets.QWidget(self.infoWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lastUpdateWidget.sizePolicy().hasHeightForWidth())
        self.lastUpdateWidget.setSizePolicy(sizePolicy)
        self.lastUpdateWidget.setObjectName("lastUpdateWidget")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.lastUpdateWidget)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.lastUpdateTag = BodyLabel(self.lastUpdateWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lastUpdateTag.sizePolicy().hasHeightForWidth())
        self.lastUpdateTag.setSizePolicy(sizePolicy)
        self.lastUpdateTag.setMinimumSize(QtCore.QSize(0, 20))
        self.lastUpdateTag.setMaximumSize(QtCore.QSize(16777215, 20))
        self.lastUpdateTag.setStyleSheet("BodyLabel {\n"
"    background-color: rgba(199, 199, 199, 50%);\n"
"    border-radius: 4px;\n"
"    padding-left: 3px solid rgba(223, 239, 232, 80%);\n"
"    padding-right: 3px solid rgba(223, 239, 232, 80%);\n"
"}")
        self.lastUpdateTag.setAlignment(QtCore.Qt.AlignCenter)
        self.lastUpdateTag.setObjectName("lastUpdateTag")
        self.horizontalLayout_4.addWidget(self.lastUpdateTag)
        self.lastUpdate = CaptionLabel(self.lastUpdateWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lastUpdate.sizePolicy().hasHeightForWidth())
        self.lastUpdate.setSizePolicy(sizePolicy)
        self.lastUpdate.setObjectName("lastUpdate")
        self.horizontalLayout_4.addWidget(self.lastUpdate)
        self.extraInfoLayout.addWidget(self.lastUpdateWidget)
        self.modSrcWidget = QtWidgets.QWidget(self.infoWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.modSrcWidget.sizePolicy().hasHeightForWidth())
        self.modSrcWidget.setSizePolicy(sizePolicy)
        self.modSrcWidget.setObjectName("modSrcWidget")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.modSrcWidget)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.modSrcTag = BodyLabel(self.modSrcWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.modSrcTag.sizePolicy().hasHeightForWidth())
        self.modSrcTag.setSizePolicy(sizePolicy)
        self.modSrcTag.setMinimumSize(QtCore.QSize(0, 20))
        self.modSrcTag.setMaximumSize(QtCore.QSize(16777215, 20))
        self.modSrcTag.setStyleSheet("BodyLabel {\n"
"    background-color: rgba(199, 199, 199, 50%);\n"
"    border-radius: 4px;\n"
"    padding-left: 3px solid rgba(223, 239, 232, 80%);\n"
"    padding-right: 3px solid rgba(223, 239, 232, 80%);\n"
"}")
        self.modSrcTag.setAlignment(QtCore.Qt.AlignCenter)
        self.modSrcTag.setObjectName("modSrcTag")
        self.horizontalLayout_5.addWidget(self.modSrcTag)
        self.modSrc = CaptionLabel(self.modSrcWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.modSrc.sizePolicy().hasHeightForWidth())
        self.modSrc.setSizePolicy(sizePolicy)
        self.modSrc.setObjectName("modSrc")
        self.horizontalLayout_5.addWidget(self.modSrc)
        self.extraInfoLayout.addWidget(self.modSrcWidget)
        self.gridLayout_2.addLayout(self.extraInfoLayout, 3, 0, 1, 2)
        self.gridLayout.addWidget(self.infoWidget, 0, 2, 1, 1)
        self.PixmapLabel = PixmapLabel(self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.PixmapLabel.sizePolicy().hasHeightForWidth())
        self.PixmapLabel.setSizePolicy(sizePolicy)
        self.PixmapLabel.setMinimumSize(QtCore.QSize(64, 64))
        self.PixmapLabel.setMaximumSize(QtCore.QSize(64, 64))
        self.PixmapLabel.setObjectName("PixmapLabel")
        self.gridLayout.addWidget(self.PixmapLabel, 0, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(10, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 0, 1, 1)

        self.retranslateUi(self)
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self, singleModWidget):
        _translate = QtCore.QCoreApplication.translate
        self.modName.setText(_translate("singleModWidget", "[模组名称]"))
        self.modDescription.setText(_translate("singleModWidget", "[模组介绍]"))
        self.versionTag.setText(_translate("singleModWidget", "版本"))
        self.version.setText(_translate("singleModWidget", "[版本]"))
        self.downloadTag.setText(_translate("singleModWidget", "下载"))
        self.download.setText(_translate("singleModWidget", "[下载量]"))
        self.lastUpdateTag.setText(_translate("singleModWidget", "最近更新"))
        self.lastUpdate.setText(_translate("singleModWidget", "[最近更新]"))
        self.modSrcTag.setText(_translate("singleModWidget", "来源"))
        self.modSrc.setText(_translate("singleModWidget", "[来源]"))
from qfluentwidgets import BodyLabel, CaptionLabel, ElevatedCardWidget, PixmapLabel, StrongBodyLabel
