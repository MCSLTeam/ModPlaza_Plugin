from .Client.Clients import CfClient
from .concurrent.curseforgeTask import GetMinecraftInfoExecutor, MinecraftModSearchExecutor, \
    MinecraftModFileEntriesExecutor
from .utils.FetchImageManager import FetchImageManagerBase

minecraftInfoManager = GetMinecraftInfoExecutor(CfClient)
minecraftModSearchManager = MinecraftModSearchExecutor(CfClient)
fetchImageManager = FetchImageManagerBase()
minecraftModFileEntriesManager = MinecraftModFileEntriesExecutor(CfClient)

