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

# 変更メモ
# diaries_idを外す
class InsertQuestionsRequest(BaseModel):
    questions: list[Question]

class InsertQuestionsResponse(BaseModel):
    id: int
    diaries_id: int
    question_id: int
    question_text: str
    choice_a: str
    choice_b: str
    choice_c: str

class GetQuestionResponse(BaseModel):
    id: int
    diaries_id: int
    question_id: int
    question_text: str
    choice_a: str
    choice_b: str
    choice_c: str

class PutQuestionRequest(BaseModel):
    diaries_id: int
    question_id: int
    question_text: str
    choice_a: str
    choice_b: str
    choice_c: str

class PutQuestionResponse(PutQuestionRequest):
    pass