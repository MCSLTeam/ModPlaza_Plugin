from PyQt5.QtCore import Qt, QRect, QSize
from PyQt5.QtWidgets import QSizePolicy
from qfluentwidgets import BodyLabel


class ModTagExample(BodyLabel):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.setGeometry(QRect(20, 10, 51, 20))
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setMinimumSize(QSize(0, 20))
        self.setMaximumSize(QSize(16777215, 20))
        self.setStyleSheet(
            "BodyLabel {\n"
            "    background-color: rgba(199, 199, 199, 50%);\n"
            "    border-radius: 4px;\n"
            "    padding-left: 3px solid rgba(223, 239, 232, 80%);\n"
            "    padding-right: 3px solid rgba(223, 239, 232, 80%);\n"
            "}"
        )
        self.setAlignment(Qt.AlignCenter)
        self.setObjectName("tagExample")
