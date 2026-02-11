from RobotController import RobotController
from PyQt5.QtCore import QThread, pyqtSignal
import math
import time


class StateThread(QThread):
    Signal = pyqtSignal(list,list,list,list)
    def __init__(self):
        super().__init__()

    def run(self):
        while(RobotController.robot.connect()):
            Temp = RobotController.robot.getActualTemperature()
            rad = RobotController.robot.getMotorPositionRadians()
            tiks = RobotController.robot.getMotorPositionTick()
            grad = []
            for item in rad:
                grad.append(math.degrees(item))

            self.Signal.emit(Temp,rad,tiks,grad)
            time.sleep(2)



class RobotStates:
    UI = None
    def __init__(self, ui):
        RobotStates.UI = ui
        self.thread = None


    def RobotStatesRun(self):
        if RobotController.robot.connect():
            self.thread = StateThread()
            self.thread.Signal.connect(self.Update)
            self.thread.start()

    @staticmethod
    def Update(TEMP,RAD,TIKS,GRAD):
        print(TEMP)
        print(RAD)
        print(TIKS)
        print(GRAD)


        
