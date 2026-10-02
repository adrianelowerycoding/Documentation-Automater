"""
This test shows how to record live audio until the user hits the "stop" button. 
The dynamic-sized audio sample is then transcribed by faster whisper and a 
word[] list is created.
"""
import threading
import keyboard
import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

sample_rate = 16000
chunks = []
words = []
stop_event = threading.Event()


def on_audio(indata, frames, time_info, status):
    chunks.append(indata.copy())

def stop_recording(): 
    print("Recording stopped")
    stream.stop()
    stream.close()
    stop_event.set() # Unblock the main thread

stream = sd.InputStream(samplerate=sample_rate, channels=1, dtype=np.float32, callback=on_audio)

# Set up global keybind Ctrl + Shift + e
keyboard.add_hotkey('ctrl+shift+e', stop_recording)

# "Start recording" button
stream.start()
print("recording...")

# Wait until hotkey is pressed to stop stream
stop_event.wait()

# Create list of audio sample
audio = np.concatenate(chunks).squeeze()

model = WhisperModel("small.en", device="cpu", compute_type="int8")
segments, info = model.transcribe(audio, word_timestamps=True)

for segment in segments:
    for word in segment.words:
        words.append((word.start, "word", word.word)) # Create a list of tuples; (timestamp, word)
       # print(f"{word.start} | {word.word}")

print(words)

