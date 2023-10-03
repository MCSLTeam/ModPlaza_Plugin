import os
import sqlite3

import requests_cache as rqc

try:
    from .CFAPI import __KEY__
except ImportError:
    pass
from ..curseforge import CurseForgeAPI

curdir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


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
# shortCachedRequest.cache.delete(expired=True)
longCachedRequest = rqc.CachedSession(
    os.path.join(curdir, "cache", "CurseForgeBlob-Cache"),
    backend="sqlite",
    expire_after=86400  # 1day
)
# longCachedRequest.cache.delete(expired=True)
CfClient = CurseForgeAPI('$2a$10$/19NYVOIjJEhtKjWg.BhPOVc4HgaekvbZoVi0Pxs9b79dOSjtTCNC', shortCachedRequest)
