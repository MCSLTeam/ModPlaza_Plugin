import json
import os
from typing import List

import requests_cache as rqc

from Plugins.Mod_Plaza.CFAPI import KEY
from Plugins.Mod_Plaza.curseforge import CurseForgeAPI, SchemaClasses as schema, Category

curdir = os.path.abspath(os.path.dirname(__file__))

csesh = rqc.CachedSession(
    os.path.join(curdir, "cache", "CurseForgeAPY-Cache"),
    backend="sqlite",
    expire_after=300
)
CfClient = CurseForgeAPI(KEY, csesh, proxies={'http': '127.0.0.1:7890', 'https': '127.0.0.1:7890'})

if __name__ == '__main__':
    classID = schema.MinecraftClassId.ResourcePack
    categories: List[Category] = CfClient.getCategories(432, classID).data
    _map = {c.id: c for c in categories}
    roots = [c for c in categories if c.parentCategoryId == classID]
    for c in categories:
        if c.parentCategoryId != classID:
            _map[c.parentCategoryId].children.append(c)

    def traverse(root: Category, depth=0):
        print("\t" * depth, root.name, root.id)
        for c in root.children:
            traverse(c, depth + 1)

    for c in roots:
        traverse(c)
