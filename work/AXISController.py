from AXISCommands import Commands
from states import AppStates, AppMods,LogOption, LogType
from ApplictationState import ApplicationState, ModeApplication
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import QThread
from RobotController import RobotController
from lightController import LightController
from LogController import LogController
from RobotController import RobotController
from LogController import LogController

class AXISThread(QThread):
    def __init__(self,button, speed):
        super().__init__()
        self.button = button
        self.speed = speed

    def run(self):
        command = Commands[self.button.objectName()][:]

        try:
            position = command.index(1)
            command[position] = int(self.speed) / 10
        except:
            position = command.index(-1)
            command[position] = int(self.speed)* -1 / 10

        while(ApplicationState.ApplicationState == AppStates.On):
            RobotController.ManualMove(command= command)
            



class AXISController:
    UI = None
    def __init__(self,ui):
        AXISController.UI = ui
        self.thread = None

        self.BindButtons()

    def BindButtons(self):
        for button in AXISController.UI.findChildren(QPushButton):
            if button.objectName().startswith("Axis"):
                button.pressed.connect(lambda checkd = False, btn = button: self.ButtonPressed(btn))
                button.released.connect(self.ButtonReleased)

    def ButtonPressed(self,button):
        if ApplicationState.ApplicationState == AppStates.wait and ModeApplication.ModeApplication == AppMods.Manual:
            ApplicationState.ApplicationState = AppStates.On
            self.thread = AXISThread(button, AXISController.UI.speed.text())
            self.thread.start()
            LogController.Log(LogType.INFO, LogOption.Move, f"Начал движение {RobotController.robot.getToolPosition()}")
            LightController.update()


    def ButtonReleased(self):
        if ApplicationState.ApplicationState != AppStates.Emergency and ApplicationState.ApplicationState != AppStates.OFF:
            if ApplicationState.ApplicationState != AppStates.Pause:
                ApplicationState.ApplicationState = AppStates.wait
                LightController.update()
                LogController.Log(LogType.INFO, LogOption.Move, f"Конец движения  {RobotController.robot.getToolPosition()}")

        