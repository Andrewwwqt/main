from RobotController import RobotController
from PyQt5.QtCore import QThread, pyqtSignal
from ApplictationState import ApplicationState
from states import AppStates
import math
import time


class StateThread(QThread):
    Signal = pyqtSignal(list,list,list,list,list,bool)
    def __init__(self):
        super().__init__()

    def run(self):
        while(ApplicationState.ApplicationState != AppStates.OFF and ApplicationState.ApplicationState != AppStates.Emergency):
            Temp = RobotController.robot.getActualTemperature()
            rad = RobotController.robot.getMotorPositionRadians()
            tiks = RobotController.robot.getMotorPositionTick()
            grad = []
            ActualToolState = RobotController.robot.getToolState()
            ActualToolPosition = RobotController.robot.getToolPosition()

            for item in rad:
                grad.append(math.degrees(item))

            self.Signal.emit(Temp,rad,tiks,grad,ActualToolPosition,ActualToolState)
            time.sleep(0.2)



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
    def Update(TEMP,RAD,TIKS,GRAD,TOOLPOSE, tool):
        #.setText(str(self.temper[0]) + "\t" + str(self.temper[1]) + "\t" + str(self.temper[2]) + "\t" + str(self.temper[3]) + "\t" + str(self.temper[4]) + "\t" + str(self.temper[5]))
        RobotStates.UI.temp.setText(str(TEMP[0]) + "\t" + str(TEMP[1]) + "\t" + str(TEMP[2]) + "\t" + str(TEMP[3]) + "\t" + str(TEMP[4]) + "\t" + str(TEMP[5]))
        RobotStates.UI.rads.setText(str(round(RAD[0],2)) + "\t" + str(round(RAD[1],2)) + "\t" + str(round(RAD[2],2)) + "\t" + str(round(RAD[3],2)) + "\t" + str(round(RAD[4],2)) + "\t" + str(round(RAD[5],2)))
        RobotStates.UI.tiks.setText(str(round(TIKS[0],2)) + "\t" + str(round(TIKS[1],2)) + "\t" + str(round(TIKS[2],2)) + "\t" + str(round(TIKS[3],2)) + "\t" + str(round(TIKS[4],2)) + "\t" + str(round(TIKS[5],2)))
        RobotStates.UI.grad.setText(str(round(GRAD[0],2)) + "\t" + str(round(GRAD[1],2)) + "\t" + str(round(GRAD[2],2)) + "\t" + str(round(GRAD[3],2)) + "\t" + str(round(GRAD[4],2)) + "\t" + str(round(GRAD[5],2)))
        RobotStates.UI.ActualTool.setText(str(round(TOOLPOSE[0],2)) + "\t" + str(round(TOOLPOSE[1],2)) + "\t" + str(round(TOOLPOSE[2],2)) + "\t" + str(round(TOOLPOSE[3],2)) + "\t" + str(round(TOOLPOSE[4],2)) + "\t" + str(round(TOOLPOSE[5],2)))
        if tool:
            RobotStates.UI.label_55.setText("Закрыт")
        else:
             RobotStates.UI.label_55.setText("Открыт")



        
