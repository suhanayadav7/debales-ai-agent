#!/usr/bin/env python3
import os, sys
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
sys.path.insert(0, str(Path(__file__).parent))

BANNER = """
╔══════════════════════════════════════════════════════╗
║          DEBALES AI  —  Intelligent Assistant        ║
║     Type your question or 'help' for commands        ║
╚══════════════════════════════════════════════════════╝
"""

def main():
    print(BANNER)
    from src.agent import run_agent
    history = []
    while True:
        try:
            query = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        if not query: continue
        if query.lower() in ("exit","quit"):
            print("Goodbye!"); break
        try:
            answer = run_agent(query, history=history)
        except Exception as exc:
            print(f"[Error] {exc}\n"); continue
        print(f"\nAssistant: {answer}\n")

if __name__ == "__main__":
    main()
