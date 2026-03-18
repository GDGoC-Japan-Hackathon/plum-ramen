from fastapi import APIRouter, HTTPException
from schemas.diaries import InsertDiaryRequest, InsertDiaryResponse, GetDiaryResponse, PutDiaryRequest, PutDiaryResponse
from services.diaries import create_diary_service, get_diaries_service, update_diary_service
from core.auth import get_current_user
from fastapi import Depends

# ここに記入するapi
## 日記保存
## 日記取得（複数）
## 日記取得（1件）

router = APIRouter()

# 変更メモ
# 引数をrequest: InsertDiaryRequestからcurrent_user: dict = Depends(get_current_user), request: InsertDiaryRequestに変更
# Depends(get_current_user) を使うことで、認証済みユーザーの情報を取得できる
# current_user["user_id"]を使用するように修正
@router.post("/api/diaries", response_model=InsertDiaryResponse)
def create_diary(request: InsertDiaryRequest, current_user: dict = Depends(get_current_user)):
    try:
        return create_diary_service(current_user["user_id"], request)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 変更メモ
# 処理責務をservices/diaries.pyに移動
# エンドポイント名を/users/{user_id}/diariesから/api/diariesに変更
# Depends(get_current_user) を使うことで、認証済みユーザーの情報を取得できる
@router.get("/api/diaries", response_model=list[GetDiaryResponse])
def get_diaries(current_user: dict = Depends(get_current_user)):
    try:
        return get_diaries_service(current_user["user_id"])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# パスから {id} を削除しました
@router.put("/api/diaries", response_model=PutDiaryResponse)
def update_diary(request: PutDiaryRequest, current_user: dict = Depends(get_current_user)):
    try:
        # requestの中に id が入っているので、そのままサービスに渡します
        return update_diary_service(current_user["user_id"], request)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="日記の更新に失敗しました")

