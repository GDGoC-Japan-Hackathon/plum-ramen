from fastapi import APIRouter, HTTPException
from schemas.diaries import InsertDiaryRequest, InsertDiaryResponse, GetDiaryResponse, GetQuestionResponse
from core.db import engine
import sqlalchemy

router = APIRouter()

@router.post("/api/diaries", response_model=InsertDiaryResponse)
def create_diary(request: InsertDiaryRequest):
    try:
        with engine.begin() as conn:
            result = conn.execute(
                sqlalchemy.text("""
                    INSERT INTO diaries (user_id, body)
                    VALUES (:user_id, :body)
                    RETURNING id, user_id, body, created_at
                """),
                {"user_id": 1, "body": request.body}
            ).mappings().fetchone()
        
        if result is None:
            raise HTTPException(status_code=400, detail="Failed to create diary")

        return InsertDiaryResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/users/{user_id}/diaries", response_model=list[GetDiaryResponse])
def get_diaries(user_id: int):
    try:
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

        return [GetDiaryResponse(**row) for row in rows]
    
    except Exception as e:
        print(f"Error fetching diaries: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch diaries")  

@router.get("/api/diaries/{diaries_id}/questions", response_model=list[GetQuestionResponse])
def get_questions(diaries_id: int):
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                sqlalchemy.text("""
                    SELECT
                        q.id, 
                        q.diaries_id, 
                        q.question_id, 
                        q.question_text, 
                        q.choice_a, 
                        q.choice_b, 
                        q.choice_c
                    FROM questions q
                    INNER JOIN diaries d ON q.diaries_id = d.id
                    WHERE d.id = :diaries_id
                    ORDER BY q.question_id ASC
                """),
                {"diaries_id": diaries_id}
            ).mappings().all()

        return [GetQuestionResponse(**row) for row in rows]

    except Exception as e:
        print(f"Error fetching questions: {e}")
        raise HTTPException(status_code=500, detail=f"質問の取得に失敗しました: {e}")
