"""Deterministic 'simple' lesson plan schedule builder.

Builds a per-day timetable from saved course details (topics, instructional
methods/duration, assessment methods/duration) following the project's lesson
plan rules:

- 9:00 AM to 6:00 PM daily
- Topics get equal time: instructional_hours * 60 / num_topics (never compressed)
- Lunch: fixed 45 mins, 12:30 PM - 1:15 PM (started early if a tiny gap remains)
- Assessment: fixed, ending at 6:00 PM on the last day
- Topics can split into 2 sessions (e.g. "T2: ... (Cont'd)") at lunch/day barriers
- Remaining time is filled with Break entries so each day fits exactly 9am-6pm

The output rows are intentionally simple: Time, Topics, Instructional Methods,
Resources.
"""
import math
import re

DAY_START = 9 * 60          # 9:00 AM in minutes from midnight
DAY_END = 18 * 60           # 6:00 PM
LUNCH_START = 12 * 60 + 30  # 12:30 PM
LUNCH_END = 13 * 60 + 15    # 1:15 PM
LUNCH_DUR = 45
MIN_SESSION = 15            # avoid tiny topic slivers next to a barrier
TRAINING_MINS_PER_DAY = 480  # 8 training hours per day

DEFAULT_RESOURCES = "Slides, TV, Wifi"


def fmt_time(minutes: int) -> str:
    """Format minutes-from-midnight as 'h:mm AM/PM'."""
    h, m = divmod(minutes, 60)
    ampm = "AM" if h < 12 else "PM"
    hh = h % 12 or 12
    return f"{hh}:{m:02d} {ampm}"


def _parse_topic_titles(course_topics: str) -> list[str]:
    """Extract topic titles from markdown '## Topic N: Title' lines."""
    titles = re.findall(r"^##\s*Topic\s*\d+\s*:\s*(.+)$", course_topics or "", re.MULTILINE)
    return [t.strip() for t in titles]


def build_simple_lesson_plan(
    course_topics: str,
    num_topics: int,
    instructional_hours: float,
    assessment_hours: float,
    instructional_methods: list[str],
    assessment_methods: list[str],
    resources: str = DEFAULT_RESOURCES,
) -> dict:
    """Build a simple per-day lesson plan schedule.

    Returns a dict with:
      - days: list of days, each a list of row dicts
              {"time", "topic", "method", "resources"}
      - topic_minutes: equal minutes allocated per topic
      - num_days: number of days
    """
    num_topics = max(1, int(num_topics))
    titles = _parse_topic_titles(course_topics)
    methods = [m for m in (instructional_methods or []) if m] or ["-"]

    topic_minutes = int(round(instructional_hours * 60 / num_topics))
    assess_min = int(round(assessment_hours * 60))

    # Topic queue, each topic gets equal time and one (rotating) instructional method.
    queue = []
    for i in range(num_topics):
        title = titles[i] if i < len(titles) else f"Topic {i + 1}"
        queue.append({
            "label": f"T{i + 1}: {title}",
            "remaining": topic_minutes,
            "method": methods[i % len(methods)],
            "started": False,
        })

    total_training = topic_minutes * num_topics + assess_min
    num_days = max(1, math.ceil(total_training / TRAINING_MINS_PER_DAY))

    assess_label = ", ".join(assessment_methods) if assessment_methods else "Assessment"

    days = []
    for day_i in range(1, num_days + 1):
        is_last = day_i == num_days
        rows = []
        t = DAY_START
        lunch_done = False
        # Topics must finish by hard_end; assessment (if any) occupies the tail of the last day.
        hard_end = (DAY_END - assess_min) if (is_last and assess_min > 0) else DAY_END

        # Assessment-only day: no topics left to place — just show the assessment
        # at the start of the day instead of padding the whole day with breaks.
        if is_last and assess_min > 0 and not queue:
            days.append([{
                "time": f"{fmt_time(DAY_START)} - {fmt_time(DAY_START + assess_min)}",
                "topic": assess_label,
                "method": "Assessment",
                "resources": resources,
            }])
            continue

        while t < hard_end and queue:
            # Lunch as soon as we reach 12:30.
            if not lunch_done and t >= LUNCH_START:
                rows.append(_break_row(t, t + LUNCH_DUR, "Lunch Break"))
                t += LUNCH_DUR
                lunch_done = True
                continue

            barrier = LUNCH_START if not lunch_done else hard_end
            avail = barrier - t

            if avail < MIN_SESSION:
                if barrier == LUNCH_START and not lunch_done:
                    # Start lunch early to avoid a tiny break next to lunch.
                    rows.append(_break_row(t, t + LUNCH_DUR, "Lunch Break"))
                    t += LUNCH_DUR
                    lunch_done = True
                else:
                    rows.append(_break_row(t, barrier, "Break"))
                    t = barrier
                continue

            chunk = queue[0]
            take = min(chunk["remaining"], avail)
            label = chunk["label"] + (" (Cont'd)" if chunk["started"] else "")
            rows.append({
                "time": f"{fmt_time(t)} - {fmt_time(t + take)}",
                "topic": label,
                "method": chunk["method"],
                "resources": resources,
            })
            t += take
            chunk["remaining"] -= take
            chunk["started"] = True
            if chunk["remaining"] <= 0:
                queue.pop(0)

        # Fill the rest of the day so it ends exactly at hard_end (with lunch if still pending).
        if t < hard_end and not lunch_done:
            if t < LUNCH_START:
                if LUNCH_START - t >= 1:
                    rows.append(_break_row(t, LUNCH_START, "Break"))
                rows.append(_break_row(LUNCH_START, LUNCH_END, "Lunch Break"))
                t = LUNCH_END
            else:
                rows.append(_break_row(t, t + LUNCH_DUR, "Lunch Break"))
                t += LUNCH_DUR
            lunch_done = True
        if t < hard_end:
            rows.append(_break_row(t, hard_end, "Break"))
            t = hard_end

        # Assessment fills the tail of the last day.
        if is_last and assess_min > 0:
            rows.append({
                "time": f"{fmt_time(hard_end)} - {fmt_time(hard_end + assess_min)}",
                "topic": assess_label,
                "method": "Assessment",
                "resources": resources,
            })

        days.append(rows)

    return {"days": days, "topic_minutes": topic_minutes, "num_days": num_days}


def _break_row(start: int, end: int, label: str) -> dict:
    return {
        "time": f"{fmt_time(start)} - {fmt_time(end)}",
        "topic": label,
        "method": "-",
        "resources": "-",
    }
