from fastapi import APIRouter, HTTPException
from fastapi import Depends
from schemas.answers import GetDiaryAnswerResponse
from services.answers import get_answers_service
from core.auth import get_current_user

router = APIRouter()

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