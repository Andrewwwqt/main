from motion.core import RobotControl
from states import AppStates, AppMods, RobotModes
from ApplictationState import ApplicationState, ModeApplication, RobotMode
from lightController import LightController
import time


class RobotController:
    robot = None
    def __init__(self):
        RobotController.robot = RobotControl(ip= "10.20.6.254")

    @staticmethod
    def Connect():
        if RobotController.robot.connect():
            if RobotController.robot.engage():
                RobotController.robot.manualCartMode()
                RobotMode.RobotMode = RobotModes.CART




    @staticmethod
    def ManualMove(command = [0,0,0,0,0,0]):
        if RobotMode.RobotMode == RobotModes.CART:
            RobotController.robot.setCartesianVelocity(command)
        else:
            RobotController.robot.setJointVelocity(command)

    @staticmethod
    def ChangeRobotMode():
        if RobotMode.RobotMode == RobotModes.CART:
            RobotController.robot.manualJointMode()
            RobotMode.RobotMode = RobotModes.JOINT
        else:
            RobotController.robot.manualCartMode()
            RobotMode.RobotMode = RobotModes.CART

    @staticmethod
    def MoveToStart():
        if RobotController.robot.connect():
           RobotController.robot.moveToInitialPose()
        time.sleep(5)
        if RobotMode.RobotMode == RobotModes.CART:
                RobotController.robot.manualCartMode()
        if RobotMode.RobotMode == RobotModes.JOINT:
            RobotController.robot.manualJointMode()
        LightController.Wait()
        
  
        

        