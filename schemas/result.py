from pydantic import BaseModel
from schemas.questions import GenerateQuestionsRequest, GenerateQuestionsResponse
from schemas.answers import InsertAnswerRequest

class GenerateResultRequest(BaseModel):
    diary: GenerateQuestionsRequest
    questions: GenerateQuestionsResponse
    answers: InsertAnswerRequest

class GenerateResultResponse(BaseModel):
    type: str
    ei_score: int
    sn_score: int
    tf_score: int
    jp_score: int
    summary: str

# 変更メモ
# diaries_idを外し、passにする
class InsertResultSummaryRequest(GenerateResultResponse):
    pass

class InsertResultSummaryResponse(BaseModel):
    id: int
    diaries_id: int
    type: str
    ei_score: int
    sn_score: int
    tf_score: int
    jp_score: int
    summary: str

class GetResultResponse(BaseModel):
    id: int
    user_id: int
    diaries_id: int
    type: str
    ei_score: int
    sn_score: int
    tf_score: int
    jp_score: int
    summary: str
