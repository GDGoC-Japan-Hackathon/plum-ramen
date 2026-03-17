from fastapi import APIRouter, HTTPException
from schemas.questions import GenerateQuestionsRequest, GenerateQuestionsResponse, InsertQuestionsRequest,InsertQuestionsResponse
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

@router.post("/api/postquestions", response_model=list[InsertQuestionsResponse])
def create_question(request: InsertQuestionsRequest):
    try:
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
                    INSERT INTO questions (
                        diaries_id, question_id, question_text, choice_a, choice_b, choice_c
                    ) VALUES (
                        :diaries_id, :question_id, :question_text, :choice_a, :choice_b, :choice_c
                    )
                    RETURNING id, diaries_id, question_id, question_text, choice_a, choice_b, choice_c
                """),
                data_to_insert
            ).mappings().all()

        return [InsertQuestionsResponse(**row) for row in result]

    except Exception as e:
        print(f"Error saving questions: {e}")
        raise HTTPException(status_code=500, detail="質問の保存に失敗しました")