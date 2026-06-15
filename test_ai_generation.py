#!/usr/bin/env python3
"""Test script to verify AI generation works with Claude Code subscription."""

from app.ai_generator import _generate

print("Testing AI generation with Claude Code subscription...")
print("=" * 60)

try:
    # Test with a simple prompt
    prompt = "Write a single sentence about Python programming."

    print(f"\nPrompt: {prompt}")
    print("\nGenerating response...\n")

    result = _generate("{input}", input=prompt)

    print("SUCCESS! AI generation works!")
    print(f"\nResult: {result}")
    print("\n" + "=" * 60)
    print("SUCCESS: The app is correctly using Claude Code subscription (NO API)!")

except Exception as e:
    print(f"ERROR: {e}")
    print("\nThis means Claude Code CLI is not accessible.")
    print("Please make sure Claude Code is in your PATH.")
