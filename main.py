import os.path
import sys

from PyQt5.QtWidgets import QApplication

if __name__ == '__main__':
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "site-packages")))
    import src

    app = QApplication(sys.argv)
    window = src.PlazaPage(None)
    window.setMinimumHeight(600)
    window.setMinimumWidth(800)
    window.show()
    sys.exit(app.exec_())
