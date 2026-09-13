import os
import json
import requests
from anthropic import Anthropic
from dotenv import load_dotenv

# ============================================================
# JARVIS - PERSONAL AI ASSISTANT
# Legal Assistant + Book Writer + General Assistant
# ============================================================

load_dotenv()

client = Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY")
)

MODEL = "claude-sonnet-4-6"

MEMORY_FILE = "memory.json"
TASKS_FILE = "tasks.json"
EXPENSES_FILE = "expenses.json"


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are JARVIS, an advanced personal AI assistant.

Your personality is professional, intelligent, calm, strategic,
precise, organized, and direct.

You assist the user with everyday tasks, business, finances,
writing, books, research, and legal matters.

============================================================
GENERAL BEHAVIOR
============================================================

Be concise but useful.

When a problem is complicated, break it into simple steps.

Do not make up facts.

If information is missing, ask for it.

If information may have changed, explain that current research
may be necessary.

Always distinguish between:
- Facts
- Assumptions
- Opinions
- Recommendations

============================================================
LEGAL ASSISTANT MODE
============================================================

You are an AI LEGAL ASSISTANT.

You are NOT a licensed attorney.

Never claim that you are a licensed lawyer or attorney.

Never claim that an attorney-client relationship exists.

Never guarantee that the user will win a case.

Your job is to help the user understand legal issues,
organize information, prepare documents, identify questions,
and prepare for conversations with a qualified attorney.

When the user asks a legal question, think like a highly
organized legal professional.

Analyze the situation using this structure when appropriate:

LEGAL ISSUE
What legal question or problem is involved?

JURISDICTION
Identify the relevant:
- Country
- State
- County
- City
- Federal jurisdiction

FACTS
Identify the facts provided by the user.

MISSING INFORMATION
Identify facts that could materially change the analysis.

APPLICABLE LAW
Explain the relevant legal concepts in plain English.

ARGUMENTS IN THE USER'S FAVOR
Identify reasonable arguments that could support the user.

ARGUMENTS AGAINST THE USER
Identify what the opposing side could argue.

EVIDENCE
Explain what documents, records, messages, photographs,
contracts, witnesses, receipts, or other evidence may matter.

RISKS
Explain possible weaknesses, risks, deadlines, and consequences.

OPTIONS
Explain possible courses of action.

NEXT STEPS
Give the user practical next steps.

QUESTIONS FOR AN ATTORNEY
Give the user a list of useful questions to ask a licensed attorney.

============================================================
LEGAL DOCUMENTS
============================================================

You may help prepare drafts of:

- Demand letters
- Cease-and-desist letters
- Contracts
- Settlement proposals
- Complaints
- Responses
- Motions
- Declarations
- Affidavits
- Case summaries
- Chronologies
- Legal correspondence
- Discovery questions
- Deposition preparation
- Attorney consultation summaries
- Business agreements
- Employment-related documents
- Consumer complaints
- Small-claims preparation
- Evidence summaries

When drafting legal documents:

1. Never invent facts.
2. Never invent signatures.
3. Never invent court cases.
4. Never invent statutes.
5. Never invent legal citations.
6. Use placeholders when information is missing.
7. Clearly identify assumptions.
8. Tell the user when attorney review is advisable.

============================================================
LEGAL RESEARCH
============================================================

If a live legal research tool is available, prioritize authoritative
sources such as:

- Official government websites
- State statutes
- Federal statutes
- Administrative regulations
- Court opinions
- Official court websites
- Government agencies

Do NOT pretend you performed live legal research if no live
research tool is available.

If current law needs to be verified, tell the user that the
information should be checked against current law.

============================================================
IMPORTANT LEGAL SITUATIONS
============================================================

If the user mentions:

- Arrest
- Criminal charges
- Eviction
- Deportation
- Immigration proceedings
- Protective orders
- Domestic violence
- Child custody emergencies
- Court hearings
- Imminent court deadlines
- Prison
- Serious injury
- Threats of immediate legal action

Tell the user that contacting a qualified attorney promptly
may be important.

============================================================
LEGAL INTERVIEW MODE
============================================================

When the user gives you a complicated legal problem and there
is not enough information, do NOT immediately give a long answer.

Instead, interview the user.

Ask the most important questions first.

For example:

1. What state are you in?
2. What happened?
3. When did it happen?
4. Who are the parties involved?
5. Is there a written agreement?
6. Do you have evidence?
7. Has anyone filed a lawsuit?
8. Have you received any official notices?
9. Is there a deadline?
10. What outcome are you trying to achieve?

Ask only the questions necessary to move the analysis forward.

============================================================
CASE ORGANIZATION
============================================================

Help the user organize a legal matter into:

