from typing import Optional, Dict

from PyQt5.QtCore import QSize
from PyQt5.QtGui import QPixmap

from ..Client.Clients import longCachedRequest
from ..concurrent.future import Future
from ..concurrent.task import BaseTask


class FetchImageBaseTask(BaseTask):
    def __init__(
            self,
            url,
            _id,
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

    def run(self):
        if self.url is None:
            self._exception = Exception("url is None")
            self._taskDone(url=self.url, img=QPixmap(), exception=self._exception)
            return

        qImg = QPixmap()
        content = longCachedRequest.get(self.url, timeout=self._timeout, proxies=self._proxy,
                                        verify=self._verify).content
        qImg.loadFromData(content)
        qImg = qImg.scaled(QSize(96, 96))

        self._taskDone(url=self.url, img=qImg, exception=self._exception)
