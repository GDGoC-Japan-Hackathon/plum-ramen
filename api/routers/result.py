from fastapi import APIRouter, HTTPException
from schemas.result import GenerateResultRequest, GenerateResultResponse, InsertResultSummaryRequest, InsertResultSummaryResponse
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
