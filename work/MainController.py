from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic
from ApplictationState import ApplicationState, ModeApplication, RobotMode, Toolstate
from states import AppStates, AppMods, RobotModes, LogOption, LogType, Toolstates
from AXISController import AXISController
from RobotController import RobotController
from RobotSates import RobotStates
from lightController import LightController
from LogController import LogController
from statistic import Statistic
from AutoController import AutoController

class MainController(QMainWindow):
    def __init__(self):
        super().__init__()

        uic.loadUi("main.ui", self)


        Statistic(self)
        LightController(self)
        RobotStates(self)
        AXISController(self)
        RobotController()
        LogController(self)
        AutoController(self)

        self.ButtonDisable.setEnabled(False)
        self.tabWidget.setTabVisible(0, False)
        self.tabWidget.setTabVisible(1, False)
        self.tabWidget.setCurrentIndex(0)
        self.frame_3.setVisible(True)
        self.frame.setVisible(False)

        RobotMode.RobotMode = RobotModes.CART
        ApplicationState.ApplicationState = AppStates.OFF
        ModeApplication.ModeApplication = AppMods.Manual
        Toolstate.Toolstate = Toolstates.Open

        self.buttons()

    



    def buttons(self):
        #self.pushobject.clicked.connect()
         self.ButtonEnable.clicked.connect(self.Enable)
         self.ButtonDisable.clicked.connect(self.Disable)
         self.Buttonpause.clicked.connect(self.Pause)
         self.handauto.clicked.connect(self.ChangeMode)
         self.ButtonEmergency.clicked.connect(self.Emergency)
         self.changemode.clicked.connect(self.ChangeRobotMode)
         self.movetostart.clicked.connect(self.MobeToStart)
         self.SaveLogs.clicked.connect(self.savelogs)
         self.pushobject.clicked.connect(self.ToolON)
         self.SaveLogs_2.clicked.connect(self.SaveStat)
         


    def SaveStat(self):
        Statistic.SaveStat()

    def ToolON(self):
        if Toolstate.Toolstate == Toolstates.Open:
            RobotController.robot.toolON()
            Toolstate.Toolstate = Toolstates.Close
            self.pushobject.setText("Открыть")
            LogController.Log(LogType.INFO, LogOption.Move, "Схват закрыт")
            
        else:
            RobotController.robot.toolOFF()
            LogController.Log(LogType.INFO, LogOption.Move, "Схват открыт")
            Toolstate.Toolstate = Toolstates.Open
            self.pushobject.setText("Закрыть")
                
    def savelogs(self):
        LogController.SaveLogs()

    def MobeToStart(self):
        RobotController.MoveToStart()
        LogController.Log(LogType.INFO, LogOption.Move, "Вернулся на старт")


    def ChangeRobotMode(self):
        if RobotMode.RobotMode == RobotModes.CART:
            self.changemode.setText("Move J")
            LogController.Log(LogType.INFO, LogOption.Move, "Режим изменен на JOIN MODE")
            self.frame.setVisible(True)
            self.frame_3.setVisible(False)
        else:
            self.changemode.setText("Move L")
            LogController.Log(LogType.INFO, LogOption.Move, "Режим изменен на CARTESIAN MODE")
            self.frame.setVisible(False)
            self.frame_3.setVisible(True)
        RobotController.ChangeRobotMode()




    def Emergency(self):
        if ApplicationState.ApplicationState != AppStates.Emergency:
            ApplicationState.ApplicationState = AppStates.Emergency
            LightController.update()
            LogController.Log(LogType.INFO, LogOption.Emetgency, "Экстренная остановка")


    def ChangeMode(self):
        if  ModeApplication.ModeApplication == AppMods.Manual:
            ModeApplication.ModeApplication = AppMods.Auto
            self.tabWidget.setCurrentIndex(1)
            LogController.Log(LogType.INFO, LogOption.Mode, "Переключен в автоматический режим")
        else: 
             ModeApplication.ModeApplication = AppMods.Manual
             LogController.Log(LogType.INFO, LogOption.Mode, "Переключен в ручной режим")
             self.tabWidget.setCurrentIndex(0)

        
    def Enable(self):
        if ApplicationState.ApplicationState == AppStates.OFF:
            ApplicationState.ApplicationState = AppStates.wait
            self.ButtonDisable.setEnabled(True)
            self.ButtonEnable.setEnabled(False)
            RobotController.Connect()
            LogController.Log(LogType.INFO, LogOption.On, "Включен")
            RobotStates.RobotStatesRun(RobotStates)
            LightController.update()
    
    def Disable(self):
        ApplicationState.ApplicationState = AppStates.OFF
        self.ButtonDisable.setEnabled(False)
        self.ButtonEnable.setEnabled(True)
        if RobotController.MoveToStart():
            RobotController.robot.disengage()
        LightController.update()
        LogController.Log(LogType.INFO, LogOption.On, "Выключен")

    def Pause(self):
        if ApplicationState.ApplicationState != AppStates.OFF and ApplicationState.ApplicationState != AppStates.Emergency:
            if ApplicationState.ApplicationState == AppStates.Pause:
                ApplicationState.ApplicationState = AppStates.wait
                LogController.Log(LogType.INFO, LogOption.Pause, "Снят с паузы")
                self.outState.setText("Ожидает")
            else:
                ApplicationState.ApplicationState = AppStates.Pause
                self.outState.setText("Пауза")
                LogController.Log(LogType.INFO, LogOption.Pause, "Поставлн на паузу")
        LightController.update()


        
         


    

