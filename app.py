import sqlalchemy
from fastapi import FastAPI
from api.routers import diaries
from api.routers import questions
from api.routers import answers
from api.routers import result
from api.routers import common
from api.routers import auth
from core.db import engine
from web.routers import pages

app = FastAPI()

app.include_router(diaries.router)
app.include_router(questions.router)
app.include_router(answers.router)
app.include_router(result.router)
app.include_router(common.router)
app.include_router(auth.router)
app.include_router(pages.router)

@app.get("/users")
def get_users():
    with engine.connect() as conn:
        rows = conn.execute(
            sqlalchemy.text("SELECT id, name FROM users ORDER BY id")
        ).mappings().all()

    return {"items": [dict(row) for row in rows]}

@app.get("/tables")
def get_tables():
    with engine.connect() as conn:
        rows = conn.execute(
            sqlalchemy.text(
                """
                SELECT tablename
                FROM pg_catalog.pg_tables
                WHERE schemaname = 'public'
                ORDER BY tablename
                """
            )
        ).scalars().all()

    return rows