CASE NAME
PARTIES
JURISDICTION
IMPORTANT DATES
FACTS
EVIDENCE
LEGAL ISSUES
POTENTIAL CLAIMS
DEFENSES
RISKS
DEADLINES
NEXT STEPS

When useful, create a chronological timeline.

============================================================
NEGOTIATION
============================================================

You may help the user prepare negotiation strategies.

Explain:

- What the user wants
- What the other side wants
- Strengths
- Weaknesses
- Leverage
- Risks
- Possible settlement positions

Do not encourage illegal threats, harassment, intimidation,
fraud, retaliation, or destruction of evidence.

============================================================
PRIVACY
============================================================

Tell the user not to provide unnecessary:

- Passwords
- Social Security numbers
- Bank account numbers
- Credit card numbers
- Authentication codes
- Private credentials

============================================================
BOOK WRITER AND PUBLISHER MODE
============================================================

When the user asks about writing a book, use the
book_writer_publisher tool when appropriate.

Help with:

- Book ideas
- Titles
- Subtitles
- Outlines
- Chapters
- Characters
- Themes
- Synopses
- Book proposals
- Query letters
- Author biographies
- Publishing strategies
- Ghostwriters
- Editors
- Literary agents
- Publishers
- Self-publishing

Never claim that a famous writer, literary agent, publisher,
or celebrity has agreed to work with the user unless verified.

============================================================
PERSONAL ASSISTANT MODE
============================================================

You also have tools for:

- Weather
- Mathematics
- Tasks
- Stocks
- Expenses
- Books
- Legal assistance

Use the appropriate tool when necessary.

You are JARVIS.

Professional.
Strategic.
Precise.
Calm.
Helpful.
"""


# ============================================================
# FILE HELPERS
# ============================================================

def load_json(filename, default):
    try:
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass

    return default


def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ============================================================
# MEMORY
# ============================================================

def load_memory():
    return load_json(MEMORY_FILE, [])


def save_memory(memory):
    save_json(MEMORY_FILE, memory)


# ============================================================
# WEATHER
# ============================================================

def get_weather(city: str) -> str:
    try:
        url = f"https://wttr.in/{city}?format=j1"

        response = requests.get(
            url,
            timeout=10
        )

        data = response.json()

        current = data["current_condition"][0]

        temperature = current["temp_F"]
        feels_like = current["FeelsLikeF"]
        humidity = current["humidity"]
        description = current["weatherDesc"][0]["value"]

        return (
            f"Weather in {city}: {description}. "
            f"Temperature: {temperature}°F. "
            f"Feels like: {feels_like}°F. "
            f"Humidity: {humidity}%."
        )

    except Exception as e:
        return f"Unable to retrieve weather: {e}"


# ============================================================
# CALCULATOR
# ============================================================

def calculate(expression: str) -> str:
    try:
        allowed = set(
            "0123456789+-*/().% "
        )

        if not all(char in allowed for char in expression):
            return "Invalid mathematical expression."

        result = eval(expression, {"__builtins__": {}}, {})

        return str(result)

    except Exception as e:
        return f"Calculation error: {e}"


# ============================================================
# TASKS
# ============================================================

def add_task(task: str) -> str:
    tasks = load_json(TASKS_FILE, [])

    tasks.append({
        "task": task,
        "completed": False
    })

    save_json(TASKS_FILE, tasks)

    return f"Task added: {task}"


def list_tasks() -> str:
    tasks = load_json(TASKS_FILE, [])

    if not tasks:
        return "You currently have no tasks."

    output = []

    for i, task in enumerate(tasks, start=1):
        status = "✓" if task["completed"] else "○"
        output.append(
            f"{i}. {status} {task['task']}"
        )

    return "\n".join(output)


def complete_task(task_number: int) -> str:
    tasks = load_json(TASKS_FILE, [])

    try:
        index = int(task_number) - 1

        if index < 0 or index >= len(tasks):
            return "That task number does not exist."

        tasks[index]["completed"] = True

        save_json(TASKS_FILE, tasks)

        return f"Completed task: {tasks[index]['task']}"

    except Exception:
        return "Invalid task number."


# ============================================================
# STOCK PRICE
# ============================================================

def get_stock_price(ticker: str) -> str:
    try:
        ticker = ticker.upper()

        url = (
            f"https://query1.finance.yahoo.com/v8/finance/"
            f"chart/{ticker}?range=1d&interval=1m"
        )

        response = requests.get(
            url,
            timeout=10,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        data = response.json()

        result = data["chart"]["result"][0]

        meta = result["meta"]

        price = meta.get("regularMarketPrice")
        currency = meta.get("currency", "USD")

        return (
            f"{ticker}: {price} {currency}"
        )

    except Exception as e:
        return f"Unable to retrieve stock price: {e}"


# ============================================================
# EXPENSES
# ============================================================

def add_expense(
    amount: float,
    category: str,
    note: str = ""
) -> str:

    expenses = load_json(EXPENSES_FILE, [])

    expense = {
        "amount": float(amount),
        "category": category,
        "note": note
    }

    expenses.append(expense)

    save_json(EXPENSES_FILE, expenses)

    return (
        f"Expense added: ${amount:.2f} "
        f"under {category}."
    )


def get_spending_summary() -> str:
    expenses = load_json(EXPENSES_FILE, [])

    if not expenses:
        return "No expenses recorded."

    total = sum(
        float(expense["amount"])
        for expense in expenses
    )

    categories = {}

    for expense in expenses:
        category = expense["category"]

        categories[category] = (
            categories.get(category, 0)
            + float(expense["amount"])
        )

    output = [
        f"Total spending: ${total:.2f}",
        "",
        "By category:"
    ]

    for category, amount in categories.items():
        output.append(
            f"- {category}: ${amount:.2f}"
        )

    return "\n".join(output)


# ============================================================
# BOOK WRITER / PUBLISHER
# ============================================================

def book_writer_publisher(
    request_type: str,
    details: str,
    book_title: str = "",
    genre: str = "",
    audience: str = ""
) -> str:

    prompt = f"""
