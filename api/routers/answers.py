from fastapi import APIRouter, HTTPException
from schemas.answers import QuestionAnswer,GetDiaryAnswerRequest, GetDiaryAnswerResponse
from core.db import engine
import sqlalchemy

router = APIRouter()

@router.get("/diaries/questions/answers", response_model=GetDiaryAnswerResponse)
def get_answers(user_id: int, diaries_id: int):
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                sqlalchemy.text("""
                    SELECT 
                        d.user_id, d.id as diaries_id,
                        q.question_id, q.question_text, q.choice_a, q.choice_b, q.choice_c,
                        a.selected_choice
                    FROM diaries d
                    JOIN questions q ON d.id = q.diaries_id
                    LEFT JOIN answers a ON q.diaries_id = a.diaries_id AND q.question_id = a.question_id
                    WHERE d.id = :diaries_id AND d.user_id = :user_id
                    ORDER BY q.question_id ASC
                """),
                {"user_id": user_id, "diaries_id": diaries_id}
            ).mappings().all()
        
        if not rows:
            raise HTTPException(status_code=404, detail="該当日記または質問が見つかりません")
        
        qa_list = [
            QuestionAnswer(
                question_id=row["question_id"],
                question_text=row["question_text"],
                choice_a=row["choice_a"],
                choice_b=row["choice_b"],
                choice_c=row["choice_c"],
                selected_choice=row["selected_choice"]
            ) for row in rows
        ]

        return GetDiaryAnswerResponse(
            user_id=rows[0]["user_id"],
            diaries_id=rows[0]["diaries_id"],
            questions=qa_list
        )
    
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="データ取得に失敗しました")