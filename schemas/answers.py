from pydantic import BaseModel

class Answer(BaseModel):
    question_text: str
    selected_choice: str

class InsertAnswerRequest(BaseModel):
    answers: list[Answer]

