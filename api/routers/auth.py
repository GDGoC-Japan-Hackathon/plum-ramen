from fastapi import APIRouter, Depends

from core.auth import get_current_user

router = APIRouter()


@router.get("/api/me")
def get_me(current_user: dict = Depends(get_current_user)):
    return current_user
