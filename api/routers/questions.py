from fastapi import APIRouter, HTTPException
from schemas.questions import GenerateQuestionsRequest, GenerateQuestionsResponse, InsertQuestionsRequest, InsertQuestionsResponse, GetQuestionResponse
from services.questions import generate_questions_service, insert_questions_service, get_questions_service

# ここに実装するapi
## 質問生成
## 質問保存
## 質問取得（1件）
## 質問取得（複数）

router = APIRouter()

@router.post("/api/questions", response_model=GenerateQuestionsResponse)
def generate_questions(request: GenerateQuestionsRequest):
    try:
        return generate_questions_service(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/postquestions", response_model=list[InsertQuestionsResponse])
def create_question(request: InsertQuestionsRequest):
    try:
        return insert_questions_service(request)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/diaries/{diaries_id}/questions", response_model=list[GetQuestionResponse])
def get_questions(diaries_id: int):
    try:
        return get_questions_service(diaries_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
