import weakref
from typing import Dict, List

from PyQt5.QtCore import QThreadPool, QObject
from psutil import cpu_count

from .future import Future, FutureCancelled
from .task import Task


class TaskManager(QObject):
    def __init__(self, useGlobalThreadPool=True):
        super().__init__()
        self.useGlobalThreadPool = useGlobalThreadPool
        if useGlobalThreadPool:
            self.threadPool = QThreadPool.globalInstance()
        else:
            self.threadPool = QThreadPool()
            self.threadPool.setMaxThreadCount(2 * cpu_count())  # IO-Bound = 2*N, CPU-Bound = N + 1
        self.taskMap = {}
        self.tasks: Dict[int, weakref.ReferenceType] = {}
        self.taskCounter = 0

    def deleteLater(self) -> None:
        if not self.useGlobalThreadPool:
            self.threadPool.clear()
            self.threadPool.waitForDone()
            self.threadPool.deleteLater()
        super().deleteLater()

    def _taskRun(self, task: Task, future: Future, **kwargs):
        self.tasks[self.taskCounter] = weakref.ref(task)
        future.setTaskID(self.taskCounter)

        task.signal.finished.connect(self._taskDone)
        self.threadPool.start(task)
        self.taskCounter += 1

    def _taskDone(self, fut: Future):
        """
        need manually set Future.setFailed() or Future.setResult() to be called!!!
        """
        raise NotImplemented

    def _taskCancel(self, fut: Future):
        stack: List[Future] = []
        stack.extend(fut.getChildren())
        while stack:
            f = stack.pop()
            if not f.hasChildren() and not f.isDone():
                self._taskSingleCancel(f)
                f.setFailed(FutureCancelled())
            stack.extend(f.getChildren())

    def _taskSingleCancel(self, fut: Future):
        _id = fut.getTaskID()
        task: Task = self.tasks[_id]()
        if task is not None:
            try:
                task.setAutoDelete(False)
                if self.threadPool.tryTake(task):
                    del self.tasks[_id]
                task.setAutoDelete(True)
            except RuntimeError:
                print("wrapped C/C++ object of type FetchImageTask has been deleted")

    def cancelTask(self, fut: Future):
        self._taskCancel(fut)
