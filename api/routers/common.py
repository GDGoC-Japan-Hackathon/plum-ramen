from fastapi import APIRouter, HTTPException
from schemas.common import GetDiaryWithQuestionResponse
from services.common import get_diary_with_questions_service
from core.auth import get_current_user
from fastapi import Depends

# ここに実装するapi
## 日記と質問を同時取得

router = APIRouter()

# 変更メモ
# エンドポイントを/diaries/questions/{diaries_id}から/api/diaries/{diaries_id}/questionsに変更
# Depends(get_current_user) を使うことで、認証済みユーザーの情報を取得できる
# current_user["user_id"]を使用するように修正
@router.get("/api/diaries/{diaries_id}/questions-with-diary", response_model=GetDiaryWithQuestionResponse)
def get_diary_with_questions(diaries_id: int, current_user: dict = Depends(get_current_user)):
    try:
        return get_diary_with_questions_service(current_user["user_id"], diaries_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
