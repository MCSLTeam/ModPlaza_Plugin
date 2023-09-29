from PyQt5.QtCore import QObject, pyqtSignal


class Signal(QObject):
    finished = pyqtSignal(object)


class Task:
    def __init__(self):
        self._signal = Signal()
