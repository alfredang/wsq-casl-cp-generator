from pydantic import BaseModel


class CourseParticulars(BaseModel):
    training_provider: str
    course_title: str
    course_type: str
    about_course: str
    what_youll_learn: str
    unique_skill_names: list[str]


class CourseBackground(BaseModel):
    targeted_sectors: str
    performance_gaps: str


class LearningOutcome(BaseModel):
    day: int
    duration_minutes: int
    lo_number: str
    learning_outcome: str
    topic: str


class InstructionMethod(BaseModel):
    day: int
    method: str
    duration_minutes: int
    mode_of_training: str


class AssessmentMode(BaseModel):
    day: int
    mode: str
    duration_minutes: int
    num_assessors: int
    num_candidates: int


class CourseSummary(BaseModel):
    total_course_duration: str
    total_instructional_duration: str
    total_assessment_duration: str
    mode_of_training: str


class ExtractedData(BaseModel):
    particulars: CourseParticulars
    background: CourseBackground
    learning_outcomes: list[LearningOutcome]
    instruction_methods: list[InstructionMethod]
    assessment_modes: list[AssessmentMode]
    summary: CourseSummary
