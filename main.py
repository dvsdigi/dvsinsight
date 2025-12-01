from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routers import students, photos
from insightface_engine import InsightFaceEngine

app = FastAPI(title="InsightFace Photo Segregator")

# initialize engine as a singleton
engine = InsightFaceEngine()

app.include_router(students.router, prefix="/students", tags=["students"])
app.include_router(photos.router, prefix="/photos", tags=["photos"])

app.mount("/static", StaticFiles(directory="/Users/peeyushdhawan/Downloads/insightface_segregator/static"), name="static")

@app.on_event("startup")
async def startup_event():
    # Warmup model
    engine.prepare()
    print("InsightFace engine prepared.")
