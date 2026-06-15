#!/usr/bin/env python3
"""Detailed test to diagnose the issue."""

import os
import sys
import traceback

# Unset CLAUDECODE to avoid nested session error
if "CLAUDECODE" in os.environ:
    print(f"Unsetting CLAUDECODE env var: {os.environ['CLAUDECODE']}")
    del os.environ["CLAUDECODE"]

print("Testing AI generation with detailed error output...")
print("=" * 60)

try:
    from app.ai_generator import _generate, _CLAUDE_CLI_PATH

    print(f"Claude CLI Path: {_CLAUDE_CLI_PATH}")
    print(f"Path exists: {os.path.exists(_CLAUDE_CLI_PATH) if _CLAUDE_CLI_PATH else False}")
    print()

    # Test with a simple prompt
    prompt = "Say 'Hello' in one word."

    print(f"Prompt: {prompt}")
    print("Generating response...")
    print()

    result = _generate("{input}", input=prompt)

    print("SUCCESS! AI generation works!")
    print(f"Result: {result}")
    print("=" * 60)

except Exception as e:
    print("ERROR occurred!")
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {e}")
    print()
    print("Full traceback:")
    traceback.print_exc()
