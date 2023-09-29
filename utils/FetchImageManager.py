from typing import Callable, List, Tuple, Optional, Dict

from PyQt5.QtCore import QThreadPool, QObject
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget

from ..cocurrent.fetchImageTask import FetchImageTask
from ..cocurrent.future import Future


class FetchImageManager(QObject):

    def __init__(self, cache):
        super().__init__()
        self.threadPool = QThreadPool()
        self.threadPool.setMaxThreadCount(16)
        self.taskMap = {}
        self.taskCounter = 0
        self.cache = cache

    def asyncFetch(
            self,
            url: Optional[str],
            target: QWidget,
            timeout: int = 10,
            proxy: Optional[Dict] = None,
            verify: bool = True,
            successCallback: Callable[[QPixmap, ], None] = lambda _: None,
            failedCallback: Callable[[Future], None] = lambda _: None
    ) -> Future:
        """
        :param url: The url to fetch
        :param target: The target widget to set the image to
        :param timeout: The timeout of the request
        :param proxy: The proxy to use
        :param verify: Whether to verify the SSL certificate
        :param successCallback: The callback to call when the image is fetched (takes the image fetched as an argument)
        :param failedCallback: The callback to call when the image is failed to fetch (takes the failed future as an argument)
        :return: None
        """
        future = Future()
        task = FetchImageTask(
            url=url,
            _id=self.taskCounter,
            db=self.cache,
            timeout=timeout,
            verify=verify,
            proxy=proxy,
            future=future
        )
        future.setExtra("url", url)
        future.setCallback(successCallback)
        future.setFailedCallback(failedCallback)

        task.signal.finished.connect(self.__onDone)
        self.taskMap[self.taskCounter] = target
        self.threadPool.start(task)
        self.taskCounter += 1
        return future

    def asyncFetchMultiple(
            self,
            tasks: List[Tuple[Optional[None], QWidget]],
            timeout: int = 10,
            proxy: Optional[Dict] = None,
            verify: bool = True,
            successCallback: Callable[[QPixmap], None] = lambda _: None,
            failedCallback: Callable[[Future], None] = lambda _: None
    ) -> Future:
        """
        :param tasks: A list of tuples of (url, target widget)
        :param timeout: The timeout of the request
        :param proxy: The proxy to use
        :param verify: Whether to verify the SSL certificate
        :param successCallback: The callback to call when an image is fetched (takes image fetched as an argument)
        :param failedCallback: The callback to call when an image is failed to fetch (takes the failed future as an argument)
        :return: A Future object that will be done when all images are fetched
        """
        futures = []
        for url, target in tasks:
            futures.append(
                self.asyncFetch(
                    url,
                    target,
                    timeout,
                    proxy,
                    verify,
                    successCallback,
                    failedCallback
                )
            )
        future = Future.gather(futures)
        return future

    def __onDone(self, data):
        """
        set Image to target widget and call callback
        """
        url, _id, fut, img, e = data
        if isinstance(e, Exception):
            fut.setFailed(e)
            self.taskMap[_id].setText("加载失败...")
        else:
            fut.setResult(img)
            self.taskMap[_id].setPixmap(img)
        del self.taskMap[_id]
