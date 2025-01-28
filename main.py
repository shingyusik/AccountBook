import sys
from PyQt5.QtWidgets import QApplication
from src.view import MainWindow
from src.table import Table
from src.controller import MainController

if __name__ == "__main__":
    app = QApplication(sys.argv)
    view = MainWindow()
    controller = MainController(view)
    view.show()
    sys.exit(app.exec_())