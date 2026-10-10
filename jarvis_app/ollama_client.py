import json
from pathlib import Path

import requests

from jarvis_app.config import OLLAMA_URL, DEFAULT_MODEL


class OllamaClient:
    def __init__(self, model_name: str = DEFAULT_MODEL):
        self.model_name = model_name
        self.history = [
            {
                "role": "system",
                "content": (
                    "You are JARVIS, an offline desktop AI assistant. "
                    "Never invent facts. Keep answers short and spoken-friendly. "
                    "Reply in the same language as the user. "
                    "Support Hindi, English, and Hinglish. "
                    "If you are unsure, admit uncertainty instead of guessing."
                ),
            }
        ]

    def ask(self, question: str) -> str:
        question = str(question).strip()
        if not question:
            return "I did not hear anything. Please say again."

        self.history.append({"role": "user", "content": question})
        if len(self.history) > 9:
            del self.history[1:3]

        try:
            response = requests.post(
                OLLAMA_URL,
                json={
                    "model": self.model_name,
                    "messages": self.history,
                    "stream": False,
                    "options": {
                        "temperature": 0.2,
                        "num_ctx": 2048,
                    },
                },
                timeout=180,
            )
            response.raise_for_status()
            answer = response.json()["message"]["content"].strip()
            self.history.append({"role": "assistant", "content": answer})
            return answer
        except requests.RequestException as exc:
            print(f"[Ollama error] {exc}")
            return "I cannot reach my local AI. Please check that Ollama is running."
