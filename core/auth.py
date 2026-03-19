# 認証トークンの検証とユーザーIDの認証認証
def verify_token_and_get_user_id(token: str) -> int:
    pass
# いずれはapi/dependencies/auth.pyに移動する
def get_current_user() -> dict:
    verify_token_and_get_user_id("Bearer <token>")
    return {"user_id": 1}
