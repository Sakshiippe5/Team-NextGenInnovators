from fastapi import APIRouter, File, UploadFile
from backend.models.schemas import SyllabusUploadResponse
from backend.services.ingestion_service import process_syllabus

router = APIRouter()

@router.post("/upload-syllabus", response_model=SyllabusUploadResponse)
async def upload_syllabus(file: UploadFile = File(...)):
    """
    Ingests syllabus content and maps into a concept tree in Qdrant.
    """
    file_bytes = await file.read()
    return process_syllabus(file_bytes, file.content_type)
