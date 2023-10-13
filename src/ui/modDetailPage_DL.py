# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\modDetailPage_DL.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets
from qfluentwidgets import BodyLabel, ComboBox, StrongBodyLabel, SwitchButton, TableView, TransparentPushButton


class ModDetailPage_DL(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.ui.retranslateUi(self)

    def onModFilesGot(self):
        # adjust table view
        self.ui.TableView.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

        self.ui.TableView.verticalHeader().setVisible(False)
        self.ui.TableView.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.ui.TableView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.ui.TableView.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.ui.TableView.setAlternatingRowColors(True)
        self.ui.TableView.setShowGrid(False)
        self.ui.TableView.setWordWrap(False)
        self.ui.TableView.setCornerButtonEnabled(False)


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(567, 386)
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.BodyLabel = BodyLabel(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.BodyLabel.sizePolicy().hasHeightForWidth())
        self.BodyLabel.setSizePolicy(sizePolicy)
        self.BodyLabel.setProperty("pixelFontSize", 16)
        self.BodyLabel.setObjectName("BodyLabel")
        self.horizontalLayout.addWidget(self.BodyLabel)
        self.ComboBox = ComboBox(Form)
        self.ComboBox.setObjectName("ComboBox")
        self.horizontalLayout.addWidget(self.ComboBox)
        self.ComboBox_2 = ComboBox(Form)
        self.ComboBox_2.setObjectName("ComboBox_2")
        self.horizontalLayout.addWidget(self.ComboBox_2)
        self.SwitchButton = SwitchButton(Form)
        self.SwitchButton.setObjectName("SwitchButton")
        self.horizontalLayout.addWidget(self.SwitchButton)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.TransparentPushButton = TransparentPushButton(Form)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(11)
        font.setBold(False)
        font.setUnderline(True)
        font.setWeight(50)
        self.TransparentPushButton.setFont(font)
        self.TransparentPushButton.setObjectName("TransparentPushButton")
        self.horizontalLayout.addWidget(self.TransparentPushButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.StrongBodyLabel = StrongBodyLabel(Form)
        self.StrongBodyLabel.setObjectName("StrongBodyLabel")
        self.horizontalLayout_2.addWidget(self.StrongBodyLabel)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.BodyLabel_2 = BodyLabel(Form)
        self.BodyLabel_2.setObjectName("BodyLabel_2")
        self.horizontalLayout_2.addWidget(self.BodyLabel_2)
        self.ComboBox_3 = ComboBox(Form)
        self.ComboBox_3.setObjectName("ComboBox_3")
        self.horizontalLayout_2.addWidget(self.ComboBox_3)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.TableView = TableView(Form)
        self.TableView.setShowGrid(False)
        self.TableView.setObjectName("TableView")
        self.verticalLayout.addWidget(self.TableView)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.BodyLabel.setText(_translate("Form", "筛选"))
        self.SwitchButton.setText(_translate("Form", "显示alpha版本"))
        self.SwitchButton.setOnText(_translate("Form", "显示alpha版本"))
        self.SwitchButton.setOffText(_translate("Form", "显示alpha版本"))
        self.TransparentPushButton.setText(_translate("Form", "清除筛选条件"))
        self.StrongBodyLabel.setText(_translate("Form", "<class: Pagenation>"))
        self.BodyLabel_2.setText(_translate("Form", "每页显示"))
