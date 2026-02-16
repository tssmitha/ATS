from fastapi import APIRouter, UploadFile, File, HTTPException
import uuid
import os
from services.resume_parser import ResumeParser
from utils.file_validator import validate_file
from services.resume_scorer import ResumeScorer

router = APIRouter()

upload_folder = "uploads"
os.makedirs(upload_folder, exist_ok=True)

@router.post("/upload")
async def upload_and_analyze(
    resume: UploadFile = File(...),
    job_description: UploadFile = File(...)
):
    try:
        # Validate files
        validate_file(resume)
        validate_file(job_description)
        
        # Generate unique filenames
        resume_filename = f"{uuid.uuid4()}_{resume.filename}"
        jd_filename = f"{uuid.uuid4()}_{job_description.filename}"
        
        resume_path = os.path.join(upload_folder, resume_filename)
        jd_path = os.path.join(upload_folder, jd_filename)
        
        # Save files
        with open(resume_path, "wb") as f:
            content = await resume.read()
            f.write(content)
        
        with open(jd_path, "wb") as f:
            content = await job_description.read()
            f.write(content)
        
        # Extract text
        resume_text = ResumeParser.extract_text(resume_path)
        jd_text = ResumeParser.extract_text(jd_path)
        
        # Calculate scores
        analysis = ResumeScorer.calculate_overall_score(resume_text, jd_text)
        
        # Clean up files
        os.remove(resume_path)
        os.remove(jd_path)
        
        return {
            'success': True,
            'analysis': analysis,
            'resume_filename': resume.filename,
            'jd_filename': job_description.filename
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )