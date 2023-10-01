from dataclasses import dataclass
from typing import Optional

from . import Task, TaskManager, Future
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


class GetMinecraftInfoTask(Task):
    def __init__(self, _id, future, cfClient, parent=None):
        super().__init__(_id=_id, future=future)
        self._parent = parent
        self.cfClient: CurseForgeAPI = cfClient

    def run(self):
        cf = self.cfClient
        modCategories = cf.getCategories(432, schemas.MinecraftClassId.Mod).data
        pluginCategories = cf.getCategories(432, schemas.MinecraftClassId.BukkitPlugin).data
        minecraftVersions = cf.getMinecraftVersions(True).data

        self._taskDone(
            modCategories=modCategories,
            minecraftVersions=minecraftVersions,
            pluginCategories=pluginCategories
        )


class MinecraftModSearchTask(Task):
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


class GetMinecraftInfoManager(TaskManager):
    def __init__(self, clClient: CurseForgeAPI, useGlobalThreadPool=False):
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
        fut.setResult({
            "modCategories": fut.getExtra("modCategories"),
            "minecraftVersions": fut.getExtra("minecraftVersions"),
            "pluginCategories": fut.getExtra("pluginCategories")
        })


class MinecraftModSearchManager(TaskManager):
    def __init__(self, clClient: CurseForgeAPI, useGlobalThreadPool=False):
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
