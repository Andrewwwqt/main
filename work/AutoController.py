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
    status_message = pyqtSignal(str)
    secSignal = pyqtSignal(int)
    updateTask = pyqtSignal()

    def __init__(self,tasks):
        super().__init__()
        self.tasks = tasks

        self.running = True

        self.PICK_POSITION = [0,0,0,0,0,0]

        self.CONTAINER_1_POSITIONS = [
            [0.3, 0.2, 0.2, 3.14, 0.0, 1.57],
            [0.3, 0.25, 0.2, 3.14, 0.0, 1.57],
            [0.3, 0.2, 0.25, 3.14, 0.0, 1.57],
            [0.3, 0.25, 0.25, 3.14, 0.0, 1.57]
        ]
        
        
        self.CONTAINER_2_POSITIONS = [
            [0.4, -0.2, 0.2, 3.14, 0.0, 1.57],
            [0.4, -0.25, 0.2, 3.14, 0.0, 1.57],
            [0.4, -0.2, 0.25, 3.14, 0.0, 1.57],
            [0.4, -0.25, 0.25, 3.14, 0.0, 1.57]
        ]
        
        
        self.CONTAINER_3_POSITIONS = [
            [0.5, 0.2, 0.2, 3.14, 0.0, 1.57],
            [0.5, 0.25, 0.2, 3.14, 0.0, 1.57],
            [0.5, 0.2, 0.25, 3.14, 0.0, 1.57],
            [0.5, 0.25, 0.25, 3.14, 0.0, 1.57]
        ]


        self.brack_POSITION = [0,0,0,0,0,0]

        self.HOME_POSITION = [0,0,0,0,0,0]

    def run(self):
        try:
            for task in self.tasks:
                if not self.running:
                    break
                
                self.status_message.emit(f"Выполнение задачи: {task}")

                self.status_message.emit("Перемещение к месту захвата")
                waypoint_pick = [self.PICK_POSITION]
                RobotController.robot.addMoveToPointL([waypoint_pick], 0.1, 0.2)
                if RobotController.robot.play():
                    time.sleep(2) 

                self.status_message.emit("Захват объекта")
                if RobotController.robot.toolON():
                    time.sleep(0.5)  

                lift_position = self.PICK_POSITION.copy()
                lift_position[2] += 0.1  
                waypoint_lift = [lift_position]
                RobotController.robot.addMoveToPointL([waypoint_lift], 0.1, 0.2)
                if RobotController.robot.play():
                    time.sleep(1)

                if task.startswith("1"):
                        container_positions = self.CONTAINER_1_POSITIONS
                        container_num = 1
                elif task.startswith("2"):
                        container_positions = self.CONTAINER_2_POSITIONS
                        container_num = 2
                elif task.startswith("3"):
                        container_positions = self.CONTAINER_3_POSITIONS
                        container_num = 3
                else:  
                    self.status_message.emit("Перемещение в зону брака")
                    waypoint_reject = [self.brack_POSITION]
                    RobotController.robot.addMoveToPointL([waypoint_reject], 0.1, 0.2)
                    if RobotController.robot.play():
                        time.sleep(2)

                    RobotController.robot.toolOFF()
                    time.sleep(0.5)
                    self.secSignal.emit(4)
                    self.updateTask.emit()
                    continue

                if container_num == 1:
                    position_index = AutoController.tara1
                elif container_num == 2:
                    position_index = AutoController.tara2
                elif container_num == 3:
                    position_index = AutoController.tara3

                self.status_message.emit(f"Перемещение к таре {container_num} позиция {position_index + 1}")
                waypoint_container = [container_positions[position_index]]
                RobotController.robot.addMoveToPointL([waypoint_container], 0.1, 0.2)
                if RobotController.robot.play():
                    time.sleep(2)

                
                self.status_message.emit("Опускание объекта")
                lower_position = container_positions[position_index].copy()
                lower_position[2] -= 0.05
                waypoint_lower = [lower_position]
                RobotController.robot.addMoveToPointL([waypoint_lower], 0.05, 0.1)
                if RobotController.robot.play():
                    time.sleep(1)
                    
                
                self.status_message.emit("Освобождение объекта")
                RobotController.robot.toolOFF()
                time.sleep(0.5)
                    
                    
                self.status_message.emit("Возврат в исходную позицию")
                waypoint_home = [self.HOME_POSITION]
                RobotController.robot.addMoveToPointL([waypoint_home], 0.1, 0.2)
                if RobotController.robot.play():
                    time.sleep(2)
                    
                self.secSignal.emit(container_num)
                self.updateTask.emit()


        except:
            LogController.Log(LogType.INFO, LogOption.Move, "Ошибка в автоматическом режиме")
            RobotController.robot.stop()
            RobotController.robot.toolOFF()
        
        finally:
            ApplicationState.ApplicationState = AppStates.wait
            LightController.update()

    def stop(self):
        try:
            RobotController.robot.stop()
            RobotController.robot.toolOFF()
        except:
            pass


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
        print(AutoController.All_tasks)
        AutoController.UI.plainTextEdit_6.clear()
        for i, element in enumerate(AutoController.All_tasks):
            AutoController.UI.plainTextEdit_6.appendPlainText(f"{i+1}. {element}")

    def start(self):
        if ApplicationState.ApplicationState == AppStates.wait and ModeApplication.ModeApplication == AppMods.Auto:
            ApplicationState.ApplicationState = AppStates.On
            LightController.update()
            LogController.Log(LogType.INFO, LogOption.Move, "Начало автоматического распределения")
            self.thread = AutoThread(AutoController.All_tasks)
            self.thread.secSignal.connect(self.UpdateUI)
            self.thread.updateTask.connect(self.UpdateTasks)
            self.thread.status_message.connect(self.log)
            self.thread.start()

    @staticmethod
    def log(message):
        LogController.Log(LogType.INFO, LogOption.Move, message)


    @staticmethod
    def UpdateUI(numer):
        if numer == 1:
            AutoController.tara1 +=1
            Statistic.sec1 += 1
            Statistic.Update()
        elif numer == 2:
            AutoController.tara2 +=1
            Statistic.sec2 += 1
            Statistic.Update()
        elif numer == 3:
            AutoController.tara3 +=1
            Statistic.sec3 += 1
            Statistic.Update()
        elif numer == 4:
            Statistic.brack += 1
            Statistic.Update()
