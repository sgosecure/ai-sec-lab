"""CLI chatbot with tool calling. Run: python agent.py"""
import json
import logging
import os
import sys

import anthropic
from dotenv import load_dotenv

from tools import TOOL_SCHEMAS, run_tool

load_dotenv()
logging.basicConfig(
    filename="agent.log", level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
log = logging.getLogger("agent")

MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5-5")
SYSTEM = (
    "You are a concise security assistant. Use tools for weather and CVE questions. "
    "If a tool returns an error, tell the user plainly. Never invent CVE details."
)
MAX_TOOL_ROUNDS = 5  # stops runaway loops


def chat_turn(client, messages):
    for _ in range(MAX_TOOL_ROUNDS):
        resp = client.messages.create(
            model=MODEL, max_tokens=1024, system=SYSTEM, tools=TOOL_SCHEMAS, messages=messages,
        )
        log.info("stop_reason=%s usage=%s", resp.stop_reason, resp.usage)
        messages.append({"role": "assistant", "content": resp.content})

        if resp.stop_reason != "tool_use":
            return "".join(b.text for b in resp.content if b.type == "text")

        results = []
        for block in resp.content:
            if block.type == "tool_use":
                print(f"  [tool] {block.name}({block.input})")
                out = run_tool(block.name, block.input)
                results.append({
                    "type": "tool_result", "tool_use_id": block.id,
                    "content": json.dumps(out), "is_error": "error" in out,
                })
        messages.append({"role": "user", "content": results})
    return "Stopped: too many tool calls in one turn."


def main():
    if not os.getenv("ANTHROPIC_API_KEY"):
        sys.exit("Set ANTHROPIC_API_KEY in .env")
    client = anthropic.Anthropic(max_retries=3)  # SDK retries 429/5xx with backoff
    messages = []
    print("Security assistant. Ctrl+C or 'quit' to exit.")
    while True:
        try:
            user = input("\nyou> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if user.lower() in {"quit", "exit"}:
            break
        if not user:
            continue
        messages.append({"role": "user", "content": user})
        try:
            print(f"bot> {chat_turn(client, messages)}")
        except anthropic.APIError as e:
            log.error("api_error %s", e)
            print(f"bot> API error: {e}")
            messages.pop()  # drop the failed user turn


if __name__ == "__main__":
    main()
