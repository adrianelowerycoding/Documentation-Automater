"""
This module simply takes the audio sample from Controller, transcribes it, then 
passes the words[] list to Controller.
"""
from faster_whisper import WhisperModel

class Transcription(): 
    def __init__(self, audio): 
        super.__init__() 

        self.audio = audio
        self.words = []


    def transcribe(self): 
        model = WhisperModel("small.en", device="cpu", compute_type="int8")
        print("Model loaded")

        segments, info = model.transcribe(self.audio, word_timestamps=True)

        for segment in segments: 
            for word in segment.words: 
                self.words.append((word.start, "word", word.word))

        return self.words






