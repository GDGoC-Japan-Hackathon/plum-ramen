from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

router = APIRouter()
templates = Jinja2Templates(directory="templates")
router.mount("/static", StaticFiles(directory="static"), name="static")

@router.get("/")
def root(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
    )

@router.get("/diary-list", response_class=HTMLResponse)
def diary_list_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="diary_list.html",
        context={},
    )

@router.get("/diary-form", response_class=HTMLResponse)
def diary_form_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="diary_form.html",
        context={},
    )

@router.get("/answer-questions", response_class=HTMLResponse)
def answer_questions_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="answer_questions.html",
        context={},
    )

@router.get("/display-result", response_class=HTMLResponse)
def display_result_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="display_result.html",
        context={},
    )

@router.get("/generate-loading", response_class=HTMLResponse)
def generate_loading_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="generate_loading.html",
        context={},
    )
