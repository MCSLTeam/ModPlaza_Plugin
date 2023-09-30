import weakref
from typing import Dict

from PyQt5.QtCore import QThreadPool, QObject

from Plugins.Mod_Plaza.cocurrent.future import Future
from Plugins.Mod_Plaza.cocurrent.task import Task


class TaskManager(QObject):
    def __init__(self, useGlobalThreadPool=False):
        super().__init__()
        if useGlobalThreadPool:
            self.threadPool = QThreadPool.globalInstance()
        else:
            self.threadPool = QThreadPool()
            self.threadPool.setMaxThreadCount(4)
        self.taskMap = {}
        self.tasks: Dict[int, weakref.ReferenceType] = {}
        self.taskCounter = 0

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
        _id = fut.getTaskID()
        task = self.tasks[_id]()
        if task is not None:
            self.threadPool.cancel(task)

    def cancelTask(self, fut: Future):
        self._taskCancel(fut)
