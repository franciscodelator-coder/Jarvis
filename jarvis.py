"""
Jarvis - Personal AI Assistant
Core text-based brain. Voice, smart home, etc. get layered on top of this later.
"""

import os
import json
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

MODEL = "claude-sonnet-4-6"
MEMORY_FILE = "memory.json"
SYSTEM_PROMPT = """You are Jarvis, a helpful personal assistant.
Be concise and direct. You'll eventually have tools for smart home control
and other tasks, but for now just have natural conversations."""


class Jarvis:
    def __init__(self):
        self.history = self._load_memory()

    def _load_memory(self):
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []

    def _save_memory(self):
        with open(MEMORY_FILE, "w") as f:
            json.dump(self.history, f, indent=2)

    def ask(self, user_input: str) -> str:
        self.history.append({"role": "user", "content": user_input})

        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=self.history,
        )

        reply = response.content[0].text
        self.history.append({"role": "assistant", "content": reply})
        self._save_memory()
        return reply

    def reset(self):
        self.history = []
        self._save_memory()


def main():
    jarvis = Jarvis()
    msg_count = len(jarvis.history)
    if msg_count > 0:
        print(f"Jarvis is online. Remembering {msg_count} previous messages.")
    else:
        print("Jarvis is online. Starting fresh.")
    print("Type 'quit' to exit, 'reset' to clear memory.\n")

    while True:
        user_input = input("You: ").strip()

        if not user_input:
            continue
        if user_input.lower() == "quit":
            print("Jarvis: Goodbye.")
            break
        if user_input.lower() == "reset":
            jarvis.reset()
            print("Jarvis: Memory cleared.\n")
            continue

        try:
            reply = jarvis.ask(user_input)
            print(f"Jarvis: {reply}\n")
        except Exception as e:
            print(f"[Error] {e}\n")


if __name__ == "__main__":
    main()
