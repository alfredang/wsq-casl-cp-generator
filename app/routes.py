import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.config import OUTPUT_DIR
from app.extractor import extract_data
from app.generator_docx import generate_docx
from app.generator_lesson_plan import generate_lesson_plan

router = APIRouter()


@router.post("/api/generate")
async def generate(file: UploadFile = File(...)):
    if not file.filename or not file.filename.endswith(".xlsx"):
        raise HTTPException(400, "Only .xlsx files are accepted")

    job_id = str(uuid.uuid4())[:8]
    job_dir = OUTPUT_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    upload_path = job_dir / file.filename
    with open(upload_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        data = extract_data(upload_path)

        safe_name = data.particulars.course_title.replace(" ", "_")
        docx_path = job_dir / f"{safe_name}.docx"
        lp_path = job_dir / f"{safe_name}_Lesson_Plan.docx"

        generate_docx(data, docx_path)
        generate_lesson_plan(data, lp_path)

        return {
            "status": "success",
            "job_id": job_id,
            "course_title": data.particulars.course_title,
            "files": {
                "docx": f"/api/download/{job_id}/{safe_name}.docx",
                "lesson_plan": f"/api/download/{job_id}/{safe_name}_Lesson_Plan.docx",
            },
        }
    except Exception as e:
        raise HTTPException(500, f"Processing error: {e}")


@router.get("/api/download/{job_id}/{filename}")
async def download(job_id: str, filename: str):
    file_path = OUTPUT_DIR / job_id / filename
    if not file_path.exists():
        raise HTTPException(404, "File not found")

    media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    return FileResponse(path=str(file_path), filename=filename, media_type=media_type)
