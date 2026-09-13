import os
import json
import requests
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

MODEL = "claude-sonnet-4-6"
MEMORY_FILE = "memory.json"
TASKS_FILE = "tasks.json"
EXPENSES_FILE = "expenses.json"

SYSTEM_PROMPT = """
You are JARVIS, a helpful personal AI assistant.

Be concise, direct, intelligent, and practical.

You have tools for:
- Weather
- Mathematics
- Tasks and to-do lists
- Stock prices
- Expenses and spending
- Book writing and publishing

When a user asks about writing a book, developing a book idea,
finding professional writers, ghostwriters, literary agents, publishers,
or preparing a book for publication, use the book_writer_publisher tool
when appropriate.

For book-related work:
- Help develop the user's original ideas.
- Help create titles, subtitles, outlines, chapter structures,
  synopses, character profiles, themes, and book proposals.
- Help prepare query letters, author bios, submission packages,
  and publishing plans.
- Help identify the appropriate type of professional:
  ghostwriter, co-writer, developmental editor, literary agent,
  traditional publisher, hybrid publisher, or self-publishing service.
- Never claim that a famous writer, agent, or publisher has agreed
  to work with the user unless there is verified evidence.
- Never invent prices, contracts, contact information, submission
  requirements, availability, or acceptance.
- Clearly distinguish between known information and information
  that needs current research.

When a request requires current information from the internet,
do not pretend you performed live research unless a web research
tool is actually available.

You are the user's personal assistant and should help turn ideas
into real projects step by step.
"""


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
        "description": "Evaluate a math expression and return the exact result. Use this for any arithmetic, even simple sums.",
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
                    "description": "The task description, e.g. 'finish chapter 3'"
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
        "description": "Mark a task as done by its number in the list. Use list_tasks first to find the number.",
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
                    "description": "The stock ticker symbol"
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
                    "description": "The amount spent"
                },
                "category": {
                    "type": "string",
                    "description": "Category of the expense"
                },
                "note": {
                    "type": "string",
                    "description": "Optional short note"
                }
            },
            "required": ["amount", "category"]
        }
    },

    {
        "name": "get_spending_summary",
        "description": "Get a summary of total spending broken down by category.",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    },

    {
        "name": "book_writer_publisher",
        "description": """
        Act as the user's professional Book Writer & Publisher assistant.

        Use this tool for requests involving:
        - Developing a book idea
        - Creating a book title
        - Creating a subtitle
        - Building a book outline
        - Creating chapter plans
        - Developing characters
        - Writing a synopsis
        - Creating a book proposal
        - Creating a query letter
        - Creating an author bio
        - Preparing a submission package
        - Finding the appropriate type of professional writer
        - Finding ghostwriters
        - Finding developmental editors
        - Finding literary agents
        - Finding publishers
        - Comparing traditional publishing, hybrid publishing,
          and self-publishing
        - Creating a publishing strategy

        The tool should never claim that a famous author, ghostwriter,
        agent, or publisher has agreed to work with the user unless
        verified evidence exists.

        Do not invent availability, prices, contact information,
        contracts, submission requirements, or acceptance decisions.

        When current internet research is unavailable, clearly state
        that current verification is needed rather than fabricating
        results.
        """,
        "input_schema": {
            "type": "object",
            "properties": {
                "request_type": {
                    "type": "string",
                    "enum": [
                        "book_idea",
                        "title",
                        "outline",
                        "chapters",
                        "synopsis",
                        "query_letter",
                        "book_proposal",
                        "author_bio",
                        "submission_package",
                        "find_writer",
                        "find_ghostwriter",
                        "find_editor",
                        "find_literary_agent",
                        "find_publisher",
                        "compare_publishers",
                        "publishing_strategy",
                        "general"
                    ],
                    "description": "The type of book or publishing help requested."
                },
                "book_title": {
                    "type": "string",
                    "description": "Current working title of the book, if available."
                },
                "genre": {
                    "type": "string",
                    "description": "Book genre, such as memoir, thriller, romance, biography, self-help, business, fantasy, etc."
                },
                "audience": {
                    "type": "string",
                    "description": "Intended readership."
                },
                "details": {
                    "type": "string",
                    "description": "The user's book idea, requirements, notes, or research request."
                }
            },
            "required": ["request_type", "details"]
        }
    }
]


# ---------------------------------------------------------
# TASKS
# ---------------------------------------------------------

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

    tasks.append({
        "task": task,
        "done": False
    })

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

    return (
        f"Marked task {task_number} as done: "
        f"{tasks[task_number - 1]['task']}"
    )


