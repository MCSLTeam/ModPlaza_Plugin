from dataclasses import dataclass
from typing import Optional

from .taskManager import BaseTaskExecutor
from .task import BaseTask
from .future import Future
from ..curseforge import CurseForgeAPI, SchemaClasses as schemas


@dataclass
class CurseForgeSearchBody:
    gameVersion: Optional[schemas.MinecraftGameVersion]
    classId: int
    categoryId: Optional[schemas.Category]
    sortField: Optional[schemas.ModSearchSortField]
    searchFilter: str
    sortOrder: schemas.SortOrder
    index: int
    pageSize: int


class GetMinecraftInfoTask(BaseTask):
    def __init__(self, _id, future, cfClient, parent=None):
        super().__init__(_id=_id, future=future)
        self._parent = parent
        self.cfClient: CurseForgeAPI = cfClient

    def run(self):
        cf = self.cfClient
        try:
            modCategories = cf.getCategories(432, schemas.MinecraftClassId.Mod).data
            pluginCategories = cf.getCategories(432, schemas.MinecraftClassId.BukkitPlugin).data
            minecraftVersions = cf.getMinecraftVersions(True).data
        except Exception as exception:
            self._taskDone(
                modCategories=[],
                minecraftVersions=[],
                pluginCategories=[],
                exception=exception
            )
            return

        self._taskDone(
            modCategories=modCategories,
            minecraftVersions=minecraftVersions,
            pluginCategories=pluginCategories,
            exception=None
        )


class MinecraftModSearchTask(BaseTask):
    def __init__(
            self,
            _id: int,
            future: Future,
            cfClient: CurseForgeAPI,
            search: CurseForgeSearchBody,
            parent=None
    ):
        super().__init__(_id=_id, future=future)
        self._parent = parent
        self.cfClient: CurseForgeAPI = cfClient
        self.searchBody = search

    def run(self) -> None:
        cf = self.cfClient
        search = self.searchBody
        response = cf.searchMods(
            gameId=432,
            gameVersion=search.gameVersion.versionString if search.gameVersion else None,
            categoryId=search.categoryId.id if search.categoryId else None,
            classId=search.classId,
            sortField=search.sortField,
            searchFilter=search.searchFilter,
            sortOrder=search.sortOrder,
            index=search.index,
            pageSize=search.pageSize
        )
        self._taskDone(response=response)


class GetMinecraftInfoExecutor(BaseTaskExecutor):
    def __init__(self, clClient: CurseForgeAPI, useGlobalThreadPool=True):
        super().__init__(useGlobalThreadPool=useGlobalThreadPool)
        self.cfClient = clClient

    def asyncGetMinecraftInfo(self) -> Future:
        future = Future()
        task = GetMinecraftInfoTask(
            _id=self.taskCounter,
            future=future,
            cfClient=self.cfClient
        )
        self._taskRun(task, future)
        return future

    def _taskDone(self, fut: Future):
        if fut.getExtra("exception"):
            fut.setFailed(fut.getExtra("exception"))
        else:
            fut.setResult({
                "modCategories": fut.getExtra("modCategories"),
                "minecraftVersions": fut.getExtra("minecraftVersions"),
                "pluginCategories": fut.getExtra("pluginCategories")
            })


class MinecraftModSearchExecutor(BaseTaskExecutor):
    def __init__(self, clClient: CurseForgeAPI, useGlobalThreadPool=True):
        super().__init__(useGlobalThreadPool=useGlobalThreadPool)
        self.cfClient = clClient

    def asyncSearchMod(self, searchBody: CurseForgeSearchBody) -> Future:
        future = Future()
        task = MinecraftModSearchTask(
            _id=self.taskCounter,
            future=future,
            cfClient=self.cfClient,
            search=searchBody
        )
        self._taskRun(task, future)
        for d in searchBody.__dict__:
            if d.startswith("_"):
                continue
            print(d, getattr(searchBody, d))
        return future

    def _taskDone(self, fut: Future):
        fut.setResult(
            fut.getExtra("response")
        )


