from functools import lru_cache
from google import genai
from google.genai import types
import os

DEFAULT_GEMINI_LOCATION = "asia-northeast1"


def _get_project_id() -> str:
    for key in (
        "GOOGLE_CLOUD_PROJECT",
        "GCP_PROJECT",
        "GCLOUD_PROJECT",
        "FIREBASE_PROJECT_ID",
    ):
        value = os.getenv(key)
        if value:
            return value

    raise RuntimeError(
        "Google Cloud project is not configured. Set GOOGLE_CLOUD_PROJECT."
    )


def _get_location() -> str:
    for key in (
        "GOOGLE_CLOUD_LOCATION",
        "GOOGLE_CLOUD_REGION",
        "VERTEX_AI_LOCATION",
    ):
        value = os.getenv(key)
        if value:
            return value

    return DEFAULT_GEMINI_LOCATION


@lru_cache
def get_gemini_client():
    return genai.Client(
        vertexai=True,
        project=_get_project_id(),
        location=_get_location(),
        http_options=types.HttpOptions(api_version="v1"),
    )
