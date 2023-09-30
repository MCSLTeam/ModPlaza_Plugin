import os
import sqlite3

import requests_cache as rqc

from Plugins.Mod_Plaza.CFAPI import KEY
from Plugins.Mod_Plaza.curseforge import CurseForgeAPI, SchemaClasses as schema

curdir = os.path.abspath(os.path.dirname(__file__))


def vacuum():
    if os.path.exists(db := os.path.join(curdir, "cache", "CurseForgeBlob-Cache")):
        conn = sqlite3.connect(db)
        conn.execute("VACUUM")
        conn.close()
        print("Vacuumed")

    if os.path.exists(db := os.path.join(curdir, "cache", "CurseForgeRequest-Cache")):
        conn = sqlite3.connect(db)
        conn.execute("VACUUM")
        conn.close()
        print("Vacuumed")


shortCachedRequest = rqc.CachedSession(
    os.path.join(curdir, "cache", "CurseForgeRequest-Cache"),
    backend="sqlite",
    expire_after=3600
)
longCachedRequest = rqc.CachedSession(
    os.path.join(curdir, "cache", "CurseForgeBlob-Cache"),
    backend="sqlite",
    expire_after=86400  # 1day
)
CfClient = CurseForgeAPI(KEY, shortCachedRequest, proxies={'http': '127.0.0.1:7890', 'https': '127.0.0.1:7890'})

if __name__ == '__main__':
    classID = schema.MinecraftClassId.Mod
    # categories: List[Category] = CfClient.getCategories(432, classID).data
    # _map = {c.id: c for c in categories}
    # roots = [c for c in categories if c.parentCategoryId == classID]
    # for c in categories:
    #     if c.parentCategoryId != classID:
    #         _map[c.parentCategoryId].children.append(c)
    #
    #
    # def traverse(root: Category, depth=0):
    #     print("\t" * depth, root.name, root.id)
    #     for c in root.children:
    #         traverse(c, depth + 1)
    #
    #
    # for c in roots:
    #     traverse(c)
    data = CfClient.searchMods(
        gameId=432,
        classId=classID,
        sortField=schema.ModSearchSortField.TotalDownloads,
        pageSize=16,
        sortOrder=schema.SortOrder.Descending
    ).data
    for d in data:
        print(d)
    print(666)
