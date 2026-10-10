from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models"
ENGLISH_MODEL_PATH = MODELS_DIR / "vosk-model"
HINDI_MODEL_PATH = MODELS_DIR / "vosk-model-small-hi-0.22"

OLLAMA_URL = "http://localhost:11434/api/chat"
DEFAULT_MODEL = "qwen2.5:3b"
AUDIO_SAMPLE_RATE = 16000

WAKE_WORDS = [
    "hey jarvis",
    "jarvis",
]

COMMAND_TIMEOUT_SECONDS = 12
