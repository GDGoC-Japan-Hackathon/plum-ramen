from schemas.questions import GenerateQuestionsRequest, GenerateQuestionsResponse, InsertQuestionsRequest, InsertQuestionsResponse, GetQuestionResponse, PutQuestionRequest, PutQuestionResponse
from prompts.generate_questions import PROMPT
from core.gemini import get_gemini_client
from google.genai import types
from core.db import engine
import sqlalchemy
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

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

# 変更メモ
# 引数をrequest: InsertQuestionsRequestからdiaries_id: int, request: InsertQuestionsRequestに変更
# diaries_idを使用するように修正
# def insert_questions_service(diaries_id: int, request: InsertQuestionsRequest) -> list[InsertQuestionsResponse]:
#     data_to_insert = []
#     for i, q in enumerate(request.questions, start=1):
#         data_to_insert.append({
#             "diaries_id": diaries_id,
#             "question_id": i,  
#             "question_text": q.question_text,
#             "choice_a": q.choice_a,
#             "choice_b": q.choice_b,
#             "choice_c": q.choice_c
#         })

#     with engine.begin() as conn:
#         result = conn.execute(
#             sqlalchemy.text("""
#                 INSERT INTO questions (diaries_id, question_id, question_text, choice_a, choice_b, choice_c)
#                 VALUES (:diaries_id, :question_id, :question_text, :choice_a, :choice_b, :choice_c)
#                 RETURNING id, diaries_id, question_id, question_text, choice_a, choice_b, choice_c
#             """),
#             data_to_insert
#         ).mappings().all()

#     return [InsertQuestionsResponse(**row) for row in result] if result else []

# 変更メモ
# 引数をdiaries_id: intからuser_id: int, diaries_id: intに変更
# user_idを使用するように修正
# user_idを使用して日記が存在するかを確認するように修正
def insert_questions_service(user_id: int, diaries_id: int, request: InsertQuestionsRequest) -> list[InsertQuestionsResponse]:
    data_to_insert = []
    for i, q in enumerate(request.questions, start=1):
        data_to_insert.append({
            "diaries_id": diaries_id,
            "question_id": i,
            "question_text": q.question_text,
            "choice_a": q.choice_a,
            "choice_b": q.choice_b,
            "choice_c": q.choice_c,
        })

    try:
        with engine.begin() as conn:
            diary = conn.execute(
                sqlalchemy.text("""
                    SELECT id
                    FROM diaries
                    WHERE id = :diaries_id AND user_id = :user_id
                """),
                {"diaries_id": diaries_id, "user_id": user_id}
            ).fetchone()

            if diary is None:
                raise HTTPException(status_code=404, detail="Diary not found")

            result = conn.execute(
                sqlalchemy.text("""
                    INSERT INTO questions (
                        diaries_id, question_id, question_text, choice_a, choice_b, choice_c
                    )
                    VALUES (
                        :diaries_id, :question_id, :question_text, :choice_a, :choice_b, :choice_c
                    )
                    RETURNING id, diaries_id, question_id, question_text, choice_a, choice_b, choice_c
                """),
                data_to_insert
            ).mappings().all()
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Questions for this diary already exist")

    return [InsertQuestionsResponse(**row) for row in result] if result else []

# 変更メモ
# 引数をdiaries_id: intからuser_id: int, diaries_id: intに変更
# user_idを使用するように修正
def get_questions_service(user_id: int, diaries_id: int) -> list[GetQuestionResponse]:
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
                WHERE d.id = :diaries_id AND d.user_id = :user_id
                ORDER BY q.question_id ASC
            """),
            {"user_id": user_id, "diaries_id": diaries_id}
        ).mappings().all()

    return [GetQuestionResponse(**row) for row in rows] if rows else []

def update_question_service(user_id: int, request: PutQuestionRequest) -> PutQuestionResponse:
    with engine.begin() as conn:
        check = conn.execute(
            sqlalchemy.text("""
                SELECT q.question_id
                FROM questions q
                JOIN diaries d ON q.diaries_id = d.id
                WHERE d.user_id = :user_id
                    AND d.id = :diaries_id
                    AND q.question_id = :question_id
            """),
            {
                "user_id": user_id, 
                "diaries_id": request.diaries_id,
                "question_id": request.question_id
            }
        ).fetchone()

        if check is None:
            raise HTTPException(status_code=404, detail="質問が見つからないか、権限がありません")

        result = conn.execute(
            sqlalchemy.text("""
                UPDATE questions
                SET
                    question_text = :question_text,
                    choice_a = :choice_a,
                    choice_b = :choice_b,
                    choice_c = :choice_c
                WHERE diaries_id = :diaries_id AND question_id = :question_id
                RETURNING diaries_id, question_id, question_text, choice_a, choice_b, choice_c
            """),
            {
                "diaries_id": request.diaries_id,
                "question_id": request.question_id,
                "question_text": request.question_text,
                "choice_a": request.choice_a,
                "choice_b": request.choice_b,
                "choice_c": request.choice_c
            }
        ).mappings().fetchone()

    return PutQuestionResponse(**result)     