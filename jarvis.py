"""
Jarvis - Personal AI Assistant
Core text-based brain. Voice, smart home, etc. get layered on top of this later.
"""

import os
import json
import requests
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

MODEL = "claude-sonnet-4-6"
MEMORY_FILE = "memory.json"
SYSTEM_PROMPT = """You are Jarvis, a helpful personal assistant.
Be concise and direct. You'll eventually have tools for smart home control
and other tasks, but for now just have natural conversations."""

TOOLS = [
    {
        "name": "get_weather",
        "description": "Get the current weather for a city.",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "The city name, e.g. 'London' or 'New York'"
                }
            },
            "required": ["city"]
        }
    },
    {
        "name": "calculate",
        "description": "Evaluate a math expression and return the exact result. Use this for any arithmetic, even simple sums, instead of computing it yourself.",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "A math expression, e.g. '23 * 47' or '(120 + 15) / 3'"
                }
            },
            "required": ["expression"]
        }
    }
]


def get_weather(city: str) -> str:
    try:
        response = requests.get(f"https://wttr.in/{city}?format=3", timeout=10)
        return response.text.strip()
    except Exception as e:
        return f"Couldn't get weather: {e}"


def calculate(expression: str) -> str:
    allowed = set("0123456789+-*/().% ")
    if not set(expression) <= allowed:
        return "Error: expression contains characters that aren't allowed."
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"Error evaluating expression: {e}"


def run_tool(name: str, tool_input: dict) -> str:
    if name == "get_weather":
        return get_weather(tool_input["city"])
    if name == "calculate":
        return calculate(tool_input["expression"])
    return f"Unknown tool: {name}"


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
            tools=TOOLS,
            messages=self.history,
        )

        # Keep handling tool calls until Claude gives a final text answer
        while response.stop_reason == "tool_use":
            serializable_content = [block.model_dump() for block in response.content]
            self.history.append({"role": "assistant", "content": serializable_content})

            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = run_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })

            self.history.append({"role": "user", "content": tool_results})

            response = client.messages.create(
                model=MODEL,
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                tools=TOOLS,
                messages=self.history,
            )

        reply = next((b.text for b in response.content if b.type == "text"), "")
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
