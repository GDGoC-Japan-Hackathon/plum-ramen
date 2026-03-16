import os
import sqlalchemy
from fastapi import FastAPI, HTTPException, Depends
from google.cloud.sql.connector import Connector, IPTypes
from pydantic import BaseModel, Field
from datetime import datetime

class InsertDiaryRequest(BaseModel):
    body: str

class InsertDiaryResponse(BaseModel):
    id: int
    user_id: int
    body: str
    created_at: datetime

class GetDiaryResponse(BaseModel):
    id: int
    user_id: int
    body: str
    created_at: datetime

class GetQuestionResponse(BaseModel):
    id: int
    diaries_id: int
    question_id: int
    question_text: str
    choice_a: str
    choice_b: str
    choice_c: str

class InsertAnswerRequest(BaseModel):
    diaries_id: int
    question_id: int
    selected_choice: str = Field(..., min_length=1, max_length=1, pattern="^[A-C]$")

class BulkInsertAnswerRequest(BaseModel):
    answers: list[InsertAnswerRequest] = Field(..., min_length=3, max_length=3)

class InsertAnswerResponse(BaseModel):
    id: int
    diaries_id: int
    question_id: int
    selected_choice: str

app = FastAPI()

def create_engine():
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return sqlalchemy.create_engine(database_url)

    connector = Connector(refresh_strategy="LAZY")

    def getconn():
        return connector.connect(
            os.environ["INSTANCE_CONNECTION_NAME"],
            "pg8000",
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASS"],
            db=os.environ["DB_NAME"],
            ip_type=IPTypes.PUBLIC,
        )

    return sqlalchemy.create_engine("postgresql+pg8000://", creator=getconn)

engine = create_engine()

@app.get("/")
def root():
    return {"message": "Brand New Hello World"}

@app.get("/users")
def get_users():
    with engine.connect() as conn:
        rows = conn.execute(
            sqlalchemy.text("SELECT id, name FROM users ORDER BY id")
        ).mappings().all()

    return {"items": [dict(row) for row in rows]}


@app.post("/diaries", response_model=InsertDiaryResponse)
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

@app.get("/diaries", response_model=list[GetDiaryResponse])
def get_diaries():
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                sqlalchemy.text("""
                    SELECT id, user_id, body, created_at 
                    FROM diaries 
                    WHERE user_id = :user_id 
                    ORDER BY created_at DESC
                """),
                {"user_id": 1}
            ).mappings().all()

        return [GetDiaryResponse(**row) for row in rows]
    
    except Exception as e:
        print(f"Error fetching diaries: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch diaries")  

@app.get("/diaries/questions/{diaries_id}", response_model=list[GetQuestionResponse])
def get_questions(diaries_id):
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
        raise HTTPException(status_code=500, detail="質問の取得に失敗しました")

@app.post("/answers", response_model=list[InsertAnswerResponse])
def create_answers(request_data: BulkInsertAnswerRequest):
    try:
        data_to_insert = [item.model_dump() for item in request_data.answers]

        with engine.begin() as conn:
            result = conn.execute(
                sqlalchemy.text("""
                INSERT INTO answers (diaries_id, question_id, selected_choice)
                VALUES (:diaries_id, :question_id, :selected_choice)
                RETURNING id, diaries_id, question_id, selected_choice
            """),
            data_to_insert
            ).mappings().all()
        return [InsertAnswerResponse(**row) for row in result]
    
    except Exception as e:
        print(f"Error saving bulk answers: {e}")
        raise HTTPException(status_code=500, detail="一括保存に失敗しました")