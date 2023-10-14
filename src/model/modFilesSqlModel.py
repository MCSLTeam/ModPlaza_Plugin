import typing

from PyQt5.QtSql import QSqlTableModel, QSqlDatabase, QSqlQuery

from . import ModFileEntry
from ..curseforge import SchemaClasses as schemas
from ..managers import minecraftModFileEntriesManager


class ModFilesSqlModel(QSqlTableModel):
    def __init__(self, parent=None, db: QSqlDatabase = ...) -> None:
        super().__init__(parent=parent, db=db)
        self.mod = None

    def onModFilesGot(self, modList: typing.List[schemas.File]):
        self.beginResetModel()
        self.setTable("modFiles")

        # add data
        self.database().transaction()
        sql = QSqlQuery(db=self.database())

        sql.prepare(
            f"INSERT INTO modFiles VALUES ({', '.join(['?' for _ in range(8)])})"
        )
        for mod in modList:
            serialized = ModFileEntry.serialize(mod)
            sql.addBindValue(serialized["releaseType"])
            sql.addBindValue(serialized["name"])
            sql.addBindValue(serialized["uploadedTime"])
            sql.addBindValue(serialized["size"])
            sql.addBindValue(serialized["gameVersions"])
            sql.addBindValue(serialized["modLoaders"])
            sql.addBindValue(serialized["downloadLink"])
            sql.addBindValue(serialized["fileHash"])

            sql.exec()
            if sql.lastError().isValid():
                print(self.__class__.__name__, sql.lastError().text())
                break
        self.database().commit()
        self.select()
        self.endResetModel()
        self.submitAll()

    def delete(self):
        self.database().close()
        QSqlDatabase.removeDatabase(self.database().connectionName())

    @staticmethod
    def getModel(mod: schemas.Mod):
        model = ModFilesSqlModel(db=ModFilesSqlModel.getDb())
        model.setTable("modFiles")
        fut = minecraftModFileEntriesManager.asyncGetModFiles(mod.id)
        fut.result.connect(model.onModFilesGot)
        model.select()
        return model

    @staticmethod
    def getDb():
        """
        {
            "releaseType": getReleaseTypeString(mod.releaseType),  # type: str
            "name": mod.displayName,  # type: str
            "uploadedTime": (mod.fileDate).split("T")[0],  # type: str
            "size": getFormatFileSizeString(mod.fileLength),  # type: str
            "gameVersions": ','.join(gameVersions),  # type: str
            "modLoaders": ','.join(modLoaders),  # type: str
            "downloadLink": mod.downloadUrl,  # type: str
            "fileHash": json.dumps(fileHash)  # type: str
        }
        """
        db = QSqlDatabase().addDatabase("QSQLITE", )
        db.setDatabaseName(":memory:")
        db.open()
        sql = QSqlQuery(db=db)
        sql.exec(
            "CREATE TABLE modFiles ("
            "releaseType TEXT, "
            "name TEXT, "
            "uploadedTime TEXT, "
            "size TEXT, "
            "gameVersions TEXT, "
            "modLoaders TEXT, "
            "downloadLink TEXT, "
            "fileHash TEXT,"
            "PRIMARY KEY (downloadLink)"
            ")"
        )
        return db
