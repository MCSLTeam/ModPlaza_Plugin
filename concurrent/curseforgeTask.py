from dataclasses import dataclass

from Plugins.Mod_Plaza.concurrent import Task, TaskManager, Future
from Plugins.Mod_Plaza.curseforge import CurseForgeAPI, SchemaClasses as schemas


@dataclass
class CurseForgeSearchBody:
    minecraftVersion: schemas.MinecraftGameVersion
    modClassId: int
    modCategory: schemas.Category
    sortType: schemas.ModSearchSortField
    sortFilter: str
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
        minecraftVersions = cf.getMinecraftVersions(True).data

        self._taskDone(modCategories=modCategories, minecraftVersions=minecraftVersions)


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
        data = cf.searchMods(
            gameId=432,
            classId=search.modClassId,
            categoryId=search.modCategory.id,
            sortField=search.sortType,
            gameVersion=search.minecraftVersion.versionString,
            sortOrder=search.sortOrder,
            index=search.index,
            pageSize=search.pageSize
        ).data
        self._taskDone(mods=data)


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
            "minecraftVersions": fut.getExtra("minecraftVersions")
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
        return future

    def _taskDone(self, fut: Future):
        fut.setResult(
            fut.getExtra("mods")
        )
