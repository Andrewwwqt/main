from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic
from ApplictationState import ApplicationState, ModeApplication, RobotMode
from states import AppStates, AppMods, RobotModes
from AXISController import AXISController
from RobotController import RobotController
from RobotSates import RobotStates
from lightController import LightController

class MainController(QMainWindow):
    def __init__(self):
        super().__init__()

        uic.loadUi("main.ui", self)

        LightController(self)
        RobotStates(self)
        AXISController(self)
        RobotController()

        self.ButtonDisable.setEnabled(False)
        self.tabWidget.setTabVisible(0, False)
        self.tabWidget.setTabVisible(1, False)
        self.tabWidget.setCurrentIndex(0)


        RobotMode.RobotMode = RobotModes.CART
        ApplicationState.ApplicationState = AppStates.OFF
        ModeApplication.ModeApplication = AppMods.Manual

        self.buttons()



    def buttons(self):
        #self..clicked.connect()
         self.ButtonEnable.clicked.connect(self.Enable)
         self.ButtonDisable.clicked.connect(self.Disable)
         self.Buttonpause.clicked.connect(self.Pause)
         self.handauto.clicked.connect(self.ChangeMode)
         self.ButtonEmergency.clicked.connect(self.Emergency)
         self.changemode.clicked.connect(self.ChangeRobotMode)


    def ChangeRobotMode(self):
        if RobotMode.RobotMode == RobotModes.CART:
            self.changemode.setText("JOIN MODE")
        else:
            self.changemode.setText("CARTESIAN MODE")
        RobotController.ChangeRobotMode()




    def Emergency(self):
        if ApplicationState.ApplicationState != AppStates.Emergency:
            ApplicationState.ApplicationState = AppStates.Emergency
            LightController.update()




    def ChangeMode(self):
        if  ModeApplication.ModeApplication == AppMods.Manual:
            ModeApplication.ModeApplication = AppMods.Auto
            self.tabWidget.setCurrentIndex(1)
        else: 
             ModeApplication.ModeApplication = AppMods.Manual
             self.tabWidget.setCurrentIndex(0)

        
    def Enable(self):
        if ApplicationState.ApplicationState == AppStates.OFF:
            ApplicationState.ApplicationState = AppStates.wait
            self.ButtonDisable.setEnabled(True)
            self.ButtonEnable.setEnabled(False)
            RobotController.Connect()
            RobotStates.RobotStatesRun(RobotStates)
            LightController.update()
    
    def Disable(self):
        ApplicationState.ApplicationState = AppStates.OFF
        self.ButtonDisable.setEnabled(False)
        self.ButtonEnable.setEnabled(True)
        RobotController.robot.disengage()
        LightController.update()

    def Pause(self):
        if ApplicationState.ApplicationState != AppStates.OFF and ApplicationState.ApplicationState != AppStates.Emergency:
            if ApplicationState.ApplicationState == AppStates.Pause:
                ApplicationState.ApplicationState = AppStates.wait
                self.outState.setText("Ожидает")
            else:
                ApplicationState.ApplicationState = AppStates.Pause
                self.outState.setText("Пауза")
        LightController.update()


        
         


    

