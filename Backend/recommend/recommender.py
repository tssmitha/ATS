import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fastapi import HTTPException

try:
    company = pd.read_csv("company.csv")

    if "Name" not in company.columns or "Description" not in company.columns:
        raise ValueError("CSV must contain 'Name' and 'Description'.")

    cv = CountVectorizer(max_features=10000, stop_words="english")
    vector = cv.fit_transform(company["Description"].astype(str)).toarray()
    similarity = cosine_similarity(vector)

except Exception as e:
    print(f"Error loading company data: {e}")
    company = None
    similarity = None

def recommend_company(comp):
    comp = comp.lower().strip()
    company["Name"] = company["Name"].str.lower().str.strip()

    if comp not in company["Name"].values:
        raise HTTPException(status_code=404, detail="Company not found")

    index = company[company["Name"] == comp].index[0]
    distances = sorted(
        list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1]
    )
    recommended = [company.iloc[i[0]].Name for i in distances[1:6]]
    return recommended
from fastapi import FastAPI
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = FastAPI()

# Load company data
company = pd.read_csv("company.csv")

# Process text data
cv = CountVectorizer(max_features=10000, stop_words="english")
vector = cv.fit_transform(company["Description"].values.astype("U")).toarray()

# Compute similarity
similarity = cosine_similarity(vector)

# Function to get recommendations
def recommend_company(comp):
    index = company[company["Name"] == comp].index[0]
    distances = sorted(
        list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1]
    )
    recommended_companies = [company.iloc[i[0]].Name for i in distances[1:6]]
    return recommended_companies

@app.get("/recommend/{company_name}")
def get_recommendations(company_name: str):
    try:
        recommendations = recommend_company(company_name)
        return {"company": company_name, "recommendations": recommendations}
    except:
        return {"error": "Company not found"}


# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# import pandas as pd
# from sklearn.feature_extraction.text import CountVectorizer
# from sklearn.metrics.pairwise import cosine_similarity

# app = FastAPI()

# # Enable CORS for frontend communication
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Change this to ["http://localhost:8100"] in production
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Load company data
# try:
#     company = pd.read_csv("company.csv")

#     # Ensure necessary columns exist
#     if "Name" not in company.columns or "Description" not in company.columns:
#         raise ValueError("CSV file must contain 'Name' and 'Description' columns.")

#     # Process text data
#     cv = CountVectorizer(max_features=10000, stop_words="english")
#     vector = cv.fit_transform(company["Description"].astype(str)).toarray()

#     # Compute similarity
#     similarity = cosine_similarity(vector)

# except Exception as e:
#     print(f"Error loading company data: {e}")
#     company = None
#     similarity = None

# # Function to get recommendations
# def recommend_company(comp):
#     comp = comp.lower().strip()  # Convert input to lowercase for better matching
#     company["Name"] = company["Name"].str.lower().str.strip()  # Normalize company names
    
#     if comp not in company["Name"].values:
#         raise HTTPException(status_code=404, detail="Company not found")

#     index = company[company["Name"] == comp].index[0]
#     distances = sorted(
#         list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1]
#     )

#     recommended_companies = [company.iloc[i[0]].Name for i in distances[1:6]]
#     return recommended_companies

# # API Endpoint to get recommendations
# @app.get("/recommend/{company_name}")
# def get_recommendations(company_name: str):
#     if company is None or similarity is None:
#         raise HTTPException(status_code=500, detail="Company data not loaded")

#     try:
#         recommendations = recommend_company(company_name)
#         return {"company": company_name, "recommendations": recommendations}
#     except HTTPException as e:
#         raise e
#     except Exception:
#         raise HTTPException(status_code=500, detail="Error processing request")
# from fastapi import FastAPI, HTTPException, Query
# from fastapi.middleware.cors import CORSMiddleware
# import pandas as pd
# from sklearn.feature_extraction.text import CountVectorizer
# from sklearn.metrics.pairwise import cosine_similarity

# app = FastAPI()

# # Enable CORS for frontend communication
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Change this to ["http://localhost:8100"] in production
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Load company data
# try:
#     company = pd.read_csv("company.csv")

#     # Ensure necessary columns exist
#     if "Name" not in company.columns or "Description" not in company.columns:
#         raise ValueError("CSV file must contain 'Name' and 'Description' columns.")
#     if "Tech Stack" not in company.columns or "CTC" not in company.columns:
#         raise ValueError("CSV file must contain 'Tech Stack' and 'CTC' columns.")

#     # Process text data
#     cv = CountVectorizer(max_features=10000, stop_words="english")
#     vector = cv.fit_transform(company["Description"].astype(str)).toarray()

#     # Compute similarity
#     similarity = cosine_similarity(vector)

# except Exception as e:
#     print(f"Error loading company data: {e}")
#     company = None
#     similarity = None

# # Function to get recommendations
# def recommend_company(comp, tech_stack=None, ctc=None):
#     comp = comp.lower().strip()  # Convert input to lowercase for better matching
#     company["Name"] = company["Name"].str.lower().str.strip()  # Normalize company names
    
#     if comp not in company["Name"].values:
#         raise HTTPException(status_code=404, detail="Company not found")

#     index = company[company["Name"] == comp].index[0]
#     distances = sorted(
#         list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1]
#     )

#     recommended_companies = []

#     # Filter by tech stack if provided
#     if tech_stack:
#         tech_stack = tech_stack.lower().strip()
#         filtered_companies = company[company["Tech Stack"].str.contains(tech_stack, case=False)]
#     else:
#         filtered_companies = company

#     # Filter by CTC if provided
#     if ctc:
#         filtered_companies = filtered_companies[filtered_companies["CTC"].str.contains(ctc, case=False)]

#     # Get top 5 recommendations
#     for i in distances[1:6]:
#         company_name = company.iloc[i[0]].Name
#         if company_name in filtered_companies["Name"].values:
#             recommended_companies.append(company_name)

#     if not recommended_companies:
#         raise HTTPException(status_code=404, detail="No matching companies found")

#     return recommended_companies

# # API Endpoint to get recommendations
# @app.get("/recommend/")
# def get_recommendations(
#     company_name: str,
#     tech_stack: str = Query(None, max_length=50),
#     ctc: str = Query(None, max_length=50),
# ):
#     if company is None or similarity is None:
#         raise HTTPException(status_code=500, detail="Company data not loaded")

#     try:
#         recommendations = recommend_company(company_name, tech_stack, ctc)
#         return {"company": company_name, "recommendations": recommendations}
#     except HTTPException as e:
#         raise e
#     except Exception:
#         raise HTTPException(status_code=500, detail="Error processing request")

