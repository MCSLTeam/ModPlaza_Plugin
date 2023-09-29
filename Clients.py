import os

import requests_cache as rqc

from Plugins.Mod_Plaza.CFAPI import KEY
from Plugins.Mod_Plaza.curseforge import CurseForgeAPI

curdir = os.path.abspath(os.path.dirname(__file__))

csesh = rqc.CachedSession(
    os.path.join(curdir, "cache", "CurseForgeAPY-Cache"),
    backend="sqlite",
    expire_after=300
)
CfClient = CurseForgeAPI(KEY, csesh)
