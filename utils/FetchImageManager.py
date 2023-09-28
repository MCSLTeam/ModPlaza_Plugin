from typing import Callable, List, Tuple, Optional, Iterable, Sized

import requests
from PyQt5.QtCore import QThreadPool, QRunnable, QObject, pyqtSignal, QMutex
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget

from Plugins.Mod_Plaza.utils.CacheDB import CacheEntryTable


class Signal(QObject):
    finished = pyqtSignal(object)


class Future(QObject):
    done = pyqtSignal(object)
    childrenDone = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self._done = False
        self._result = None
        self._children = []
        self._counter = 0
        self._parent = None
        self._callback = None
        self._mutex = QMutex()

    def __onChildDone(self, childFuture: 'Future') -> None:
        self._mutex.lock()
        self._counter += 1
        try:
            idx = getattr(childFuture, "_idx")
            self._result[idx] = childFuture._result
        except AttributeError:
            raise Exception(
                "Invalid child future: please ensure that the child future is created by method 'Future.setChildren'")
        if self._counter == len(self._children):
            self.setResult(self._result)
        self._mutex.unlock()

    def __setChildren(self, children: List['Future']) -> None:
        self._children = children
        self._result = [None] * len(children)
        for i, fut in enumerate(self._children):
            setattr(fut, f"_idx", i)
            fut.childrenDone.connect(self.__onChildDone)
            fut._parent = self

    def setResult(self, result) -> None:
        """
        :param result: The result to set
        :return: None

        do not set result in thread pool,or it may not set correctly
        please use in main thread,or use signal-slot to set result !!!
        """
        self._result = result
        self._done = True
        if self._parent:
            self.childrenDone.emit(self)
        if self._callback:
            self._callback(result)
        self.done.emit(result)
        self.deleteLater()  # delete this future object

    def setCallback(self, callback: Callable[[object, ], None]) -> None:
        self._callback = callback

    @staticmethod
    def gather(futures: {Iterable, Sized}) -> 'Future':
        """
        :param futures: An iterable of Future objects
        :return: A Future object that will be done when all futures are done
        """

        future = Future()
        future.__setChildren(futures)
        return future

    def isDone(self) -> bool:
        return self._done

    def getResult(self) -> object:
        return self._result

    def __repr__(self):
        return f"Future({self._result})"

    def __str__(self):
        return f"Future({self._result})"

    def __eq__(self, other):
        return self._result == other._result


class FetchImageTask(QRunnable):
    def __init__(self, url, _id, db, future: Optional[Future] = None, parent=None):
        super().__init__()
        self.url = url
        self._parent = parent
        self._id = _id
        self.signal = Signal()
        self._future = future
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

        self.signal.finished.emit((self._id, self._future, qImg))

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

    def asyncFetch(self, url: str, target: QWidget, callback: Callable[[QPixmap, ], None] = lambda _: None) -> Future:
        """
        :param url: The url to fetch
        :param target: The target widget to set the image to
        :param callback: The callback to call when the image is fetched (takes the image fetched as an argument)
        :return: None
        """
        future = Future()
        task = FetchImageTask(url, self.taskCounter, self.cache, future)
        task.signal.finished.connect(self.__onDone)
        self.taskMap[self.taskCounter] = target
        self.callbackMap[self.taskCounter] = callback
        self.threadPool.start(task)
        self.taskCounter += 1
        return future

    def asyncFetchMultiple(self,
                           tasks: List[Tuple[str, QWidget]],
                           callback: Callable[[List[QPixmap]], None] = lambda _: None) -> Future:
        """
        :param tasks: A list of tuples of (url, target widget)
        :param callback: The callback to call when all images are fetched (takes the list of images fetched as an argument)
        :return: A Future object that will be done when all images are fetched
        """
        futures = []
        for url, target in tasks:
            futures.append(self.asyncFetch(url, target))
        future = Future.gather(futures)
        future.setCallback(callback)
        return future

    def __onDone(self, data):
        """
        set Image to target widget and call callback
        """
        _id, fut, img = data
        self.taskMap[_id].setPixmap(img)
        self.callbackMap[_id](img)
        if fut:
            fut.setResult(img)
        del self.taskMap[_id]
        del self.callbackMap[_id]
