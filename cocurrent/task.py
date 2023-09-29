from typing import Optional

from PyQt5.QtCore import QObject, pyqtSignal, QRunnable

from Plugins.Mod_Plaza.cocurrent.future import Future


class Signal(QObject):
    finished = pyqtSignal(object)


class Task(QRunnable):
    def __init__(self, _id: int, future: Future):
        super().__init__()
        self._signal: Signal = Signal()  # pyqtSignal(object)
        self._future: Future = future
        self._id: int = _id
        self._exception: Optional[BaseException] = None

    @property
    def finished(self):
        return self._signal.finished

    @property
    def signal(self):
        return self._signal

    def _taskDone(self, **data):
        for d in data.items():
            self._future.setExtra(*d)
        self._signal.finished.emit(self._future)
