from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List , Dict , Any
import fitz 
import docx
import uuid
import os
import re
from datetime import datetime
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords

#configuration
router = APIRouter()
upload_folder = "uploads"
max_file_size = 10 * 1024 * 1024 #10MB
allowed_extensions = {'.pdf' , '.doc' , '.txt'}
os.makedirs(upload_folder, exist_ok=True)

#loading nlp models
try:
    nlp = spacy.load("eng_core_web_sm")
except:
    nlp = None

#to extract stopwords
try:
    nltk.download('stopwords')
    stop_words = set(stopwords.words('english'))
except:
    stop_words = set()

class ResumeParser:
    @staticmethod
    def validate_file(file: UploadFile) -> None:
        # Checking extension
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Checking file size
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)
        
        if file_size > max_file_size:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Max size: {max_file_size / 1024 / 1024}MB"
            )
            
    #extracting text from pdf
    @staticmethod
    def extract_text_from_pdf(pdf_path: str) -> str:
        try:
            doc = fitz.open(pdf_path)
            text = ""
            for page_num, page in enumerate(doc):
                page_text = page.get_text()
                if page_text.strip():
                    text += page_text + "\n"
            doc.close()
            
            if not text.strip():
                raise ValueError("No text found in PDF")
            
            return text
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to extract text from PDF: {str(e)}"
            )
    
    #extract text from docs   
    @staticmethod
    def extract_text_from_docx(docx_path: str) -> str:
        try:
            doc = docx.Document(docx_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            
            if not text.strip():
                raise ValueError("No text found in DOCX")
            
            return text
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to extract text from DOCX: {str(e)}"
            )
    
    #extract text from .txt
    @staticmethod
    def extract_text_from_txt(txt_path: str) -> str:
        try:
            with open(txt_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            if not text.strip():
                raise ValueError("Empty text file")
            
            return text
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to read text file: {str(e)}"
            )
    
    #extracting text based on file ext
    @staticmethod
    def extract_text(file_path: str) -> str:
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.pdf':
            return ResumeParser.extract_text_from_pdf(file_path)
        elif ext == '.docx':
            return ResumeParser.extract_text_from_docx(file_path)
        elif ext == '.txt':
            return ResumeParser.extract_text_from_txt(file_path)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")
        
    #text cleaning
    @staticmethod
    def clean_text(text: str) -> str:
        # Convert to lowercase
        text = text.lower()
        
        # Remove emails
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove URLs
        text = re.sub(r'http\S+|www.\S+', '', text)
        
        # Remove phone numbers
        text = re.sub(r'\b\d{10}\b|\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b', '', text)
        
        # Remove special characters but keep spaces
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    #extract keywords
    @staticmethod
    def extract_keywords(text: str, top_n: int = 50) -> List[str]:
        # Clean text
        cleaned = ResumeParser.clean_text(text)
        
        # Remove stopwords
        words = []

        for word in cleaned.split():
            if word not in stop_words and len(word) > 2:
                words.append(word)
                return words
            
    @staticmethod
    def extract_skills(text: str) -> List[str]:
        skill_keywords = {
            # Programming Languages
            'python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'php', 'swift', 'kotlin',
            'go', 'rust', 'typescript', 'r', 'matlab', 'scala', 'perl',
            
            # Data Science / ML
            'machine learning', 'deep learning', 'nlp', 'computer vision', 'tensorflow',
            'pytorch', 'keras', 'scikit-learn', 'sklearn', 'pandas', 'numpy', 'matplotlib',
            'seaborn', 'data analysis', 'data visualization', 'statistics', 'sql',
            
            # Web Development
            'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask', 'fastapi',
            'html', 'css', 'bootstrap', 'tailwind', 'jquery', 'rest api', 'graphql',
            
            # Databases
            'mysql', 'postgresql', 'mongodb', 'redis', 'cassandra', 'oracle', 'sql server',
            
            # Cloud & DevOps
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'ci/cd', 'git',
            'terraform', 'ansible',
            
            # Other
            'agile', 'scrum', 'jira', 'excel', 'tableau', 'power bi', 'spark', 'hadoop'
        }
        
        text_lower = text.lower()
        found_skills = []
        
        for skill in skill_keywords:
            if skill in text_lower:
                found_skills.append(skill)
        
        return found_skills
    
