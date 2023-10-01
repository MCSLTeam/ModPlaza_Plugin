"""
使用dict作为缓存的管理器
并使用pickle模块将dict序列化
"""
import enum
import json
import os.path
import _pickle as pickle
import time
from typing import Dict, Union, Optional, List

from PyQt5.QtCore import QReadWriteLock


class EntryType(enum.Enum):
    Entry = "ENTRY"
    Table = "TABLE"


class SerializableReadWriteLock:
    def __init__(self):
        self.lock = QReadWriteLock()

    def __getstate__(self):
        return {}

    def __setstate__(self, state):
        self.lock = QReadWriteLock()

    def __getattr__(self, item):
        return getattr(self.lock, item)


class CacheTableError(BaseException):
    pass


class ParentAlreadySet(CacheTableError):
    def __init__(self):
        super().__init__("Parent already set")


class ParentNotFound(CacheTableError):
    def __init__(self, parent: 'CacheEntryTable'):
        super().__init__(f"Parent not found: {parent}")


class EntryNotFound(CacheTableError):
    def __init__(self, entryName: str, entryType: enum.Enum):
        super().__init__(f"{entryType.value} not found: {entryName}")


class TableNotFound(CacheTableError):
    def __init__(self, tableName: str):
        super().__init__(f"Table not found: {tableName}")


class InvalidEntryType(CacheTableError):
    def __init__(self, entryName: str, entryType: enum.Enum):
        super().__init__(f"invalid entry type ({entryName}): {entryType.value}")


class InvalidEntryName(CacheTableError):
    def __init__(self, entryName: str):
        super().__init__(f"invalid entry name: {entryName}")


class EntryMixin:
    def __init__(self, _type: EntryType):
        self.__parent: Optional[CacheEntryTable] = None
        self.__parentFlag = False
        self.__entryType = _type

    def setParent(self, parent: 'CacheEntryTable'):
        """
        Set the parent of the entry
        :param parent: The parent of the entry

        :raise ParentAlreadySetError: If the parent is already set
        """
        if self.__parentFlag:
            raise ParentAlreadySet
        self.__parent = parent

    def hasParent(self) -> bool:
        """
        Check if the entry has a parent
        :return: Whether the entry has a parent
        """
        return self.__parentFlag

    def getSize(self):
        raise NotImplementedError

    @property
    def parent(self) -> Optional['CacheEntryTable']:
        if p := self.__parent:
            raise ParentNotFound
        return p

    @property
    def entryType(self) -> EntryType:
        return self.__entryType


class CacheEntry(EntryMixin):
    def __init__(self, key, value, expireTime=3600):
        """
        :param key: The key of the cache entry
        :param value: The value of the cache entry
        :param expireTime: The expire time of the cache entry (in seconds)
        """
        super().__init__(EntryType.Entry)
        self.key = key
        self.value = value
        self.expireTime = expireTime + int(time.time())

    def __copy__(self):
        rv = CacheEntry(self.key, self.value)
        rv.expireTime = self.expireTime
        return rv

    def dump(self):
        return {
            "key": self.key,
            "value": str(self.value[:10]) + "...",
            "expireTime": self.expireTime
        }

    def isExpired(self) -> bool:
        """
        Check if the entry is expired
        :return: Whether the entry is expired
        """
        return self.expireTime < time.time()

    def getSize(self):
        return len(self.value)


class CacheDBUtils:
    @staticmethod
    def checkEntryNameValid(name: str) -> bool:
        return not name.startswith(".") and not name.startswith("_") and not name.startswith("$")