class MinecraftModFileEntriesTask(BaseTask):
    def __init__(
            self,
            _id: int,
            future: Future,
            cfClient: CurseForgeAPI,
            modId: int,
            pageOffset: int = 0,
            pageSize: int = 50,
            modLoaderType: Optional[schemas.ModLoaderType] = None,
            gameVersion: Optional[int] = None,
            gameVersionTypeId: Optional[int] = None,
            parent=None
    ):
        super().__init__(_id=_id, future=future)
        self._parent = parent
        self.cfClient: CurseForgeAPI = cfClient
        self.modId = modId
        self.pageOffset = pageOffset
        self.modLoaderType = modLoaderType
        self.gameVersion = gameVersion
        self.gameVersionTypeId = gameVersionTypeId
        self.pageSize = pageSize

    def run(self) -> None:
        cf = self.cfClient
        try:
            response = cf.getModFiles(
                self.modId,
                index=self.pageOffset * 50,
                modLoaderType=self.modLoaderType,
                gameVersion=self.gameVersion,
                gameVersionTypeId=self.gameVersionTypeId,
                pageSize=self.pageSize,
            )
        except Exception as exception:
            self._taskDone(response=exception)
            return
        self._taskDone(response=response)


class MinecraftModFileEntriesExecutor(BaseTaskExecutor):
    def __init__(self, clClient: CurseForgeAPI, useGlobalThreadPool=True):
        super().__init__(useGlobalThreadPool=useGlobalThreadPool)
        self.cfClient = clClient

    def asyncGetModFiles(
            self,
            modId: int,
            pageOffset: int = 0,
            modLoaderType: Optional[schemas.ModLoaderType] = None,
            gameVersion: Optional[int] = None,
            gameVersionTypeId: Optional[int] = None,
            pageSize: int = 50
    ) -> Future:
        future = Future()
        taskFuture = Future()
        task = MinecraftModFileEntriesTask(
            _id=self.taskCounter,
            future=taskFuture,
            cfClient=self.cfClient,
            pageOffset=pageOffset,
            modId=modId,
            modLoaderType=modLoaderType,
            gameVersion=gameVersion,
            gameVersionTypeId=gameVersionTypeId,
            pageSize=pageSize
        )
        self._taskRun(task, taskFuture)
        taskFuture.setExtra("original", future)
        taskFuture.setExtra("modId", modId)
        return future

    def asyncGetSpecificPage(
            self,
            modId: int,
            pageOffset: int
    ) -> Future:
        future = Future()
        task = MinecraftModFileEntriesTask(
            _id=self.taskCounter,
            future=future,
            cfClient=self.cfClient,
            pageOffset=pageOffset,
            modId=modId
        )
        self._taskRun(task, future)
        return future

    def _taskDone(self, fut: Future):
        if isinstance(resp := fut.getExtra("response"), schemas.ApiResponseCode):
            resp: schemas.ApiResponseCode
            print(resp)
            fut.setFailed(Exception(resp.value))
            return

        if fut.hasExtra("head"):  # 如果是第二次gathered future
            rv = fut.getExtra("head")
            for r in fut.getResult():
                rv.extend(r)
            fut.getExtra("original").setResult(rv)  # 返回总结果

        elif fut.hasExtra("original"):  # 如果是第一次future
            print('1 done')
            resp: schemas.GetModFilesResponse = fut.getExtra("response")
            pages = (resp.pagination.totalCount) // resp.pagination.pageSize + 1
            print(resp.pagination.totalCount)

            if pages > 1:
                futures = []
                for i in range(2, pages + 1):
                    future = self.asyncGetSpecificPage(
                        fut.getExtra("modId"),
                        pageOffset=i - 1
                    )
                    future.setExtra("page", i)
                    future.setExtra(f"index", i)
                    futures.append(future)
                gatherFuture = Future.gather(futures)
                gatherFuture.setExtra("original", fut.getExtra("original"))
                gatherFuture.setExtra("head", resp.data)
                gatherFuture.done.connect(self._taskDone)
                fut.setResult(resp.data)  # 第一次future的结果
            else:
                fut.setResult(resp.data)  # 第一次future的结果
                fut.getExtra("original").setResult(resp.data)  # 如果只有一页，直接返回结果

        elif fut.hasExtra("index"):  # 第二次子future
            print(fut.getExtra("index"), 'done')
            resp: schemas.GetModFilesResponse = fut.getExtra("response")
            fut.setResult(resp.data)
