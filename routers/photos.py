from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from db import SessionLocal, init_db, Student
from insightface_engine import InsightFaceEngine
from utils import cosine_similarity, ensure_dirs
from sqlalchemy.orm import Session
import os, json, uuid
from typing import List

router = APIRouter()
init_db()

engine = InsightFaceEngine()
engine.prepare()

EVENTS_DIR = '/Users/peeyushdhawan/Downloads/insightface_segregator/static/events'
STUDENTS_DIR = '/Users/peeyushdhawan/Downloads/insightface_segregator/static/students'
ensure_dirs(EVENTS_DIR)
ensure_dirs(STUDENTS_DIR)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

MATCH_THRESHOLD = float(os.environ.get('MATCH_THRESHOLD', '0.35'))

@router.post('/upload')
async def upload_photos(files: List[UploadFile] = File(...), db: Session = Depends(get_db)):
    responses = []
    for file in files:
        contents = await file.read()
        event_filename = f"{uuid.uuid4().hex}_{file.filename}"
        event_path = os.path.join(EVENTS_DIR, event_filename)
        with open(event_path, 'wb') as f:
            f.write(contents)

        # process image
        img = engine.read_image_bgr(event_path)
        faces = engine.get_faces(img)
        matched_students = set()

        # load all student embeddings into memory (small-medium scale)
        students = db.query(Student).all()
        students_embeddings = []
        for s in students:
            students_embeddings.append((s.student_id, json.loads(s.embedding_json)))

        for face in faces:
            emb = face['embedding']
            best = (None, 0.0)
            for sid, s_emb in students_embeddings:
                sim = cosine_similarity(emb, s_emb)
                if sim > best[1]:
                    best = (sid, sim)
            if best[0] and best[1] >= MATCH_THRESHOLD:
                matched_students.add(best[0])
                # copy or symlink event image into student's folder
                student_dir = os.path.join(STUDENTS_DIR, best[0])
                ensure_dirs(student_dir)
                dest_path = os.path.join(student_dir, event_filename)
                # write a copy
                with open(dest_path, 'wb') as f:
                    f.write(contents)

        responses.append({
            'filename': event_filename,
            'detected_faces': len(faces),
            'matched_students': list(matched_students)
        })

    return {'results': responses}