# ---------------------------------------------------------
# EXPENSES
# ---------------------------------------------------------

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


def add_expense(
    amount: float,
    category: str,
    note: str = ""
) -> str:

    expenses = _load_expenses()

    expenses.append({
        "amount": amount,
        "category": category.lower(),
        "note": note
    })

    _save_expenses(expenses)

    note_str = f" ({note})" if note else ""

    return (
        f"Logged ${amount:.2f} under "
        f"'{category}'{note_str}"
    )


def get_spending_summary() -> str:
    expenses = _load_expenses()

    if not expenses:
        return "No expenses logged yet."

    totals = {}

    for expense in expenses:
        category = expense["category"]
        amount = expense["amount"]

        totals[category] = totals.get(category, 0) + amount

    total = sum(totals.values())

    lines = [
        f"{cat}: ${amt:.2f}"
        for cat, amt in sorted(
            totals.items(),
            key=lambda x: -x[1]
        )
    ]

    lines.append(f"---\nTotal: ${total:.2f}")

    return "\n".join(lines)


# ---------------------------------------------------------
# STOCKS
# ---------------------------------------------------------

def get_stock_price(ticker: str) -> str:
    try:
        import yfinance as yf

        stock = yf.Ticker(ticker.upper())

        price = stock.fast_info.last_price
        currency = stock.fast_info.currency

        return (
            f"{ticker.upper()} is currently trading at "
            f"{price:.2f} {currency}"
        )

    except Exception as e:
        return (
            f"Couldn't get stock price for "
            f"{ticker}: {e}"
        )


# ---------------------------------------------------------
# WEATHER
# ---------------------------------------------------------

def get_weather(city: str) -> str:
    try:
        response = requests.get(
            f"https://wttr.in/{city}?format=3",
            timeout=10
        )

        response.raise_for_status()

        return response.text.strip()

    except Exception as e:
        return f"Couldn't get weather: {e}"


# ---------------------------------------------------------
# CALCULATOR
# ---------------------------------------------------------

def calculate(expression: str) -> str:

    allowed = set(
        "0123456789+-*/().% "
    )

    if not set(expression) <= allowed:
        return (
            "Error: expression contains "
            "characters that aren't allowed."
        )

    try:
        result = eval(
            expression,
            {"__builtins__": {}},
            {}
        )

        return str(result)

    except Exception as e:
        return f"Error evaluating expression: {e}"


# ---------------------------------------------------------
# BOOK WRITER & PUBLISHER
# ---------------------------------------------------------