You are JARVIS's Book Writer and Publishing Specialist.

Request type:
{request_type}

Book title:
{book_title}

Genre:
{genre}

Target audience:
{audience}

User's details:
{details}

Help the user professionally.

If the user is developing a book:
- Improve the concept.
- Develop the structure.
- Create a strong title.
- Develop chapters.
- Improve writing.
- Create a synopsis.
- Create a publishing strategy.

If the user wants a professional:
Explain whether they may need:
- Ghostwriter
- Co-writer
- Developmental editor
- Copy editor
- Literary agent
- Traditional publisher
- Hybrid publisher
- Self-publishing service

Never claim a specific professional has agreed to work
with the user unless verified.

Return a practical, professional answer.
"""

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=3000,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return next(
            (
                block.text
                for block in response.content
                if block.type == "text"
            ),
            ""
        )

    except Exception as e:
        return f"Book writer error: {e}"


# ============================================================
# LEGAL ASSISTANT
# ============================================================

def legal_assistant(
    request_type: str,
    details: str,
    jurisdiction: str = "",
    objective: str = ""
) -> str:

    prompt = f"""
You are JARVIS's Legal Assistant.

You are an AI legal assistant, NOT a licensed attorney.

The user needs help with the following legal matter.

Request type:
{request_type}

Jurisdiction:
{jurisdiction}

User's objective:
{objective}

Details:
{details}

Analyze the matter carefully.

Use this structure when appropriate:

1. LEGAL ISSUE
2. IMPORTANT FACTS
3. MISSING INFORMATION
4. GENERAL LEGAL PRINCIPLES
5. ARGUMENTS IN THE USER'S FAVOR
6. POSSIBLE ARGUMENTS AGAINST THE USER
7. IMPORTANT EVIDENCE
8. RISKS
9. POSSIBLE OPTIONS
10. RECOMMENDED NEXT STEPS
11. QUESTIONS FOR A LICENSED ATTORNEY

Important rules:

- Do not invent laws.
- Do not invent cases.
- Do not invent statutes.
- Do not invent legal citations.
- Do not guarantee an outcome.
- Clearly state when current legal research is necessary.
- If the matter appears urgent, recommend contacting a qualified
  attorney promptly.
- Explain legal terminology in plain English.
- Ask for missing facts when they are necessary.

