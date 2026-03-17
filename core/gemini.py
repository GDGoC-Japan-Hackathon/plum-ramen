from functools import lru_cache
from google import genai
from google.genai import types
import os

@lru_cache
def get_gemini_client():
    return genai.Client(
        vertexai=True,
        project=os.environ["GOOGLE_CLOUD_PROJECT"],
        location=os.environ["GOOGLE_CLOUD_LOCATION"],
        http_options=types.HttpOptions(api_version="v1"),
    )