def book_writer_publisher(
    request_type: str,
    details: str,
    book_title: str = "",
    genre: str = "",
    audience: str = ""
) -> str:

    context_parts = []

    if book_title:
        context_parts.append(
            f"Working book title: {book_title}"
        )

    if genre:
        context_parts.append(
            f"Genre: {genre}"
        )

    if audience:
        context_parts.append(
            f"Target audience: {audience}"
        )

    context = "\n".join(context_parts)

    request_descriptions = {
        "book_idea":
            "Develop and strengthen the user's book idea.",

        "title":
            "Create strong, marketable book titles and subtitles.",

        "outline":
            "Create a professional book outline.",

        "chapters":
            "Create a detailed chapter-by-chapter structure.",

        "synopsis":
            "Create a professional synopsis.",

        "query_letter":
            "Create a professional literary query letter.",

        "book_proposal":
            "Create a professional book proposal.",

        "author_bio":
            "Create a compelling professional author biography.",

        "submission_package":
            "Create a complete publishing submission package.",

        "find_writer":
            "Help determine what kind of professional writer would be appropriate.",

        "find_ghostwriter":
            "Help determine what kind of ghostwriter would be appropriate.",

        "find_editor":
            "Help determine what type of editor is needed.",

        "find_literary_agent":
            "Explain how to identify appropriate literary agents.",

        "find_publisher":
            "Explain how to identify appropriate publishers.",

        "compare_publishers":
            "Create a framework for comparing publishers.",

        "publishing_strategy":
            "Create a professional publishing strategy.",

        "general":
            "Provide professional book-writing and publishing assistance."
    }

    description = request_descriptions.get(
        request_type,
        request_descriptions["general"]
    )

    prompt = f"""
You are the Book Writer & Publisher module inside JARVIS.

Task:
{description}

User request:
{details}

Book context:
{context}

Important rules:

1. Do not fabricate facts about real writers, agents, publishers,
   contracts, prices, availability, or submission requirements.

2. If the request requires current research, explain that current
   web verification is required unless live web research is available.

3. Help the user turn their idea into a professional book project.

4. When recommending a professional, distinguish between:
   - Famous author
   - Ghostwriter
   - Co-writer
   - Developmental editor
   - Copy editor
   - Literary agent
   - Traditional publisher
   - Hybrid publisher
   - Self-publishing service

5. For publishing recommendations, consider:
   - Genre
   - Target audience
   - Commercial potential
   - Author platform
   - Geographic market
   - Traditional vs independent publishing
   - Agent requirements
   - Submission requirements

6. If the user wants a famous writer, explain that famous authors
   may not personally accept outside writing projects and that a
   professional ghostwriter or co-writer may be more realistic.

7. Never state that a person has agreed to work with the user unless
   that agreement is verified.

8. Make the result practical and actionable.

Return a polished response that JARVIS can give directly to the user.
"""

    try:

        response = client.messages.create(
            model=MODEL,
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        text_parts = [
            block.text
            for block in response.content
            if block.type == "text"
        ]

        return "\n".join(text_parts)

    except Exception as e:
        return (
            "The Book Writer & Publisher module encountered "
            f"an error: {e}"
        )


# ---------------------------------------------------------
# TOOL ROUTER
# ---------------------------------------------------------

def run_tool(name: str, tool_input: dict) -> str:

    if name == "get_weather":
        return get_weather(
            tool_input["city"]
        )

    if name == "calculate":
        return calculate(
            tool_input["expression"]
        )

    if name == "add_task":
        return add_task(
            tool_input["task"]
        )

    if name == "list_tasks":
        return list_tasks()

    if name == "complete_task":
        return complete_task(
            tool_input["task_number"]
        )

    if name == "get_stock_price":
        return get_stock_price(
            tool_input["ticker"]
        )

    if name == "add_expense":
        return add_expense(
            tool_input["amount"],
            tool_input["category"],
            tool_input.get("note", "")
        )

    if name == "get_spending_summary":
        return get_spending_summary()

    if name == "book_writer_publisher":
        return book_writer_publisher(
            request_type=tool_input["request_type"],
            details=tool_input["details"],
            book_title=tool_input.get("book_title", ""),
            genre=tool_input.get("genre", ""),
            audience=tool_input.get("audience", "")
        )

    return f"Unknown tool: {name}"


# ---------------------------------------------------------
# JARVIS
# ---------------------------------------------------------

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
            json.dump(
                self.history,
                f,
                indent=2
            )

    def ask(self, user_input: str) -> str:

        self.history.append({
            "role": "user",
            "content": user_input
        })

        response = client.messages.create(
            model=MODEL,
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=self.history
        )

        # Continue handling tools until Claude
        # produces the final answer.

        while response.stop_reason == "tool_use":

            serializable_content = [
                block.model_dump()
                for block in response.content
            ]

            self.history.append({
                "role": "assistant",
                "content": serializable_content
            })

            tool_results = []

            for block in response.content:

                if block.type == "tool_use":

                    result = run_tool(
                        block.name,
                        block.input
                    )

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })

            self.history.append({
                "role": "user",
                "content": tool_results
            })

            response = client.messages.create(
                model=MODEL,
                max_tokens=2048,
                system=SYSTEM_PROMPT,
                tools=TOOLS,
                messages=self.history
            )

        reply = next(
            (
                block.text
                for block in response.content
                if block.type == "text"
            ),
            ""
        )

        self.history.append({
            "role": "assistant",
            "content": reply
        })

        self._save_memory()

        return reply

    def reset(self):

        self.history = []

        self._save_memory()


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main():

    jarvis = Jarvis()

    msg_count = len(jarvis.history)

    if msg_count > 0:

        print(
            f"JARVIS is online. "
            f"Remembering {msg_count} previous messages."
        )

    else:

        print(
            "JARVIS is online. "
            "Starting fresh."
        )

    print(
        "Type 'quit' to exit, "
        "'reset' to clear memory.\n"
    )

    while True:

        user_input = input(
            "You: "
        ).strip()

        if not user_input:
            continue

        if user_input.lower() == "quit":

            print(
                "JARVIS: Goodbye."
            )

            break

        if user_input.lower() == "reset":

            jarvis.reset()

            print(
                "JARVIS: Memory cleared.\n"
            )

            continue

        try:

            reply = jarvis.ask(
                user_input
            )

            print(
                f"JARVIS: {reply}\n"
            )

        except Exception as e:

            print(
                f"[Error] {e}\n"
            )


if __name__ == "__main__":
    main()
