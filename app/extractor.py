from pathlib import Path

import openpyxl

from app import config
from app.models import (
    AssessmentMode,
    CourseBackground,
    CourseParticulars,
    CourseSummary,
    ExtractedData,
    InstructionMethod,
    LearningOutcome,
)


def _cell_val(ws, ref: str) -> str:
    """Read a cell value as a stripped string, returning '' if None."""
    val = ws[ref].value
    return str(val).strip() if val is not None else ""


def _extract_particulars(wb) -> CourseParticulars:
    ws = wb[config.SHEET_PARTICULARS]

    # Collect unique skill names from C10:C79
    unique_skills = []
    for row in range(config.CELL_UNIQUE_SKILL_START_ROW, config.UNIQUE_SKILL_MAX_ROW + 1):
        val = ws.cell(row=row, column=3).value  # column C
        if val is None:
            break
        unique_skills.append(str(val).strip())

    return CourseParticulars(
        training_provider=_cell_val(ws, config.CELL_TRAINING_PROVIDER),
        course_title=_cell_val(ws, config.CELL_COURSE_TITLE),
        course_type=_cell_val(ws, config.CELL_COURSE_TYPE),
        about_course=_cell_val(ws, config.CELL_ABOUT_COURSE),
        what_youll_learn=_cell_val(ws, config.CELL_WHAT_YOULL_LEARN),
        unique_skill_names=unique_skills if unique_skills else ["N/A"],
    )


def _extract_background(wb) -> CourseBackground:
    ws = wb[config.SHEET_BACKGROUND]
    return CourseBackground(
        targeted_sectors=_cell_val(ws, config.CELL_TARGETED_SECTORS),
        performance_gaps=_cell_val(ws, config.CELL_PERFORMANCE_GAPS),
    )


def _extract_learning_outcomes(wb) -> list[LearningOutcome]:
    ws = wb[config.SHEET_INSTRUCTIONAL_DESIGN]
    outcomes = []
    row = config.ID_DATA_START_ROW
    while True:
        lo_num = ws[f"{config.ID_COL_LO_NUM}{row}"].value
        if lo_num is None:
            break
        outcomes.append(
            LearningOutcome(
                day=int(ws[f"{config.ID_COL_DAY}{row}"].value or 0),
                duration_minutes=int(ws[f"{config.ID_COL_DURATION}{row}"].value or 0),
                lo_number=str(lo_num).strip(),
                learning_outcome=_cell_val(ws, f"{config.ID_COL_LO_TEXT}{row}"),
                topic=_cell_val(ws, f"{config.ID_COL_TOPIC}{row}").split("\n")[0].strip(),
            )
        )
        row += 1
    return outcomes


def _extract_instruction_methods(wb) -> list[InstructionMethod]:
    ws = wb[config.SHEET_METHODOLOGIES]
    methods = []
    row = config.METH_DATA_START_ROW
    while True:
        method = ws[f"{config.METH_COL_METHOD}{row}"].value
        if method is None:
            break
        methods.append(
            InstructionMethod(
                day=int(ws[f"{config.METH_COL_DAY}{row}"].value or 0),
                method=str(method).strip(),
                duration_minutes=int(ws[f"{config.METH_COL_DURATION}{row}"].value or 0),
                mode_of_training=_cell_val(ws, f"{config.METH_COL_TRAINING_MODE}{row}"),
            )
        )
        row += 1
    return methods


def _extract_assessment_modes(wb) -> list[AssessmentMode]:
    ws = wb[config.SHEET_METHODOLOGIES]
    assessments = []
    row = config.METH_DATA_START_ROW
    while True:
        mode = ws[f"{config.ASSESS_COL_MODE}{row}"].value
        if mode is None:
            break
        assessments.append(
            AssessmentMode(
                day=int(ws[f"{config.ASSESS_COL_DAY}{row}"].value or 0),
                mode=str(mode).strip(),
                duration_minutes=int(ws[f"{config.ASSESS_COL_DURATION}{row}"].value or 0),
                num_assessors=int(ws[f"{config.ASSESS_COL_ASSESSORS}{row}"].value or 0),
                num_candidates=int(ws[f"{config.ASSESS_COL_CANDIDATES}{row}"].value or 0),
            )
        )
        row += 1
    return assessments


def _extract_summary(wb) -> CourseSummary:
    ws = wb[config.SHEET_SUMMARY]
    return CourseSummary(
        total_course_duration=_cell_val(ws, config.SUMM_TOTAL_COURSE_DURATION),
        total_instructional_duration=_cell_val(ws, config.SUMM_TOTAL_INSTRUCTIONAL),
        total_assessment_duration=_cell_val(ws, config.SUMM_TOTAL_ASSESSMENT),
        mode_of_training=_cell_val(ws, config.SUMM_MODE_OF_TRAINING),
    )


def extract_data(file_path: Path) -> ExtractedData:
    wb = openpyxl.load_workbook(file_path, data_only=True)
    try:
        return ExtractedData(
            particulars=_extract_particulars(wb),
            background=_extract_background(wb),
            learning_outcomes=_extract_learning_outcomes(wb),
            instruction_methods=_extract_instruction_methods(wb),
            assessment_modes=_extract_assessment_modes(wb),
            summary=_extract_summary(wb),
        )
    finally:
        wb.close()
