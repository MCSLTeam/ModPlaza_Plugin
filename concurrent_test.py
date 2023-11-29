import functools
import os
import random
import sys
import time

from PyQt5.QtCore import QThread, QTimer
from PyQt5.QtWidgets import QApplication

sys.path.append(os.path.join(os.getcwd(), "site-packages"))
print(os.path.join(os.getcwd(), "site-packages"))
from Plugins.ModPlaza_Plugin.src.Client.Clients import CfClient
from Plugins.ModPlaza_Plugin.src.concurrent.task.taskManager import TaskExecutor

app = QApplication(sys.argv)


def func(i: int, *args, **kwargs) -> int:
    r = random.randint(1, 5)
    print("task <{}> sleep {}s,current Thread:{}".format(i, r, QThread.currentThread()))
    time.sleep(r)
    print("task <{}> done".format(i))
    return r


func_ptr = functools.partial(func)

# partial test (没必要)
manager = TaskExecutor(useGlobalThreadPool=False)
for i in range(10):
    manager.asyncRun(func_ptr, i)
manager.threadPool.waitForDone()
manager.deleteLater()

print("var test done\n" + "-" * 50)

# partial wrapped lambda test (多此一举)
manager = TaskExecutor(useGlobalThreadPool=False)
for i in range(10):
    manager.asyncRun(
        functools.partial(
            lambda i, *args, **kwargs: {
                (r := random.randint(1, 5)),
                print("task <{}> sleep {}s,current Thread:{}".format(i, r, QThread.currentThread())),
                time.sleep(r),
                print("task <{}> done".format(i)),
                r
            }),
        i)

manager.threadPool.waitForDone()
manager.deleteLater()
print("lambda test done\n" + "-" * 50)

# lambda test (直接用lambda就行,因为manager.asyncRun()会自动包装成functools.partial)
manager = TaskExecutor(useGlobalThreadPool=False)
for i in range(10):
    manager.asyncRun(lambda i: {
        (r := random.randint(1, 5)),
        print("task <{}> sleep {}s,current Thread:{}".format(i, r, QThread.currentThread())),
        time.sleep(r),
        print("task <{}> done".format(i)),
        r
    }, i)

manager.threadPool.waitForDone()
manager.deleteLater()
print("lambda test done\n" + "-" * 50)


def _p(fut):
    print(fut)


run = TaskExecutor.getGlobalInstance().asyncRun(CfClient.getMinecraftVersions, True)
run.done.connect(_p)
run.done.connect(lambda _: QTimer.singleShot(1000, app.quit))
sys.exit(app.exec_())
