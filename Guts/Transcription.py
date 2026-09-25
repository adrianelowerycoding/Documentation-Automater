"""
"""
import threading
import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

sample_rate = 16000
chunks = []
words = []


def on_audio(indata, frames, time_info, status):
    chunks.append(indata.copy())

def start_recording(): 
    stream.start()

def stop_recording(): 
    print("Recording stopped")
    stream.stop()
    stream.close()

stream = sd.InputStream(samplerate=sample_rate, channels=1, dtype=np.float32, callback=on_audio)

# Create list of audio sample
audio = np.concatenate(chunks).squeeze()

model = WhisperModel("small.en", device="cpu", compute_type="int8")
segments, info = model.transcribe(audio, word_timestamps=True)

for segment in segments:
    for word in segment.words:
        words.append((word.start, "word", word.word)) # Create a list of tuples; (timestamp, word)
       # print(f"{word.start} | {word.word}")



