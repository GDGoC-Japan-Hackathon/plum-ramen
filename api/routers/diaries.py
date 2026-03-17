from fastapi import APIRouter, HTTPException
from schemas.diaries import InsertDiaryRequest, InsertDiaryResponse, GetDiaryResponse
from services.diaries import create_diary_service, get_diaries_service

# ここに記入するapi
## 日記保存
## 日記取得（複数）
## 日記取得（1件）

router = APIRouter()

@router.post("/api/diaries", response_model=InsertDiaryResponse)
def create_diary(request: InsertDiaryRequest):
    try:
        return create_diary_service(request)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/users/{user_id}/diaries", response_model=list[GetDiaryResponse])
def get_diaries(user_id: int):
    try:
        return get_diaries_service(user_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
