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
    },
    {
        "name": "add_task",
        "description": "Add a new to-do item to the task list.",
        "input_schema": {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "The task description, e.g. 'buy milk'"
                }
            },
            "required": ["task"]
        }
    },
    {
        "name": "list_tasks",
        "description": "List all current to-do items, showing which are done and which are still pending.",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "complete_task",
        "description": "Mark a task as done, by its number in the list (use list_tasks first to find the number).",
        "input_schema": {
            "type": "object",
            "properties": {
                "task_number": {
                    "type": "integer",
                    "description": "The number of the task to mark complete, starting at 1"
                }
            },
            "required": ["task_number"]
        }
    },
    {
        "name": "get_stock_price",
        "description": "Get the current stock price for a ticker symbol, e.g. AAPL, TSLA, GOOGL.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "The stock ticker symbol, e.g. 'AAPL' for Apple"
                }
            },
            "required": ["ticker"]
        }
    },
    {
        "name": "add_expense",
        "description": "Log a new expense with an amount and category.",
        "input_schema": {
            "type": "object",
            "properties": {
                "amount": {
                    "type": "number",
                    "description": "The amount spent, e.g. 12.50"
                },
                "category": {
                    "type": "string",
                    "description": "Category of the expense, e.g. 'food', 'transport', 'entertainment'"
                },
                "note": {
                    "type": "string",
                    "description": "Optional short note about the expense"
                }
            },
            "required": ["amount", "category"]
        }
    },
    {
        "name": "get_spending_summary",
        "description": "Get a summary of total spending, broken down by category.",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    }
]

TASKS_FILE = "tasks.json"


def _load_tasks():
    if os.path.exists(TASKS_FILE):
        try:
            with open(TASKS_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def _save_tasks(tasks):
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=2)


def add_task(task: str) -> str:
    tasks = _load_tasks()
    tasks.append({"task": task, "done": False})
    _save_tasks(tasks)
    return f"Added task: {task}"


def list_tasks() -> str:
    tasks = _load_tasks()
    if not tasks:
        return "No tasks yet."
    lines = []
    for i, t in enumerate(tasks, start=1):
        mark = "x" if t["done"] else " "
        lines.append(f"{i}. [{mark}] {t['task']}")
    return "\n".join(lines)


def complete_task(task_number: int) -> str:
    tasks = _load_tasks()
    if task_number < 1 or task_number > len(tasks):
        return f"No task number {task_number}."
    tasks[task_number - 1]["done"] = True
    _save_tasks(tasks)
    return f"Marked task {task_number} as done: {tasks[task_number - 1]['task']}"


EXPENSES_FILE = "expenses.json"


def _load_expenses():
    if os.path.exists(EXPENSES_FILE):
        try:
            with open(EXPENSES_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def _save_expenses(expenses):
    with open(EXPENSES_FILE, "w") as f:
        json.dump(expenses, f, indent=2)


def add_expense(amount: float, category: str, note: str = "") -> str:
    expenses = _load_expenses()
    expenses.append({"amount": amount, "category": category.lower(), "note": note})
    _save_expenses(expenses)
    note_str = f" ({note})" if note else ""
    return f"Logged ${amount:.2f} under '{category}'{note_str}"


def get_spending_summary() -> str:
    expenses = _load_expenses()
    if not expenses:
        return "No expenses logged yet."

    totals = {}
    for e in expenses:
        totals[e["category"]] = totals.get(e["category"], 0) + e["amount"]

    total = sum(totals.values())
    lines = [f"{cat}: ${amt:.2f}" for cat, amt in sorted(totals.items(), key=lambda x: -x[1])]
    lines.append(f"---\nTotal: ${total:.2f}")
    return "\n".join(lines)


def get_stock_price(ticker: str) -> str:
    try:
        import yfinance as yf
        stock = yf.Ticker(ticker.upper())
        price = stock.fast_info.last_price
        currency = stock.fast_info.currency
        return f"{ticker.upper()} is currently trading at {price:.2f} {currency}"
    except Exception as e:
        return f"Couldn't get stock price for {ticker}: {e}"


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
    if name == "add_task":
        return add_task(tool_input["task"])
    if name == "list_tasks":
        return list_tasks()
    if name == "complete_task":
        return complete_task(tool_input["task_number"])
    if name == "get_stock_price":
        return get_stock_price(tool_input["ticker"])
    if name == "add_expense":
        return add_expense(tool_input["amount"], tool_input["category"], tool_input.get("note", ""))
    if name == "get_spending_summary":
        return get_spending_summary()
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
