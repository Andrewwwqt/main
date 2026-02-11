from enum import Enum

class AppStates(Enum):
    On = 1,
    OFF = 2,
    Pause = 3,
    wait = 4,
    Emergency = 5,

class AppMods(Enum):
    Manual = 1,
    Auto = 2,

class RobotModes(Enum):
    CART = 1,
    JOINT = 2,

class LogOption(Enum):
    Mode = 1,
    On = 2,
    Move = 3,
    Emetgency = 4,
    Pause = 5,

class LogType(Enum):
    INFO = 1

class Toolstates(Enum):
    Open = 1,
    Close = 2,