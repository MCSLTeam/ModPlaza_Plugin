from typing import Callable, List, Tuple, Optional, Dict

from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget

from ..concurrent.taskManager import BaseTaskExecutor
from ..concurrent.task import BaseTask
from ..concurrent.future import Future
from ..concurrent.fetchImageTask import FetchImageBaseTask


class FetchImageManagerBase(BaseTaskExecutor):

    def __init__(self, useGlobalThreadPool=False):
        super().__init__(useGlobalThreadPool)
        self.__successCbMap = {}
        self.__failedCbMap = {}

    def asyncFetch(
            self,
            url: Optional[str],
            target: QWidget,
            timeout: int = 10,
            proxy: Optional[Dict] = None,
            size: Tuple[int, int] = (-1, -1),
            verify: bool = True,
            successCallback: Callable[[Future, ], None] = lambda _: None,
            failedCallback: Callable[[Future], None] = lambda _: None
    ) -> Future:
        """
        :param url: The url to fetch
        :param target: The target widget to set the image to
        :param timeout: The timeout of the request
        :param proxy: The proxy to use
        :param verify: Whether to verify the SSL certificate
        :param size: The size of the image to fetch
        :param successCallback: The callback to call when the image is fetched (takes the image fetched as an argument)
        :param failedCallback: The callback to call when the image is failed to fetch (takes the failed future as an argument)
        :return: None
        """
        future = Future()
        task = FetchImageBaseTask(
            url=url,
            _id=self.taskCounter,
            timeout=timeout,
            verify=verify,
            proxy=proxy,
            future=future
        )
        future.setExtra("url", url)
        future.setExtra("size", size)
        self.__successCbMap[self.taskCounter] = successCallback
        self.__failedCbMap[self.taskCounter] = failedCallback

        self._taskRun(task, future, target=target)
        return future

    def asyncFetchMultiple(
            self,
            tasks: List[Tuple[Optional[None], QWidget]],
            size: Tuple[int, int] = (-1, -1),
            timeout: int = 10,
            proxy: Optional[Dict] = None,
            verify: bool = True,
            successCallback: Callable[[Future], None] = lambda _: None,
            failedCallback: Callable[[Future], None] = lambda _: None
    ) -> Future:
        """
        :param tasks: A list of tuples of (url, target widget)
        :param size: The size of the image to fetch
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
                    size,
                    verify,
                    successCallback,
                    failedCallback
                )
            )
        future = Future.gather(futures)
        return future

    def _taskRun(self, task: BaseTask, future: Future, **kwargs):
        self.taskMap[self.taskCounter] = kwargs.get("target")
        super()._taskRun(task, future, **kwargs)

    def _taskDone(self, fut: Future):
        """
        set Image to target widget and call callback
        """
        e = fut.getExtra("exception")
        _id = fut.getTaskID()
        img: QPixmap = fut.getExtra("img")
        size = fut.getExtra("size")
        if size != (-1, -1):
            img = img.scaled(size[0], size[1])  # resize image

        if isinstance(e, Exception):
            fut.setFailed(e)
            self.taskMap[_id].setText("加载失败...")

            self.__failedCbMap[_id](fut)
            del self.__failedCbMap[_id]
        else:
            fut.setResult(img)
            self.taskMap[_id].setPixmap(img)

            self.__successCbMap[_id](fut)
            del self.__successCbMap[_id]

        del self.taskMap[_id]
