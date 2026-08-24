from enum import Enum, auto

class RecordingState(Enum): 
    RECORDING = auto()
    PAUSED = auto() 
    STOPPED = auto() 
    SAVED = auto()
    CLEARED = auto()

    