from schemas.result import GenerateResultRequest, GenerateResultResponse, InsertResultSummaryRequest, InsertResultSummaryResponse, GetResultResponse
from prompts.generate_result import PROMPT
from core.gemini import get_gemini_client
from google.genai import types
from core.db import engine
from fastapi import HTTPException
import sqlalchemy
import json

def generate_result_service(request: GenerateResultRequest):
    diary_text = request.diary.diary

    questions_text = json.dumps(
        [
            {
                "question_text": q.question_text,
                "choice_a": q.choice_a,
                "choice_b": q.choice_b,
                "choice_c": q.choice_c,
            } 
            for q in request.questions.questions
        ],
        ensure_ascii=False,
        indent=2,
    )

    question_map = {
        index: question
        for index, question in enumerate(request.questions.questions, start=1)
    }

    answer_items = []
    for answer in request.answers.answers:
        question = question_map.get(answer.question_id)
        if question is None:
            raise HTTPException(status_code=400, detail="Invalid question_id in answers")

        answer_items.append(
            {
                "question_id": answer.question_id,
                "question_text": question.question_text,
                "selected_choice": answer.selected_choice,
            }
        )

    answers_text = json.dumps(
        answer_items,
        ensure_ascii=False,
        indent=2,
    )

    prompt = PROMPT.format(
        diary=diary_text,
        questions=questions_text,
        answers=answers_text,
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

def save_result_service(user_id: int, diaries_id: int, request: InsertResultSummaryRequest) -> InsertResultSummaryResponse:
    with engine.begin() as conn:
        result = conn.execute(
            sqlalchemy.text("""
                INSERT INTO results (diaries_id, type, ei_score, sn_score, tf_score, jp_score, summary)
                SELECT d.id, :type, :ei_score, :sn_score, :tf_score, :jp_score, :summary
                FROM diaries d
                WHERE d.id = :diaries_id AND d.user_id = :user_id
                RETURNING id, diaries_id, type, ei_score, sn_score, tf_score, jp_score, summary
            """),
            {
                "user_id": user_id,
                "diaries_id": diaries_id,
                "type": request.type,
                "ei_score": request.ei_score,
                "sn_score": request.sn_score,
                "tf_score": request.tf_score,
                "jp_score": request.jp_score,
                "summary": request.summary,
            }
        ).mappings().fetchone()

    if result is None:
        raise HTTPException(status_code=404, detail="Diary not found")

    return InsertResultSummaryResponse(**result)

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
