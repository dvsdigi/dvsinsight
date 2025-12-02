import os
import requests
import cv2
import numpy as np
from fastapi import APIRouter, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pymongo import MongoClient
from insightface_engine import InsightFaceEngine

router = APIRouter()

# Configuration
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
DB_NAME = os.environ.get('MONGO_DB_NAME', 'DigitalVidyaSaarthi')
# We save to studentEmbedding as requested
COLLECTION_NAME = 'studentEmbedding'

# External API Config
EXTERNAL_API_BASE_URL = os.environ.get('EXTERNAL_API_BASE_URL', 'https://dvsserver-d7fk.onrender.com/api/v1/adminRoute/students')
JWT_TOKEN = os.environ.get('JWT_TOKEN', '')

# Templates
templates = Jinja2Templates(directory="templates")

# MongoDB Connection
try:
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")

# InsightFace Engine (Singleton access pattern or new instance?)
# Better to use the singleton from main, but for simplicity we'll create a new one or import if possible.
# Ideally, we should inject it. For now, let's instantiate it here or rely on the one in main being available?
# No, let's instantiate a fresh one or use a shared module.
# Since InsightFaceEngine is a class, we can instantiate it.
# Note: In a real app, use dependency injection.
engine = InsightFaceEngine()
# We'll prepare it on first use or rely on startup event if we shared it.
# Let's just prepare it here lazily.

def get_engine():
    if engine.app is None:
        engine.prepare()
    return engine

@router.get("/ui", response_class=HTMLResponse)
async def get_enroll_ui(request: Request):
    return templates.TemplateResponse("enroll.html", {"request": request})

@router.get("/fetch/{student_id}")
async def fetch_student(student_id: str):
    """
    Fetches student details from the external API using the static JWT.
    """
    # The user mentioned "fetch the student data filtered on the bases of schoolId" earlier,
    # but now says "entering studentId filter".
    # Assuming the API supports filtering by studentId via query param or path.
    # Let's try query param first as it's common for "filtering": ?studentId=...
    # Or if it's a direct resource: /students/{id}
    # Given the URL .../students, it's likely a list endpoint that accepts filters.
    
    url = f"{EXTERNAL_API_BASE_URL}"
    params = {"studentId": student_id}
    headers = {"Authorization": f"Bearer {JWT_TOKEN}"}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # API might return a list or a single object.
        # We need to find the matching student from the list if it's a list.
        target_student = None
        
        all_students = []
        if isinstance(data, dict) and "allStudent" in data and isinstance(data["allStudent"], list):
             all_students = data["allStudent"]
        elif isinstance(data, list):
             all_students = data
        elif isinstance(data, dict) and "data" in data and isinstance(data["data"], list):
             all_students = data["data"]
        elif isinstance(data, dict):
             # Single object? Check if it matches
             sid = data.get("studentId") or data.get("id")
             if sid == student_id:
                 target_student = data

        if not target_student and all_students:
            # Filter client-side to be safe
            for s in all_students:
                sid = s.get("studentId") or s.get("id")
                if sid == student_id:
                    target_student = s
                    break
            
            # If not found in list, but list is not empty, maybe we should just return 404?
            # Or if the API was supposed to filter, maybe the first one IS the one? 
            # But user says it's wrong. So explicit filtering is best.
            
        if not target_student:
             raise HTTPException(status_code=404, detail=f"Student {student_id} not found in API response")
             
        student_data = target_student

        # Extract photo URL safely
        photo_data = student_data.get("studentImage")
        photo_url = None
        if isinstance(photo_data, dict):
            photo_url = photo_data.get("url")
        elif isinstance(photo_data, str):
            photo_url = photo_data
        
        # Fallback to photoUrl if studentImage is not present/valid
        if not photo_url:
            photo_url = student_data.get("photoUrl")

        # Map fields
        return JSONResponse({
            "student_id": student_data.get("studentId") or student_data.get("id"),
            "student_name": student_data.get("studentName") or student_data.get("name"),
            "photo_url": photo_url,
            "school_id": student_data.get("schoolId")
        })
    except Exception as e:
        print(f"API Error: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching student: {str(e)}")

@router.post("/save")
async def save_student(
    student_id: str = Form(...),
    student_name: str = Form(...),
    photo_url: str = Form(...),
    school_id: str = Form(...)
):
    """
    Downloads image, generates embedding, and saves to MongoDB.
    """
    # 1. Download Image
    try:
        resp = requests.get(photo_url, timeout=10)
        resp.raise_for_status()
        image_array = np.asarray(bytearray(resp.content), dtype=np.uint8)
        img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        if img is None:
             raise HTTPException(status_code=400, detail="Could not decode image")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error downloading image: {str(e)}")

    # 2. Generate Embedding
    eng = get_engine()
    faces = eng.get_faces(img)
    if not faces:
        raise HTTPException(status_code=400, detail="No face detected in the image")
    
    embedding = faces[0]['embedding']

    # 3. Save to MongoDB
    student_doc = {
        "studentId": student_id,
        "studentName": student_name,
        "studentImage": photo_url,
        "schoolId": school_id,
        "vectorEmbedding": embedding
    }
    
    # Upsert based on studentId
    result = collection.update_one(
        {"studentId": student_id},
        {"$set": student_doc},
        upsert=True
    )

    return JSONResponse({
        "status": "success", 
        "message": f"Student {student_id} enrolled successfully.",
        "id": str(result.upserted_id) if result.upserted_id else "Updated"
    })
