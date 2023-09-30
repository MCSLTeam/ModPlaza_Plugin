from typing import Dict, List

from PyQt5.QtCore import QSize, Qt, QRect, pyqtSlot
from PyQt5.QtWidgets import (
    QWidget,
    QSizePolicy,
    QGridLayout,
    QHBoxLayout,
    QSpacerItem,
    QFrame, QVBoxLayout,
)
from qfluentwidgets import (
    ComboBox,
    EditableComboBox,
    SearchLineEdit,
    SimpleCardWidget,
    SmoothScrollArea,
    StrongBodyLabel,
    TitleLabel,
)

import Plugins.Mod_Plaza.curseforge.SchemaClasses as schemas
from Plugins.Mod_Plaza.Clients import CfClient
from Plugins.Mod_Plaza.concurrent.curseforgeTask import GetMinecraftInfoManager, CurseForgeSearchBody, \
    MinecraftModSearchManager
from Plugins.Mod_Plaza.curseforge.Utils import getStructureCategories
from Plugins.Mod_Plaza.ui.singleModWidget import SingleModWidget
from Plugins.Mod_Plaza.utils.FetchImageManager import FetchImageManager


class PlazaPage(QWidget):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.setupUI()
        # mod repository
        self.searchSrcComboBox.addItem("CurseForge")
        self.sortTypeComboBox.addItems(schemas.ModSearchSortField._member_names_)

        # curseforge
        # fetch minecraft info
        self.minecraftInfoManager = GetMinecraftInfoManager(CfClient)
        self.minecraftModSearchManager = MinecraftModSearchManager(CfClient)
        self.fetchImageManager = FetchImageManager()

        self.minecraftInfoManager.asyncGetMinecraftInfo().done.connect(self.getCurseForgeInfo)
        # data structure
        self.minecraftVersionMap: Dict[str, schemas.MinecraftGameVersion] = {}
        self.modCategoryMap: Dict[str, schemas.Category] = {}
        self.sortBodyMap: Dict[str, schemas.ModSearchSortField] = {
            name: schemas.ModSearchSortField[name].value for name in schemas.ModSearchSortField._member_names_
        }

        # connect
        self.SearchLineEdit.returnPressed.connect(self.searchMod)
        self.SearchLineEdit.searchButton.clicked.connect(self.searchMod)

    @pyqtSlot(object)
    def getCurseForgeInfo(self, data):
        minecraftVersions: List[schemas.MinecraftGameVersion] = data["minecraftVersions"]
        modCategories: List[schemas.Category] = getStructureCategories(data["modCategories"], 6)  # Mod
        for mcVersion in minecraftVersions:
            self.minecraftVersionMap[mcVersion.versionString] = mcVersion
            self.mcVersionComboBox.addItem(mcVersion.versionString)

        for root in modCategories:
            self.modCategoryMap[root.name] = root
            self.modTypeComboBox.addItem(root.name)
            if root.children:
                for child in root.children:
                    name = f"{root.name} > {child.name}"
                    self.modCategoryMap[name] = child
                    self.modTypeComboBox.addItem(name)
        self.SearchLineEdit.setEnabled(True)

    def getCurrentSearchBody(self) -> CurseForgeSearchBody:
        mcVersion = self.minecraftVersionMap[self.mcVersionComboBox.currentText()]
        modCategory = self.modCategoryMap[self.modTypeComboBox.currentText()]
        sortType = self.sortBodyMap[self.sortTypeComboBox.currentText()]
        sortFilter = self.SearchLineEdit.text().strip()
        return CurseForgeSearchBody(
            minecraftVersion=mcVersion,
            modCategory=modCategory,
            sortType=sortType,
            sortFilter=sortFilter,
            modClassId=schemas.MinecraftClassId.Mod,
            sortOrder=schemas.SortOrder.Descending,
            index=0,
            pageSize=20
        )

    def searchMod(self):
        self.clearWidget()
        future = self.minecraftModSearchManager.asyncSearchMod(self.getCurrentSearchBody())
        future.done.connect(self.onSearchModDone)

    def clearWidget(self):
        while self.resultScrollAreaWidgetContents.layout().count():
            item = self.resultScrollAreaWidgetContents.layout().takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    @pyqtSlot(object)
    def onSearchModDone(self, mods: List[schemas.Mod]):
        for mod in mods:
            widget = SingleModWidget.getWidget(mod, parent=self.resultScrollArea)
            self.resultScrollAreaWidgetContents.layout().addWidget(widget)
            self.fetchImageManager.asyncFetch(
                url=mod.logo.thumbnailUrl,
                target=widget.ModImageRef,
                timeout=3,
            )

    def setupUI(self):
        self.setObjectName("PlazaPage")

        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.gridLayout = QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")

        self.titleLabel = TitleLabel(self)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.titleLabel.sizePolicy().hasHeightForWidth())
        self.titleLabel.setSizePolicy(sizePolicy)
        self.titleLabel.setObjectName("titleLabel")

        self.gridLayout.addWidget(self.titleLabel, 1, 1, 1, 2)
        spacerItem = QSpacerItem(5, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 4, 4, 1)
        spacerItem1 = QSpacerItem(10, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 1, 0, 4, 1)
        spacerItem2 = QSpacerItem(20, 5, QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.gridLayout.addItem(spacerItem2, 5, 1, 1, 3)
        self.searchWidget = SimpleCardWidget(self)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.searchWidget.sizePolicy().hasHeightForWidth())
        self.searchWidget.setSizePolicy(sizePolicy)
        self.searchWidget.setMinimumSize(QSize(0, 180))
        self.searchWidget.setMaximumSize(QSize(16777215, 180))
        self.searchWidget.setObjectName("searchWidget")

        self.gridLayout_2 = QGridLayout(self.searchWidget)
        self.gridLayout_2.setObjectName("gridLayout_2")

        self.sortTypeWidget = QWidget(self.searchWidget)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.sortTypeWidget.sizePolicy().hasHeightForWidth()
        )
        self.sortTypeWidget.setSizePolicy(sizePolicy)
        self.sortTypeWidget.setMinimumSize(QSize(0, 50))
        self.sortTypeWidget.setMaximumSize(QSize(16777215, 50))
        self.sortTypeWidget.setObjectName("sortTypeWidget")

        self.horizontalLayout_2 = QHBoxLayout(self.sortTypeWidget)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")

        self.sortTypeTitle = StrongBodyLabel(self.sortTypeWidget)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.sortTypeTitle.sizePolicy().hasHeightForWidth()
        )
        self.sortTypeTitle.setSizePolicy(sizePolicy)
        self.sortTypeTitle.setObjectName("sortTypeTitle")

        self.horizontalLayout_2.addWidget(self.sortTypeTitle)
        self.sortTypeComboBox = ComboBox(self.sortTypeWidget)
        self.sortTypeComboBox.setObjectName("sortTypeComboBox")

        self.horizontalLayout_2.addWidget(self.sortTypeComboBox)
        self.gridLayout_2.addWidget(self.sortTypeWidget, 2, 0, 1, 6)
        self.mcVersionWidget = QWidget(self.searchWidget)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.mcVersionWidget.sizePolicy().hasHeightForWidth()
        )
        self.mcVersionWidget.setSizePolicy(sizePolicy)
        self.mcVersionWidget.setMinimumSize(QSize(0, 50))
        self.mcVersionWidget.setMaximumSize(QSize(16777215, 50))
        self.mcVersionWidget.setObjectName("mcVersionWidget")

        self.horizontalLayout_3 = QHBoxLayout(self.mcVersionWidget)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")

        self.mcVersionTitle = StrongBodyLabel(self.mcVersionWidget)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.mcVersionTitle.sizePolicy().hasHeightForWidth()
        )
        self.mcVersionTitle.setSizePolicy(sizePolicy)
        self.mcVersionTitle.setObjectName("mcVersionTitle")

        self.horizontalLayout_3.addWidget(self.mcVersionTitle)
        self.mcVersionComboBox = EditableComboBox(self.mcVersionWidget)
        self.mcVersionComboBox.setObjectName("mcVersionComboBox")

        self.horizontalLayout_3.addWidget(self.mcVersionComboBox)
        self.gridLayout_2.addWidget(self.mcVersionWidget, 1, 0, 1, 6)
        self.searchSrcWidget = QWidget(self.searchWidget)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.searchSrcWidget.sizePolicy().hasHeightForWidth()
        )
        self.searchSrcWidget.setSizePolicy(sizePolicy)
        self.searchSrcWidget.setMinimumSize(QSize(0, 50))
        self.searchSrcWidget.setMaximumSize(QSize(16777215, 50))
        self.searchSrcWidget.setObjectName("searchSrcWidget")

        self.horizontalLayout_4 = QHBoxLayout(self.searchSrcWidget)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")

        self.searchSrcTitle = StrongBodyLabel(self.searchSrcWidget)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.searchSrcTitle.sizePolicy().hasHeightForWidth()
        )
        self.searchSrcTitle.setSizePolicy(sizePolicy)
        self.searchSrcTitle.setObjectName("searchSrcTitle")

        self.horizontalLayout_4.addWidget(self.searchSrcTitle)
        self.searchSrcComboBox = ComboBox(self.searchSrcWidget)
        self.searchSrcComboBox.setObjectName("searchSrcComboBox")

        self.horizontalLayout_4.addWidget(self.searchSrcComboBox)
        self.gridLayout_2.addWidget(self.searchSrcWidget, 2, 6, 1, 1)
        self.modTypeWidget = QWidget(self.searchWidget)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.modTypeWidget.sizePolicy().hasHeightForWidth()
        )
        self.modTypeWidget.setSizePolicy(sizePolicy)
        self.modTypeWidget.setMinimumSize(QSize(0, 50))
        self.modTypeWidget.setMaximumSize(QSize(16777215, 50))
        self.modTypeWidget.setObjectName("modTypeWidget")

        self.horizontalLayout = QHBoxLayout(self.modTypeWidget)
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.modTypeTitle = StrongBodyLabel(self.modTypeWidget)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.modTypeTitle.sizePolicy().hasHeightForWidth())
        self.modTypeTitle.setSizePolicy(sizePolicy)
        self.modTypeTitle.setObjectName("modTypeTitle")

        self.horizontalLayout.addWidget(self.modTypeTitle)
        self.modTypeComboBox = ComboBox(self.modTypeWidget)
        self.modTypeComboBox.setObjectName("modTypeComboBox")

        self.horizontalLayout.addWidget(self.modTypeComboBox)
        self.gridLayout_2.addWidget(self.modTypeWidget, 1, 6, 1, 1)
        self.SearchLineEdit = SearchLineEdit(self.searchWidget)
        self.SearchLineEdit.setObjectName("SearchLineEdit")

        self.gridLayout_2.addWidget(self.SearchLineEdit, 4, 0, 1, 7)
        self.gridLayout.addWidget(self.searchWidget, 3, 1, 1, 3)
        spacerItem3 = QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.gridLayout.addItem(spacerItem3, 0, 1, 1, 3)
        spacerItem4 = QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.gridLayout.addItem(spacerItem4, 2, 1, 1, 3)
        self.resultScrollArea = SmoothScrollArea(self)
        self.resultScrollArea.setFrameShape(QFrame.NoFrame)
        self.resultScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.resultScrollArea.setWidgetResizable(True)
        self.resultScrollArea.setAlignment(Qt.AlignLeading | Qt.AlignLeft | Qt.AlignTop)
        self.resultScrollArea.setObjectName("resultScrollArea")

        self.resultScrollAreaWidgetContents = QWidget()
        self.resultScrollAreaWidgetContents.setGeometry(QRect(0, 0, 655, 259))
        self.resultScrollAreaWidgetContents.setObjectName(
            "resultScrollAreaWidgetContents"
        )
        self.resultScrollAreaWidgetContents.setLayout(QVBoxLayout())

        self.resultScrollArea.setWidget(self.resultScrollAreaWidgetContents)
        self.gridLayout.addWidget(self.resultScrollArea, 4, 1, 1, 3)

        self.titleLabel.setText("Mod广场")
        self.sortTypeTitle.setText("排序方式        ")
        self.mcVersionTitle.setText("Minecraft版本")
        self.searchSrcTitle.setText("搜索源  ")
        self.modTypeTitle.setText("分类      ")
        self.SearchLineEdit.setPlaceholderText("支持中英文搜索")

        #
        self.SearchLineEdit.setEnabled(False)
