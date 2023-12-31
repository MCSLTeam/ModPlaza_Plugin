import os.path
import sys

from PyQt5.QtCore import Qt, QThreadPool
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import NavigationItemPosition, InfoBar, InfoBarPosition

from Adapters.Plugin import Plugin
from MCSL2Lib.windowInterface import Window

sys.path.append(os.path.join(os.path.dirname(__file__), "site-packages"))
sys.path.append(os.path.join("./Plugins/ModPlaza_Plugin/"))
from src.ui import ModPlazaStackedWidget, PlazaPage

ModPlaza_Plugin = Plugin()

# init stacked widget
stackedWidget = ModPlazaStackedWidget()
stackedWidget.setObjectName("modPlazaStackedWidget")

# add widgets
stackedWidget.addWidget(PlazaPage(stackedWidget))


def load():
    pass


def enable():
    try:
        Window().addSubInterface(
            stackedWidget, FIF.DOWNLOAD, "ModPlaza", position=NavigationItemPosition.SCROLL
        )
        InfoBar.success(
            title="提示",
            content="ModPlaza 插件已启用。\n如果看不到所有功能，请展开导航栏，\n然后点击“ModPlaza”的“展开”按钮。",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.BOTTOM_LEFT,
            duration=2500,
            parent=Window().pluginsInterface,
        )
    except Exception as e:
        InfoBar.error(
            title="提示",
            content="ModPlaza 插件启用失败。\n请将以下错误信息反馈给插件作者：\n" + str(e),
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.BOTTOM_LEFT,
            duration=2500,
            parent=Window().pluginsInterface,
        )



def disable():
    try:
        Window().navigationInterface.removeWidget(routeKey=stackedWidget.objectName())
        InfoBar.success(
            title="提示",
            content="ModPlaza 插件已禁用。",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.BOTTOM_LEFT,
            duration=2500,
            parent=Window().pluginsInterface,
        )
    except Exception as e:
        InfoBar.error(
            title="提示",
            content="ModPlaza 插件禁用失败。\n请将以下错误信息反馈给插件作者：\n" + str(e),
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.BOTTOM_LEFT,
            duration=2500,
            parent=Window().pluginsInterface,
        )
    stackedWidget.setCurrentIndex(0)
    stackedWidget.currentWidget().deleteSelf()


ModPlaza_Plugin.register_loadFunc(load)
ModPlaza_Plugin.register_enableFunc(enable)
ModPlaza_Plugin.register_disableFunc(disable)
