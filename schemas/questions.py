from pydantic import BaseModel

class Question(BaseModel):
    question_text: str
    choice_a: str
    choice_b: str
    choice_c: str

class GenerateQuestionsRequest(BaseModel):
    diary: str

class GenerateQuestionsResponse(BaseModel):
    questions: list[Question]

class InsertQuestionsRequest(BaseModel):
    diaries_id: int
    questions: list[Question]

class InsertQuestionsResponse(BaseModel):
    id: int
    diaries_id: int
    question_id: int
    question_text: str
    choice_a: str
    choice_b: str
    choice_c: str
