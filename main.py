import sys
from PyQt5.QtWidgets import QApplication
from src import MainController, MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    view = MainWindow()
    controller = MainController(view)
    view.show()
    sys.exit(app.exec_())