class CacheEntryTable(EntryMixin):
    """
    {
        "TABLE_NAME1": {...},
        "TABLE_NAME2": {...},
        "ENTRY_NAME1": <class: CacheEntry>,
        "ENTRY_NAME2": <class: CacheEntry>,
    }

    {
        "TABLE_NAME1": <class: SerializableReadWriteLock>,
        "TABLE_NAME2": <class: SerializableReadWriteLock>,
        "ENTRY_NAME1": <class: SerializableReadWriteLock>,
        "ENTRY_NAME2": <class: SerializableReadWriteLock>,
    }
    """

    def __init__(self, tableName: str, defaultExpireTime=3600):
        super().__init__(EntryType.Table)
        self.tableName = tableName
        self.table: Dict[str, Union[CacheEntry, CacheEntryTable]] = {}
        self.indexLockers: Dict[str, SerializableReadWriteLock] = {}
        self.__defaultExpireTime = defaultExpireTime

    def __addNested(self, keys: List[str], value: bytes, _type: EntryType, expiredTime: int, default: bool,
                    replace: bool) -> bool:
        """
        Add a nested entry to the table
        :param keys: The keys to add the entry to: [key1, key2, key3, ...] -> key1[key2[key3[...]]]
        :param value: The entry to add
        :param _type: The type of the entry,if the entry is a table, entry will be ignored
        :param expiredTime: The expired time of the entry
        :param default: Whether to create the table if not found
        :param replace: Whether to force add the entry
        :return: Whether the entry is added successfully

        :raise CacheTableError: If the table is not found
        """
        if len(keys) == 1:
            return self._add(keys[0], _type, value, expiredTime, replace)
        else:

            if self.has(keys[0], EntryType.Table):
                return self.__get(keys[0], EntryType.Table).__addNested(keys[1:], value, _type, expiredTime, default,
                                                                        replace)
            else:
                if default:
                    self.createTable(keys[0])
                    table = self.__get(keys[0], EntryType.Table)
                else:
                    raise TableNotFound(keys[0])
                return table.__addNested(keys[1:], value, _type, expiredTime, default, replace)

    def __getNested(self, keys: List[str], _type: EntryType) -> Union[
        CacheEntry, 'CacheEntryTable']:
        """
        Get a nested entry from the table
        :param keys: The keys to get the entry from: [key1, key2, key3, ...] -> key1[key2[key3[...]]]
        :param _type: The type of the entry
        :return: The entry

        :raise CacheTableError: If the table is not found
        """
        if not keys:
            return self
        if len(keys) == 1:
            return self.__get(keys[0], _type)
        else:
            if self.has(keys[0], EntryType.Table):
                return self.__get(keys[0], EntryType.Table).__getNested(keys[1:], _type)
            else:
                raise CacheTableError(f"Table not found: {keys[0]}")

    def __get(self, key, _type: EntryType = EntryType.Entry) -> Union[CacheEntry, 'CacheEntryTable']:
        """
        Get an entry from the table
        :param key: The key of the entry
        :param _type: The type of the entry
        :return: The entry
        """
        if key == '..' and _type == EntryType.Table:
            return self.parent
        elif key == '.' and _type == EntryType.Table:
            return self
        elif key not in {'.', '..'}:

            (locker := self.getLocker(key, _type)).lockForRead()
            rv = self.table[f"{_type.value}_{key}"]
            locker.unlock()

            return rv
        else:
            raise InvalidEntryType(key, _type)

    def __has(self, key, _type):
        if key == '.' and _type == EntryType.Table:
            return True
        elif key == '..' and _type == EntryType.Table:
            return self.hasParent()
        elif key not in {'.', '..'}:
            return f"{_type.value}_{key}" in self.table

    def __hasNested(self, keys, _type):
        key = keys[0]
        if len(keys) == 1:
            return self.__has(key, _type)
        else:
            if self.__has(key, EntryType.Table):
                return self.__get(key, EntryType.Table).__hasNested(keys[1:], _type)

    def _addEntry(self, entry: CacheEntry, replace=False) -> bool:
        """
        Add an entry to the table
        :param entry: The entry to add
        :param replace: Whether to force add the entry, if enabled, the entry will be added even if the entry already exists
        :return: Whether the entry is added successfully
        """
        (locker := self.getLocker(entry.key, EntryType.Entry)).lockForWrite()

        if entry.key in self.table and not replace:
            locker.unlock()
            return False

        self.table[f"ENTRY_{entry.key}"] = entry
        locker.unlock()
        entry.setParent(self)
        return True

    def _addTableTree(self, table: 'CacheEntryTable', replace=False) -> bool:
        """
        Add a table to the table
        :param table: The table to add
        :param replace: Whether to force add the table, if enabled, the table will be added even if the table already exists
        :return: Whether the table is added successfully

        :raise ParentAlreadySetError: If the table already has a parent
        """
        (locker := self.getLocker(table.tableName, EntryType.Table)).lockForWrite()

        if table.tableName in self.table and not replace:
            locker.unlock()
            return False

        self.table[f"TABLE_{table.tableName}"] = table
        locker.unlock()
        table._tableLockRef = locker
        table.setParent(self)
        return True

    def _add(self, key: str, _type: EntryType, value: Optional[bytes] = None, expiredTime: Optional[int] = None,
             replace=False) -> bool:
        """
        Add an entry or a table to the table
        :param key: The key of the entry or the table
        :param value: The value of the entry or the table
        :param _type: The type of the entry or the table
        :param expiredTime: The expired time of the entry
        :param replace: Whether to force add the entry or the table, if enabled, the entry or the table will be added even if the entry or the table already exists
        :return: Whether the entry or the table is added successfully
        """
        expiredTime = self.defaultExpireTime if expiredTime is None else expiredTime
        if _type == EntryType.Entry:
            return self._addEntry(CacheEntry(key, value, expiredTime), replace)
        elif _type == EntryType.Table:
            return self.createTable(key, replace)
        else:
            raise InvalidEntryType(key, _type)

    def _pop(self, key, _type) -> Union[CacheEntry, 'CacheEntryTable']:
        if key == '..' and _type == EntryType.Table:
            return self.parent.parent._pop(self.parent.tableName, _type)
        elif key == '.' and _type == EntryType.Table:
            if self.parent is None:
                raise CacheTableError("Cannot pop root table")
            return self.parent._pop(self.tableName, _type)
        elif key not in {'.', '..'}:
            (locker := self.getLocker(key, _type)).lockForWrite()
            rv = self.table.pop(f"{_type.value}_{key}")
            locker.unlock()
            self.indexLockers.pop(f"{_type.value}_{key}")
            return rv
        else:
            raise InvalidEntryType(key, _type)

    def addRecord(self, key: str, value, expiredTime: Optional[int] = None, replace: bool = False) -> bool:
        """
        Add an entry to the table
        :param key: The key of the entry
        :param value: The value of the entry
        :param replace: Whether to force add the entry, if enabled, the entry will be added even if the entry already exists
        :param expiredTime: The expired time of the entry
        :return: Whether the entry is added successfully
        """
        expiredTime = self.defaultExpireTime if expiredTime is None else expiredTime
        if not CacheDBUtils.checkEntryNameValid(key):
            raise InvalidEntryName(key)
        return self.addNested(key, value, EntryType.Entry, expiredTime, True, replace)

    def createTable(self, tableName: str, replace=False) -> bool:
        """
        Create a table
        :param tableName: The name of the table
        :param replace: Whether to force create the table, if enabled, the table will be created even if the table already exists
        :return: Whether the table is created successfully
        """
        if not CacheDBUtils.checkEntryNameValid(tableName):
            raise InvalidEntryName(tableName)
        (locker := self.getLocker(tableName, EntryType.Table)).lockForWrite()

        if tableName in self.table and not replace:
            locker.unlock()
            return False
        table = CacheEntryTable(tableName, self.defaultExpireTime)
        self.table[f"TABLE_{tableName}"] = table
        locker.unlock()
        table.setParent(self)
        return True

    def has(self, key, _type: EntryType = EntryType.Entry) -> bool:
        """
        Check if the table has an entry
        :param key: The key of the entry
        :param _type: The type of the entry
        :return: Whether the entry is found
        """
        keys = self.convertToKeys(key)
        return self.__hasNested(keys, _type)

    def getRecord(self, key: str) -> bytes:
        """
        Get a record from the table
        :param key: The key of the record
        :return: The record

        :raise CacheTableError: If the record is not found
        """
        keys = self.convertToKeys(key)

        return self.__getNested(keys, EntryType.Entry).value

    def isEntryExpired(self, key: str) -> bool:
        """
        Check if an entry is expired
        :param key: The key of the entry
        :return: Whether the entry is expired
        """
        try:
            return self.getNested(key, EntryType.Entry).isExpired()
        except CacheTableError:
            return True

    def pop(self, key, _type: EntryType) -> Union[CacheEntry, 'CacheEntryTable']:
        """
        Pop an entry from the table
        :param key: The key of the entry
        :param _type: The type of the entry
        :return: The entry, or None if not found

        raise CacheTableError: If the entry is not found,or the entry is the root table
        """
        keys = self.convertToKeys(key)
        return self.__getNested(keys[:-1], EntryType.Table)._pop(keys[-1], _type)

    def addNested(self, key: str, value: bytes, _type: EntryType, expiredTime: Optional[int] = None,
                  default: bool = True, replace: bool = False) -> bool:
        """
        Add a nested entry to the table
        :param key: The key to add the entry to: key1/key2/key3/... -> key1[key2[key3[...]]]
        :param value: The entry to add
        :param _type: The type of the entry,if the entry is a table, entry will be ignored
        :param expiredTime: The expired time of the entry
        :param default: Whether to create the table if not found
        :param replace: Whether to force add the entry
        :return: Whether the entry is added successfully

        :raise CacheTableError: If the table is not found
        :raise InvalidEntryName: If the entry name is invalid
        """
        if not CacheDBUtils.checkEntryNameValid(key):
            raise InvalidEntryName(key)
        expiredTime = self.defaultExpireTime if expiredTime is None else expiredTime
        return self.__addNested(self.convertToKeys(key), value, _type, expiredTime, default, replace)

    def getNested(self, key: str, _type: EntryType) -> Union[CacheEntry, 'CacheEntryTable']:
        """
        Get a nested entry from the table
        :param key: The key to get the entry from: key1/key2/key3/... -> key1[key2[key3[...]]]
        :return: The entry

        :raise CacheTableError: If the table is not found
        """
        return self.__getNested(self.convertToKeys(key), _type)

    def vacuum(self):
        items = list(self.table.items())
        for key, value in items:
            if isinstance(value, CacheEntry):
                if value.isExpired():
                    self._pop(key[6:], EntryType.Entry)
            elif isinstance(value, CacheEntryTable):
                if value.isEmpty():
                    self._pop(key[6:], EntryType.Table)
                else:
                    value.vacuum()
                    if value.isEmpty():
                        self._pop(key[6:], EntryType.Table)
            else:
                raise InvalidEntryType(key, value.entryType)

    def getSize(self):
        size = 0
        for key, value in self.table.items():
            if isinstance(value, CacheEntry):
                size += value.getSize()
            elif isinstance(value, CacheEntryTable):
                size += value.getSize()
            else:
                raise InvalidEntryType(key, value.entryType)
        return size

    def isEmpty(self):
        if self.table == {}:
            return True

    def copy(self):
        return self.__copy__()

    def dump(self):
        table = {}
        for key, value in self.table.items():
            if isinstance(value, CacheEntry):
                table[key] = value.dump()
            elif isinstance(value, CacheEntryTable):
                table[key] = value.dump()
            else:
                raise InvalidEntryType(key, value.entryType)
        return table

    def getLocker(self, key: str, _type: EntryType) -> SerializableReadWriteLock:
        """
        Get the locker of an entry
        :param key: The key of the entry
        :param _type: The type of the entry
        :return: The locker of the entry
        """
        lockerName = f"{_type.value}_{key}"
        if lockerName not in self.indexLockers:
            self.indexLockers[lockerName] = SerializableReadWriteLock()
        return self.indexLockers[lockerName]

    def dispatcher(self, method: str, **kwargs):
        getattr(self, method)(**kwargs)

    @property
    def defaultExpireTime(self) -> int:
        return self.__defaultExpireTime

    @staticmethod
    def convertToKeys(key: str) -> List[str]:
        return os.path.normpath(key).split(os.sep)

    def __iter__(self):
        return self.table.__iter__()

    def __copy__(self):
        newTable = CacheEntryTable(self.tableName, self.defaultExpireTime)
        for key, value in self.table.items():
            if isinstance(value, CacheEntry):
                newTable._addEntry(value.__copy__())
            elif isinstance(value, CacheEntryTable):
                newTable._addTableTree(value.__copy__())
            else:
                raise InvalidEntryType(key, value.entryType)
        return newTable

    def __deepcopy__(self):
        return self.__copy__()


