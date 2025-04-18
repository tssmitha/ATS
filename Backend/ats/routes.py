# from fastapi import APIRouter, UploadFile, File, HTTPException
# from fastapi.responses import JSONResponse
# import fitz  # PyMuPDF
# import os

# router = APIRouter()
# UPLOAD_FOLDER = "uploads"
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# def extract_text_from_pdf(pdf_file_path):
#     doc = fitz.open(pdf_file_path)
#     text = ""
#     for page in doc:
#         text += page.get_text()
#     doc.close()
#     return text.lower()

# def calculate_score(resume_text, jd_text):
#     jd_keywords = set(jd_text.split())
#     resume_words = set(resume_text.split())
#     matched = jd_keywords.intersection(resume_words)
#     score = (len(matched) / len(jd_keywords)) * 100 if jd_keywords else 0
#     return round(score, 2)

# @router.post("/upload")
# async def upload(resume: UploadFile = File(...), job_description: UploadFile = File(...)):
#     try:
#         resume_path = os.path.join(UPLOAD_FOLDER, "resume.pdf")
#         jd_path = os.path.join(UPLOAD_FOLDER, "jd.pdf")

#         with open(resume_path, "wb") as f:
#             f.write(await resume.read())
#         with open(jd_path, "wb") as f:
#             f.write(await job_description.read())

#         resume_text = extract_text_from_pdf(resume_path)
#         jd_text = extract_text_from_pdf(jd_path)
#         score = calculate_score(resume_text, jd_text)

#         return {"score": score}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
# ats/routes.py
from fastapi import APIRouter, UploadFile, File, HTTPException
import fitz  # PyMuPDF
import os

router = APIRouter()
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def extract_text_from_pdf(pdf_file_path):
    doc = fitz.open(pdf_file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text.lower()

def calculate_score(resume_text, jd_text):
    jd_keywords = set(jd_text.split())
    resume_words = set(resume_text.split())
    matched = jd_keywords.intersection(resume_words)
    score = (len(matched) / len(jd_keywords)) * 100 if jd_keywords else 0
    return round(score, 2)

@router.post("/upload")
async def upload(resume: UploadFile = File(...), job_description: UploadFile = File(...)):
    try:
        resume_path = os.path.join(UPLOAD_FOLDER, "resume.pdf")
        jd_path = os.path.join(UPLOAD_FOLDER, "jd.pdf")

        with open(resume_path, "wb") as f:
            f.write(await resume.read())
        with open(jd_path, "wb") as f:
            f.write(await job_description.read())

        resume_text = extract_text_from_pdf(resume_path)
        jd_text = extract_text_from_pdf(jd_path)
        score = calculate_score(resume_text, jd_text)

        return {"score": score}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
