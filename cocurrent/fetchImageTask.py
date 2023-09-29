from typing import Optional, Dict

import requests
from PyQt5.QtCore import QRunnable
from PyQt5.QtGui import QPixmap

from ..cocurrent.future import Future
from ..cocurrent.task import Task
from ..utils.CacheDB import CacheEntryTable


class FetchImageTask(QRunnable, Task):
    def __init__(
            self,
            url,
            _id,
            db,
            timeout,
            proxy,
            verify,
            future: Optional[Future] = None,
            parent=None
    ):
        super().__init__()
        self.url: Optional[str] = url
        self._parent = parent
        self._id: int = _id
        self._timeout: int = timeout
        self._proxy: Optional[Dict] = proxy
        self._future: Future = future
        self._verify = verify
        self._exception: Optional[BaseException] = None
        self.CacheTable: CacheEntryTable = db.root

    def run(self):
        if self.url is None:
            self._exception = Exception("url is None")
            self._signal.finished.emit((self.url, self._id, self._future, QPixmap(), self._exception))
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

        self._signal.finished.emit((self.url, self._id, self._future, qImg, self._exception))

    @property
    def finished(self):
        return self._signal.finished

    @property
    def signal(self):
        return self._signal
