from pydantic import BaseModel
from typing import Optional

class Answer(BaseModel):
    selected_choice: str

class InsertAnswerRequest(BaseModel):
    answer: Answer

class InsertAnswerResponse(BaseModel):
    id: int
    diaries_id: int
    question_id: int
    selected_choice: str

class Answers(Answer):
    question_id: int

class InsertAnswersRequest(BaseModel):
    answers: list[Answers]

class InsertAnswersResponse(BaseModel):
    diaries_id: int
    answers: list[InsertAnswerResponse]

class QuestionAnswer(BaseModel):
    question_id: int
    question_text: str
    choice_a: str
    choice_b: str
    choice_c: str
    selected_choice: Optional[str] = None

class GetDiaryAnswerResponse(BaseModel):
    user_id: int
    diaries_id: int
    questions: list[QuestionAnswer]

class PutAnswerRequest(BaseModel):
    diaries_id: int
    question_id: int
    selected_choice: str

class PutAnswerResponse(PutAnswerRequest):
    pass