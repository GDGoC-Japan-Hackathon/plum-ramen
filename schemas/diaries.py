from pydantic import BaseModel
from datetime import datetime

class InsertDiaryRequest(BaseModel):
    body: str

class InsertDiaryResponse(BaseModel):
    id: int
    user_id: int
    body: str
    created_at: datetime

class GetDiaryResponse(BaseModel):
    id: int
    user_id: int
    body: str
    created_at: datetime

class PutDiaryRequest(BaseModel):
    id: int
    body: str
    
class PutDiaryResponse(BaseModel):
    id: int
    body: str