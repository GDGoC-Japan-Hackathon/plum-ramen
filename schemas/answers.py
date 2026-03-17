from pydantic import BaseModel
from typing import Optional

class Answer(BaseModel):
    question_text: str
    selected_choice: str

class InsertAnswerRequest(BaseModel):
    answers: list[Answer]

class QuestionAnswer(BaseModel):
    question_id: int
    question_text: str
    choice_a: str
    choice_b: str
    choice_c: str
    selected_choice: Optional[str] = None

class GetDiaryAnswerRequest(BaseModel):
    user_id: int
    diaries_id: int

class GetDiaryAnswerResponse(BaseModel):
    user_id: int
    diaries_id: int
    questions: list[QuestionAnswer]