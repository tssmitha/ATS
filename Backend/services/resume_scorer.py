from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Dict , Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords
from services.resume_parser import ResumeParser

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