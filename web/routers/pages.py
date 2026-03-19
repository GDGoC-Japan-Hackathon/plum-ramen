import json
import os

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

router = APIRouter()
templates = Jinja2Templates(directory="templates")
router.mount("/static", StaticFiles(directory="static"), name="static")

@router.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={},
    )


@router.get("/firebase-config.js")
def firebase_config():
    firebase_config = {
        "apiKey": os.getenv("FIREBASE_API_KEY", ""),
        "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN", ""),
        "projectId": os.getenv("FIREBASE_PROJECT_ID", ""),
        "appId": os.getenv("FIREBASE_APP_ID", ""),
        "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID", ""),
        "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET", ""),
        "measurementId": os.getenv("FIREBASE_MEASUREMENT_ID", ""),
    }
    sdk_version = os.getenv("FIREBASE_WEB_SDK_VERSION", "11.6.0")

    body = (
        f"window.__FIREBASE_CONFIG__ = {json.dumps(firebase_config, ensure_ascii=False)};\n"
        f"window.__FIREBASE_SDK_VERSION__ = {json.dumps(sdk_version)};\n"
    )
    return Response(content=body, media_type="application/javascript")

@router.get("/_test_list", response_class=HTMLResponse)
def test_list_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="_test_list.html",
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
