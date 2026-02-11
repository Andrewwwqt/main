from PyQt5.QtWidgets import QApplication
from MainController import MainController
import sys

def run():
    app = QApplication(sys.argv)
    window = MainController()
    window.show()
    exit(app.exec_())
    

if __name__ == "__main__":
    run()