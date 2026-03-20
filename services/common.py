from schemas.common import GetFullDiaryDataResponse, DiarySection,QuestionsWrapper,QuestionDetail,AnswersWrapper,AnswerDetail, GetFullTypesResponse
from fastapi import HTTPException
from core.db import engine
import sqlalchemy

def get_full_diary_data_service(user_id: int, diaries_id:int) -> GetFullDiaryDataResponse:
    with engine.connect() as conn:
        
        sql = sqlalchemy.text("""
            SELECT 
                d.body,
                -- 質問をJSON配列に集約
                (SELECT json_agg(q_list) FROM (
                    SELECT q.question_id, q.question_text, q.choice_a, q.choice_b, q.choice_c
                    FROM questions q
                    WHERE q.diaries_id = d.id
                    ORDER BY q.question_id
                ) q_list) as questions,
                -- 回答をJSON配列に集約
                (SELECT json_agg(a_list) FROM (
                    SELECT a.question_id, a.selected_choice
                    FROM answers a
                    WHERE a.diaries_id = d.id
                    ORDER BY a.question_id
                ) a_list) as answers
            FROM diaries d
            WHERE d.id = :diaries_id AND d.user_id = :user_id
        """)

        result = conn.execute(sql, {"diaries_id": diaries_id, "user_id": user_id}).mappings().fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="Diary not found")
        
    return GetFullDiaryDataResponse(
        diary=DiarySection(body=result["body"]),
        questions=QuestionsWrapper(questions=result["questions"] or []),
        answers=AnswersWrapper(answers=result["answers"] or [])
    )

def get_full_types_service(user_id: int) -> list[GetFullTypesResponse]:
    with engine.connect() as conn:
        sql = sqlalchemy.text("""
            SELECT
                d.body,
                TO_CHAR(d.created_at, 'YYYY-MM-DD') as date,
                TO_CHAR(d.created_at, 'HH24:MI') as time,
                r.type
            FROM diaries d
            INNER JOIN results r ON d.id = r.diaries_id
            WHERE d.user_id = :user_id
            ORDER BY d.created_at DESC
        """)

        rows = conn.execute(sql, {"user_id": user_id}).mappings().all()
    
    return [GetFullTypesResponse(**row) for row in rows]
