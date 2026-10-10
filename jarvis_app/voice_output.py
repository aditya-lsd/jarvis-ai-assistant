import pyttsx3


class VoiceOutput:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 170)
        self.engine.setProperty("volume", 1.0)

    def speak(self, text: str):
        text = str(text).strip()
        if not text:
            return
        print(f"\nJARVIS: {text}")
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as exc:
            print(f"[TTS error] {exc}")
