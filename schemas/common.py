from pydantic import BaseModel
from schemas.questions import Question
from datetime import datetime
class GetDiaryWithQuestionResponse(BaseModel):
    id: int
    body: str
    created_at: datetime
    questions: list[Question]
