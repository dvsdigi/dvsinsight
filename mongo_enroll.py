import os
import requests
import numpy as np
import cv2
from pymongo import MongoClient
from insightface_engine import InsightFaceEngine

# Configuration
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://admin:digividya@147.93.106.220:27017/')
DB_NAME = os.environ.get('MONGO_DB_NAME', 'DigitalVidyaSaarthi')
COLLECTION_NAME = os.environ.get('MONGO_COLLECTION', 'newstudentmodels')

def download_image_from_url(url):
    """
    Downloads an image from a URL and converts it to a numpy array (OpenCV format).
    """
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        
        # Convert bytes to numpy array
        image_array = np.asarray(bytearray(resp.content), dtype=np.uint8)
        # Decode image
        img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        
        if img is None:
            print(f"Error: Could not decode image from {url}")
            return None
            
        return img
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return None

def main():
    # 1. Connect to MongoDB
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        print(f"Connected to MongoDB: {MONGO_URI} (DB: {DB_NAME}, Coll: {COLLECTION_NAME})")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return

    # 2. Initialize InsightFace Engine
    print("Initializing InsightFace Engine...")
    engine = InsightFaceEngine()
    engine.prepare()
    print("Engine ready.")

    # 3. Fetch students
    # You might want to filter for students who don't have embeddings yet
    # query = {"vector_embedding": {"$exists": False}}
    # For now, let's process everyone or just log if they already have it.
    cursor = collection.find({})
    
    count = 0
    for doc in cursor:
        student_id = doc.get('student_id')
        name = doc.get('student_name')
        photo_url = doc.get('photo_url')
        
        if not photo_url:
            print(f"Skipping student {student_id} ({name}): No photo_url")
            continue
            
        print(f"Processing Student: {student_id} ({name})...")
        
        # Download Image
        img = download_image_from_url(photo_url)
        if img is None:
            continue

        # Detect Face & Get Embedding
        faces = engine.get_faces(img)
        if len(faces) == 0:
            print(f"  WARNING: No face detected for {student_id}. Skipping.")
            continue
        
        # Use the first face found
        embedding = faces[0]['embedding']
        
        # Update MongoDB document
        # We store it as a list of floats
        collection.update_one(
            {'_id': doc['_id']},
            {'$set': {'vector_embedding': embedding}}
        )
        print(f"  SUCCESS: Updated embedding for {student_id}.")
        count += 1

    print(f"\nFinished. Processed {count} students.")
    client.close()

if __name__ == "__main__":
    main()
