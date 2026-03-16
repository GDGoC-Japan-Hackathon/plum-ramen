from fastapi import APIRouter, HTTPException
from schemas.questions import GenerateQuestionsRequest, GenerateQuestionsResponse
from core.db import engine
import sqlalchemy
import os
from functools import lru_cache
from google import genai
from google.genai import types
from prompts.generate_questions import PROMPT

router = APIRouter()

@lru_cache
def get_gemini_client():
    return genai.Client(
        vertexai=True,
        project=os.environ["GOOGLE_CLOUD_PROJECT"],
        location=os.environ["GOOGLE_CLOUD_LOCATION"],
        http_options=types.HttpOptions(api_version="v1"),
    )


@router.post("/api/questions", response_model=GenerateQuestionsResponse)
def generate_questions(request: GenerateQuestionsRequest):
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
