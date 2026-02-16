from fastapi import HTTPException
from typing import List
import fitz 
import docx
import os
import re
from utils.nlp_models import nlp_models

class ResumeParser:            
    #extracting text from pdf
    @staticmethod
    def extract_text_from_pdf(pdf_path: str) -> str:
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
    
    #extract text from docs   
    @staticmethod
    def extract_text_from_docx(docx_path: str) -> str:
        doc = docx.Document(docx_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            
        if not text.strip():
            raise ValueError("No text found in DOCX")
            
        return text
    
    #extract text from .txt
    @staticmethod
    def extract_text_from_txt(txt_path: str) -> str:
        with open(txt_path, 'r', encoding='utf-8') as f:
            text = f.read()
            
        if not text.strip():
            raise ValueError("Empty text file")
            
        return text
    
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
            raise ValueError("Unsupported file format")
        
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
        stop_words = nlp_models.stop_words
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