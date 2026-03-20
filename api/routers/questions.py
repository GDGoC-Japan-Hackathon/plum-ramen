from fastapi import APIRouter, HTTPException
from schemas.questions import GenerateQuestionsRequest, GenerateQuestionsResponse, InsertQuestionsRequest, InsertQuestionsResponse, GetQuestionResponse
from services.questions import generate_questions_service, insert_questions_service, get_questions_service
from core.auth import get_current_user
from fastapi import Depends
import logging

# ここに実装するapi
## 質問生成
## 質問保存
## 質問取得（1件）
## 質問取得（複数）

router = APIRouter()
logger = logging.getLogger(__name__)

# 変更メモ
# エンドポイントを/api/questionsから/api/generate/questionsに変更
@router.post("/api/generate/questions", response_model=GenerateQuestionsResponse)
def generate_questions(request: GenerateQuestionsRequest):
    try:
        return generate_questions_service(request)
    except Exception as e:
        logger.exception("Failed to generate questions")
        raise HTTPException(status_code=500, detail=str(e))

# 変更メモ
# エンドポイントを/api/postquestionsから/api/diaries/{diaries_id}/questionsに変更
# 引数をrequest: InsertQuestionsRequestからcurrent_user: dict = Depends(get_current_user), diaries_id: int, request: InsertQuestionsRequestに変更
# current_user["user_id"]を使用するように修正
@router.post("/api/diaries/{diaries_id}/questions", response_model=list[InsertQuestionsResponse])
def create_question(diaries_id: int, request: InsertQuestionsRequest, current_user: dict = Depends(get_current_user)):
    try:
        return insert_questions_service(current_user["user_id"], diaries_id, request)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to save questions for diary_id=%s", diaries_id)
        raise HTTPException(status_code=500, detail=str(e))

# 変更メモ
# 引数をdiaries_id: intからcurrent_user: dict = Depends(get_current_user), diaries_id: intに変更
# current_user["user_id"]を使用するように修正
@router.get("/api/diaries/{diaries_id}/questions", response_model=list[GetQuestionResponse])
def get_questions(diaries_id: int, current_user: dict = Depends(get_current_user)):
    try:
        return get_questions_service(current_user["user_id"], diaries_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to get questions for diary_id=%s", diaries_id)
        raise HTTPException(status_code=500, detail=str(e))
