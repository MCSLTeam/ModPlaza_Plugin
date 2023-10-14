from PyQt5.QtWidgets import QVBoxLayout, QWidget, QStackedWidget
from qfluentwidgets import SegmentedWidget


class ModDetailPageBody(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.pivot = SegmentedWidget(self)
        self.stackedWidget = QStackedWidget(self)
        self.stackedWidget.addWidget(QWidget(self))
        self.vBoxLayout = QVBoxLayout(self)

        self.vBoxLayout.addWidget(self.pivot)
        self.vBoxLayout.addWidget(self.stackedWidget)
        self.vBoxLayout.setContentsMargins(30, 10, 30, 30)

        self.stackedWidget.currentChanged.connect(self.onCurrentIndexChanged)

    def addSubInterface(self, widget: QWidget, objectName, text):
        widget.setObjectName(objectName)
        self.stackedWidget.addWidget(widget)
        self.pivot.addItem(
            routeKey=objectName,
            text=text,
            onClick=lambda: self.stackedWidget.setCurrentWidget(widget),
        )

    def onCurrentIndexChanged(self, index):
        widget = self.stackedWidget.widget(index)
        self.pivot.setCurrentItem(widget.objectName())

    def prepareDeleteLater(self) -> None:
        self.stackedWidget.setCurrentIndex(0)
        for widget in self.stackedWidget.children():
            widget.deleteLater()
