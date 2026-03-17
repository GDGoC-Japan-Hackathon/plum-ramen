from fastapi import APIRouter, HTTPException, Depends
from schemas.common import GetDiaryWithQuestionResponse, GetDiaryRequest
from schemas.questions import Question
from core.db import engine
import sqlalchemy

router = APIRouter()

@router.get("/diaries/questions/{diary_id}", response_model=GetDiaryWithQuestionResponse)
def get_diary_with_questions(request: GetDiaryRequest = Depends()):
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                sqlalchemy.text("""
                    SELECT 
                        d.id, d.body, d.created_at,
                        q.question_id, q.question_text, q.choice_a, q.choice_b, q.choice_c
                    FROM diaries d
                    LEFT JOIN questions q ON d.id = q.diaries_id
                    WHERE d.id = :diary_id
                    ORDER BY q.question_id ASC
                """),
                {"diary_id": request.diaries_id}
            ).mappings().all()
        
        if not rows:
            raise HTTPException(status_code=404, detail="日記が見つかりません")
        
        first_row = rows[0]

        questions_list = []
        for row in rows:
            if row["question_id"] is not None:
                questions_list.append(Question(
                    question_id=row["question_id"],
                    question_text=row["question_text"],
                    choice_a=row["choice_a"],
                    choice_b=row["choice_b"],
                    choice_c=row["choice_c"]
                ))

        return GetDiaryWithQuestionResponse(
            id=first_row["id"],
            body=first_row["body"],
            created_at=str(first_row["created_at"]),
            questions=questions_list
        )

    except Exception as e:
        # 修正5: エラーの中身を詳しくログに出す（デバッグ用）
        import traceback
        traceback.print_exc() 
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")