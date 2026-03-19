from fastapi import HTTPException
from core.db import engine
import sqlalchemy
from schemas.answers import QuestionAnswer, GetDiaryAnswerResponse, InsertAnswerRequest, InsertAnswerResponse, InsertAnswersRequest, InsertAnswersResponse

def insert_answers_service(user_id: int, diaries_id: int, question_id: int, request: InsertAnswerRequest):
    # 日記が存在するか確認
    with engine.begin() as conn:
        diary = conn.execute(
            sqlalchemy.text("""
                SELECT id
                FROM diaries
                WHERE id = :diaries_id AND user_id = :user_id
            """),
            {"diaries_id": diaries_id, "user_id": user_id}
        ).fetchone()

        if diary is None:
            raise HTTPException(status_code=404, detail="Diary not found")

    # 回答保存
    with engine.begin() as conn:
        result = conn.execute(
            sqlalchemy.text("""
                INSERT INTO answers (diaries_id, question_id, selected_choice)
                VALUES (:diaries_id, :question_id, :selected_choice)
                RETURNING id, diaries_id, question_id, selected_choice
            """),
            {"diaries_id": diaries_id, "question_id": question_id, "selected_choice": request.answer.selected_choice}
        ).mappings().fetchone()

        if result is None:
            raise HTTPException(status_code=400, detail="Failed to insert answer")

        return InsertAnswerResponse(**result)

def insert_answers_bulk_service(user_id: int, diaries_id: int, answers: InsertAnswersRequest):
    if not answers.answers:
        return InsertAnswersResponse(diaries_id=diaries_id, answers=[])

    inserted_rows = []

    with engine.begin() as conn:
        diary = conn.execute(
            sqlalchemy.text("""
                SELECT id
                FROM diaries
                WHERE id = :diaries_id AND user_id = :user_id
            """),
            {"diaries_id": diaries_id, "user_id": user_id}
        ).fetchone()

        if diary is None:
            raise HTTPException(status_code=404, detail="Diary not found")

        for answer in answers.answers:
            row = conn.execute(
                sqlalchemy.text("""
                    INSERT INTO answers (diaries_id, question_id, selected_choice)
                    VALUES (:diaries_id, :question_id, :selected_choice)
                    RETURNING id, diaries_id, question_id, selected_choice
                """),
                {
                    "diaries_id": diaries_id,
                    "question_id": answer.question_id,
                    "selected_choice": answer.selected_choice,
                }
            ).mappings().fetchone()

            if row is None:
                raise HTTPException(status_code=400, detail="Failed to insert answers")

            inserted_rows.append(InsertAnswerResponse(**row))

    return InsertAnswersResponse(diaries_id=diaries_id, answers=inserted_rows)

def get_answers_service(user_id: int, diaries_id: int):
    with engine.connect() as conn:
        rows = conn.execute(
            sqlalchemy.text("""
                SELECT 
                    d.id as diaries_id,
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
            diaries_id=rows[0]["diaries_id"],
            questions=qa_list
        )
    
