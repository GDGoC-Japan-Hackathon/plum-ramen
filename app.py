from fastapi import FastAPI
from api.routers import diaries
from api.routers import questions
from api.routers import answers
from api.routers import result
from api.routers import common
from web.routers import pages

app = FastAPI()

app.include_router(diaries.router)
app.include_router(questions.router)
app.include_router(answers.router)
app.include_router(result.router)
app.include_router(common.router)
app.include_router(pages.router)
