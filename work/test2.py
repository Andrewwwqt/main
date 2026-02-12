from PyQt5.QtCore import QThread, pyqtSignal
from RobotController import RobotController
from ApplictationState import ApplicationState, ModeApplication
from states import AppStates, AppMods, LogOption, LogType
from lightController import LightController
from LogController import LogController
from statistic import Statistic
from motion.core import Waypoint
from math import radians
import time


class AutoWorker(QThread):
    """Поток для выполнения автоматических задач с управлением роботом"""
    task_completed = pyqtSignal(int)  # Сигнал о завершении задачи (номер тары)
    task_updated = pyqtSignal()       # Сигнал об обновлении списка задач
    status_message = pyqtSignal(str)  # Сигнал для статусных сообщений
    
    def __init__(self, tasks):
        super().__init__()
        self.tasks = tasks
        self.running = True
        
        # Координаты точек в декартовой системе (x, y, z, rx, ry, rz)
        # Зона захвата - место где появляются объекты
        self.PICK_POSITION = [0.5, 0.0, 0.3, 3.14, 0.0, 1.57]
        
        # Позиции для размещения в таре 1
        self.CONTAINER_1_POSITIONS = [
            [0.3, 0.2, 0.2, 3.14, 0.0, 1.57],
            [0.3, 0.25, 0.2, 3.14, 0.0, 1.57],
            [0.3, 0.2, 0.25, 3.14, 0.0, 1.57],
            [0.3, 0.25, 0.25, 3.14, 0.0, 1.57]
        ]
        
        # Позиции для размещения в таре 2
        self.CONTAINER_2_POSITIONS = [
            [0.4, -0.2, 0.2, 3.14, 0.0, 1.57],
            [0.4, -0.25, 0.2, 3.14, 0.0, 1.57],
            [0.4, -0.2, 0.25, 3.14, 0.0, 1.57],
            [0.4, -0.25, 0.25, 3.14, 0.0, 1.57]
        ]
        
        # Позиции для размещения в таре 3
        self.CONTAINER_3_POSITIONS = [
            [0.5, 0.2, 0.2, 3.14, 0.0, 1.57],
            [0.5, 0.25, 0.2, 3.14, 0.0, 1.57],
            [0.5, 0.2, 0.25, 3.14, 0.0, 1.57],
            [0.5, 0.25, 0.25, 3.14, 0.0, 1.57]
        ]
        
        # Позиция для брака
        self.REJECT_POSITION = [0.6, 0.0, 0.2, 3.14, 0.0, 1.57]
        
        # Позиция ожидания/старта
        self.HOME_POSITION = [0.0, 0.0, 0.5, 3.14, 0.0, 1.57]
        
    def run(self):
        """Выполнение задач в очереди с реальными движениями робота"""
        try:
            # Переключаем робота в автоматический режим если нужно
            RobotController.robot.semiAutoMode()
            
            for task in self.tasks:
                if not self.running:
                    break
                
                self.status_message.emit(f"Выполнение задачи: {task}")
                
                # 1. Движение к позиции захвата
                self.status_message.emit("Перемещение к месту захвата...")
                waypoint_pick = Waypoint(self.PICK_POSITION)
                RobotController.robot.addMoveToPointL([waypoint_pick], 0.1, 0.2)
                RobotController.robot.play()
                time.sleep(2)  # Ждем завершения движения
                
                # 2. Захват объекта
                self.status_message.emit("Захват объекта...")
                RobotController.robot.toolON()
                time.sleep(0.5)  # Время на захват
                
                # 3. Подъем объекта
                lift_position = self.PICK_POSITION.copy()
                lift_position[2] += 0.1  # Поднимаем на 10 см
                waypoint_lift = Waypoint(lift_position)
                RobotController.robot.addMoveToPointL([waypoint_lift], 0.1, 0.2)
                RobotController.robot.play()
                time.sleep(1)
                
                # 4. Перемещение к целевой таре
                if task.startswith("1"):
                    container_positions = self.CONTAINER_1_POSITIONS
                    container_num = 1
                elif task.startswith("2"):
                    container_positions = self.CONTAINER_2_POSITIONS
                    container_num = 2
                elif task.startswith("3"):
                    container_positions = self.CONTAINER_3_POSITIONS
                    container_num = 3
                else:  # Брак
                    self.status_message.emit("Перемещение в зону брака...")
                    waypoint_reject = Waypoint(self.REJECT_POSITION)
                    RobotController.robot.addMoveToPointL([waypoint_reject], 0.1, 0.2)
                    RobotController.robot.play()
                    time.sleep(2)
                    
                    # Сброс брака
                    RobotController.robot.toolOFF()
                    time.sleep(0.5)
                    self.task_completed.emit(0)  # 0 - брак
                    self.task_updated.emit()
                    continue
                
                # Выбираем свободную позицию в таре
                # В реальном проекте нужно получать текущее заполнение из AutoController
                position_index = 0  # Заглушка, нужно получать реальное значение
                
                self.status_message.emit(f"Перемещение к таре {container_num}...")
                waypoint_container = Waypoint(container_positions[position_index])
                RobotController.robot.addMoveToPointL([waypoint_container], 0.1, 0.2)
                RobotController.robot.play()
                time.sleep(2)
                
                # 5. Опускание объекта
                self.status_message.emit("Опускание объекта...")
                lower_position = container_positions[position_index].copy()
                lower_position[2] -= 0.05  # Опускаем на 5 см
                waypoint_lower = Waypoint(lower_position)
                RobotController.robot.addMoveToPointL([waypoint_lower], 0.05, 0.1)
                RobotController.robot.play()
                time.sleep(1)
                
                # 6. Освобождение объекта
                self.status_message.emit("Освобождение объекта...")
                RobotController.robot.toolOFF()
                time.sleep(0.5)
                
                # 7. Возврат в исходную позицию
                self.status_message.emit("Возврат в исходную позицию...")
                waypoint_home = Waypoint(self.HOME_POSITION)
                RobotController.robot.addMoveToPointL([waypoint_home], 0.1, 0.2)
                RobotController.robot.play()
                time.sleep(2)
                
                # Отправляем сигнал о завершении
                self.task_completed.emit(container_num)
                self.task_updated.emit()
                
                # Небольшая пауза между задачами
                time.sleep(0.5)
            
            self.status_message.emit("Все задачи выполнены")
            
        except Exception as e:
            self.status_message.emit(f"Ошибка: {str(e)}")
            LogController.Log(LogType.ERROR, LogOption.Move, f"Ошибка в автоматическом режиме: {e}")
            # Аварийная остановка
            RobotController.robot.toolOFF()
            RobotController.robot.stop()
        
        finally:
            # Завершение работы
            ApplicationState.ApplicationState = AppStates.wait
            LightController.update()
    
    def stop(self):
        """Остановка выполнения"""
        self.running = False
        # Аварийная остановка робота
        try:
            RobotController.robot.stop()
            RobotController.robot.toolOFF()
        except:
            pass


