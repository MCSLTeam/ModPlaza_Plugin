from typing import List, Optional, Callable, Iterable, Sized, Tuple

from PyQt5.QtCore import QObject, pyqtSignal, QMutex


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
        self._extra = {}

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
        # self.deleteLater()

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

    def setExtra(self, key, value):
        self._extra[key] = value

    def getExtra(self, key):
        return self._extra.get(key, None)

    def __getattr__(self, item):
        return self.getExtra(item)

    def __repr__(self):
        return f"Future({self._result})"

    def __str__(self):
        return f"Future({self._result})"

    def __eq__(self, other):
        return self._result == other._result
