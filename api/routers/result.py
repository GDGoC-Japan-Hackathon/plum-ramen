from fastapi import APIRouter, HTTPException
from schemas.result import GenerateResultRequest, GenerateResultResponse, InsertResultSummaryRequest, InsertResultSummaryResponse, GetResultResponse
from services.result import generate_result_service, save_result_service, get_result_by_user_and_diary_service
import sqlalchemy
from core.db import engine

# ここに実装するapi
## 結果生成
## 結果保存
## 結果取得（1件）
## 結果取得（複数）

router = APIRouter()

@router.post("/api/result", response_model=GenerateResultResponse)
def generate_result(request: GenerateResultRequest):
    try:
        return generate_result_service(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/result/save", response_model=InsertResultSummaryResponse)
def save_result(request: InsertResultSummaryRequest):
    try:
        result = save_result_service(request)
        if result is None:
            raise HTTPException(status_code=400, detail="Failed to save result")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/user/{user_id}/{diaries_id}/result", response_model=GetResultResponse)
def get_result_by_user_and_diaries(user_id: int, diaries_id: int):
    try:
        result = get_result_by_user_and_diary_service(user_id, diaries_id)
        if result is None:
            raise HTTPException(status_code=404, detail="Result not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
