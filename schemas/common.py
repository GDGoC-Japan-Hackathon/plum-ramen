from pydantic import BaseModel
from datetime import datetime

class DiarySection(BaseModel):
    body: str

class QuestionDetail(BaseModel):
    question_id: int
    question_text: str
    choice_a: str
    choice_b: str
    choice_c: str

class AnswerDetail(BaseModel):
    question_id: int
    selected_choice: str | None = None

class QuestionsWrapper(BaseModel):
    questions: list[QuestionDetail]

class AnswersWrapper(BaseModel):
    answers: list[AnswerDetail]

class GetFullDiaryDataResponse(BaseModel):
    diary: DiarySection
    questions: QuestionsWrapper
    answers: AnswersWrapper

class GetFullTypesResponse(BaseModel):
    body: str
    date: str
    time: str
    type: str | None = None