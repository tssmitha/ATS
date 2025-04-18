# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import fitz  # PyMuPDF
# import os

# app = Flask(__name__)
# CORS(app)  # Enable CORS for all routes

# UPLOAD_FOLDER = "uploads"
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# def extract_text_from_pdf(pdf_file):
#     doc = fitz.open(pdf_file)
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


# @app.route('/upload', methods=['POST'])
# def upload():
#     if 'resume' not in request.files or 'job_description' not in request.files:
#         return jsonify({"error": "Both resume and job description files are required"}), 400

#     resume_file = request.files['resume']
#     jd_file = request.files['job_description']

#     resume_path = os.path.join(UPLOAD_FOLDER, "resume.pdf")
#     jd_path = os.path.join(UPLOAD_FOLDER, "jd.pdf")

#     resume_file.save(resume_path)
#     jd_file.save(jd_path)

#     try:
#         resume_text = extract_text_from_pdf(resume_path)
#         jd_text = extract_text_from_pdf(jd_path)
#         score = calculate_score(resume_text, jd_text)
#         return jsonify({"score": score})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500


# if __name__ == '__main__':
#     app.run(debug=True)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ats.routes import router as ats_router
from recommend.routes import router as recommend_router

app = FastAPI()
print("Hello from app.py")

# Enable CORS for all origins (change this in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(ats_router, prefix="/ats")
app.include_router(recommend_router, prefix="/recommend")
