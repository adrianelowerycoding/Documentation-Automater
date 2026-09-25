"""
This test shows how to record live audio and create word[] and 
button_history[] lists and merge them into events[] list.

How timer works: 
    - There's a global timer that starts and doesn't stop
    until the program ends; this timer starts when the 
    "record" button is pressed. 

    - Audio starts recording as well whenever "record"
    button is pressed. 

    - Click record -> clock_start = 100.0 and segment_start = 100.0
    -> 5 seconds pass & user hits pause, global clock is now 105 
    -> In pause accumulated += 105.0 - 100.0, so = 5.0. That's 
    storing "5 seconds of active recording just happened." 
    Segment_start is still unchanged 100.0. 
    -> 6 seconds of pause passes, user hits resume -> 
    Global clock now reads 111, so segment_start = 111.0
    -> 10 seconds passes and the user hits the heading 
    button -> clock is now 121; find the difference between
    121 and the old segment_start 111 and add that number
    to the accumulated number to correspond to the
    audio recording/words[] timeline. 10 + 5 = 15 seconds. 
    # come back later and finish explaining this



"""
import customtkinter as ctk
import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel
import time

sample_rate = 16000
chunks = []
words = []
button_history = []
events = []
clock_start = None
accumulated = 0.0
segment_start = None
is_recording = False
heading_on = False

print("loading model...")
model = WhisperModel("small.en", device="cpu", compute_type="int8")
print("model loaded")


def on_audio(indata, frames, time_info, status):
    if is_recording:
        chunks.append(indata.copy())


def get_active_timestamp():
    if is_recording:
        # Ex. 5 seconds accumulated + 820 - 810 = 15 seconds total for audio, meaning this timestamp is at 15 seconds.
        return round(accumulated + (time.perf_counter() - segment_start), 2)
    return round(accumulated, 2)


def start_recording():
    global clock_start, segment_start, is_recording
    clock_start = time.perf_counter()
    segment_start = clock_start
    is_recording = True
    stream.start()
    print("recording...")


def pause_recording():
    global accumulated, is_recording
    accumulated += time.perf_counter() - segment_start
    is_recording = False
    # button_history.append((get_active_timestamp(), "pause"))


def resume_recording():
    global segment_start, is_recording
    segment_start = time.perf_counter()
    is_recording = True


def on_heading():
    global heading_on
    if is_recording and not heading_on:
        button_history.append((get_active_timestamp(), "heading_on"))
        heading_on = True
    elif is_recording:
        button_history.append((get_active_timestamp(), "heading_off"))
        heading_on = False


def stop_recording():
    global is_recording, events
    is_recording = False
    stream.stop()
    stream.close()
    print("Recording stopped")

    if not chunks:
        print("No audio recorded.")
        return

    audio = np.concatenate(chunks).squeeze()
    segments, info = model.transcribe(audio, word_timestamps=True)

    for segment in segments:
        for word in segment.words:
            words.append((word.start, "word", word.word))

    print("Words[]:\n", words)
    print("Button_history[]:\n", button_history)
    events = words + button_history
    events.sort(key=lambda item: item[0])
    print("Events[]:\n", events)


def on_closing():
    global is_recording
    is_recording = False
    try:
        stream.stop()
        stream.close()
    except Exception:
        pass
    root.destroy()


stream = sd.InputStream(samplerate=sample_rate, channels=1, dtype=np.float32, callback=on_audio)

root = ctk.CTk()
root.title("Timer Example")
root.geometry("250x150")

record_button = ctk.CTkButton(root, hover=False, text="Record", command=start_recording)
pause_button = ctk.CTkButton(root, text="Pause", command=pause_recording)
stop_button = ctk.CTkButton(root, text="Stop", command=stop_recording)
heading_button = ctk.CTkButton(root, text="Heading", command=on_heading)

record_button.pack(pady=5)
pause_button.pack(pady=5)
stop_button.pack(pady=5)
heading_button.pack(pady=5)

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()