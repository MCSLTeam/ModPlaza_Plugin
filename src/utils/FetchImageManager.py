from typing import Callable, List, Tuple, Optional, Dict

from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget

from ..concurrent import TaskManager, Task, Future, FetchImageTask


class FetchImageManager(TaskManager):

    def __init__(self, useGlobalThreadPool=False):
        super().__init__(useGlobalThreadPool)
        # self.threadPool.setMaxThreadCount(16)

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
            timeout=timeout,
            verify=verify,
            proxy=proxy,
            future=future
        )
        future.setExtra("url", url)
        future.setCallback(successCallback)
        future.setFailedCallback(failedCallback)

        self._taskRun(task, future, target=target)
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

    def _taskRun(self, task: Task, future: Future, **kwargs):
        self.taskMap[self.taskCounter] = kwargs.get("target")
        super()._taskRun(task, future, **kwargs)

    def _taskDone(self, fut: Future):
        """
        set Image to target widget and call callback
        """
        e = fut.getExtra("exception")
        _id = fut.getTaskID()
        img = fut.getExtra("img")

        if isinstance(e, Exception):
            fut.setFailed(e)
            self.taskMap[_id].setText("加载失败...")
        else:
            fut.setResult(img)
            self.taskMap[_id].setPixmap(img)
        del self.taskMap[_id]
