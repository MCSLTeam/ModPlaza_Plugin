from .Client.Clients import CfClient
from .concurrent.curseforgeTask import GetMinecraftInfoManager, MinecraftModSearchManager, \
    MinecraftModFileEntriesManager
from .utils.FetchImageManager import FetchImageManager

minecraftInfoManager = GetMinecraftInfoManager(CfClient)
minecraftModSearchManager = MinecraftModSearchManager(CfClient)
fetchImageManager = FetchImageManager()
minecraftModFileEntriesManager = MinecraftModFileEntriesManager(CfClient)

