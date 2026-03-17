from pydantic import BaseModel
from schemas.questions import Question

class GetDiaryRequest(BaseModel):
    diaries_id: int

class GetDiaryWithQuestionResponse(BaseModel):
    id: int
    body: str
    created_at: str
    questions: list[Question]