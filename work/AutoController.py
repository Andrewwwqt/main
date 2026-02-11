from statistic import Statistic
from PyQt5.QtCore import QThread, pyqtSignal
from RobotController import RobotController
from ApplictationState import ApplicationState, ModeApplication
from states import AppStates, AppMods, LogOption, LogType
from lightController import LightController
from LogController import LogController
from statistic import Statistic
import time 



class AutoThread(QThread):
    LogSignal = pyqtSignal(str)
    secSignal = pyqtSignal(int)
    updateTask = pyqtSignal()
    
    def __init__(self):
        super().__init__()

    def run(self):
        while True:
            if not AutoController.All_tasks:
                break
            task = AutoController.All_tasks.pop(0)
            match(task):
                case "1_Категория":
                    if AutoController.tara1 < 4:
                        self.secSignal.emit(1)
                    else:
                        AutoController.UI.stat_one.setText("Заполнена")
                case "2_Категория":
                    if AutoController.tara2 < 4:
                        self.secSignal.emit(2)
                    else:
                        AutoController.UI.stat_two.setText("Заполнена")
                case "3_Категория":
                    if AutoController.tara3 < 4:
                        self.secSignal.emit(3)
                    else:
                        AutoController.UI.stat_three.setText("Заполнена")
            self.updateTask.emit()
            time.sleep(1)
        ApplicationState.ApplicationState = AppStates.wait
            

class AutoController:
    tara1 = 0
    tara2 = 0
    tara3 = 0
    All_tasks = []
    UI = None

    def __init__(self, ui):
        AutoController.UI = ui
        self.thread = None
        self.buttons()

    def buttons(self):
        AutoController.UI.add_one.clicked.connect(lambda checked=False, name="1_Категория": self.AddElement(name))
        AutoController.UI.add_two.clicked.connect(lambda checked=False, name="2_Категория": self.AddElement(name))
        AutoController.UI.add_tree.clicked.connect(lambda checked=False, name="3_Категория": self.AddElement(name))
        AutoController.UI.add_brack.clicked.connect(lambda checked=False, name="Брак": self.AddElement(name))
        AutoController.UI.deleteElement.clicked.connect(self.deletElement)
        AutoController.UI.clearElements.clicked.connect(self.ClearElements)
        AutoController.UI.ClearTars_1.clicked.connect(lambda checked=False, number=1: self.ClearTars(number))
        AutoController.UI.ClearTars_2.clicked.connect(lambda checked=False, number=2: self.ClearTars(number))
        AutoController.UI.ClearTars_3.clicked.connect(lambda checked=False, number=3: self.ClearTars(number))
        AutoController.UI.StartAutoSort.clicked.connect(self.start)

    @staticmethod
    def AddElement(element: str):
        AutoController.All_tasks.append(element)
        AutoController.UpdateTasks()

    @staticmethod
    def deletElement():
        if len(AutoController.All_tasks) > 0:
            AutoController.All_tasks.pop()
            AutoController.UpdateTasks()

    @staticmethod
    def ClearElements():
        AutoController.All_tasks.clear()
        AutoController.UpdateTasks()

    @staticmethod
    def ClearTars(tar: int):
        if tar == 1:
            AutoController.tara1 = 0
            AutoController.UI.stat_one.setText("Свободна")
        elif tar == 2:
            AutoController.tara2 = 0
            AutoController.UI.stat_two.setText("Свободна")
        elif tar == 3:
            AutoController.tara3 = 0
            AutoController.UI.stat_three.setText("Свободна")

    @staticmethod
    def UpdateTasks():
        AutoController.UI.plainTextEdit_6.clear()
        for i, element in enumerate(AutoController.All_tasks):
            AutoController.UI.plainTextEdit_6.appendPlainText(f"{i+1}. {element}")

    def start(self):
        if ApplicationState.ApplicationState == AppStates.wait and ModeApplication.ModeApplication == AppMods.Auto:
            waypoints = [0,0,0,0,0,0]
            RobotController.MoveToPointJ(waypoints=waypoints)
            ApplicationState.ApplicationState = AppStates.On
            LightController.update()
            LogController.Log(LogType.INFO, LogOption.Move, "Начало автоматического распределения")
            self.thread = AutoThread()
            self.thread.secSignal.connect(self.UpdateUI)
            self.thread.updateTask.connect(self.UpdateTasks)
            self.thread.start()

    @staticmethod
    def UpdateUI(numer):
        if numer == 1:
            Statistic.sec1 += 1
            Statistic.Update()
        elif numer == 2:
            Statistic.sec2 += 1
            Statistic.Update()
        elif numer == 3:
            Statistic.sec3 += 1
            Statistic.Update()