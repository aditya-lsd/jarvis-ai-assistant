import json
import time
from typing import Optional

from vosk import Model, KaldiRecognizer

from jarvis_app.audio_engine import AudioCapture
from jarvis_app.command_router import CommandRouter, detect_language
from jarvis_app.config import (
    ENGLISH_MODEL_PATH,
    HINDI_MODEL_PATH,
    WAKE_WORDS,
    COMMAND_TIMEOUT_SECONDS,
    AUDIO_SAMPLE_RATE,
)
from jarvis_app.ollama_client import OllamaClient
from jarvis_app.voice_output import VoiceOutput


class JARVISAssistant:
    def __init__(self):
        self.voice = VoiceOutput()
        self.llm = OllamaClient()
        self.router = CommandRouter(self.llm)
        self.audio = AudioCapture(AUDIO_SAMPLE_RATE)

    def check_model_exists(self, path):
        return path.exists() and path.is_dir()

    def create_wake_recognizer(self, english_model):
        return KaldiRecognizer(english_model, AUDIO_SAMPLE_RATE, json.dumps(WAKE_WORDS))

    def get_recognized_text(self, recognizer) -> str:
        try:
            result = json.loads(recognizer.Result())
            text = (result.get("text") or "").strip().lower()
            if text and text != "[unk]":
                return text
        except Exception:
            pass
        return ""

    def get_partial_text(self, recognizer) -> str:
        try:
            partial = json.loads(recognizer.PartialResult())
            text = (partial.get("partial") or "").strip().lower()
            return text if text and text != "[unk]" else ""
        except Exception:
            return ""

    def choose_best_text(self, english_text: str, hindi_text: str) -> str:
        english_text = (english_text or "").strip().lower()
        hindi_text = (hindi_text or "").strip().lower()

        # Devanagari detection
        if any("\u0900" <= ch <= "\u097F" for ch in hindi_text):
            return hindi_text

        if hindi_text and len(hindi_text) > len(english_text):
            return hindi_text

        if english_text:
            return english_text

        if hindi_text:
            return hindi_text

        return ""

    def listen_for_command(self, english_rec, hindi_rec):
        deadline = time.monotonic() + COMMAND_TIMEOUT_SECONDS
        command_text = ""

        while time.monotonic() < deadline:
            block = self.audio.get_audio_block(timeout=0.5)
            if block is None:
                continue

            english_rec.AcceptWaveform(block)
            hindi_rec.AcceptWaveform(block)

            en_partial = self.get_partial_text(english_rec)
            hi_partial = self.get_partial_text(hindi_rec)
            if en_partial or hi_partial:
                print(f"[Partial] EN: {en_partial} | HI: {hi_partial}")

            final_en = self.get_recognized_text(english_rec)
            final_hi = self.get_recognized_text(hindi_rec)
            if final_en or final_hi:
                command_text = self.choose_best_text(final_en, final_hi)
                if command_text:
                    return command_text

        return ""

    def run(self):
        if not self.check_model_exists(ENGLISH_MODEL_PATH):
            print(f"English model not found at: {ENGLISH_MODEL_PATH}")
            print("Download Vosk English model and place it in the 'models' folder.")
            return

        if not self.check_model_exists(HINDI_MODEL_PATH):
            print(f"Hindi model not found at: {HINDI_MODEL_PATH}")
            print("Download Vosk Hindi model and place it in the 'models' folder.")
            return

        print("Loading English model...")
        english_model = Model(str(ENGLISH_MODEL_PATH))

        print("Loading Hindi model...")
        hindi_model = Model(str(HINDI_MODEL_PATH))

        english_recognizer = KaldiRecognizer(english_model, 16000)
        hindi_recognizer = KaldiRecognizer(hindi_model, 16000)
        wake_recognizer = self.create_wake_recognizer(english_model)

        self.voice.speak("JARVIS is ready. Say Hey Jarvis to wake me.")

        with self.audio.stream() as stream:
            while True:
                block = self.audio.get_audio_block(timeout=0.5)
                if block is None:
                    continue

                wake_recognizer.AcceptWaveform(block)
                wake_text = self.get_recognized_text(wake_recognizer)
                if not wake_text:
                    continue

                lower_wake = wake_text.lower()
                if "jarvis" not in lower_wake:
                    continue

                print("\nWake word detected!")
                self.voice.speak("Yes, I am listening.")

                english_recognizer.Reset()
                hindi_recognizer.Reset()

                while True:
                    print("Listening for your command...")
                    command = self.listen_for_command(english_recognizer, hindi_recognizer)
                    if not command:
                        self.voice.speak("I did not hear a command. Say Hey Jarvis when you need me.")
                        break

                    print(f"Command captured: {command}")
                    response = self.router.execute(command)
                    self.voice.speak(response)

                    if response.lower().startswith("going to sleep"):
                        break
                    if response.lower().startswith("goodbye"):
                        return

                    english_recognizer.Reset()
                    hindi_recognizer.Reset()

                    self.audio.clear()
