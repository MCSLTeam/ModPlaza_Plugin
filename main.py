import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from Plugins.Mod_Plaza.Clients import vacuum
from ui.plazaPage import PlazaPage

if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    window = PlazaPage(None)
    window.setMinimumHeight(600)
    window.setMinimumWidth(800)
    window.show()
    sys.exit(app.exec_())