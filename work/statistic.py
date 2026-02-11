import pandas as pd
from ApplicationCFG import AppCFG


class Statistic:
    sec1 = 0
    sec2 = 0
    sec3 = 0
    brack = 0
    UI = None
    def __init__(self, ui):
        Statistic.UI = ui

        self.buttons()
        self.Update()

    def buttons(self):
        Statistic.UI.add1.clicked.connect(lambda cheked = False, btn = "sec1" : self.AddElement(btn))
        Statistic.UI.add2.clicked.connect(lambda cheked = False, btn = "sec2" : self.AddElement(btn))
        Statistic.UI.add3.clicked.connect(lambda cheked = False, btn = "sec3" : self.AddElement(btn))
        Statistic.UI.addbrack.clicked.connect(lambda cheked = False, btn = "brack" : self.AddElement(btn))
    
    def AddElement(self,btn):
        match(btn):
            case "sec1":
                Statistic.sec1 += 1
            case "sec2":
                Statistic.sec2 += 1
            case "sec3":
                Statistic.sec3 += 1
            case "brack":
                Statistic.brack += 1

        Statistic.Update()

    @staticmethod           
    def Update():
        Statistic.UI.sec1.setPlainText(str(Statistic.sec1))
        Statistic.UI.sec2.setPlainText(str(Statistic.sec2))
        Statistic.UI.sec3.setPlainText(str(Statistic.sec3))
        Statistic.UI.brack.setPlainText(str(Statistic.brack))

    @staticmethod
    def SaveStat():

        dict = {"Категории": ["Категория 1", "Категория 2", "Категория 3", "брак"], "Кол-во объектов": [Statistic.sec1, Statistic.sec2, Statistic.sec3, Statistic.brack], "Время": [Statistic.UI.timeEdit.text(), Statistic.UI.timeEdit_2.text(), Statistic.UI.timeEdit_3.text(), Statistic.UI.timeEdit_4.text()]}
        df = pd.DataFrame.from_dict(dict)

        if Statistic.UI.textEdit_2.toPlainText() == "":
            path = (AppCFG.PATH["DEFAULT_STAT_PATH"] + "stats.xlsx")
        else:
            path = Statistic.UI.textEdit_2.toPlainText() + "stats.xlsx"

        try:
            df.to_excel(path, index=False)
            Statistic.UI.statusSave_2.setText("Сохранено успешно!")
        except:
            Statistic.UI.statusSave_2.setText("Неправильный путь!")


        

        