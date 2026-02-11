from states import LogOption, LogType
from datetime import datetime
from ApplicationCFG import AppCFG


class LogController:
    UI = None
    LOGS = []
    def __init__(self,ui):
        LogController.UI = ui


    @staticmethod
    def Log(type: LogType, area: LogOption, message: str):
        out_message = str(datetime.now()) + " " +type.name + " - " + message
        LogController.LOGS.append(out_message)

        match(area):
            case LogOption.On:
                LogController.UI.plainTextEdit.appendPlainText(out_message)
            case LogOption.Pause:
                LogController.UI.plainTextEdit_4.appendPlainText(out_message)
            case LogOption.Emetgency:
                LogController.UI.plainTextEdit_5.appendPlainText(out_message)
            case LogOption.Mode:
                LogController.UI.plainTextEdit_2.appendPlainText(out_message)
            case LogOption.Move:
                LogController.UI.plainTextEdit_3.appendPlainText(out_message)

        path = (AppCFG.PATH["DEFAULT_LOG_PATH"] + "systemlogs.txt")
        with open(path, 'a') as file:
                for log in LogController.LOGS:
                    file.write(log + "\n")
                file.close

    @staticmethod
    def SaveLogs():
        if LogController.UI.textEdit.toPlainText() == "":
            path = (AppCFG.PATH["DEFAULT_LOG_PATH"] + "systemlogs.txt")
        else:
            path = LogController.UI.textEdit.toPlainText() + "systemlogs.txt"

        try:
            with open(path, 'a') as file:
                for log in LogController.LOGS:
                    file.write(log + "\n")
                file.close
                LogController.UI.statusSave.setText("Сохранено успешно!")
        except:
            LogController.UI.statusSave.setText("Неправильный путь!")



        