class AutoController:
    """Контроллер автоматического режима сортировки с управлением роботом"""
    
    def __init__(self, ui):
        self.ui = ui
        self.worker = None
        self.tasks = []           # Очередь задач
        self.container_count = {  # Счетчики для каждой тары
            1: 0,
            2: 0,
            3: 0
        }
        self.max_per_container = 4  # Максимум предметов в таре
        
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """Настройка начального состояния UI"""
        self._update_tasks_display()
        self._update_containers_display()
    
    def _connect_signals(self):
        """Подключение сигналов от кнопок"""
        # Добавление задач
        self.ui.add_one.clicked.connect(lambda: self.add_task("1_Категория"))
        self.ui.add_two.clicked.connect(lambda: self.add_task("2_Категория"))
        self.ui.add_tree.clicked.connect(lambda: self.add_task("3_Категория"))
        self.ui.add_brack.clicked.connect(lambda: self.add_task("Брак"))
        
        # Управление очередью
        self.ui.deleteElement.clicked.connect(self.remove_last_task)
        self.ui.clearElements.clicked.connect(self.clear_tasks)
        
        # Очистка тары
        self.ui.ClearTars_1.clicked.connect(lambda: self.clear_container(1))
        self.ui.ClearTars_2.clicked.connect(lambda: self.clear_container(2))
        self.ui.ClearTars_3.clicked.connect(lambda: self.clear_container(3))
        
        # Запуск и остановка автоматической сортировки
        self.ui.StartAutoSort.clicked.connect(self.start_sorting)
        self.ui.StopAutoSort.clicked.connect(self.stop_sorting)
    
    def add_task(self, task_name):
        """Добавление задачи в очередь"""
        # Проверяем, не запущена ли сортировка
        if self.worker and self.worker.isRunning():
            LogController.Log(LogType.WARNING, LogOption.Task, 
                            "Нельзя добавить задачу во время выполнения")
            return
            
        # Проверяем лимит очереди
        if len(self.tasks) >= 20:
            LogController.Log(LogType.WARNING, LogOption.Task, 
                            "Очередь задач переполнена")
            return
        
        # Для задач сортировки проверяем наличие свободного места
        if task_name.startswith("1") and self.container_count[1] >= self.max_per_container:
            LogController.Log(LogType.WARNING, LogOption.Task, "Тара 1 заполнена")
            return
        elif task_name.startswith("2") and self.container_count[2] >= self.max_per_container:
            LogController.Log(LogType.WARNING, LogOption.Task, "Тара 2 заполнена")
            return
        elif task_name.startswith("3") and self.container_count[3] >= self.max_per_container:
            LogController.Log(LogType.WARNING, LogOption.Task, "Тара 3 заполнена")
            return
        
        self.tasks.append(task_name)
        self._update_tasks_display()
        LogController.Log(LogType.INFO, LogOption.Task, f"Добавлена задача: {task_name}")
    
    def remove_last_task(self):
        """Удаление последней задачи из очереди"""
        if self.worker and self.worker.isRunning():
            LogController.Log(LogType.WARNING, LogOption.Task, 
                            "Нельзя удалить задачу во время выполнения")
            return
            
        if self.tasks:
            removed = self.tasks.pop()
            self._update_tasks_display()
            LogController.Log(LogType.INFO, LogOption.Task, f"Удалена задача: {removed}")
    
    def clear_tasks(self):
        """Очистка всей очереди задач"""
        if self.worker and self.worker.isRunning():
            LogController.Log(LogType.WARNING, LogOption.Task, 
                            "Нельзя очистить очередь во время выполнения")
            return
            
        self.tasks.clear()
        self._update_tasks_display()
        LogController.Log(LogType.INFO, LogOption.Task, "Очередь задач очищена")
    
    def clear_container(self, container_num):
        """Очистка указанной тары"""
        if container_num in self.container_count:
            self.container_count[container_num] = 0
            self._update_containers_display()
            LogController.Log(LogType.INFO, LogOption.Task, f"Тара {container_num} очищена")
    
    def _update_tasks_display(self):
        """Обновление отображения очереди задач"""
        self.ui.plainTextEdit_6.clear()
        for i, task in enumerate(self.tasks, 1):
            self.ui.plainTextEdit_6.appendPlainText(f"{i}. {task}")
    
    def _update_containers_display(self):
        """Обновление состояния тары"""
        status_texts = {
            0: "Свободна",
            1: "1/4",
            2: "2/4", 
            3: "3/4",
            4: "Заполнена"
        }
        
        # Обновляем для каждой тары
        labels = [self.ui.stat_one, self.ui.stat_two, self.ui.stat_three]
        for i, label in enumerate(labels, 1):
            count = self.container_count[i]
            status = status_texts.get(count, f"{count}/4")
            label.setText(status)
    
    def start_sorting(self):
        """Запуск автоматической сортировки"""
        # Проверка условий для запуска
        if not self.tasks:
            LogController.Log(LogType.WARNING, LogOption.Move, "Нет задач для выполнения")
            return
            
        if ApplicationState.ApplicationState != AppStates.wait:
            LogController.Log(LogType.WARNING, LogOption.Move, 
                            f"Робот не в режиме ожидания (текущий: {ApplicationState.ApplicationState})")
            return
            
        if ModeApplication.ModeApplication != AppMods.Auto:
            LogController.Log(LogType.WARNING, LogOption.Move, 
                            "Приложение не в автоматическом режиме")
            return
        
        # Проверяем подключение к роботу
        if not RobotController.robot or not RobotController.robot._is_connected:
            LogController.Log(LogType.ERROR, LogOption.Move, "Робот не подключен")
            return
        
        # Запуск сортировки
        ApplicationState.ApplicationState = AppStates.On
        LightController.update()
        
        LogController.Log(LogType.INFO, LogOption.Move, 
                         f"Начало автоматической сортировки ({len(self.tasks)} задач)")
        
        # Создаем и запускаем рабочий поток
        self.worker = AutoWorker(self.tasks.copy())
        self.worker.task_completed.connect(self._on_task_completed)
        self.worker.task_updated.connect(self._on_tasks_updated)
        self.worker.status_message.connect(self._update_status)
        self.worker.finished.connect(self._on_sorting_finished)
        self.worker.start()
        
        # Очищаем очередь задач
        self.tasks.clear()
        self._update_tasks_display()
    
    def stop_sorting(self):
        """Принудительная остановка сортировки"""
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()
            self.worker = None
            
            # Возвращаем робота в безопасное состояние
            try:
                RobotController.robot.stop()
                RobotController.robot.toolOFF()
                # Возврат в домашнюю позицию
                waypoint_home = Waypoint([0.0, 0.0, 0.5, 3.14, 0.0, 1.57])
                RobotController.robot.addMoveToPointL([waypoint_home], 0.1, 0.2)
                RobotController.robot.play()
            except:
                pass
            
            ApplicationState.ApplicationState = AppStates.wait
            LightController.update()
            LogController.Log(LogType.INFO, LogOption.Move, "Сортировка остановлена оператором")
    
    def _on_task_completed(self, container_num):
        """Обработка завершения задачи"""
        if container_num in [1, 2, 3]:
            # Проверяем, не заполнена ли тара
            if self.container_count[container_num] >= self.max_per_container:
                LogController.Log(LogType.WARNING, LogOption.Move, 
                                f"Тара {container_num} заполнена, пропуск")
                return
            
            # Увеличиваем счетчик
            self.container_count[container_num] += 1
            self._update_containers_display()
            
            # Обновляем статистику
            if container_num == 1:
                Statistic.sec1 += 1
            elif container_num == 2:
                Statistic.sec2 += 1
            elif container_num == 3:
                Statistic.sec3 += 1
            Statistic.Update()
            
            LogController.Log(LogType.INFO, LogOption.Move, 
                            f"Предмет помещен в тару {container_num}")
        elif container_num == 0:
            LogController.Log(LogType.INFO, LogOption.Move, "Предмет отправлен в брак")
    
    def _on_tasks_updated(self):
        """Обновление отображения после выполнения задачи"""
        # Обновляем статистику или UI при необходимости
        pass
    
    def _update_status(self, message):
        """Обновление статусного сообщения в UI"""
        if hasattr(self.ui, 'status_label'):
            self.ui.status_label.setText(message)
    
    def _on_sorting_finished(self):
        """Завершение сортировки"""
        self.worker = None
        LogController.Log(LogType.INFO, LogOption.Move, "Автоматическая сортировка завершена")
