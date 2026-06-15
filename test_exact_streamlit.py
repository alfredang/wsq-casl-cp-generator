#!/usr/bin/env python3
"""Test EXACTLY what Streamlit does when you click Generate Topics."""

import os
import sys

# Mimic streamlit_app.py
if "CLAUDECODE" in os.environ:
    print(f"Removing CLAUDECODE: {os.environ['CLAUDECODE']}")
    del os.environ["CLAUDECODE"]

# Import exactly as streamlit does
from app.ai_generator import generate_course_topics, SKILL_DESCRIPTIONS

print("="*70)
print("TESTING EXACT STREAMLIT SCENARIO")
print("="*70)

# Your exact inputs
course_title = "Introduction to Wisdom Teeth Surgery"
unique_skill_name = "Clinical Supervision"
num_days = 2  # Assuming 2 days for 16 hours

print(f"\nCourse Title: {course_title}")
print(f"Unique Skill Name: {unique_skill_name}")
print(f"Duration: {num_days} days")

# Get skill description (CASL mode)
skill_description = SKILL_DESCRIPTIONS.get(unique_skill_name, "")
print(f"\nSkill Description Found: {bool(skill_description)}")
if skill_description:
    print(f"Description: {skill_description[:100]}...")

print("\n" + "="*70)
print("GENERATING TOPICS (as Streamlit does)...")
print("="*70)

try:
    result = generate_course_topics(
        course_title=course_title,
        num_days=num_days,
        skill_description=skill_description
    )

    print("\nSUCCESS!")
    print("="*70)
    print(result)
    print("="*70)
    print("\nIf you see this, Streamlit WILL work!")

except Exception as e:
    print(f"\nERROR (This is what you're seeing in Streamlit):")
    print(f"{type(e).__name__}: {e}")
    print("\nFull traceback:")
    import traceback
    traceback.print_exc()
