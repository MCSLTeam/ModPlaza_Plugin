import typing

from PyQt5.QtCore import QObject, QAbstractTableModel, QModelIndex, Qt

from . import ModFileEntry
from ..curseforge import SchemaClasses as schemas
from ..managers import minecraftModFileEntriesManager


class ModFilesModel(QAbstractTableModel):
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
        self.__tableData: typing.List[ModFileEntry] = []

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
        self.__tableData = [ModFileEntry(
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
        model = ModFilesModel()
        fut = minecraftModFileEntriesManager.asyncGetModFiles(mod.id)
        fut.result.connect(model.onModFilesGot)
        return model
