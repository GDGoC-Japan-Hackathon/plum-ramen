from schemas.diaries import InsertDiaryRequest, InsertDiaryResponse, GetDiaryResponse
from fastapi import HTTPException
from core.db import engine
import sqlalchemy

# 変更メモ
# 引数をrequest: InsertDiaryRequestからuser_id: int, request: InsertDiaryRequestに変更
# user_idを使用するように修正
def create_diary_service(user_id: int, request: InsertDiaryRequest) -> InsertDiaryResponse:
    with engine.begin() as conn:
        result = conn.execute(
            sqlalchemy.text("""
                INSERT INTO diaries (user_id, body)
                VALUES (:user_id, :body)
                RETURNING id, user_id, body, created_at
            """),
            {"user_id": user_id, "body": request.body}
        ).mappings().fetchone()

    if result is None:
        raise HTTPException(status_code=400, detail="Failed to create diary")

    return InsertDiaryResponse(**result)

def get_diaries_service(user_id: int) -> list[GetDiaryResponse]:
    with engine.connect() as conn:
        rows = conn.execute(
            sqlalchemy.text("""
                SELECT id, user_id, body, created_at
                FROM diaries
                WHERE user_id = :user_id
                ORDER BY created_at DESC
            """),
            {"user_id": user_id}
        ).mappings().all()
    return [GetDiaryResponse(**row) for row in rows] if rows else []
