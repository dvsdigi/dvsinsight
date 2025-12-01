from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from db import SessionLocal, init_db, Student
from insightface_engine import InsightFaceEngine
from utils import ensure_dirs
import json, os
from sqlalchemy.orm import Session

router = APIRouter()
init_db()

engine = InsightFaceEngine()
engine.prepare()

STATIC_STUDENTS = '/Users/peeyushdhawan/Downloads/insightface_segregator/static/students'
ensure_dirs(STATIC_STUDENTS)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post('/enroll')
async def enroll_student(student_id: str = Form(...), student_name: str = Form(None), file: UploadFile = File(...), db: Session = Depends(get_db)):
    # save ref image
    ensure_dirs(STATIC_STUDENTS)
    filename = f"{student_id}_{file.filename}"
    save_path = os.path.join(STATIC_STUDENTS, filename)
    with open(save_path, 'wb') as f:
        f.write(await file.read())

    # get embedding
    img = engine.read_image_bgr(save_path)
    faces = engine.get_faces(img)
    if len(faces) == 0:
        raise HTTPException(status_code=400, detail="No face detected in reference image.")

    # take the first face's embedding
    embedding = faces[0]['embedding']

    # save to DB
    existing = db.query(Student).filter(Student.student_id == student_id).first()
    if existing:
        existing.embedding_json = json.dumps(embedding)
        existing.reference_image = save_path
        existing.student_name = student_name
    else:
        student = Student(student_id=student_id, student_name=student_name, embedding_json=json.dumps(embedding), reference_image=save_path)
        db.add(student)
    db.commit()

    return {"student_id": student_id, "student_name": student_name, "reference_image": save_path}