class CacheDB:

    def __init__(self, filename: str, defaultExpireTime=3600):
        self.defaultExpireTime = defaultExpireTime
        self.filename = filename
        self.root: CacheEntryTable = CacheEntryTable(
            "$ROOT$",
            defaultExpireTime=self.defaultExpireTime
        )
        if os.path.exists(self.filename):
            self.__deserialize()
        self.__isOpening = True

    def __serialize(self):
        with open(self.filename, "wb") as f:
            try:
                pickle.dump(self.root, f)
                self.root._defaultExpireTime = self.defaultExpireTime
            except BaseException as e:
                print(e)

    def __deserialize(self):
        with open(self.filename, "rb") as f:
            self.root = pickle.load(f)

    def save(self):
        """
        Save the database to disk
        """
        if self.__isOpening:
            self.__serialize()

    def close(self):
        """
        Close the database
        """
        self.save()
        self.__isOpening = False

    def isOpening(self):
        """
        Check if the database is opening
        """
        return self.__isOpening

    def vacuum(self):
        """
        Remove all expired entries, and remove all empty tables
        """
        self.root.vacuum()

    def json(self):
        """
        dump database structure to json
        """
        return json.dumps(self.root.dump(), indent=4, ensure_ascii=False, sort_keys=True)

    def dumpToJson(self, filename: str):
        """
        dump database structure to json file
        """
        with open(filename, "w") as f:
            json.dump(self.root.dump(), f, indent=4, ensure_ascii=False, sort_keys=True)

    # def __del__(self):
    #     self.close()


if __name__ == '__main__':
    # db = CacheDB("test.cache")
    # db.root.addRecord("test/1/2", b"test", expiredTime=1)
    # db.root.addRecord("test/1/2/3", b"test")
    # db.root.addRecord("test2/1/2/3", b"test2")
    # db.root.addRecord("test3/test3", b"test3")
    # print(db.root.has("test3/../test3/test3"))
    # print(db.root.pop("test3/../test3/test3", EntryType.Entry).value)
    # # print(db.root.pop("test2", EntryType.Table))
    # print(db.root.pop("test2/1/2/3", EntryType.Entry))
    # time.sleep(1)
    # print(">>> before vacuum\n")
    # print(db.json())
    # print(">>> after vacuum\n")
    # db.root.vacuum()
    # print(db.json())
    # print(db.root.pop("..", EntryType.Table))
    # db.close()
    db = CacheDB("../cache/curseforge.cache")
    print(db.json())
    db.close()
