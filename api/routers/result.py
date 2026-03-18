from fastapi import APIRouter, HTTPException
from schemas.result import GenerateResultRequest, GenerateResultResponse, InsertResultSummaryRequest, InsertResultSummaryResponse, GetResultResponse
from services.result import generate_result_service, save_result_service, get_result_by_user_and_diary_service
import sqlalchemy
from core.db import engine
from core.auth import get_current_user
from fastapi import Depends

# ここに実装するapi
## 結果生成
## 結果保存
## 結果取得（1件）
## 結果取得（複数）

router = APIRouter()

# 変更メモ
# エンドポイントを/api/resultから/api/generate/resultに変更
@router.post("/api/generate/result", response_model=GenerateResultResponse)
def generate_result(request: GenerateResultRequest):
    try:
        return generate_result_service(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 変更メモ
# エンドポイントを/api/result/saveから/api/diaries/{diaries_id}/resultに変更
# 引数をrequest: InsertResultSummaryRequestからdiaries_id: int, request: InsertResultSummaryRequestに変更
# service側の引数をrequest: InsertResultSummaryRequestからdiaries_id: int, request: InsertResultSummaryRequestに変更
@router.post("/api/diaries/{diaries_id}/result", response_model=InsertResultSummaryResponse)
def save_result(diaries_id: int, request: InsertResultSummaryRequest):
    try:
        return save_result_service(diaries_id, request)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 変更メモ
# dependsを使うことで、認証済みユーザーの情報を取得できる
# エンドポイントを/api/user/{user_id}/{diaries_id}/resultから/api/diaries/{diaries_id}/resultに変更
@router.get("/api/diaries/{diaries_id}/result", response_model=GetResultResponse)
def get_result_by_user_and_diaries(diaries_id: int, current_user: dict = Depends(get_current_user)):
    try:
        result = get_result_by_user_and_diary_service(current_user["user_id"], diaries_id)
        if result is None:
            raise HTTPException(status_code=404, detail="Result not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