class ResumeScorer:  
    #to calculate keyword match scores btw resume and jd
    @staticmethod
    def keyword_matching_score(resume_text: str, jd_text: str) -> Dict[str, Any]:
        resume_keywords = set(ResumeParser.extract_keywords(resume_text))
        jd_keywords = set(ResumeParser.extract_keywords(jd_text))
        
        if not jd_keywords:
            return {
                'score': 0,
                'matched_keywords': [],
                'missing_keywords': [],
                'match_percentage': 0
            }
        
        matched = resume_keywords.intersection(jd_keywords)
        missing = jd_keywords - resume_keywords
        
        score = (len(matched) / len(jd_keywords)) * 100
        
        return {
            'score': round(score, 2),
            'matched_keywords': sorted(list(matched)), 
            'missing_keywords': sorted(list(missing)), 
            'match_percentage': round(len(matched) / len(jd_keywords) * 100, 2)
        }
        
    #semantic searching using tf-idf and cosine similarity
    @staticmethod
    def semantic_similarity_score(resume_text: str, jd_text: str) -> float:
        try:
            # Clean texts
            resume_clean = ResumeParser.clean_text(resume_text)
            jd_clean = ResumeParser.clean_text(jd_text)
            
            # Create TF-IDF vectors
            vectorizer = TfidfVectorizer(
                stop_words='english',
                max_features=1000,
                ngram_range=(1, 2) 
            )
            
            tfidf_matrix = vectorizer.fit_transform([resume_clean, jd_clean])
            
            # Calculate cosine similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            return round(similarity * 100, 2)
        except Exception as e:
            print(f"Semantic similarity error: {e}")
            return 0.0
       
    #matching technical skills
    @staticmethod
    def skills_matching_score(resume_text: str, jd_text: str) -> Dict[str, Any]:
        resume_skills = set(ResumeParser.extract_skills(resume_text))
        jd_skills = set(ResumeParser.extract_skills(jd_text))
        
        if not jd_skills:
            return {
                'score': 0,
                'matched_skills': [],
                'missing_skills': []
            }
        
        matched_skills = resume_skills.intersection(jd_skills)
        missing_skills = jd_skills - resume_skills
        
        score = (len(matched_skills) / len(jd_skills)) * 100
        
        return {
            'score': round(score, 2),
            'matched_skills': sorted(list(matched_skills)),
            'missing_skills': sorted(list(missing_skills))
        }
   
    #calculating overall score
    @staticmethod
    def calculate_overall_score(resume_text: str, jd_text: str) -> Dict[str, Any]:
        # Get individual scores
        keyword_result = ResumeScorer.keyword_matching_score(resume_text, jd_text)
        semantic_score = ResumeScorer.semantic_similarity_score(resume_text, jd_text)
        skills_result = ResumeScorer.skills_matching_score(resume_text, jd_text)
        
        # Weighted scoring
        weights = {
            'keyword': 0.3,
            'semantic': 0.4,
            'skills': 0.3
        }
        
        overall_score = (
            keyword_result['score'] * weights['keyword'] +
            semantic_score * weights['semantic'] +
            skills_result['score'] * weights['skills']
        )
        
        return {
            'overall_score': round(overall_score, 2),
            'breakdown': {
                'keyword_matching': keyword_result,
                'semantic_similarity': semantic_score,
                'skills_matching': skills_result
            },
            'recommendation': ResumeScorer.get_recommendation(overall_score)
        }
    
    #defing hiring recommendation based on score
    @staticmethod
    def get_recommendation(score: float) -> str:
        if score >= 75:
            return "Strong Match - Highly Recommended"
        elif score >= 60:
            return "Good Match - Recommended"
        elif score >= 45:
            return "Moderate Match - Consider for Interview"
        elif score >= 30:
            return "Weak Match - Further Review Needed"
        else:
            return "Poor Match - Not Recommended"

@router.post("/upload")
async def upload_and_analyze(
    resume: UploadFile = File(...),
    job_description: UploadFile = File(...)
):
    try:
        # Validate files
        ResumeParser.validate_file(resume)
        ResumeParser.validate_file(job_description)
        
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
        # os.remove(resume_path)
        # os.remove(jd_path)
        
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