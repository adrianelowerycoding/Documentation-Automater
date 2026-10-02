"""
This test shows how to record a set amount of time with sounddevice and convert 
transcribe the audio sample with faster whisper
"""


import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

sample_rate = 16000
duration = 10  # seconds

print("Recording...")
audio = sd.rec(int(sample_rate * duration), samplerate=sample_rate, channels=1, dtype=np.float32)
sd.wait()
audio = audio.squeeze()  # sounddevice returns shape (N, 1); faster-whisper wants shape (N,)

model = WhisperModel("small.en", device="cpu", compute_type="int8")
segments, info = model.transcribe(audio, word_timestamps=True)

for segment in segments:
    for word in segment.words:
        print(f"[{word.start:.2f}s -> {word.end:.2f}s] {word.word}")


