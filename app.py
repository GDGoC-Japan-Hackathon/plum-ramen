import sqlalchemy
from fastapi import FastAPI
from api.routers import diaries
from core.db import engine

app = FastAPI()

app.include_router(diaries.router)

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
