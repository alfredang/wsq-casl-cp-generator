from pathlib import Path

from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

from app.models import ExtractedData

HEADING_COLOR = RGBColor(0x44, 0x72, 0xC4)  # Steel blue matching PDF template
DAY_START_MINUTES = 9 * 60  # 9:00 AM in minutes from midnight
LUNCH_DURATION = 60  # 1 hour lunch
DAY_TOTAL_MINUTES = 480  # 8 hours of usable time (9 AM to 6 PM minus 1h lunch)


def _fmt_time(minutes_from_midnight: int) -> str:
    """Format minutes from midnight as clock time (e.g. 540 -> '9:00', 800 -> '1:20')."""
    h = minutes_from_midnight // 60
    m = minutes_from_midnight % 60
    # Use 12-hour display without AM/PM (matching PDF template style)
    if h > 12:
        h -= 12
    elif h == 0:
        h = 12
    return f"{h}:{m:02d}"


def _build_schedule(data: ExtractedData) -> dict[int, list[dict]]:
    """Build a per-day schedule of time slots from extracted data.

    Returns {day_num: [{"start": str, "end": str, "label": str}, ...]}.
    """
    # Group topics by day
    topics_by_day: dict[int, list] = {}
    for lo in data.learning_outcomes:
        topics_by_day.setdefault(lo.day, []).append(lo)

    # Group assessment by day
    assess_by_day: dict[int, int] = {}
    for am in data.assessment_modes:
        assess_by_day[am.day] = assess_by_day.get(am.day, 0) + am.duration_minutes

    num_days = max(topics_by_day.keys()) if topics_by_day else 1
    schedule: dict[int, list[dict]] = {}

    for day in range(1, num_days + 1):
        slots: list[dict] = []
        topics = topics_by_day.get(day, [])
        assess_min = assess_by_day.get(day, 0)

        # Available instruction time = total day minus assessment
        instruction_min = DAY_TOTAL_MINUTES - assess_min
        num_topics = len(topics)
        per_topic = instruction_min // num_topics if num_topics else 0

        current = DAY_START_MINUTES
        lunch_inserted = False

        for topic in topics:
            # Insert lunch if we've crossed ~1:00 PM and haven't yet
            if not lunch_inserted and current >= 13 * 60 - 10:
                lunch_end = current + LUNCH_DURATION
                slots.append({
                    "start": _fmt_time(current),
                    "end": _fmt_time(lunch_end),
                    "label": "Lunch Break",
                })
                current = lunch_end
                lunch_inserted = True

            end = current + per_topic
            # Strip the topic prefix (e.g. "T1: ...") is already in the topic string
            slots.append({
                "start": _fmt_time(current),
                "end": _fmt_time(end),
                "label": topic.topic,
            })
            current = end

        # Insert lunch after last topic if not yet (unlikely but safe)
        if not lunch_inserted and assess_min > 0:
            lunch_end = current + LUNCH_DURATION
            slots.append({
                "start": _fmt_time(current),
                "end": _fmt_time(lunch_end),
                "label": "Lunch Break",
            })
            current = lunch_end

        # Assessment slot at end of day
        if assess_min > 0:
            end = current + assess_min
            slots.append({
                "start": _fmt_time(current),
                "end": _fmt_time(end),
                "label": "Assessment",
            })

        schedule[day] = slots

    return schedule


def _extract_overview(data: ExtractedData) -> str:
    """Extract a concise course overview paragraph from about_course text."""
    text = data.particulars.about_course
    # Find first substantive paragraph (skip section headers like "a. Benefits...")
    for para in text.split("\n"):
        stripped = para.strip()
        if not stripped:
            continue
        # Skip section header lines (e.g. "a. Benefits of the Course...")
        if len(stripped) < 80:
            continue
        if stripped.startswith("- "):
            continue
        return stripped
    return text[:500]


def _add_colored_heading(doc, text: str, level: int = 2):
    """Add a heading with the steel blue color matching the PDF template."""
    heading = doc.add_heading(text, level=level)
    for run in heading.runs:
        run.font.color.rgb = HEADING_COLOR


def generate_lesson_plan(data: ExtractedData, output_path: Path) -> Path:
    doc = Document()

    # Configure default style
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(11)
    style.paragraph_format.space_after = Pt(6)

    # --- Title ---
    title_para = doc.add_paragraph()
    title_run = title_para.add_run(f"Lesson Plan: {data.particulars.course_title}")
    title_run.bold = True
    title_run.font.size = Pt(14)
    title_run.font.name = "Calibri"

    # --- Metadata lines ---
    num_days = max(lo.day for lo in data.learning_outcomes) if data.learning_outcomes else 1
    unique_methods = list(dict.fromkeys(im.method for im in data.instruction_methods))

    # Parse hours from summary strings like "14 hour 0 minutes"
    training_hours = data.summary.total_instructional_duration
    assessment_hours = data.summary.total_assessment_duration

    metadata_lines = [
        f"Course Duration: {num_days} Days (9:00 AM \u2013 6:00 PM daily)",
        f"Total Training Hours: {training_hours} (excluding lunch breaks)",
        f"Total Assessment Hours: {assessment_hours}",
        f"Instructional Methods: {', '.join(m.lower() for m in unique_methods)}",
    ]
    for line in metadata_lines:
        p = doc.add_paragraph(line)
        p.paragraph_format.space_after = Pt(2)

    # --- Course Overview ---
    _add_colored_heading(doc, "Course Overview")
    overview_text = _extract_overview(data)
    doc.add_paragraph(overview_text)

    # --- Day schedules ---
    schedule = _build_schedule(data)

    for day_num in sorted(schedule.keys()):
        _add_colored_heading(doc, f"Day {day_num}")
        for slot in schedule[day_num]:
            slot_text = f"{slot['start']} \u2013 {slot['end']} | {slot['label']}"
            doc.add_paragraph(slot_text)

    doc.save(str(output_path))
    return output_path
