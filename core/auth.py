from firebase_admin import auth
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from core.firebase import *
from core.db import engine
import sqlalchemy

# ヘッダーからトークン取得
security = HTTPBearer()

def verify_token_and_get_firebase_uid(token: str):
    # ユーザー情報取得
    user_data = auth.verify_id_token(token) # {"uid", "email", "name", "picture"}
    return user_data["uid"]

def get_user_id_from_firebase_uid(firebase_uid: str) -> int:
    with engine.connect() as conn:
        user = conn.execute(
            sqlalchemy.text("""
                select user_id
                from firebase_users
                where firebase_uid = :firebase_uid
            """),
            {"firebase_uid": firebase_uid}
        ).mappings().fetchone()

    return user["user_id"] if user else None

def insert_firebase_user(firebase_uid: str) -> int:
    with engine.begin() as conn:
        result = conn.execute(
            sqlalchemy.text("""
                insert into firebase_users (firebase_uid)
                values (:firebase_uid)
                returning user_id
            """),
            {"firebase_uid": firebase_uid}
        ).mappings().fetchone()

    return result["user_id"]

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    firebase_uid = verify_token_and_get_firebase_uid(credentials.credentials)

    user_id = get_user_id_from_firebase_uid(firebase_uid)
    if not user_id:
        user_id = insert_firebase_user(firebase_uid)

    return {"user_id": user_id}
