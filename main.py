import sys

from PyQt5.QtWidgets import QApplication

from src.ui.plazaPage import PlazaPage

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PlazaPage(None)
    window.setMinimumHeight(600)
    window.setMinimumWidth(800)
    window.show()
    sys.exit(app.exec_())
