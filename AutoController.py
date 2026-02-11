from statistic import Statistic
from PyQt5.QtCore import QThread, pyqtSignal
from RobotController import RobotController
from ApplictationState import ApplicationState, ModeApplication
from states import AppStates, AppMods, LogOption, LogType
from lightController import LightController
from LogController import LogController



class AutoThread(QThread):
    LogSignal = pyqtSignal(str)
    def __init__(self):
        super().__init__()

    def run(self):
        if AutoController.All_tasks != None and RobotController.robot.engage():
            RobotController.robot
            
            


class AutoController:
    tara1 = 0
    tara2 = 0
    tara3 = 0
    All_tasks = []
    UI = None

    def __init__(self,ui):
        AutoController.UI = ui
        self.thread = None

        self.buttons()

    def buttons(self):
        #self.ClearTars_1.clicked.connect()
        AutoController.UI.add_one.clicked.connect(lambda checkd = False,name = "1_Категория": self.AddElement(name))
        AutoController.UI.add_two.clicked.connect(lambda checkd = False,name = "2_Категория": self.AddElement(name))
        AutoController.UI.add_tree.clicked.connect(lambda checkd = False,name = "3_Категория": self.AddElement(name))
        AutoController.UI.add_brack.clicked.connect(lambda checkd = False,name = "Брак": self.AddElement(name))
        AutoController.UI.deleteElement.clicked.connect(self.deletElement)
        AutoController.UI.clearElements.clicked.connect(self.ClearElements)
        AutoController.UI.ClearTars_1.clicked.connect(lambda checkd = False,numer = 1: self.ClearTars(numer))
        AutoController.UI.ClearTars_2.clicked.connect(lambda checkd = False,numer = 2: self.ClearTars(numer))
        AutoController.UI.ClearTars_3.clicked.connect(lambda checkd = False,numer = 3: self.ClearTars(numer))
        AutoController.UI.StartAutoSort.clicked.connect(self.start)

    @staticmethod
    def AddElement(element: str):
        AutoController.All_tasks.append(element)
        AutoController.UpdateTasks()

    @staticmethod
    def deletElement():
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
        if tar == 2:
            AutoController.tara2 = 0
        if tar == 3:
            AutoController.tara3 = 0


    @staticmethod
    def UpdateTasks():
        AutoController.UI.plainTextEdit_6.clear()
        for i, elemet in enumerate(AutoController.All_tasks):
             AutoController.UI.plainTextEdit_6.appendPlainText(str(i+1) +". " + str(elemet))


    def start(self):
        if ApplicationState.ApplicationState == AppStates.wait and ModeApplication.ModeApplication == AppMods.Auto:
            waypoints = [0,0,0,0,0,0]
            RobotController.MoveToPointJ(waypoints= waypoints)
            """ApplicationState.ApplicationState = AppStates.On
            LightController.update()
            LogController.Log(LogType.INFO, LogOption.Move, "Начало автоматического распределения")
            self.thread = AutoThread()
            self.thread.LogSignal.connect()"""

        
    @staticmethod
    def logUpdater(message):
        LogController.Log(LogType.INFO, LogOption.Move, message )
            
            
        


    
