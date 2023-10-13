import dataclasses
import typing

from PyQt5.QtCore import QObject, QAbstractTableModel, QModelIndex, Qt

from ..curseforge import SchemaClasses as schemas
from ..managers import minecraftModFileEntriesManager


def getReleaseTypeString(releaseType: schemas.FileReleaseType):
    return {
        schemas.FileReleaseType.Alpha: "A",
        schemas.FileReleaseType.Beta: "B",
        schemas.FileReleaseType.Release: "R",
    }[releaseType]


def getFormatFileSizeString(size: int):
    if size < 1024:
        return f"{size}B"
    elif size < 1024 ** 2:
        return f"{size / 1024:.2f}KB"
    elif size < 1024 ** 3:
        return f"{size / (1024 ** 2):.2f}MB"


def getGameVersionAndModLoader(sortableGameVersions: typing.List[schemas.SortableGameVersion]):
    gameVersions = []
    modLoaders = []
    for gm in sortableGameVersions:
        if gm.gameVersion == '':
            modLoaders.append(gm.gameVersionName)
        else:
            gameVersions.append(gm.gameVersion)
    gameVersions.sort()
    modLoaders.sort()
    return gameVersions, modLoaders


@dataclasses.dataclass
class ModDLEntry:
    releaseType: schemas.FileReleaseType
    name: str
    uploadedTime: str
    size: int
    gameVersions: typing.List[schemas.SortableGameVersion]

    downloadLink: str
    fileHash: typing.List[schemas.FileHash]

    def __seq(self):
        gameVersions, modLoaders = getGameVersionAndModLoader(self.gameVersions)
        return (
            getReleaseTypeString(self.releaseType),  # 0: releaseType,
            self.name,  # 1: name,
            (self.uploadedTime).split("T")[0],  # 2: uploadedTime
            getFormatFileSizeString(self.size),  # 3: size
            ','.join(gameVersions),  # 4: gameVersion
            ','.join(modLoaders),  # 5: modLoaders
            self.downloadLink,  # 6: downloads
            self.fileHash  # 7: fileHash
        )

    def __getitem__(self, item: int):
        return self.__seq()[item]


class ModDLLinkModel(QAbstractTableModel):
    """
    display role:
    0: releaseType,
    1: name,
    2: uploadedTime
    3: size
    4: gameVersion
    5: modLoaders
    6: downloads

    user role:
    1: downloadLink
    2: fileHash
    """

    def __init__(self, parent: QObject = None):
        super().__init__(parent=parent)
        self.__tableData: typing.List[ModDLEntry] = []

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self.__tableData)

    # TODO: Implement this
    def columnCount(self, parent: QModelIndex = ...) -> int:

        return 6

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        if role == Qt.ItemDataRole.DisplayRole:
            return self.__tableData[index.row()][index.column()]
        if role == Qt.ItemDataRole.UserRole:
            return self.__tableData[index.row()]

    def onModFilesGot(self, modList: typing.List[schemas.File]):
        self.beginResetModel()
        self.__tableData = [ModDLEntry(
            releaseType=mod.releaseType,
            name=mod.displayName,
            uploadedTime=mod.fileDate,
            size=mod.fileLength,
            gameVersions=mod.sortableGameVersions,
            downloadLink=mod.downloadUrl,
            fileHash=mod.hashes
        ) for mod in modList]
        self.endResetModel()

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...) -> typing.Any:
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return {
                0: "Type",
                1: "Name",
                2: "Uploaded Time",
                3: "Size",
                4: "Game Version",
                5: "Mod Loaders",
            }[section]

    @staticmethod
    def getModel(mod: schemas.Mod):
        model = ModDLLinkModel()
        fut = minecraftModFileEntriesManager.asyncGetModFiles(mod.id)
        fut.result.connect(model.onModFilesGot)
        return model
