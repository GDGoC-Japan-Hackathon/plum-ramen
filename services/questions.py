from schemas.questions import GenerateQuestionsRequest, GenerateQuestionsResponse, InsertQuestionsRequest, InsertQuestionsResponse, GetQuestionResponse
from prompts.generate_questions import PROMPT
from core.gemini import get_gemini_client
from google.genai import types
from core.db import engine
import sqlalchemy

def generate_questions_service(request: GenerateQuestionsRequest) -> GenerateQuestionsResponse:
    prompt = PROMPT.format(diary=request.diary)
    response = get_gemini_client().models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=GenerateQuestionsResponse,
        ),
    )
    return response.parsed

def insert_questions_service(request: InsertQuestionsRequest) -> list[InsertQuestionsResponse]:
    data_to_insert = []
    for i, q in enumerate(request.questions, start=1):
        data_to_insert.append({
            "diaries_id": request.diaries_id,
            "question_id": i,  
            "question_text": q.question_text,
            "choice_a": q.choice_a,
            "choice_b": q.choice_b,
            "choice_c": q.choice_c
        })

    with engine.begin() as conn:
        result = conn.execute(
            sqlalchemy.text("""
                INSERT INTO questions (diaries_id, question_id, question_text, choice_a, choice_b, choice_c)
                VALUES (:diaries_id, :question_id, :question_text, :choice_a, :choice_b, :choice_c)
                RETURNING id, diaries_id, question_id, question_text, choice_a, choice_b, choice_c
            """),
            data_to_insert
        ).mappings().all()

    return [InsertQuestionsResponse(**row) for row in result] if result else []

def get_questions_service(diaries_id: int) -> list[GetQuestionResponse]:
    with engine.connect() as conn:
        rows = conn.execute(
            sqlalchemy.text("""
                SELECT
                    q.id,
                    q.diaries_id,
                    q.question_id,
                    q.question_text,
                    q.choice_a,
                    q.choice_b,
                    q.choice_c
                FROM questions q
                INNER JOIN diaries d ON q.diaries_id = d.id
                WHERE d.id = :diaries_id
                ORDER BY q.question_id ASC
            """),
            {"diaries_id": diaries_id}
        ).mappings().all()

    return [GetQuestionResponse(**row) for row in rows] if rows else []
