import os
from pathlib import Path

from fpdf import FPDF

from app.models import ExtractedData

HEADING_COLOR = (68, 114, 196)  # Steel blue matching DOCX template

# Unicode-capable TrueType fonts to use so non-Latin text (e.g. Chinese) renders
# in the PDF. The fpdf2 core fonts (Helvetica) only support Latin-1 and raise on
# characters outside that range. We register the first font found, else fall back
# to Helvetica with unsupported characters replaced (so generation never throws).
_UNICODE_FONT_PATHS = [
    "/Library/Fonts/Arial Unicode.ttf",
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]


def _register_unicode_font(pdf: FPDF) -> str | None:
    """Register a Unicode TTF on the pdf instance. Returns the family name to use,
    or None if no Unicode font is available (caller should fall back to Helvetica)."""
    for path in _UNICODE_FONT_PATHS:
        if os.path.exists(path):
            try:
                pdf.add_font("uni", "", path)
                pdf.add_font("uni", "B", path)  # reuse same file for bold style
                return "uni"
            except Exception:
                continue
    return None


def _safe(text: str, unicode_ok: bool) -> str:
    """Sanitize text for the PDF. With a Unicode font, only smart punctuation is
    normalised. Without one, characters outside Latin-1 are replaced so fpdf2
    never raises."""
    text = _sanitize(text)
    if unicode_ok:
        return text
    return text.encode("latin-1", "replace").decode("latin-1")
_UNICODE_REPLACEMENTS = {
    "\u2013": "-", "\u2014": "-",  # en-dash, em-dash
    "\u2018": "'", "\u2019": "'",  # smart single quotes
    "\u201c": '"', "\u201d": '"',  # smart double quotes
    "\u2026": "...",               # ellipsis
}
DAY_START_MINUTES = 9 * 60
LUNCH_DURATION = 60
DAY_TOTAL_MINUTES = 480


def _sanitize(text: str) -> str:
    for char, replacement in _UNICODE_REPLACEMENTS.items():
        text = text.replace(char, replacement)
    return text


def _fmt_time(minutes_from_midnight: int) -> str:
    h = minutes_from_midnight // 60
    m = minutes_from_midnight % 60
    if h > 12:
        h -= 12
    elif h == 0:
        h = 12
    return f"{h}:{m:02d}"


def _build_schedule(data: ExtractedData) -> dict[int, list[dict]]:
    topics_by_day: dict[int, list] = {}
    for lo in data.learning_outcomes:
        topics_by_day.setdefault(lo.day, []).append(lo)

    assess_by_day: dict[int, int] = {}
    for am in data.assessment_modes:
        assess_by_day[am.day] = assess_by_day.get(am.day, 0) + am.duration_minutes

    num_days = max(topics_by_day.keys()) if topics_by_day else 1
    schedule: dict[int, list[dict]] = {}

    for day in range(1, num_days + 1):
        slots: list[dict] = []
        topics = topics_by_day.get(day, [])
        assess_min = assess_by_day.get(day, 0)

        instruction_min = DAY_TOTAL_MINUTES - assess_min
        num_topics = len(topics)
        per_topic = instruction_min // num_topics if num_topics else 0

        current = DAY_START_MINUTES
        lunch_inserted = False

        for topic in topics:
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
            slots.append({
                "start": _fmt_time(current),
                "end": _fmt_time(end),
                "label": topic.topic,
            })
            current = end

        if not lunch_inserted and assess_min > 0:
            lunch_end = current + LUNCH_DURATION
            slots.append({
                "start": _fmt_time(current),
                "end": _fmt_time(lunch_end),
                "label": "Lunch Break",
            })
            current = lunch_end

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
    text = data.particulars.about_course
    for para in text.split("\n"):
        stripped = para.strip()
        if not stripped:
            continue
        if len(stripped) < 80:
            continue
        if stripped.startswith("- "):
            continue
        return stripped
    return text[:500]


