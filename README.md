# InsightFace Photo Segregator (FastAPI)

## What this project does
This is a **production-ready reference codebase** that uses **InsightFace** to automatically segregate school photos by student faces.  
It provides a FastAPI backend that:

- Lets you **enroll students** with reference photos (creates & stores face embeddings).
- Lets you **upload event/group photos** — the system detects faces, matches them to enrolled students, and stores copies of images under each matched student's folder.
- Provides simple endpoints to fetch student albums.

> Note: This project contains the full codebase. You must install dependencies and InsightFace models. See Installation below.

---

## File structure
```
insightface_segregator/
├── app/
│   ├── main.py
│   ├── db.py
│   ├── models.py
│   ├── insightface_engine.py
│   ├── routers/
│   │   ├── students.py
│   │   └── photos.py
│   └── utils.py
├── static/
│   ├── students/
│   └── events/
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## Quickstart (local, CPU)

1. Create a Python virtualenv and activate it:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install requirements:
```bash
pip install -r requirements.txt
```

3. **Important** — install insightface model dependencies. On many platforms:
```bash
pip install insightface
```
*If installation issues occur, follow the official InsightFace docs: https://insightface.ai/*

4. Run the app:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

5. Open docs: `http://localhost:8000/docs`

---

## Design & How it works (high-level)

1. **Enroll**
   - Endpoint: `POST /students/enroll`
   - Upload a clear reference photo + `student_id`.
   - Backend extracts face embedding and stores it in the SQLite DB (table `students`).

2. **Upload Event Photo**
   - Endpoint: `POST /photos/upload`
   - Upload one or more event/group images.
   - For each image:
     - Detect faces with InsightFace.
     - Compute embedding per face.
     - Compare embedding with stored student embeddings using cosine similarity.
     - If match found above threshold, save a copy under `static/students/{student_id}/`.
     - Also keep event original under `static/events/`.

3. **Fetch Student Photos**
   - Endpoint: `GET /students/{student_id}/photos` returns filenames.

---

## Matching & Thresholds

We use **cosine similarity** on 512-D embeddings.
- Default threshold: **0.35** (tune between 0.28 - 0.40 for your dataset)
- Lower threshold → more permissive (more false positives)
- Higher threshold → more strict (more false negatives)

---

## Deployment tips

- For large collections or faster processing, use GPU (CUDA). InsightFace will use GPU if available.
- Use a job queue (Redis + RQ/Celery) for bulk uploads to avoid blocking HTTP requests.
- Backup the `students.db` and `static/` data regularly.

---

## Notes & caveats

- Face recognition is probabilistic. Provide 2–3 reference images per student for better accuracy.
- For masked faces or occluded faces, accuracy drops.
- This code stores embeddings and image file paths locally. Adjust storage and DB as required for production.

---

## Want me to deploy this as a Docker image and create a minimal frontend example?
Reply: **"Dockerize and frontend"** and I'll add it.
