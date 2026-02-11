from AXISCommands import Commands
from states import AppStates, AppMods
from ApplictationState import ApplicationState, ModeApplication
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import QThread
from RobotController import RobotController


class AXISThread(QThread):
    def __init__(self,button):
        super().__init__()
        self.button = button

    def run(self):
        command = Commands[self.button.objectName()][:]

        while(ApplicationState.ApplicationState == AppStates.On):
            print(command)



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
            self.thread = AXISThread(button)
            self.thread.start()


    def ButtonReleased(self):
        if ApplicationState.ApplicationState != AppStates.Emergency and ApplicationState.ApplicationState != AppStates.OFF:
            ApplicationState.ApplicationState = AppStates.wait

        