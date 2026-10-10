import subprocess
import webbrowser
from datetime import datetime


def is_sleep_command(text: str) -> bool:
    t = text.lower().strip()
    commands = [
        "go to sleep",
        "sleep now",
        "stop listening",
        "so jao",
        "ab so jao",
        "sunna band karo",
        "chup raho",
        "band ho jao",
        "सो जाओ",
        "sleep",
        "chup",
    ]
    return any(cmd in t for cmd in commands)


def is_exit_command(text: str) -> bool:
    t = text.lower().strip()
    commands = [
        "exit",
        "quit",
        "goodbye",
        "goodbye jarvis",
        "shutdown",
        "jarvis band ho jao",
        "band ho jao",
    ]
    return any(cmd in t for cmd in commands)


def detect_language(text: str) -> str:
    text = (text or "").strip()
    if not text:
        return "unknown"

    # Devanagari detection
    if any("\u0900" <= ch <= "\u097F" for ch in text):
        return "hindi"

    hi_keywords = [
        "namaste", "kya", "kaise", "hai", "batao", "samay", "tarikh",
        "kholo", "khol do", "so jao", "chup", "raho", "open"
    ]
    lowered = text.lower()
    if any(keyword in lowered for keyword in hi_keywords):
        return "hindi"

    return "english"


def classify_command(text: str) -> str:
    t = (text or "").lower().strip()
    if not t:
        return "unknown"

    if is_sleep_command(t):
        return "sleep"
    if is_exit_command(t):
        return "exit"
    if "notepad" in t or "notepad kholo" in t:
        return "open_notepad"
    if "calculator" in t or "calc" in t:
        return "open_calculator"
    if "explorer" in t or "file explorer" in t:
        return "open_explorer"
    if "browser" in t or "chrome" in t or "browser kholo" in t:
        return "open_browser"
    if "time" in t or "samay" in t or "kitne baje" in t:
        return "get_time"
    if "date" in t or "tarikh" in t or "aaj ki date" in t:
        return "get_date"
    return "general"


class CommandRouter:
    def __init__(self, llm_client):
        self.llm_client = llm_client

    def execute(self, text: str) -> str:
        command = classify_command(text)

        if command == "sleep":
            return "Going to sleep. Say Hey Jarvis to wake me."
        if command == "exit":
            return "Goodbye. JARVIS is shutting down."
        if command == "open_notepad":
            try:
                subprocess.Popen(["notepad.exe"])
                return "Opening Notepad."
            except Exception:
                return "I could not open Notepad on this system."
        if command == "open_calculator":
            try:
                subprocess.Popen(["calc.exe"])
                return "Opening Calculator."
            except Exception:
                return "I could not open Calculator on this system."
        if command == "open_explorer":
            try:
                subprocess.Popen(["explorer.exe"])
                return "Opening File Explorer."
            except Exception:
                return "I could not open File Explorer on this system."
        if command == "open_browser":
            try:
                webbrowser.open("https://www.google.com")
                return "Opening browser."
            except Exception:
                return "I could not open the browser."
        if command == "get_time":
            now = datetime.now().strftime("%I:%M %p")
            return f"The time is {now}."
        if command == "get_date":
            today = datetime.now().strftime("%B %d, %Y")
            return f"Today is {today}."

        return self.llm_client.ask(text)
