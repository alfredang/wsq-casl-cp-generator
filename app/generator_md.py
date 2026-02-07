from pathlib import Path

from app.models import ExtractedData


def generate_md(data: ExtractedData, output_path: Path) -> Path:
    lines: list[str] = []

    # Title
    lines.append(f"# {data.particulars.course_title}")
    lines.append("")
    lines.append(f"**Training Provider:** {data.particulars.training_provider}")
    lines.append(f"**Course Type:** {data.particulars.course_type}")
    lines.append(f"**Unique Skill:** {', '.join(data.particulars.unique_skill_names)}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Section 1: Course Particulars
    lines.append("## Section 1: Course Particulars")
    lines.append("")
    lines.append(f"**Name of Registered Training Provider:** {data.particulars.training_provider}")
    lines.append("")
    lines.append(f"**Course Title:** {data.particulars.course_title}")
    lines.append("")
    lines.append(f"**Course Type:** {data.particulars.course_type}")
    lines.append("")
    lines.append("### About This Course")
    lines.append("")
    lines.append(data.particulars.about_course)
    lines.append("")
    lines.append("### What You Will Learn")
    lines.append("")
    lines.append(data.particulars.what_youll_learn)
    lines.append("")
    lines.append(f"**Unique Skill Name:** {', '.join(data.particulars.unique_skill_names)}")
    lines.append("")

    # Section 2: Course Background
    lines.append("---")
    lines.append("")
    lines.append("## Section 2: Course Background")
    lines.append("")
    lines.append(data.background.targeted_sectors)
    lines.append("")
    if data.background.performance_gaps:
        lines.append(data.background.performance_gaps)
        lines.append("")

    # Section 3: Instructional Design
    lines.append("---")
    lines.append("")
    lines.append("## Section 3: Instructional Design")
    lines.append("")

    # Learning Outcomes table
    lines.append("### Learning Outcomes")
    lines.append("")
    lines.append("| Day | Duration (min) | LO# | Learning Outcome | Topic |")
    lines.append("|-----|---------------|-----|------------------|-------|")
    for lo in data.learning_outcomes:
        lines.append(
            f"| {lo.day} | {lo.duration_minutes} | {lo.lo_number} "
            f"| {lo.learning_outcome} | {lo.topic} |"
        )
    lines.append("")

    # Instruction Methods table
    lines.append("### Instruction Methods")
    lines.append("")
    lines.append("| Day | Method | Duration (min) | Mode of Training |")
    lines.append("|-----|--------|---------------|------------------|")
    for im in data.instruction_methods:
        lines.append(
            f"| {im.day} | {im.method} | {im.duration_minutes} "
            f"| {im.mode_of_training} |"
        )
    lines.append("")

    # Section 4: Assessment
    lines.append("---")
    lines.append("")
    lines.append("## Section 4: Assessment")
    lines.append("")
    lines.append("| Day | Mode of Assessment | Duration (min) | # Assessors | # Candidates |")
    lines.append("|-----|-------------------|---------------|------------|-------------|")
    for am in data.assessment_modes:
        lines.append(
            f"| {am.day} | {am.mode} | {am.duration_minutes} "
            f"| {am.num_assessors} | {am.num_candidates} |"
        )
    lines.append("")

    # Summary
    lines.append("---")
    lines.append("")
    lines.append("## Summary")
    lines.append("")

    # (1) Topics
    lines.append("### (1) Topics covered in this course")
    lines.append("")
    for lo in data.learning_outcomes:
        lines.append(f"- {lo.topic}")
    lines.append("")

    # (2) Instructional methods
    lines.append("### (2) Instructional methods")
    lines.append("")
    unique_methods = list(dict.fromkeys(im.method for im in data.instruction_methods))
    lines.append(", ".join(unique_methods))
    lines.append("")

    # (3) Duration for each topic
    lines.append("### (3) Duration for each topic")
    lines.append("")
    lines.append("| Topic | Duration (min) |")
    lines.append("|-------|---------------|")
    for lo in data.learning_outcomes:
        lines.append(f"| {lo.topic} | {lo.duration_minutes} |")
    lines.append("")

    # Course totals
    lines.append("### Course Totals")
    lines.append("")
    lines.append(f"- **Total Course Duration:** {data.summary.total_course_duration}")
    lines.append(f"- **Total Instructional Duration:** {data.summary.total_instructional_duration}")
    lines.append(f"- **Total Assessment Duration:** {data.summary.total_assessment_duration}")
    lines.append(f"- **Mode of Training:** {data.summary.mode_of_training}")
    lines.append("")

    content = "\n".join(lines)
    output_path.write_text(content, encoding="utf-8")
    return output_path
