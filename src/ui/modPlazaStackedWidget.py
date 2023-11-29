from typing import List

from PyQt5.QtCore import QPropertyAnimation
from PyQt5.QtWidgets import QStackedWidget, QWidget, QGraphicsOpacityEffect


class ModPlazaStackedWidget(QStackedWidget):
    """ Stacked widget with fade in and fade out animation """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.__nextIndex = 0
        self.__effects = []  # type:List[QPropertyAnimation]
        self.__anis = []  # type:List[QPropertyAnimation]

    def addWidget(self, w: QWidget):
        super().addWidget(w)

        effect = QGraphicsOpacityEffect(w)
        effect.setOpacity(1)
        ani = QPropertyAnimation(effect, b'opacity', w)
        ani.setDuration(170)
        ani.finished.connect(self.__onFadeAniFinished)
        self.__anis.append(ani)
        self.__effects.append(effect)
        w.setGraphicsEffect(effect)

    def setCurrentIndex(self, index: int):
        index_ = self.currentIndex()
        if index == index_:
            return
        ani = self.__anis[index_]
        ani.setStartValue(1)
        ani.setEndValue(0)

        self.__nextIndex = index
        ani.start()

    def removeWidget(self, w: QWidget) -> None:
        index = self.indexOf(w)
        if index == -1:
            return
        self.__effects.pop(index)
        self.__anis.pop(index)
        super().removeWidget(w)

    def removeWidgetByIndex(self, index: int) -> None:
        w = self.widget(index)
        w.deleteLater()
        self.removeWidget(w)

    def setCurrentWidget(self, w: QWidget):
        self.setCurrentIndex(self.indexOf(w))

    def __onAniFinished(self):
        super().setCurrentIndex(self.__nextIndex)

    def __onFadeAniFinished(self):
        if self.currentIndex() == self.__nextIndex:
            return self.__onAniFinished()  # 第二段动画结束

        ani = self.__anis[self.__nextIndex]
        ani.setStartValue(0)
        ani.setEndValue(1)
        super().setCurrentIndex(self.__nextIndex)
        ani.start()
