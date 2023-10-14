import dataclasses
import json
import typing

from ..curseforge import SchemaClasses as schemas


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
class ModFileEntry:
    releaseType: schemas.FileReleaseType
    name: str
    uploadedTime: str
    size: int
    gameVersions: typing.List[schemas.SortableGameVersion]

    downloadLink: str
    fileHash: typing.List[schemas.FileHash]

    @staticmethod
    def serialize(mod: schemas.File):
        gameVersions, modLoaders = getGameVersionAndModLoader(mod.sortableGameVersions)
        fileHash = {
            e.algo.name: e.value for e in mod.hashes  # type: typing.Dict[str, str]
        }  # 通常会有两个hash，一个是sha1，一个是MD5

        return {
            "releaseType": getReleaseTypeString(mod.releaseType),  # type: str
            "name": mod.displayName,  # type: str
            "uploadedTime": (mod.fileDate).split("T")[0],  # type: str
            "size": getFormatFileSizeString(mod.fileLength),  # type: str
            "gameVersions": ','.join(gameVersions),  # type: str
            "modLoaders": ','.join(modLoaders),  # type: str
            "downloadLink": mod.downloadUrl,  # type: str
            "fileHash": json.dumps(fileHash)  # type: str
        }

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
