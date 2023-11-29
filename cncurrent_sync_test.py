import sys
import time

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication

from Plugins.ModPlaza_Plugin.src.concurrent.future.future import Future
from Plugins.ModPlaza_Plugin.src.concurrent.task.taskManager import TaskExecutor

app = QApplication(sys.argv)
manager = TaskExecutor(useGlobalThreadPool=False)
fut1 = manager.asyncRun(lambda: time.sleep(3))
fut2 = manager.asyncRun(lambda: time.sleep(5))
print("task start")
t = time.time()
fut = Future.gather([fut1, fut2])
fut.synchronize()  # equivalent to: fut.wait()
print("task done:", time.time() - t)
QTimer.singleShot(1000, app.quit)
app.exec_()
