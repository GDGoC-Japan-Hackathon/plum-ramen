import os
import sqlalchemy
from fastapi import FastAPI
from google.cloud.sql.connector import Connector, IPTypes

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


@app.post("/diaries")
def create_diary(body: str):
    try:
        with engine.begin() as conn:
            result = conn.execute(
                sqlalchemy.text("""
                    INSERT INTO diaries (user_id, body)
                    VALUES (:user_id, :body)
                    RETURNING id, user_id, body, created_at
                """),
                {"user_id": 1, "body": body}
            ).mappings().fetchone()

        return {"success": True, "data": dict(result)}

    except Exception as e:
        return {"success": False, "message": str(e)}
