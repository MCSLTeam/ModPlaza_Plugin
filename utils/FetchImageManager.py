import random
from typing import Callable, List, Tuple, Optional, Iterable, Sized

import requests
from PyQt5.QtCore import QThreadPool, QRunnable, QObject, pyqtSignal, QMutex
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget

from Plugins.Mod_Plaza.utils.CacheDB import CacheEntryTable


class Signal(QObject):
    finished = pyqtSignal(object)


class FutureError(BaseException):
    pass


class FutureFailed(FutureError):
    def __init__(self, _exception: Optional[BaseException]):
        super().__init__()
        self.exception = _exception

    def __repr__(self):
        return f"FutureFailed({self.exception})"

    def __str__(self):
        return f"FutureFailed({self.exception})"


class GatheredFutureFailed(FutureError):
    def __init__(self, failures: List[Tuple['Future', BaseException]]):
        super().__init__()
        self.failures = failures

    def __repr__(self):
        return f"GatheredFutureFailed({self.failures})"

    def __str__(self):
        return f"GatheredFutureFailed({self.failures})"

    def __iter__(self):
        return iter(self.failures)

    def __len__(self):
        return len(self.failures)


class Future(QObject):
    done = pyqtSignal(object)
    childrenDone = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self._failedCallback = lambda e: None
        self._done = False
        self._failed = False
        self._result = None
        self._exception = None
        self._children = []
        self._counter = 0
        self._parent = None
        self._callback = lambda _: None
        self._mutex = QMutex()

    def __onChildDone(self, childFuture: 'Future') -> None:
        self._mutex.lock()
        if childFuture.isFailed():
            self._failed = True
        self._counter += 1
        try:
            idx = getattr(childFuture, "_idx")
            self._result[idx] = childFuture._result
            self._mutex.unlock()
        except AttributeError:
            self._mutex.unlock()
            raise RuntimeError(
                "Invalid child future: please ensure that the child future is created by method 'Future.setChildren'")
        if self._counter == len(self._children):
            if self._failed:  # set failed
                l = []
                for i, child in enumerate(self._children):
                    if isinstance(e := child.getException(), FutureError):
                        l.append((self._children[i], e))
                self.setFailed(GatheredFutureFailed(l))
            else:
                self.setResult(self._result)

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
        if not self._done:
            self._result = result
            self._done = True
            if self._parent:
                self.childrenDone.emit(self)
            if self._callback:
                self._callback(result)
            self.done.emit(result)
        else:
            raise RuntimeError("Future already done")
        self.deleteLater()  # delete this future object

    def setFailed(self, exception: Optional[BaseException]) -> None:
        """
        :param exception: The exception to set
        :return: None
        """
        if not self._done:
            self._exception = FutureFailed(exception)
            self._done = True
            self._failed = True
            if self._parent:
                self.childrenDone.emit(self)
            if self._failedCallback:
                self._failedCallback(self)
            self.done.emit(self._result)
        else:
            raise RuntimeError("Future already done")
        self.deleteLater()

    def setCallback(self, callback: Callable[[object, ], None]) -> None:
        self._callback = callback

    def setFailedCallback(self, callback: Callable[['Future', ], None]) -> None:
        self._failedCallback = lambda e: callback(self)

    def hasException(self) -> bool:
        if self._children:
            return any([fut.hasException() for fut in self._children])
        else:
            return self._exception is not None

    def getException(self) -> Optional[BaseException]:
        return self._exception

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

    def isFailed(self) -> bool:
        return self._failed

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

    def asyncFetch(
            self,
            url: str,
            target: QWidget,
            callback: Callable[[QPixmap, ], None] = lambda _: None
    ) -> Future:
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

    def asyncFetchMultiple(
            self,
            tasks: List[Tuple[str, QWidget]],
            callback: Callable[[QPixmap], None] = lambda _: None,
            failedCallback: Callable[[Future], None] = lambda _: None
    ) -> Future:
        """
        :param tasks: A list of tuples of (url, target widget)
        :param callback: The callback to call when an image is fetched (takes image fetched as an argument)
        :param failedCallback: The callback to call when an image is failed to fetch (takes the failed future as an argument)
        :return: A Future object that will be done when all images are fetched
        """
        futures = []
        for url, target in tasks:
            futures.append(fut := self.asyncFetch(url, target))
            fut.setCallback(callback)
            fut.setFailedCallback(failedCallback)
        future = Future.gather(futures)
        return future

    def __onDone(self, data):
        """
        set Image to target widget and call callback
        """
        # 75%概率正常返回,25%概率返回异常
        choice = random.randint(0, 3)
        _id, fut, img = data

        if fut:
            # fut.setResult(img)
            if choice:
                fut.setResult(img)
                self.taskMap[_id].setPixmap(img)
                self.callbackMap[_id](img)
            else:
                fut.setFailed(Exception("Test Exception"))
                self.taskMap[_id].setText("加载失败")
        del self.taskMap[_id]
        del self.callbackMap[_id]
