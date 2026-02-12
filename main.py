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


"""
pip uninstall torch torchvision torchaudio ultralytics numpy opencv-python -y
pip cache purge

pip install numpy==1.24.3
pip install torch==2.0.1 torchvision==0.15.1 --index-url https://download.pytorch.org/whl/cpu
pip install opencv-python==4.8.1.78
pip install ultralytics==8.0.200
"""