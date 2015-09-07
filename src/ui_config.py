# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'config.ui'
#
# Created by: PyQt5 UI code generator 5.5
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_AccountSettingDialog(object):
    def setupUi(self, AccountSettingDialog):
        AccountSettingDialog.setObjectName("AccountSettingDialog")
        AccountSettingDialog.resize(223, 118)
        self.verticalLayout = QtWidgets.QVBoxLayout(AccountSettingDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(AccountSettingDialog)
        self.label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.username = QtWidgets.QLineEdit(AccountSettingDialog)
        self.username.setMinimumSize(QtCore.QSize(150, 0))
        self.username.setObjectName("username")
        self.gridLayout.addWidget(self.username, 0, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(AccountSettingDialog)
        self.label_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.password = QtWidgets.QLineEdit(AccountSettingDialog)
        self.password.setMinimumSize(QtCore.QSize(150, 0))
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password.setObjectName("password")
        self.gridLayout.addWidget(self.password, 1, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(AccountSettingDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(AccountSettingDialog)
        self.buttonBox.accepted.connect(AccountSettingDialog.accept)
        self.buttonBox.rejected.connect(AccountSettingDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(AccountSettingDialog)

    def retranslateUi(self, AccountSettingDialog):
        _translate = QtCore.QCoreApplication.translate
        AccountSettingDialog.setWindowTitle(_translate("AccountSettingDialog", "账号设置"))
        self.label.setText(_translate("AccountSettingDialog", "用户名"))
        self.label_2.setText(_translate("AccountSettingDialog", "密码"))

