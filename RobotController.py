from motion.core import RobotControl
from states import AppStates, AppMods, RobotModes
from ApplictationState import ApplicationState, ModeApplication, RobotMode



class RobotController:
    robot = None
    def __init__(self):
        RobotController.robot = RobotControl(ip= "10.20.6.254")

    @staticmethod
    def Connect():
        if RobotController.robot.connect():
            if RobotController.robot.engage():
                RobotController.robot.manualCartMode
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
            RobotController.robot.manualJointMode()
            RobotMode.RobotMode = RobotModes.CART

        