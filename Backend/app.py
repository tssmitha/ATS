from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ats.routes import router as ats_router
from recommend.routes import router as recommend_router
import uvicorn

app = FastAPI(
    title = "ATS and company recommendation API",
    description = "Resume screening and company recommendation system",
    version = "1.0.0",
    docs_url = "/docs",
    redoc_url = "/redocs"   
)

app.add_middleware(
    CORSMiddleware,
    allow_origins= ["http://localhost : 5173"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)

@app.get("/")
async def root():
    return{
        "message" : "ATS and company recommendation system",
        "endpoints":{
            "ats" : "/ats",
            "recommend" : "/recommend",
            "docs" :"/docs"
        }
    }
    
app.include_router(ats_router,prefix="/ats" , tags=["ATS"])
app.include_router(recommend_router,prefix="/recommend" , tags=["Recommendations"])

if __name__ == "__main__":
    uvicorn.run("app:app",host = "0.0.0.0",port=8000, reload=True)
