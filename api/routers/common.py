from fastapi import APIRouter, HTTPException
from schemas.common import GetFullDiaryDataResponse
from services.common import get_full_diary_data_service
from core.auth import get_current_user
from fastapi import Depends

router = APIRouter()

@router.get("/api/diaries/{diary_id}/diary-questions-answers", response_model=GetFullDiaryDataResponse)
def get_full_diary_data(diary_id: int, current_user: dict = Depends(get_current_user)):
    try:
        return get_full_diary_data_service(current_user["user_id"], diary_id)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="データの一括取得に失敗しました")