Be analytical, strategic, and professional.
"""

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=4000,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return next(
            (
                block.text
                for block in response.content
                if block.type == "text"
            ),
            ""
        )

    except Exception as e:
        return f"Legal assistant error: {e}"


# ============================================================
# ANTHROPIC TOOLS
# ============================================================

TOOLS = [

    {
        "name": "get_weather",
        "description": "Get current weather for a city.",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "City name"
                }
            },
            "required": ["city"]
        }
    },

    {
        "name": "calculate",
        "description": "Perform a mathematical calculation.",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Mathematical expression"
                }
            },
            "required": ["expression"]
        }
    },

    {
        "name": "add_task",
        "description": "Add a task to the user's task list.",
        "input_schema": {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string"
                }
            },
            "required": ["task"]
        }
    },

    {
        "name": "list_tasks",
        "description": "List the user's tasks.",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    },

    {
        "name": "complete_task",
        "description": "Mark a task as completed.",
        "input_schema": {
            "type": "object",
            "properties": {
                "task_number": {
                    "type": "integer"
                }
            },
            "required": ["task_number"]
        }
    },

    {
        "name": "get_stock_price",
        "description": "Get a stock's current market price.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string"
                }
            },
            "required": ["ticker"]
        }
    },

    {
        "name": "add_expense",
        "description": "Record an expense.",
        "input_schema": {
            "type": "object",
            "properties": {
                "amount": {
                    "type": "number"
                },
                "category": {
                    "type": "string"
                },
                "note": {
                    "type": "string"
                }
            },
            "required": [
                "amount",
                "category"
            ]
        }
    },

    {
        "name": "get_spending_summary",
        "description": "Show the user's spending summary.",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    },

    {
        "name": "book_writer_publisher",
        "description": """
        Help with book writing, publishing, ghostwriters,
        literary agents, publishers, editing, book proposals,
        and publishing strategy.
        """,
        "input_schema": {
            "type": "object",
            "properties": {

                "request_type": {
                    "type": "string",
                    "description": "Type of book request"
                },

                "details": {
                    "type": "string",
                    "description": "Details about the request"
                },

                "book_title": {
                    "type": "string"
                },

                "genre": {
                    "type": "string"
                },

                "audience": {
                    "type": "string"
                }
            },
            "required": [
                "request_type",
                "details"
            ]
        }
    },

    {
        "name": "legal_assistant",
        "description": """
        Analyze legal situations, organize case information,
        explain legal concepts, prepare legal documents,
        identify evidence, analyze arguments and risks,
        and prepare questions for a licensed attorney.
        """,
        "input_schema": {
            "type": "object",
            "properties": {

                "request_type": {
                    "type": "string",
                    "description": """
                    Type of legal request, such as legal analysis,
                    contract review, demand letter, case preparation,
                    lawsuit preparation, employment issue,
                    landlord tenant issue, business issue, etc.
                    """
                },

                "details": {
                    "type": "string",
                    "description": "Detailed description of the legal matter"
                },

                "jurisdiction": {
                    "type": "string",
                    "description": "State, county, city, or federal jurisdiction"
                },

                "objective": {
                    "type": "string",
                    "description": "What the user wants to accomplish"
                }
            },
            "required": [
                "request_type",
                "details"
            ]
        }
    }
]


# ============================================================
# TOOL ROUTER
# ============================================================

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

    if name == "legal_assistant":
        return legal_assistant(
            request_type=tool_input["request_type"],
            details=tool_input["details"],
            jurisdiction=tool_input.get(
                "jurisdiction",
                ""
            ),
            objective=tool_input.get(
                "objective",
                ""
            )
        )

    return f"Unknown tool: {name}"


# ============================================================
# JARVIS CLASS
# ============================================================

class Jarvis:

    def __init__(self):
        self.history = load_memory()

    def save(self):
        save_memory(self.history)

    def ask(self, user_input: str) -> str:

        self.history.append({
            "role": "user",
            "content": user_input
        })

        response = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=self.history
        )

        while response.stop_reason == "tool_use":

            assistant_content = [
                block.model_dump()
                for block in response.content
            ]

            self.history.append({
                "role": "assistant",
                "content": assistant_content
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
                max_tokens=4096,
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

        self.save()

        return reply

    def reset(self):

        self.history = []

        self.save()


# ============================================================
# MAIN
# ============================================================

def main():

    jarvis = Jarvis()

    print()
    print("==========================================")
    print("           JARVIS ONLINE")
    print("==========================================")
    print()

    if jarvis.history:

        print(
            f"Memory loaded: "
            f"{len(jarvis.history)} messages"
        )

    else:

        print(
            "Memory loaded: Starting fresh."
        )

    print()
    print("Available systems:")
    print("  • Personal Assistant")
    print("  • Legal Assistant")
    print("  • Book Writer & Publisher")
    print("  • Tasks")
    print("  • Expenses")
    print("  • Stocks")
    print("  • Weather")
    print("  • Calculator")
    print()
    print("Type 'quit' to exit.")
    print("Type 'reset' to clear memory.")
    print()
    print("==========================================")
    print()

    while True:

        try:

            user_input = input("You: ").strip()

            if not user_input:
                continue

            if user_input.lower() == "quit":

                print()
                print("JARVIS: Goodbye.")
                print()

                break

            if user_input.lower() == "reset":

                jarvis.reset()

                print()
                print("JARVIS: Memory cleared.")
                print()

                continue

            reply = jarvis.ask(user_input)

            print()
            print("JARVIS:")
            print(reply)
            print()

        except KeyboardInterrupt:

            print()
            print()
            print("JARVIS: Shutdown.")
            break

        except Exception as e:

            print()
            print(f"[ERROR] {e}")
            print()


# ============================================================
# START JARVIS
# ============================================================

if __name__ == "__main__":
    main()
