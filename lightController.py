from motion.core import LedLamp
from ApplictationState import ApplicationState
from states import AppStates

class LightController:
    ui = None
    ledLamp = None

    def __init__(self,ui):
        LightController.ui = ui
        LightController.ledLamp = LedLamp('192.168.1.211')
        LightController.ledLamp.setLamp('0000')
    
    @staticmethod
    def Off():
        if LightController.ui != None:
            LightController.ui.outState.setText("Выключен")
            LightController.ui.outState.setStyleSheet("color: rgb(0, 0, 0);")
        if LightController.ledLamp != None:
            LightController.ledLamp.setLamp("0000")

    @staticmethod
    def Wait():
        if LightController.ui != None:
            LightController.ui.outState.setText("Ожидание")
            LightController.ui.outState.setStyleSheet("color: rgb(0, 0, 0);")
        if LightController.ledLamp != None:
            LightController.ledLamp.setLamp("1000")

    @staticmethod
    def Active():
        if LightController.ui != None:
            LightController.ui.outState.setText("Работает")
            LightController.ui.outState.setStyleSheet("color: rgb(0, 0, 0);")
        if LightController.ledLamp != None:
            LightController.ledLamp.setLamp("0100")

    @staticmethod
    def Emergency():
        if LightController.ui != None:
            LightController.ui.outState.setText("Экстренная остановка!")
            LightController.ui.outState.setStyleSheet("color: rgb(255, 0, 0);")
        if LightController.ledLamp != None:
            LightController.ledLamp.setLamp("0001")


    @staticmethod
    def Pause():
        if LightController.ui != None:
            LightController.ui.outState.setStyleSheet("color: rgb(0, 0, 0);")
        if LightController.ledLamp != None:
            LightController.ledLamp.setLamp("0010")

    @staticmethod
    def update():
        match(ApplicationState.ApplicationState):
            case AppStates.OFF:
                LightController.Off()
            case AppStates.wait:
                LightController.Wait()
            case AppStates.On:
                LightController.Active()
            case AppStates.Emergency:
                LightController.Emergency()
            case AppStates.Pause:
                LightController.Pause()

    