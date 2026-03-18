from schemas.common import GetDiaryWithQuestionResponse
from schemas.questions import Question
from fastapi import HTTPException
from core.db import engine
import sqlalchemy

# 変更メモ
# 引数をdiaries_id: intからuser_id: int, diaries_id: intに変更
# user_idを使用するように修正
def get_diary_with_questions_service(user_id: int, diaries_id: int) -> GetDiaryWithQuestionResponse:
    with engine.connect() as conn:
        rows = conn.execute(
            sqlalchemy.text("""
                SELECT
                    d.id, d.body, d.created_at,
                    q.question_id, q.question_text, q.choice_a, q.choice_b, q.choice_c
                FROM diaries d
                LEFT JOIN questions q ON d.id = q.diaries_id
                WHERE d.id = :diaries_id AND d.user_id = :user_id
                ORDER BY q.question_id ASC
            """),
            {"user_id": user_id, "diaries_id": diaries_id}
        ).mappings().all()

    if not rows:
        raise HTTPException(status_code=404, detail="日記が見つかりません")

    first_row = rows[0]

    questions_list = []
    for row in rows:
        if row["question_id"] is not None:
            questions_list.append(Question(
                question_text=row["question_text"],
                choice_a=row["choice_a"],
                choice_b=row["choice_b"],
                choice_c=row["choice_c"]
            ))

    return GetDiaryWithQuestionResponse(
        id=first_row["id"],
        body=first_row["body"],
        created_at=first_row["created_at"],
        questions=questions_list
    )
