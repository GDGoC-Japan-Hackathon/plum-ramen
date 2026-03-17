from schemas.result import GenerateResultRequest, GenerateResultResponse, InsertResultSummaryRequest, InsertResultSummaryResponse, GetResultResponse
from prompts.generate_result import PROMPT
from core.gemini import get_gemini_client
from google.genai import types
from core.db import engine
import sqlalchemy

def generate_result_service(request: GenerateResultRequest):
    prompt = PROMPT.format(
        diary=request.diary,
        questions=request.questions,
        answers=request.answers,
    )

    response = get_gemini_client().models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=GenerateResultResponse,
        ),
    )

    return response.parsed

def save_result_service(request: InsertResultSummaryRequest) -> InsertResultSummaryResponse:
    with engine.begin() as conn:
        result = conn.execute(
            sqlalchemy.text("""
                INSERT INTO results (diaries_id, type, ei_score, sn_score, tf_score, jp_score, summary)
                VALUES (:diaries_id, :type, :ei_score, :sn_score, :tf_score, :jp_score, :summary)
                RETURNING id, diaries_id, type, ei_score, sn_score, tf_score, jp_score, summary
            """),
            {"diaries_id": request.diaries_id, "type": request.type, "ei_score": request.ei_score, "sn_score": request.sn_score, "tf_score": request.tf_score, "jp_score": request.jp_score, "summary": request.summary}
        ).mappings().fetchone()

    return InsertResultSummaryResponse(**result) if result else None

def get_result_by_user_and_diary_service(user_id: int, diaries_id: int) -> GetResultResponse:
    with engine.connect() as conn:
        result = conn.execute(
            sqlalchemy.text("""
                SELECT results.id, diaries.user_id, results.diaries_id, type, ei_score, sn_score, tf_score, jp_score, summary
                FROM results
                INNER JOIN diaries ON results.diaries_id = diaries.id
                WHERE diaries.user_id = :user_id AND diaries.id = :diaries_id
            """),
            {"user_id": user_id, "diaries_id": diaries_id}
        ).mappings().fetchone()

    return GetResultResponse(**result) if result else None