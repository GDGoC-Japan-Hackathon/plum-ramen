from fastapi import APIRouter, HTTPException
from schemas.common import GetDiaryWithQuestionResponse
from services.common import get_diary_with_questions_service

# ここに実装するapi
## 日記と質問を同時取得

router = APIRouter()

@router.get("/diaries/questions/{diaries_id}", response_model=GetDiaryWithQuestionResponse)
def get_diary_with_questions(diaries_id: int):
    try:
        return get_diary_with_questions_service(diaries_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
