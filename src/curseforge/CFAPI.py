import enum
import sys
from typing import Union, Optional, List, Dict
from urllib.parse import quote

import requests_cache as rqc

from ..curseforge import SchemaClasses as schemas


class CurseForgeAPI(object):
    def __init__(self, api_key, csesh=None, **kwargs) -> None:
        self.__api_key: str = api_key
        self.base_url: str = "https://api.curseforge.com"
        self.__headers: Dict[str, str] = {
            'Content-Type': 'application/json',
            "Accept": "application/json",
            "x-api-key": self.__api_key
        }
        self.csesh = rqc.CachedSession("CurseForgeAPY-Cache", backend="sqlite",
                                       expire_after=300) if csesh is None else csesh
        self.kwargs = kwargs

    def __query_builder(self, func, *params):
        assert type(func) == type(self.getGames), "func must be a function"

        values = {}
        for i, v in enumerate(params):
            if v is not None:
                if isinstance(v, enum.Enum):
                    v = v.value
                values[func.__code__.co_varnames[:func.__code__.co_argcount][i + 1]] = v
        return "?" + "&".join([quote(f"{k}={v}", safe="=") for k, v in values.items()])

    def getGames(self, index: Optional[int] = None, pageSize: Optional[
        int] = None) -> Union[schemas.GetGamesResponse, schemas.ApiResponseCode]:
        """
        get all games from CurseForge

        index: A zero based index of the first item to include in the response, the limit is: (index + pageSize <= 10,000).

        pageSize: The number of items to include in the response, the default/maximum value is 50.
        
        returns GetGamesResponse
        """
        # region init
        # region bounds checking
        if index is not None:
            if not 0 <= index <= 10000:
                return schemas.ApiResponseCode.BadRequest
        if pageSize is not None:
            if not 0 <= pageSize <= 50:
                return schemas.ApiResponseCode.BadRequest
        if index is not None and pageSize is not None:
            if not index + pageSize <= 10000:
                return schemas.ApiResponseCode.BadRequest
        # endregion
        # region this init
        this = eval(f"self.{sys._getframe().f_code.co_name}")
        lvars = []
        for i in this.__code__.co_varnames[:this.__code__.co_argcount][1:]:
            lvars.append(locals()[i])
        # endregion
        url = self.base_url + f"/v1/games{self.__query_builder(this, *lvars)}"
        # endregion

        response = self.csesh.get(url, headers=self.__headers, **self.kwargs)
        status = schemas.ApiResponseCode(response.status_code)

        if status == schemas.ApiResponseCode.OK:
            return schemas.GetGamesResponse(**response.json())
        else:
            return status

    def getGame(self, gameId: int) -> Union[schemas.GetGameResponse, schemas.ApiResponseCode]:
        """
        Get a specific game from CurseForge

        gameId: The id of the game to get

        returns GetGameResponse
        """

        # region init
        # region this init
        this = eval(f"self.{sys._getframe().f_code.co_name}")
        lvars = []
        for i in this.__code__.co_varnames[:this.__code__.co_argcount][1:]:
            lvars.append(locals()[i])
        # endregion
        url = self.base_url + f"/v1/games/{gameId}"
        # endregion

        response = self.csesh.get(url, headers=self.__headers, **self.kwargs)
        status = schemas.ApiResponseCode(response.status_code)

        if status == schemas.ApiResponseCode.OK:
            return schemas.GetGameResponse(**response.json())
        else:
            return status

    def getVersions(self, gameId: int) -> Union[schemas.GetVersionsResponse, schemas.ApiResponseCode]:
        """
        Get all versions for a specific game

        gameId: The id of the game to get versions for

        returns GetVersionsResponse
        """

        # region init
        url = self.base_url + f"/v1/games/{gameId}/versions"
        # endregion

        response = self.csesh.get(url, headers=self.__headers, **self.kwargs)
        status = schemas.ApiResponseCode(response.status_code)

        if status == schemas.ApiResponseCode.OK:
            return schemas.GetVersionsResponse(**response.json())
        else:
            return status

    def getVersionTypes(self, gameId: int) -> Union[schemas.GetVersionTypesResponse, schemas.ApiResponseCode]:
        """
        Get all version types for a specific game

        gameId: The id of the game to get version types for

        returns GetVersionTypesResponse
        """

        # region init
        url = self.base_url + f"/v1/games/{gameId}/version-types"
        # endregion

        response = self.csesh.get(url, headers=self.__headers, **self.kwargs)
        status = schemas.ApiResponseCode(response.status_code)

        if status == schemas.ApiResponseCode.OK:
            return schemas.GetVersionTypesResponse(**response.json())
        else:
            return status

    def getCategories(self, gameId: int, classId: Optional[int] = None, classesOnly: Optional[
        bool] = None) -> Union[schemas.GetCategoriesResponse, schemas.ApiResponseCode]:
        """
        Get all categories for a specific game

        gameId: The id of the game to get categories for
        classId: A unique class ID
        classesOnly: A flag used with gameId to return only classes

        returns GetCategoriesResponse
        """

        # region init
        # region this init
        this = eval(f"self.{sys._getframe().f_code.co_name}")
        lvars = []
        for i in this.__code__.co_varnames[:this.__code__.co_argcount][1:]:
            lvars.append(locals()[i])
        # endregion
        url = self.base_url + f"/v1/categories{self.__query_builder(this, *lvars)}"
        # endregion

        response = self.csesh.get(url, headers=self.__headers, **self.kwargs)
        status = schemas.ApiResponseCode(response.status_code)

        if status == schemas.ApiResponseCode.OK:
            return schemas.GetCategoriesResponse(**response.json())
        else:
            return status

    def searchMods(self, gameId: int, classId: Optional[int] = None, categoryId: Optional[int] = None, gameVersion:
    Optional[str] = None, searchFilter: Optional[str] = None, sortField: Optional[schemas.ModSearchSortField] = None,
                   sortOrder:
                   Optional[schemas.SortOrder] = None, modLoaderType: Optional[schemas.ModLoaderType] = None,
                   gameVersionTypeId:
                   Optional[int] = None, slug: Optional[str] = None, index: Optional[int] = None, pageSize: Optional[
                int] = None) -> Union[schemas.SearchModsResponse, schemas.ApiResponseCode]:
        """
        searches for mods using the given parameters

        gameId: The id of the game to search mods for

        Optional:
        
        classId: A unique class ID
        categoryId: A unique category ID
        gameVersion: A game version
        searchFilter: A search filter
        sortField: A sort field
        sortOrder: A sort order
        modLoaderType: A mod loader type
        gameVersionTypeId: A game version type ID
        slug: A slug
        index: The index of the first result to return
        pageSize: The number of results to return

        returns SearchModsResponse

        """

        # region init
        # region bounds checking
        if index is not None:
            if not 0 <= index <= 10000:
                return schemas.ApiResponseCode.BadRequest
        if pageSize is not None:
            if not 0 <= pageSize <= 50:
                return schemas.ApiResponseCode.BadRequest
        if index is not None and pageSize is not None:
            if not index + pageSize <= 10000:
                return schemas.ApiResponseCode.BadRequest
        # endregion
        # region this init
        this = eval(f"self.{sys._getframe().f_code.co_name}")
        lvars = []
        for i in this.__code__.co_varnames[:this.__code__.co_argcount][1:]:
            lvars.append(locals()[i])
        # endregion
        url = self.base_url + f"/v1/mods/search{self.__query_builder(this, *lvars)}"
        # endregion

        response = self.csesh.get(url, headers=self.__headers, **self.kwargs)
        status = schemas.ApiResponseCode(response.status_code)

        if status == schemas.ApiResponseCode.OK:
            return schemas.SearchModsResponse(**response.json())
        else:
            return status

    def getMod(self, modId: int) -> Union[schemas.GetModResponse, schemas.ApiResponseCode]:
        # region init
        url = self.base_url + f"/v1/mods/{modId}"
        # endregion

        response = self.csesh.get(url, headers=self.__headers, **self.kwargs)
        status = schemas.ApiResponseCode(response.status_code)

        if status == schemas.ApiResponseCode.OK:
            return schemas.GetModResponse(**response.json())
        else:
            return status

    def getMods(self, modIds: Union[
        schemas.GetModsByIdsListRequestBody, List[int]]) -> Union[schemas.GetModsResponse, schemas.ApiResponseCode]:
        # region init
        url = self.base_url + f"/v1/mods"
        # endregion

        if isinstance(modIds, list):
            modIds = schemas.GetModsByIdsListRequestBody(modIds)
        response = self.csesh.post(url, headers=self.__headers, data=str(modIds))
        status = schemas.ApiResponseCode(response.status_code)

        if status == schemas.ApiResponseCode.OK:
            return schemas.GetModsResponse(**response.json())
        else:
            return status

    def getFeatured_mods(self, body: schemas.GetFeaturedModsRequestBody) -> Union[
        schemas.GetFeaturedModsResponse, schemas.ApiResponseCode]:
        # region init
        # endregion
        response = self.csesh.post(self.base_url + '/v1/mods/featured', headers=self.__headers, data=str(body))

        status = schemas.ApiResponseCode(response.status_code)

        if status == schemas.ApiResponseCode.OK:
            return schemas.GetFeaturedModsResponse(**response.json())
        else:
            return status

    def getModDescription(self, modId: int) -> Union[schemas.StringResponse, schemas.ApiResponseCode]:
        # region init
        url = self.base_url + f"/v1/mods/{modId}/description"
        # endregion

        response = self.csesh.get(url, headers=self.__headers, **self.kwargs)
        status = schemas.ApiResponseCode(response.status_code)

        if status == schemas.ApiResponseCode.OK:
            return schemas.StringResponse(**response.json())
        else:
            return status

    def getModFile(self, modId: int, fileId: int) -> Union[schemas.GetModFileResponse, schemas.ApiResponseCode]:
        # region init
        url = self.base_url + f"/v1/mods/{modId}/files/{fileId}"
        # endregion

        response = self.csesh.get(url, headers=self.__headers, **self.kwargs)
        status = schemas.ApiResponseCode(response.status_code)

        if status == schemas.ApiResponseCode.OK:
            return schemas.GetModFileResponse(**response.json())
        else:
            return status

    def getModFiles(self, modId: int, gameVersion: Optional[int] = None, modLoaderType: Optional[
        schemas.ModLoaderType] = None, gameVersionTypeId: Optional[int] = None, index: Optional[int] = None, pageSize:
    Optional[int] = None) -> Union[schemas.GetModFilesResponse, schemas.ApiResponseCode]:
        # region init
        # region bounds checking
        if index is not None:
            if not 0 <= index <= 10000:
                return schemas.ApiResponseCode.BadRequest
        if pageSize is not None:
            if not 0 <= pageSize <= 50:
                return schemas.ApiResponseCode.BadRequest
        if index is not None and pageSize is not None:
            if not index + pageSize <= 10000:
                return schemas.ApiResponseCode.BadRequest
        # endregion
        # region this init
        this = eval(f"self.{sys._getframe().f_code.co_name}")
        lvars = []
        for i in this.__code__.co_varnames[:this.__code__.co_argcount][1:]:
            lvars.append(locals()[i])
        # endregion
        url = self.base_url + f"/v1/mods/{modId}/files{self.__query_builder(this, *lvars)}"
        # endregion

        response = self.csesh.get(url, headers=self.__headers, **self.kwargs)
        status = schemas.ApiResponseCode(response.status_code)

        if status == schemas.ApiResponseCode.OK:
            return schemas.GetModFilesResponse(**response.json())
        else:
            return status

    def getFiles(self, body: schemas.GetModFilesRequestBody) -> Union[
        schemas.GetFilesResponse, schemas.ApiResponseCode]:
        # region init
        # endregion
        response = self.csesh.post(self.base_url + '/v1/mods/files', headers=self.__headers, data=str(body))

        status = schemas.ApiResponseCode(response.status_code)

        if status == schemas.ApiResponseCode.OK:
            return schemas.GetFilesResponse(**response.json())
        else:
            return status

    def getModFileChangelog(self, modId: int, fileId: int) -> Union[schemas.StringResponse, schemas.ApiResponseCode]:
        # region init
        url = self.base_url + f"/v1/mods/{modId}/files/{fileId}/changelog"
        # endregion

        response = self.csesh.get(url, headers=self.__headers, **self.kwargs)
        status = schemas.ApiResponseCode(response.status_code)

        if status == schemas.ApiResponseCode.OK:
            return schemas.StringResponse(**response.json())
        else:
            return status

    def getModFileDownloadUrl(self, modId: int, fileId: int) -> Union[schemas.StringResponse, schemas.ApiResponseCode]:
        # region init
        url = self.base_url + f"/v1/mods/{modId}/files/{fileId}/download-url"
        # endregion

        response = self.csesh.get(url, headers=self.__headers, **self.kwargs)
        status = schemas.ApiResponseCode(response.status_code)

        if status == schemas.ApiResponseCode.OK:
            return schemas.StringResponse(**response.json())
        else:
            return status

    def getFingerprintsMatches(self, body: schemas.GetFingerprintMatchesRequestBody) -> Union[
        schemas.GetFingerprintMatchesResponse, schemas.ApiResponseCode]:
        # region init
        # endregion
        response = self.csesh.post(self.base_url + '/v1/fingerprints/', headers=self.__headers, data=str(body))

        status = schemas.ApiResponseCode(response.status_code)

        if status == schemas.ApiResponseCode.OK:
            return schemas.GetFingerprintMatchesResponse(**response.json())
        else:
            return status

    def getFingerprintsFuzzyMatches(self, body: schemas.GetFuzzyMatchesRequestBody) -> Union[
        schemas.GetFingerprintsFuzzyMatchesResponse, schemas.ApiResponseCode]:
        # region init
        # endregion
        response = self.csesh.post(self.base_url + '/v1/fingerprints/fuzzy', headers=self.__headers, data=str(body))

        status = schemas.ApiResponseCode(response.status_code)

        if status == schemas.ApiResponseCode.OK:
            return schemas.GetFingerprintsFuzzyMatchesResponse(**response.json())
        else:
            return status

    def getMinecraftVersions(self, sortDescending: Optional[
        bool] = None) -> Union[schemas.ApiResponseOfListOfMinecraftGameVersion, schemas.ApiResponseCode]:
        # region init
        # region this init
        this = eval(f"self.{sys._getframe().f_code.co_name}")
        lvars = []
        for i in this.__code__.co_varnames[:this.__code__.co_argcount][1:]:
            lvars.append(locals()[i])
        # endregion
        url = self.base_url + f"/v1/minecraft/version{self.__query_builder(this, *lvars)}"
        # endregion

        response = self.csesh.get(url, headers=self.__headers, **self.kwargs)
        status = schemas.ApiResponseCode(response.status_code)

        if status == schemas.ApiResponseCode.OK:
            return schemas.ApiResponseOfListOfMinecraftGameVersion(**response.json())
        else:
            return status

    def getSpecificMinecraftVersion(self, version: str) -> Union[
        schemas.ApiResponseOfMinecraftGameVersion, schemas.ApiResponseCode]:
        # region init
        url = self.base_url + f"/v1/minecraft/version/{version}"
        # endregion

        response = self.csesh.get(url, headers=self.__headers, **self.kwargs)
        status = schemas.ApiResponseCode(response.status_code)

        if status == schemas.ApiResponseCode.OK:
            return schemas.ApiResponseOfMinecraftGameVersion(**response.json())
        else:
            return status

    def getMinecraftModloaders(self, version: Optional[str] = None, includeAll: Optional[
        bool] = None) -> Union[schemas.ApiResponseOfListOfMinecraftModLoaderIndex, schemas.ApiResponseCode]:
        # region init
        # region this init
        this = eval(f"self.{sys._getframe().f_code.co_name}")
        lvars = []
        for i in this.__code__.co_varnames[:this.__code__.co_argcount][1:]:
            lvars.append(locals()[i])
        # endregion
        url = self.base_url + f"/v1/minecraft/modloader{self.__query_builder(this, *lvars)}"
        # endregion

        response = self.csesh.get(url, headers=self.__headers, **self.kwargs)
        status = schemas.ApiResponseCode(response.status_code)

        if status == schemas.ApiResponseCode.OK:
            return schemas.ApiResponseOfListOfMinecraftModLoaderIndex(**response.json())
        else:
            return status

    def getSpecificMinecraftModloader(self, modLoaderName: str) -> Union[
        schemas.ApiResponseOfMinecraftModLoaderVersion, schemas.ApiResponseCode]:
        # region init
        url = self.base_url + f"/v1/minecraft/modloader/{modLoaderName}"
        # endregion

        response = self.csesh.get(url, headers=self.__headers, **self.kwargs)
        status = schemas.ApiResponseCode(response.status_code)

        if status == schemas.ApiResponseCode.OK:
            return schemas.ApiResponseOfMinecraftModLoaderVersion(**response.json())
        else:
            return status
