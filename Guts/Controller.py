import sys
from pathlib import Path
import os
import numpy as np
import sounddevice as sd
import time

# parent_dir = Path(__file__).resolve().parent.parent

# if str(parent_dir) not in sys.path:
#     sys.path.append(str(parent_dir))

from Guts.Transcription import Transcription

class Controller(): 
    def __init__(self, guide_path): 
        super().__init__()

        # path to current guide folder
        self.guide_path = Path(guide_path)

        self.sample_rate = 1600
        self.chunks = []
        self.stream = None
        self.words = []
        self.button_history = []
        self.clock_start = None
        self.accumulated = 0.0
        self.segment_start = None
        self.is_recording = False
        self.heading_on = False
        self.arrow_on = False
        self.italic_on = False
        self.bullet_on = False
        self.in_sct_mode = False

        # screenshots folder for this guide
        self.sct_dir = self.guide_path / "screenshots"
        # make the folder if it's not there yet
        self.sct_dir.mkdir(parents=True, exist_ok=True)
        # counts each screenshot saved
        self.sct_counter = 0

        self.transcribe = Transcription()


    def start_recording(self): 
        # Creating stream
        self.stream = sd.InputStream(samplerate=self.sample_rate, channels=1, dtype=np.float32, callback=self.on_audio)
        
        self.clock_start = time.perf_counter()
        self.segment_start = self.clock_start
        self.is_recording = True
        self.stream.start()
        print("Recording...")

    def pause_recording(self):
        self.accumulated += time.perf_counter() - self.segment_start
        self.is_recording = False

    def resume_recording(self):
        self.segment_start - time.perf_counter()
        self.is_recording = True

    def stop_recording(self): 
        self.is_recording = False
        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
            self.stream = None
            print("Recording stopped")

        if not self.chunks:
            print("No audio recorded")
            return

        audio = np.concatenate(self.chunks).squeeze()
        self.transcribe(audio) # Send audio to transcribe()

    def on_audio(self, indata, frames, time_info, status): 
        if self.is_recording: 
            self.chunks.append(indata.copy())

    def block_end(self): 
        self.button_history.append((self.get_active_timestamp(), "block_end", None))

    def on_heading(self, heading_value): 

        # If there was a pgh before this heading block then you insert a "end" element in list 
        # and then insert a "heading_on" element in list right after. 
        if self.is_recording and not self.heading_on:
            self.block_end()
            self.button_history.append((self.get_active_timestamp(), "heading", heading_value))
            self.heading_on = True
            print(self.button_history)

        elif self.is_recording: 
            self.block_end()
            self.heading_on = False
            print(self.button_history)

    def on_italic(self):
        if self.is_recording and not self.italic_on:
            self.button_history.append((self.get_active_timestamp(), "italic_on", None))
            self.italic_on = True
            print(self.button_history)

        elif self.is_recording:
            self.button_history.append((self.get_active_timestamp(), "italic_off", None))
            self.italic_on = False
            print(self.button_history)

    def on_bullet(self, bullet_style): 
        if self.is_recording and not self.bullet_on:
            self.block_end()
            self.button_history.append((self.get_active_timestamp(), "bullet", bullet_style))
            self.italic_on = True
            print(self.button_history)
        
        elif self.is_recording:
            self.block_end()
            self.italic_on = False
            print(self.button_history)

    def on_arrow(self): 
        if self.is_recording and not self.arrow_on:
            self.button_history.append((self.get_active_timestamp(), "arrow_segment_on", None))
            self.arrow_on = True
            print(self.button_history)

        elif self.is_recording: 
            self.button_history.append((self.get_active_timestamp(), "arrow_segment_off", None))
            self.arrow_on = False
            print(self.button_history)


    def sct_save(self, screenshot): 
        # receive the ImageGrab data and save the photo 
        # add filepath to the button_history[] list
        self.in_sct_mode = True

        # bump count for this screenshot
        self.sct_counter += 1
        filename = f"sct_{self.sct_counter}.png"
        # full path to save to
        filepath = self.sct_dir / filename

        screenshot.save(filepath)

        # log timestamp + path
        self.button_history.append((timestamp, "screenshot", str(filepath)))

        return filepath

    def get_active_timestamp(self): 
        if self.is_recording: 
            return round(self.accumulated + (time.perf_counter() - self.segment_start), 2)
        return round(self.accumulated, 2)