def generate_lesson_plan_pdf(data: ExtractedData, output_path: Path) -> Path:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # --- Title ---
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, _sanitize(f"Lesson Plan: {data.particulars.course_title}"), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # --- Metadata ---
    num_days = max(lo.day for lo in data.learning_outcomes) if data.learning_outcomes else 1
    unique_methods = list(dict.fromkeys(im.method for im in data.instruction_methods))

    training_hours = data.summary.total_instructional_duration
    assessment_hours = data.summary.total_assessment_duration

    pdf.set_font("Helvetica", "", 10)
    metadata_lines = [
        f"Course Duration: {num_days} Days (9:00 AM \u2013 6:00 PM daily)",
        f"Total Training Hours: {training_hours} (excluding lunch breaks)",
        f"Total Assessment Hours: {assessment_hours}",
        f"Instructional Methods: {', '.join(m.lower() for m in unique_methods)}",
    ]
    for line in metadata_lines:
        pdf.cell(0, 6, _sanitize(line), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)

    # --- Course Overview ---
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(*HEADING_COLOR)
    pdf.cell(0, 8, "Course Overview", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(2)

    pdf.set_font("Helvetica", "", 10)
    overview_text = _extract_overview(data)
    pdf.multi_cell(0, 5, _sanitize(overview_text))
    pdf.ln(4)

    # --- Day schedules ---
    schedule = _build_schedule(data)

    for day_num in sorted(schedule.keys()):
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(*HEADING_COLOR)
        pdf.cell(0, 8, f"Day {day_num}", new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(0, 0, 0)
        pdf.ln(2)

        pdf.set_font("Helvetica", "", 10)
        for slot in schedule[day_num]:
            slot_text = f"{slot['start']} - {slot['end']}  |  {slot['label']}"
            pdf.cell(0, 6, _sanitize(slot_text), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)

    pdf.output(str(output_path))
    return output_path


def generate_simple_lesson_plan_pdf(
    course_title: str,
    days: list[list[dict]],
    output_path: Path,
    topic_minutes: int | None = None,
    course_duration_hrs: float | None = None,
) -> Path:
    """Generate a simple lesson plan .pdf with a 4-column table per day:
    Time, Topics, Instructional Methods, Resources.

    ``days`` is the ``days`` list returned by ``build_simple_lesson_plan``.
    """
    from fpdf.fonts import FontFace

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    uni = _register_unicode_font(pdf)
    font = uni or "Helvetica"
    unicode_ok = uni is not None

    # Title (14pt bold)
    pdf.set_font(font, "B", 14)
    pdf.multi_cell(0, 8, _safe(f"Lesson Plan: {course_title}", unicode_ok), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    # Metadata (10pt)
    duration_label = (
        f"{course_duration_hrs:g} hrs / {len(days)} Day(s)"
        if course_duration_hrs
        else f"{len(days)} Day(s)"
    )
    pdf.set_font(font, "", 10)
    meta = [f"Course Duration: {duration_label} (9:00 AM - 6:00 PM daily)"]
    if topic_minutes:
        meta.append(f"Duration per Topic: {topic_minutes} mins")
    for line in meta:
        pdf.multi_cell(0, 6, _safe(line, unicode_ok), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    col_widths = (30, 90, 40, 30)  # total 190mm = full A4 usable width
    heading_style = FontFace(family=font, emphasis="BOLD", color=(255, 255, 255), fill_color=(68, 114, 196))
    keys = ["time", "topic", "method", "resources"]

    for day_idx, rows in enumerate(days, start=1):
        pdf.set_font(font, "B", 12)
        pdf.set_text_color(*HEADING_COLOR)
        pdf.cell(0, 8, f"Day {day_idx}", new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(0, 0, 0)
        pdf.ln(1)

        pdf.set_font(font, "", 10)
        with pdf.table(
            col_widths=col_widths,
            headings_style=heading_style,
            first_row_as_headings=True,
            line_height=pdf.font_size * 1.8,
            text_align="LEFT",
            v_align="TOP",
        ) as table:
            header = table.row()
            for h in ("Time", "Topics", "Instructional Methods", "Resources"):
                header.cell(_safe(h, unicode_ok))
            for row_data in rows:
                row = table.row()
                for key in keys:
                    row.cell(_safe(str(row_data.get(key, "")), unicode_ok))

        pdf.ln(4)

    pdf.output(str(output_path))
    return output_path


def generate_lesson_plan_pdf_table(
    course_title: str,
    course_duration_hrs: int,
    instructional_hrs: int,
    assessment_hrs: int,
    schedule: dict[int, list[dict]],
    output_path: Path,
    instructional_methods: list[str] | None = None,
) -> Path:
    """Generate a lesson plan .pdf with 4-column table (Timing, Duration, Description, Methods).

    Uses Helvetica (PDF equivalent of Arial), 11pt body / 14pt title.
    """
    from fpdf.enums import TableBordersLayout
    from fpdf.fonts import FontFace

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # Title (14pt bold)
    pdf.set_font("Helvetica", "B", 14)
    pdf.multi_cell(0, 8, _sanitize(f"Lesson Plan: {course_title}"), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    # Metadata (10pt)
    num_days = len(schedule)
    methods_text = ", ".join(instructional_methods) if instructional_methods else "N/A"
    pdf.set_font("Helvetica", "", 10)
    meta = [
        f"Course Duration: {course_duration_hrs} hrs / {num_days} Day(s) (9:00 AM - 6:00 PM daily)",
        f"Total Instructional Hours: {instructional_hrs} hrs",
        f"Total Assessment Hours: {assessment_hrs} hrs",
        f"Instructional Methods: {methods_text}",
    ]
    for line in meta:
        pdf.multi_cell(0, 6, _sanitize(line), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # Table styling
    col_widths = (30, 20, 75, 65)  # total 190mm = full A4 usable width
    heading_style = FontFace(emphasis="BOLD", color=(255, 255, 255), fill_color=(68, 114, 196))

    for day_num in sorted(schedule.keys()):
        # Day heading
        pdf.set_font("Helvetica", "BU", 12)
        pdf.set_text_color(*HEADING_COLOR)
        pdf.cell(0, 8, f"Day {day_num}", new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(0, 0, 0)
        pdf.ln(1)

        # Build table using fpdf2 table API (handles text wrapping automatically)
        pdf.set_font("Helvetica", "", 10)
        with pdf.table(
            col_widths=col_widths,
            headings_style=heading_style,
            first_row_as_headings=True,
            line_height=pdf.font_size * 1.8,
            text_align="LEFT",
            v_align="TOP",
        ) as table:
            # Header row
            header = table.row()
            header.cell("Timing")
            header.cell("Duration")
            header.cell("Description")
            header.cell("Instructional Methods")

            # Data rows
            for row_data in schedule[day_num]:
                row = table.row()
                row.cell(_sanitize(row_data["timing"]))
                row.cell(_sanitize(row_data["duration"]))
                row.cell(_sanitize(row_data["description"]))
                row.cell(_sanitize(row_data.get("methods", "")))

        pdf.ln(4)

    pdf.output(str(output_path))
    return output_path
