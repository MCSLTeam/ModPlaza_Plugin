import sys
import time

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication

from Plugins.ModPlaza_Plugin.src.concurrent.future.future import Future
from Plugins.ModPlaza_Plugin.src.concurrent.task.taskManager import TaskExecutor

work_time = 10

app = QApplication(sys.argv)
manager = TaskExecutor(useGlobalThreadPool=False)
futures = []
t = time.time()

for _ in range(1, work_time + 1):  # 创建work_time个任务,每个任务sleep 1~work_time 秒
    futures.append(
        manager.asyncRun(
            lambda i: {time.sleep(i), print(f"task_{i} done, waited: {i}s")}, _
        )
    )  # add coroutine tasks
print("task start")

gathered = Future.gather(futures)
gathered.synchronize()  # equivalent to: fut.wait()

print("all tasks done:", time.time() - t, ",expected:", work_time)
QTimer.singleShot(1000, app.quit)  # close app after 1s
app.exec_()
