import sqlalchemy
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from api.routers import diaries
from api.routers import questions
from api.routers import answers
from api.routers import result
from api.routers import common
from core.db import engine

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(diaries.router)
app.include_router(questions.router)
app.include_router(answers.router)
app.include_router(result.router)
app.include_router(common.router)

@app.get("/diary-form", response_class=HTMLResponse)
def diary_form_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="diary_form.html",
        context={},
    )

@app.get("/answer-questions", response_class=HTMLResponse)
def answer_questions_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="answer_questions.html",
        context={},
    )

@app.get("/display-result", response_class=HTMLResponse)
def display_result_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="display_result.html",
        context={},
    )

@app.get("/generate-loading", response_class=HTMLResponse)
def generate_loading_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="generate_loading.html",
        context={},
    )

@app.get("/")
def root(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="base.html",
        context={
            "page_title": "今日の記録",
            "active_page": "editor",
        },
    )

@app.get("/_test_list", response_class=HTMLResponse)
def test_list_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="_test_list.html",
        context={},
    )

@app.get("/diaries", response_class=HTMLResponse)
def diaries_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="diaries.html",
        context={
            "page_title": "過去帳",
            "active_page": "diaries",
            "main_class": "overflow-hidden",
        },
    )

@app.get("/generate-question", response_class=HTMLResponse)
def generate_question_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="generate-question.html",
        context={},
    )

@app.get("/questions", response_class=HTMLResponse)
def questions_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="questions.html",
        context={},
    )

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
