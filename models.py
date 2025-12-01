from pydantic import BaseModel
from typing import List, Optional

class EnrollRequest(BaseModel):
    student_id: str
    student_name: Optional[str] = None

class UploadResponse(BaseModel):
    filename: str
    matched_students: List[str]
