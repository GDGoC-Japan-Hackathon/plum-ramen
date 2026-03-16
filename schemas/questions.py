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
