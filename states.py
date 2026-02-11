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