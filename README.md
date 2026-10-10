# JARVIS AI Assistant

A powerful offline desktop voice assistant for Indian usage with Hindi, English, and Hinglish support.

Features:
- Wake word detection: "Hey Jarvis"
- Offline speech recognition with Vosk
- Local LLM via Ollama (qwen2.5:3b or other local models)
- Voice output using pyttsx3
- Basic desktop control: Notepad, Calculator, File Explorer, browser
- Time/date queries
- Sleep/standby mode
- Smart command routing
- Multi-language support

## Project structure

- `main.py` - entry point
- `jarvis_app/` - assistant modules
- `README.md` - usage guide
- `requirements.txt` - Python dependencies

## Quick start

1. Install Python 3.10+
2. Create a virtual environment
3. Install dependencies:
   `pip install -r requirements.txt`
4. Download Vosk models and place them in a `models/` folder:
   - `models/vosk-model`
   - `models/vosk-model-small-hi-0.22`
5. Make sure Ollama is installed and a model is pulled:
   `ollama pull qwen2.5:3b`
6. Start Ollama:
   `ollama serve`
7. Run:
   `python main.py`

## Notes

- This is designed for Windows desktop usage, but the structure can be adapted for Linux/macOS.
- Vosk models are not bundled due to size.
- For best results, use a good microphone and clear spoken commands.
