from fastapi import APIRouter, HTTPException
from fastapi import Depends
from schemas.answers import GetDiaryAnswerResponse
from services.answers import get_answers_service
from core.auth import get_current_user
from schemas.answers import InsertAnswerRequest, InsertAnswerResponse, InsertAnswersRequest, InsertAnswersResponse
from services.answers import insert_answers_service, insert_answers_bulk_service

router = APIRouter()

@router.post("/api/diaries/{diaries_id}/questions/{question_id}/answers", response_model=InsertAnswerResponse)
def insert_answers(diaries_id: int, question_id: int, request: InsertAnswerRequest, current_user: dict = Depends(get_current_user)):
    try:
        return insert_answers_service(current_user["user_id"], diaries_id, question_id, request)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/diaries/{diaries_id}/questions/answers", response_model=InsertAnswersResponse)
def insert_answers_bulk(diaries_id: int, request: InsertAnswersRequest, current_user: dict = Depends(get_current_user)):
    try:
        return insert_answers_bulk_service(current_user["user_id"], diaries_id, request)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 変更メモ
# 処理責務をservices/answers.pyに移動
# エンドポイント名を/diaries/questions/answersから/api/diaries/{diaries_id}/questions/answersに変更
# Depends(get_current_user) を使うことで、認証済みユーザーの情報を取得できる
@router.get("/api/diaries/{diaries_id}/questions/answers", response_model=GetDiaryAnswerResponse)
def get_answers(diaries_id: int, current_user: dict = Depends(get_current_user)):
    try:
        return get_answers_service(current_user["user_id"], diaries_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))