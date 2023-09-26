import time
from typing import Callable

import requests
from PyQt5.QtCore import QThreadPool, QRunnable, QObject, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget

from Plugins.Mod_Plaza.utils.CacheDB import CacheEntryTable


class Signal(QObject):
    finished = pyqtSignal(object)


class FetchImageTask(QRunnable):
    def __init__(self, url, _id, db, parent=None):
        super().__init__()
        self.url = url
        self._parent = parent
        self._id = _id
        self.signal = Signal()
        self.CacheTable: CacheEntryTable = db.root

    def run(self):
        path = self.url.replace("https://media.forgecdn.net/avatars/thumbnails/", "")
        filename = path.split("/")[-1]
        path = path.replace(filename, "")[:-1]
        ext = filename.split(".")[-1]

        if not self.CacheTable.isEntryExpired(path):
            print(f"<<< Cache hit ! {self.url}")
            qImg = QPixmap()
            qImg.loadFromData(self.CacheTable.getRecord(path), ext)

        else:
            print(f">>> Fetching {self.url}")
            image = requests.get(self.url).content
            self.CacheTable.addRecord(path, image, replace=True)
            print(f"<<< Caching {self.url}")
            qImg = QPixmap()
            qImg.loadFromData(image, ext)

        self.signal.finished.emit((self._id, qImg))
        time.sleep(1)


    @property
    def finished(self):
        return self.signal.finished


class FetchImageManager(QObject):

    def __init__(self, cache):
        super().__init__()
        self.threadPool = QThreadPool()
        self.threadPool.setMaxThreadCount(16)
        self.taskMap = {}
        self.callbackMap = {}
        self.taskCounter = 0
        self.cache = cache

    def asyncFetch(self, url: str, target: QWidget, callback: Callable[[QPixmap, ], None] = lambda _: None) -> None:
        """
        :param url: The url to fetch
        :param target: The target widget to set the image to
        :param callback: The callback to call when the image is fetched (takes the image fetched as an argument)
        :return: None
        """
        task = FetchImageTask(url, self.taskCounter, self.cache)
        task.signal.finished.connect(self.__onDone)
        self.taskMap[self.taskCounter] = target
        self.callbackMap[self.taskCounter] = callback
        self.threadPool.start(task)
        self.taskCounter += 1

    def __onDone(self, data):
        _id, img = data
        self.taskMap[_id].setPixmap(img)
        self.callbackMap[_id](img)
        del self.taskMap[_id]
        del self.callbackMap[_id]
