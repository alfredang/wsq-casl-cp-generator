#!/usr/bin/env python3
"""Test topic generation specifically."""

from app.ai_generator import generate_course_topics

print("Testing topic generation...")
print("=" * 60)

try:
    # Test generating topics for a simple course
    course_title = "Introduction to Python Programming"
    num_days = 2

    print(f"Course: {course_title}")
    print(f"Duration: {num_days} days")
    print()
    print("Generating topics...")
    print()

    topics = generate_course_topics(
        course_title=course_title,
        num_days=num_days
    )

    print("SUCCESS! Topics generated!")
    print()
    print("Generated Topics:")
    print("=" * 60)
    print(topics)
    print("=" * 60)
    print()
    print("Topic generation works with Claude Code subscription (NO API)!")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
