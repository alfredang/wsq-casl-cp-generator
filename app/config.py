from pathlib import Path

OUTPUT_DIR = Path("output")

# Sheet names
SHEET_PARTICULARS = "1 - Course Particulars"
SHEET_BACKGROUND = "2 - Background"
SHEET_INSTRUCTIONAL_DESIGN = "3 - Instructional Design"
SHEET_METHODOLOGIES = "3 - Methodologies"
SHEET_SUMMARY = "3 - Summary"

# --- Course Particulars (Sheet 1) ---
CELL_TRAINING_PROVIDER = "C2"
CELL_COURSE_TITLE = "C3"
CELL_COURSE_TYPE = "C4"
CELL_ABOUT_COURSE = "C6"
CELL_WHAT_YOULL_LEARN = "C7"
CELL_UNIQUE_SKILL_START_ROW = 10  # Column C, rows 10-79
UNIQUE_SKILL_MAX_ROW = 79

# --- Background (Sheet 2) ---
CELL_TARGETED_SECTORS = "B4"  # merged B4:H6
CELL_PERFORMANCE_GAPS = "B8"  # merged B8:H10

# --- Instructional Design (Sheet 3) ---
ID_DATA_START_ROW = 15
ID_COL_DAY = "B"
ID_COL_DURATION = "C"
ID_COL_LO_NUM = "D"
ID_COL_LO_TEXT = "E"
ID_COL_TOPIC = "F"

# --- Methodologies - Instruction (Sheet 3 - Methodologies) ---
METH_DATA_START_ROW = 7
METH_COL_DAY = "B"
METH_COL_METHOD = "C"
METH_COL_DURATION = "D"
METH_COL_TRAINING_MODE = "E"

# --- Methodologies - Assessment (Sheet 3 - Methodologies) ---
ASSESS_COL_DAY = "J"
ASSESS_COL_MODE = "K"
ASSESS_COL_DURATION = "L"
ASSESS_COL_ASSESSORS = "M"
ASSESS_COL_CANDIDATES = "N"

# --- Summary (Sheet 3 - Summary) ---
SUMM_TOTAL_COURSE_DURATION = "G3"
SUMM_TOTAL_INSTRUCTIONAL = "G4"
SUMM_TOTAL_ASSESSMENT = "I4"
SUMM_MODE_OF_TRAINING = "K4"
