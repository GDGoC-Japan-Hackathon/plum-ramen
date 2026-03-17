from fastapi import APIRouter, HTTPException
from schemas.result import GenerateResultRequest, GenerateResultResponse
from functools import lru_cache
from google import genai
from google.genai import types
from prompts.generate_result import PROMPT
import os
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