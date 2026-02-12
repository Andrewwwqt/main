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
import cv2
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import numpy as np
import os
from ultralytics import YOLO
import torch


class VideoThread(QThread):
    ImageUpdate = pyqtSignal(QImage)
    
    def __init__(self, model_path='best.pt'):
        super().__init__()
        self.threadActive = True
        self.model_path = model_path
        self.model = None
        self.confidence = 0.5
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
    def load_model(self):
        try:
            if not os.path.exists(self.model_path):
                return False
            self.model = YOLO(self.model_path)
            
            dummy_input = np.zeros((640, 640, 3), dtype=np.uint8)
            self.model(dummy_input, verbose=False)
            return True
        except:
            return False

    def detect_objects(self, frame):
        if self.model is None:
            return frame
        
        try:
            results = self.model(frame, conf=self.confidence, verbose=False, device=self.device)[0]
            
            if results.boxes is not None and len(results.boxes) > 0:
                boxes = results.boxes.xyxy.cpu().numpy()
                confs = results.boxes.conf.cpu().numpy()
                cls_ids = results.boxes.cls.cpu().numpy()
                
                for i, (box, conf, cls_id) in enumerate(zip(boxes, confs, cls_ids)):
                    x1, y1, x2, y2 = map(int, box)
                    cls_name = results.names[int(cls_id)]

                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                    label = f'{cls_name} {conf:.2f}'
                    (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)

                    cv2.rectangle(frame, (x1, y1-h-5), (x1+w, y1), (0, 255, 0), -1)

                    cv2.putText(frame, label, (x1, y1-5), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
                    
        except:
            pass
        
        return frame
    
    def run(self):
        if not self.load_model():
            pass

        video_path = "11129981897232.mp4"     
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            return
            
        frame_count = 0
        fps_update = 0
        fps_start = cv2.getTickCount()
        
        while self.threadActive:
            ret, frame = cap.read()
            if ret:
                if self.model is not None:
                    frame = self.detect_objects(frame)

                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb.shape
                bytes_per_line = ch * w
                img = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
                scaled_img = img.scaled(640, 480, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.ImageUpdate.emit(scaled_img)
                
                frame_count += 1
                fps_update += 1
                
                if fps_update >= 30:
                    fps_end = cv2.getTickCount()
                    fps = cv2.getTickFrequency() * 30 / (fps_end - fps_start)
                    print(f"FPS: {fps:.1f}", end='\r')
                    fps_update = 0
                    fps_start = cv2.getTickCount()
                
                self.msleep(30)
            else:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                frame_count = 0
    
    def stop(self):
        self.threadActive = False
        self.wait()

class VideoController:
    def __init__(self, ui, model_path='best.pt'):
        self.ui = ui
        self.videoThread = None
        self.model_path = model_path
        self.Buttons()
    
    
    def Buttons(self):
        self.ui.turnCAM.clicked.connect(self.StartVideoPlay)
        self.ui.turnoffCAM.clicked.connect(self.StopVideo)
    
    def StartVideoPlay(self):
        if self.videoThread and self.videoThread.isRunning():
            self.StopVideo()
        
        self.videoThread = VideoThread(self.model_path)
        self.videoThread.ImageUpdate.connect(self.imageUpdate)
        self.videoThread.finished.connect(self.onThreadFinished)
        self.videoThread.start()
    
    def StopVideo(self):
        if self.videoThread and self.videoThread.isRunning():
            self.videoThread.stop()
            self.videoThread = None
    
    def onThreadFinished(self):
        self.videoThread = None
    
    def imageUpdate(self, image):
        if hasattr(self.ui, 'video') and self.ui.video:
            self.ui.video.setPixmap(QPixmap.fromImage(image))
    
    def set_confidence(self, value):
        if self.videoThread:
            self.videoThread.confidence = value / 100.0



class MainController(QMainWindow):
    def __init__(self):
        super().__init__()

        uic.loadUi("main.ui", self)
        
        self.video_controller = VideoController(self)  

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
            RobotMode.RobotMode = RobotModes.JOINT
        else:
            self.changemode.setText("Move L")
            LogController.Log(LogType.INFO, LogOption.Move, "Режим изменен на CARTESIAN MODE")
            self.frame.setVisible(False)
            self.frame_3.setVisible(True)
            RobotMode.RobotMode = RobotModes.CART
        RobotController.ChangeRobotMode()

    def Emergency(self):
        if ApplicationState.ApplicationState != AppStates.Emergency:
            ApplicationState.ApplicationState = AppStates.Emergency
            LightController.update()
            LogController.Log(LogType.INFO, LogOption.Emetgency, "Экстренная остановка")

    def ChangeMode(self):
        if ModeApplication.ModeApplication == AppMods.Manual:
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
            self.outState.setText("Ожидает")
    
    def Disable(self):
        ApplicationState.ApplicationState = AppStates.OFF
        self.ButtonDisable.setEnabled(False)
        self.ButtonEnable.setEnabled(True)
        if RobotController.MoveToStart():
            RobotController.robot.disengage()
        LightController.update()
        LogController.Log(LogType.INFO, LogOption.On, "Выключен")
        self.outState.setText("Выключен")

    def Pause(self):
        if ApplicationState.ApplicationState != AppStates.OFF and ApplicationState.ApplicationState != AppStates.Emergency:
            if ApplicationState.ApplicationState == AppStates.Pause:
                ApplicationState.ApplicationState = AppStates.wait
                LogController.Log(LogType.INFO, LogOption.Pause, "Снят с паузы")
                self.outState.setText("Ожидает")
            else:
                ApplicationState.ApplicationState = AppStates.Pause
                self.outState.setText("Пауза")
                LogController.Log(LogType.INFO, LogOption.Pause, "Поставлен на паузу")
        LightController.update()