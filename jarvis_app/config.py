# JARVIS AI Assistant

A strong offline desktop AI voice assistant for Indian usage with Hindi, English, and Hinglish support.

## Features
- Wake word detection: "Hey Jarvis"
- Offline speech recognition with Vosk
- Local LLM support using Ollama
- Voice output with pyttsx3
- Desktop control: Notepad, Calculator, File Explorer, browser
- Time/date handling
- Sleep/standby mode
- Conversation and command routing
- Simple contextual memory

## Project structure
- `main.py` - app entry point
- `jarvis_app/assistant.py` - speech loop, wake word flow, command handling
- `jarvis_app/command_router.py` - command detection and action execution
- `jarvis_app/audio_engine.py` - microphone capture
- `jarvis_app/voice_output.py` - text-to-speech
- `jarvis_app/ollama_client.py` - local LLM requests
- `jarvis_app/config.py` - app configuration

## Setup
1. Install Python 3.10+
2. Install dependencies:
   `pip install -r requirements.txt`
3. Create a `models/` folder and add:
   - `models/vosk-model`
   - `models/vosk-model-small-hi-0.22`
4. Start Ollama:
   `ollama serve`
5. Pull a model:
   `ollama pull qwen2.5:3b`
6. Run:
   `python main.py`

## Important notes
- This app is optimized for Windows desktop usage.
- For best results, use a good microphone and speak clearly.
- Vosk models are large and are not included in this repository.
- If a command is unclear, JARVIS will ask you to repeat it instead of guessing.

## Example commands
- "Hey Jarvis"
- "What time is it"
- "Open notepad"
- "Open calculator"
- "So jao"
- "Goodbye"
- "What is the capital of India?"

## Roadmap
- Better intent routing
- More app/file actions
- Browser automation
- Startup integration
- Better memory and context
- Full Indian-language command tuning
