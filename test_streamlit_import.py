#!/usr/bin/env python3
"""Test that mimics how Streamlit imports and uses the AI generator."""

import os
import sys

# Mimic what streamlit_app.py does
if "CLAUDECODE" in os.environ:
    print(f"Unsetting CLAUDECODE: {os.environ['CLAUDECODE']}")
    del os.environ["CLAUDECODE"]
else:
    print("CLAUDECODE not set in environment")

# Now import the generator
from app.ai_generator import generate_course_topics

print("\n" + "=" * 60)
print("Testing topic generation (as Streamlit would do it)")
print("=" * 60)

try:
    # Test with simple parameters
    result = generate_course_topics(
        course_title="Digital Marketing Fundamentals",
        num_days=1
    )

    print("\nSUCCESS! Topics generated:")
    print("=" * 60)
    print(result)
    print("=" * 60)
    print("\nStreamlit will work!")

except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
