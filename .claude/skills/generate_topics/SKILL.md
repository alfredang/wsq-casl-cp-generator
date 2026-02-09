# Course Topics Generation

You are generating or modifying the course topics generation logic. Follow these rules strictly.

## Overview

When generating course topics for CASL mode, the AI should reference the corresponding **skill description** from `skills_description.csv` to produce relevant, aligned topics and learning outcomes.

## Data Source

- `skills_description.csv` in this directory contains the CASL Course Approval Skills List
- Columns: S/N, Skill, Skills Description
- 270 skills with official descriptions from SSG

## How It Works

1. User selects a **Unique Skill Name** from the dropdown (CASL mode)
2. The app looks up the skill's description from the CSV
3. The skill description is included in the AI prompt for topic generation
4. The AI generates topics that are directly relevant to the skill description

## Key Rules

- Topics MUST align with the selected skill description
- Learning outcomes should reflect the competencies described in the skill description
- Use the skill description as context, not as a rigid template
- Topics should still follow a logical learning progression (foundational to advanced)
- Each topic must include 3-5 specific learning outcomes starting with action verbs

## Key Files

- `.claude/skills/generate_topics/skills_description.csv` - CASL skills data (skill names + descriptions)
- `app/ai_generator.py` - `generate_course_topics()` function and prompt template
- `app/ai_generator.py` - `load_skills_data()` loads CSV into (names_list, descriptions_dict)
- `streamlit_app.py` - Course Details page, "Generate Topics with AI" section
