import json
import time
from pathlib import Path

from jarvis_app.command_router import CommandRouter
from jarvis_app.ollama_client import OllamaClient
from jarvis_app.voice_output import VoiceOutput
from jarvis_app.audio_engine import AudioCapture
from vosk import Model, KaldiRecognizer

from jarvis_app.config import (
    ENGLISH_MODEL_PATH,
    HINDI_MODEL_PATH,
    WAKE_WORDS,
    COMMAND_TIMEOUT_SECONDS,
    AUDIO_SAMPLE_RATE,
)


class JARVISAssistant:
    def __init__(self):
        self.voice = VoiceOutput()
        self.llm = OllamaClient()
        self.router = CommandRouter(self.llm)
        self.audio = AudioCapture(AUDIO_SAMPLE_RATE)

    def check_model_exists(self, path: Path) -> bool:
        return path.exists() and path.is_dir()

    def create_wake_recognizer(self, english_model):
        return KaldiRecognizer(english_model, AUDIO_SAMPLE_RATE, json.dumps(WAKE_WORDS))

    def get_vosk_result(self, recognizer):
        try:
            result = json.loads(recognizer.Result())
            text = (result.get("text") or "").strip().lower()
            return text if text and text != "[unk]" else ""
        except Exception:
            return ""

    def get_partial_result(self, recognizer):
        try:
            partial = json.loads(recognizer.PartialResult())
            text = (partial.get("partial") or "").strip().lower()
            return text if text and text != "[unk]" else ""
        except Exception:
            return ""

    def choose_best_text(self, english_text: str, hindi_text: str) -> str:
        english_text = (english_text or "").strip().lower()
        hindi_text = (hindi_text or "").strip().lower()

        if not english_text and not hindi_text:
            return ""

        if any("\u0900" <= ch <= "\u097F" for ch in hindi_text):
            return hindi_text

        if hindi_text and len(hindi_text) > len(english_text):
            return hindi_text

        if english_text:
            return english_text

        return hindi_text

    def listen_for_command(self, english_rec, hindi_rec):
        start_time = time.monotonic()
        speech_started = False
        silence_started = None

        while time.monotonic() - start_time < COMMAND_TIMEOUT_SECONDS:
            block = self.audio.get_audio_block(timeout=0.25)
            if block is None:
                continue

            english_rec.AcceptWaveform(block)
            hindi_rec.AcceptWaveform(block)

            en_partial = self.get_partial_result(english_rec)
            hi_partial = self.get_partial_result(hindi_rec)

            if en_partial or hi_partial:
                speech_started = True
                silence_started = None
                print(f"[Partial] EN: {en_partial} | HI: {hi_partial}")

            if speech_started and not en_partial and not hi_partial:
                if silence_started is None:
                    silence_started = time.monotonic()
                elif time.monotonic() - silence_started > 0.8:
                    final_en = self.get_vosk_result(english_rec)
                    final_hi = self.get_vosk_result(hindi_rec)
                    if final_en or final_hi:
                        best = self.choose_best_text(final_en, final_hi)
                        if best:
                            return best

            final_en = self.get_vosk_result(english_rec)
            final_hi = self.get_vosk_result(hindi_rec)
            if final_en or final_hi:
                best = self.choose_best_text(final_en, final_hi)
                if best:
                    return best

        return ""

    def run(self):
        if not self.check_model_exists(ENGLISH_MODEL_PATH):
            print(f"English model not found: {ENGLISH_MODEL_PATH}")
            return

        if not self.check_model_exists(HINDI_MODEL_PATH):
            print(f"Hindi model not found: {HINDI_MODEL_PATH}")
            return

        print("Loading English model...")
        english_model = Model(str(ENGLISH_MODEL_PATH))

        print("Loading Hindi model...")
        hindi_model = Model(str(HINDI_MODEL_PATH))

        english_recognizer = KaldiRecognizer(english_model, AUDIO_SAMPLE_RATE)
        hindi_recognizer = KaldiRecognizer(hindi_model, AUDIO_SAMPLE_RATE)
        wake_recognizer = self.create_wake_recognizer(english_model)

        self.voice.speak("JARVIS is ready. Say Hey Jarvis to wake me.")

        with self.audio.stream() as stream:
            while True:
                block = self.audio.get_audio_block(timeout=0.5)
                if block is None:
                    continue

                wake_recognizer.AcceptWaveform(block)
                wake_text = self.get_vosk_result(wake_recognizer)

                if not wake_text or "jarvis" not in wake_text:
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
