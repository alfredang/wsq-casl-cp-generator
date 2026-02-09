# Lesson Plan Generation

You are generating or modifying the lesson plan schedule logic. Follow these rules strictly.

## Best Practices

- 9:00 AM to 6:00 PM daily
- Lunch: fixed 45 mins, 12:30 PM - 1:15 PM
- Assessment: fixed 4:00 PM - 6:00 PM on last day
- Total duration must match course details
- Duration per topic must match course details (`instructional_hours * 60 / num_topics`)
- Topics can split into 2 sessions (e.g. T2, T2 Cont'd)
- Fill remaining time with breaks to fit exactly 9am-6pm

## Topic Duration (CRITICAL)

- Each topic gets exactly: `instructional_hours * 60 / num_topics` minutes
- Topics must NEVER be compressed, shortened, or dropped
- All topics receive equal time allocation

## Topic Splitting

- Topics CAN be split into 2 sessions to fit the schedule
- Label: "T2: Topic Name" for first session, "T2: Topic Name (Cont'd)" for continuation
- Splits happen at natural barriers: lunch break, end of day
- Minimum session length: 15 minutes (avoid tiny splits; use a Break instead)

## Time Filling

- Fill remaining gaps with "Break" entries to make each day fit exactly 9am-6pm
- Breaks appear before lunch (if topics end early), before assessment, or between sessions
- No empty/unlabeled gaps in the schedule

## Algorithm Overview

The schedule uses a "barrier" approach:
1. Pack topics sequentially from 9:00 AM
2. When approaching a barrier (12:30 lunch, 4:00 assessment, 6:00 day end):
   - If remaining time < 15 mins and barrier is lunch: start lunch early (avoids tiny break next to lunch)
   - If remaining time < 15 mins and barrier is assessment/day-end: insert a Break
   - If topic fits completely: place it
   - If topic doesn't fit: split it at the barrier
3. After all topics placed, fill remaining time with Breaks
4. Always insert Lunch (45 mins) and Assessment at their fixed times
5. Breaks go between topics, never adjacent to lunch

## Reference Example

6 topics, 2 days, 14hr instruction, 2hr assessment. Each topic = 140 mins.

**Day 1:**
```
9:00 - 11:20  | T1: Topic Name (140 mins)
11:20 - 12:30 | T2: Topic Name (70 mins)
12:30 - 1:15  | Lunch Break (45 mins)
1:15 - 2:25   | T2: Topic Name (Cont'd) (70 mins)
2:25 - 4:45   | T3: Topic Name (140 mins)
4:45 - 6:00   | T4: Topic Name (75 mins)
```

**Day 2:**
```
9:00 - 10:05  | T4: Topic Name (Cont'd) (65 mins)
10:05 - 12:25 | T5: Topic Name (140 mins)
12:25 - 1:10  | Lunch Break (45 mins)
1:10 - 3:30   | T6: Topic Name (140 mins)
3:30 - 4:00   | Break (30 mins)
4:00 - 6:00   | Assessment (120 mins)
```

Both days fit exactly 9:00 AM - 6:00 PM.

## Key Files

- `streamlit_app.py` — Schedule building algorithm (search for "Build schedule")
- `app/generator_lesson_plan.py` — Word document table generation
- `app/generator_lesson_plan_pdf.py` — PDF document table generation

## Document Format

Both DOCX and PDF follow the same structure:
1. Title: "Lesson Plan: {Course Title}"
2. Metadata: Course Duration (days), Total Training Hours, Total Assessment Hours, Instructional Methods
3. Course Overview (AI-generated from `lp_text` session state)
4. Day-by-day schedule: Timing | Duration | Description (3-column table)

## Styling

- **DOCX**: Calibri font, steel blue (#4472C4) table headers with white text
- **PDF**: Helvetica font, same steel blue headers, sanitize Unicode (smart quotes, em-dashes, ellipsis)
