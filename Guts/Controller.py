import numpy as np
import sounddevice as sd
import time

class Controller(): 
    def __init__(self): 
        super().__init__()

        self.sample_rate = 1600
        self.chunks = []
        self.words = []
        self.button_history = []
        self.clock_start = None
        self.accumulated = 0.0
        self.segment_start = None
        self.is_recording = False
        self.heading_on = False
        self.arrow_on = False
        self.italic_on = False

    def on_heading(self, heading_value): 
        if self.is_recording and not self.heading_on:
            self.button_history.append((self.get_active_timestamp(), "heading_on", heading_value))
            self.heading_on = True
            print(self.button_history)

        elif self.is_recording: 
            self.button_history.append((self.get_active_timestamp(), "heading_off", None))
            self.heading_on = False
            print(self.button_history)


        # Italic()
    def on_italic(self):
        if self.is_recording and not self.italic_on:
            self.button_history.append((self.get_active_timestamp(), "italic_on", None))
            self.italic_on = True
            print(self.button_history)

        elif self.is_recording:
            self.button_history.append((self.get_active_timestamp(), "italic_off", None))
            self.italic_on = False
            print(self.button_history)

        # Bullet()
    def on_arrow(self): 
        if self.is_recording and not self.arrow_on:
            self.button_history.append((self.get_active_timestamp(), "arrow_segment_on", None))
            self.arrow_on = True
            print(self.button_history)

        elif self.is_recording: 
            self.button_history.append((self.get_active_timestamp(), "arrow_segment_off", None))
            self.arrow_on = False
            print(self.button_history)



        # Camera() (pause_recording())
        # Add something about saving screenshot data into button_history[] 

        # start_recording()
        # pause_recording()
        # stop_recording() 

    def get_active_timestamp(self): 
        if self.is_recording: 
            return round(self.accumulated + (time.perf_counter() - self.segment_start), 2)
        return round(self.accumulated, 2)

    







