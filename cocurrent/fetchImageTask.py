from typing import Optional, Dict

import requests
from PyQt5.QtGui import QPixmap

from Plugins.Mod_Plaza.cocurrent.future import Future
from Plugins.Mod_Plaza.cocurrent.task import Task
from Plugins.Mod_Plaza.utils.CacheDB import CacheEntryTable


class FetchImageTask(Task):
    def __init__(
            self,
            url,
            _id,
            db,
            timeout,
            proxy,
            verify,
            future: Future,
            parent=None
    ):
        super().__init__(_id=_id, future=future)
        self.url: Optional[str] = url
        self._parent = parent
        self._timeout: int = timeout
        self._proxy: Optional[Dict] = proxy
        self._verify = verify
        self.CacheTable: CacheEntryTable = db.root

    def run(self):
        if self.url is None:
            self._exception = Exception("url is None")
            self._taskDone(url=self.url, img=QPixmap(), exception=self._exception)
            return

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
            qImg = QPixmap()
            try:
                qImg.loadFromData(
                    image := requests.get(self.url, timeout=self._timeout, proxies=self._proxy,
                                          verify=self._verify).content,
                    ext
                )
                self.CacheTable.addRecord(path, image, replace=True)
                print(f"<<< Caching {self.url}")
            except Exception as e:
                self._exception = e

        self._taskDone(url=self.url, img=qImg, exception=self._exception)
