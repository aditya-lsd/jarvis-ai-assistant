import queue
import json
from typing import Optional

import sounddevice as sd


class AudioCapture:
    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
        self.queue = queue.Queue()

    def callback(self, indata, frames, time_info, status):
        if status:
            print(f"[Audio status] {status}")
        self.queue.put(bytes(indata))

    def stream(self):
        return sd.RawInputStream(
            samplerate=self.sample_rate,
            blocksize=8000,
            dtype="int16",
            channels=1,
            callback=self.callback,
        )

    def clear(self):
        while not self.queue.empty():
            try:
                self.queue.get_nowait()
            except queue.Empty:
                break

    def get_audio_block(self, timeout: float = 0.5):
        try:
            return self.queue.get(timeout=timeout)
        except queue.Empty:
            return None
