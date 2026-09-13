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
        
