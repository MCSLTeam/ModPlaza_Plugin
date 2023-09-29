import os.path
import sys
from typing import List

import requests_cache as rqc
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QGridLayout, QLabel, QWidget, QPushButton, QMessageBox
from pyqt5_plugins.examplebuttonplugin import QtGui

from Plugins.Mod_Plaza.CFAPI import KEY
from Plugins.Mod_Plaza.curseforge import CurseForgeAPI, SchemaClasses as schemas
from Plugins.Mod_Plaza.utils.CacheDB import CacheDB
from Plugins.Mod_Plaza.utils.FetchImageManager import FetchImageManager


# from Adapters.Plugin import Plugin


# Mod_Plaza = Plugin()


def load():
    pass


def enable():
    curdir = os.path.abspath(os.path.dirname(__file__))
    os.makedirs(os.path.join(curdir, "cache"), exist_ok=True)
    csesh = rqc.CachedSession(
        os.path.join(curdir, "cache", "CurseForgeAPY-Cache"),
        backend="sqlite",
        expire_after=300
    )
    cf = CurseForgeAPI('$2a$10$/19NYVOIjJEhtKjWg.BhPOVc4HgaekvbZoVi0Pxs9b79dOSjtTCNC', csesh)
    # featuredModsSearch = schemas.GetFeaturedModsRequestBody(432, [], 73242)

    # get featured mods within specific game
    # featuredMods = cf.getFeatured_mods(featuredModsSearch)
    mods = cf.searchMods(
        gameId=432,
        modLoaderType=schemas.ModLoaderType.Forge,
        pageSize=128,
        classId=schemas.MinecraftClassId.Mod,
        searchFilter="",
        sortField=schemas.ModSearchSortField.TotalDownloads,
        sortOrder=schemas.SortOrder.Descending,
    )

    # for mod in featuredMods.data.popular:
    #     print(f"{mod.name}, {mod.summary}, {mod.id}, {mod.latestFiles[0].downloadUrl}")
    print("====")
    counter = 0
    for mod in mods.data:
        print(
            f"{mod.name}, "
            f"{mod.classId}, "
            f"{[c.name for c in mod.categories]}, "
            f"{mod.id}, "
            f"{mod.latestFilesIndexes[0].fileId},"
            f"{mod.logo.thumbnailUrl}")
        task = FetchImageTask(mod.logo.thumbnailUrl)
        task.finished.connect(lambda img: window.labels[counter].setPixmap(img))
        threadPool.start(task)
        counter += 1


def disable():
    pass


class AThread(QThread):
    onFinished = pyqtSignal(object)

    def __init__(self, cf: CurseForgeAPI):
        super().__init__()
        self.mods = None
        self.cf = cf

    def run(self) -> None:
        self.mods = self.cf.searchMods(
            gameId=432,
            modLoaderType=schemas.ModLoaderType.Forge,
            index=128,
            pageSize=16,
            classId=schemas.MinecraftClassId.Mod,
            searchFilter="",
            sortField=schemas.ModSearchSortField.TotalDownloads,
            sortOrder=schemas.SortOrder.Descending,
        )
        self.onFinished.emit(self.mods.data)
        # print(self.mods)


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.labels = []
        self.setWindowTitle("Mod Plaza")
        self.setGeometry(1000, 100, 800, 600)
        self.gridLayout = QGridLayout()
        self.button = QPushButton("加载")
        # 为gridLayout添加4 x 4的网格
        for i in range(4):
            for j in range(4):
                label = QLabel("Row %d, Column %d" % (i, j))
                label.setText("空白")
                self.labels.append(label)
                label.setFixedSize(200, 200)
                self.gridLayout.addWidget(label, i, j)
        self.gridLayout.addWidget(self.button, 5, 0, 2, 4)
        # 创建一个QWidget对象
        widget = QWidget()
        # 将gridLayout设置为widget的布局
        widget.setLayout(self.gridLayout)
        # 将widget设置为Window的中心控件
        self.setCentralWidget(widget)
        self.cacheDB = CacheDB("cache/curseforge.cache", defaultExpireTime=86400)

        curdir = os.path.abspath(os.path.dirname(__file__))
        os.makedirs(os.path.join(curdir, "cache"), exist_ok=True)
        self.csesh = rqc.CachedSession(
            os.path.join(curdir, "cache", "CurseForgeAPY-Cache"),
            backend="sqlite",
            expire_after=300
        )
        self.cf = CurseForgeAPI(KEY, self.csesh)

        self.mod = None

        self._thread = None

        self.button.clicked.connect(self.onClicked)
        self.manager = FetchImageManager(cache=self.cacheDB)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.cacheDB.close()
        super().closeEvent(a0)

    def onClicked(self):
        print("开始加载...")
        # self.button.setEnabled(False)
        self._thread = AThread(self.cf)
        self._thread.start()
        self._thread.onFinished.connect(lambda mods: {
            self.onFinished(mods),
            # QTimer.singleShot(5000, self.onTimer0),
            self._thread.deleteLater()
        })

    def onFetchFinished(self, data):
        _id, img = data
        self.labels[_id].setPixmap(img)

    def onFinished(self, mods: List[schemas.Mod]):
        self.rv = mods
        # counter = 0
        # for mod in mods:
        #     self.manager.asyncFetch(mod.logo.thumbnailUrl, self.labels[counter])
        #     counter = (counter + 1) % 16
        future = self.manager.asyncFetchMultiple(
            tasks=[(mod.logo.url if mod.logo is not None else None, self.labels[i % 16]) for i, mod in enumerate(mods)],
            timeout=1,
            successCallback=lambda _: print("单个加载完成", _),
            failedCallback=lambda _: print(f"单个加载失败,url={_.url}", _.getException())
        )
        future.setFailedCallback(lambda _: print("加载失败,failedCallback", _.getException()))
        future.done.connect(self.onFutureDone)
        self.fut = future

    def onFutureDone(self, result):
        failed = len([i for i in result if i is None])
        success = len(result) - failed
        QMessageBox.information(self, "加载完成", f"加载完成,\n共尝试加载{len(result)}个,\n成功{success}个,\n失败{failed}个")

    def clear(self):
        for label in self.labels:
            label.setText("空白")

    def onTimer0(self):
        self.clear()
        print("测试一: 已全部缓存,5s后再次加载...")
        QTimer.singleShot(5000, lambda: {
            self.onFinished(self.rv),
            QTimer.singleShot(5000, self.onTimer1)
        })

    def onTimer1(self):
        self.clear()
        print("缓存将在5秒后过期...")
        QTimer.singleShot(5000, self.onTimer2)

    def onTimer2(self):
        print("测试二: 缓存已过期,再次加载...")
        self.onFinished(self.rv)
        QTimer.singleShot(5000, self.endTest)

    def endTest(self):
        QMessageBox.information(self, "测试完成", "测试完成,请关闭窗口退出程序")
        self.button.setEnabled(True)


# Mod_Plaza.register_loadFunc(load)
# Mod_Plaza.register_enableFunc(enable)
# Mod_Plaza.register_disableFunc(disable)
def main():
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    # enable()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
