from fastapi import APIRouter, HTTPException
from schemas.result import GenerateResultRequest, GenerateResultResponse, InsertResultSummaryRequest, InsertResultSummaryResponse, GetResultResponse
from functools import lru_cache
from google import genai
from google.genai import types
from prompts.generate_result import PROMPT
import os
import sqlalchemy
from core.db import engine

router = APIRouter()

@lru_cache
def get_gemini_client():
    return genai.Client(
        vertexai=True,
        project=os.environ["GOOGLE_CLOUD_PROJECT"],
        location=os.environ["GOOGLE_CLOUD_LOCATION"],
        http_options=types.HttpOptions(api_version="v1"),
    )

@router.post("/api/result", response_model=GenerateResultResponse)
def generate_result(request: GenerateResultRequest):
    prompt = PROMPT.format(diary=request.diary, questions=request.questions, answers=request.answers)

    response = get_gemini_client().models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=GenerateResultResponse,
        ),
    )

    return response.parsed

@router.post("/api/result/save")
def save_result(request: InsertResultSummaryRequest):
    try:
        with engine.begin() as conn:
            result = conn.execute(
                sqlalchemy.text("""
                    INSERT INTO results (diaries_id, type, ei_score, sn_score, tf_score, jp_score, summary)
                    VALUES (:diaries_id, :type, :ei_score, :sn_score, :tf_score, :jp_score, :summary)
                    RETURNING id, diaries_id, type, ei_score, sn_score, tf_score, jp_score, summary
                """),
                {"diaries_id": request.diaries_id, "type": request.type, "ei_score": request.ei_score, "sn_score": request.sn_score, "tf_score": request.tf_score, "jp_score": request.jp_score, "summary": request.summary}
            ).mappings().fetchone()
    
        if result is None:
            raise HTTPException(status_code=400, detail="Failed to insert result summary")

        return InsertResultSummaryResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/user/{user_id}/{diaries_id}/result", response_model=GetResultResponse)
def get_result_by_user_and_diaries(user_id: int, diaries_id: int):
    try:
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

        if result is None:
            raise HTTPException(status_code=404, detail="Result not found")

        return GetResultResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))