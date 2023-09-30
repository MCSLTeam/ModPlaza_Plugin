from Plugins.Mod_Plaza.cocurrent import Task, TaskManager, Future
from Plugins.Mod_Plaza.curseforge import CurseForgeAPI, SchemaClasses as schemas


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


class GetMinecraftInfoManager(TaskManager):
    def __init__(self, clClient: CurseForgeAPI, useGlobalThreadPool=False):
        super().__init__(useGlobalThreadPool=useGlobalThreadPool)
        self.cfClient = clClient

    def getMinecraftInfo(self) -> Future:
        future = Future()
        task = GetMinecraftInfoTask(
            _id=self.taskCounter,
            future=future,
            cfClient=self.cfClient
        )
