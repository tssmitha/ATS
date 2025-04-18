from fastapi import APIRouter, HTTPException
from recommend.recommender import recommend_company, company, similarity

router = APIRouter()

@router.get("/{company_name}")
def get_recommendations(company_name: str):
    if company is None or similarity is None:
        raise HTTPException(status_code=500, detail="Company data not loaded")

    try:
        recommendations = recommend_company(company_name)
        return {"company": company_name, "recommendations": recommendations}
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(status_code=500, detail="Error processing request")
