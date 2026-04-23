import os
from .utils import load_config

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

CONFIG = load_config()
API_KEY = os.environ.get("OPENAI_API_KEY") or CONFIG.get("api_key")
BASE_URL = os.environ.get("OPENAI_BASE_URL") or CONFIG.get("base_url", "http://localhost:1234/v1")
MODEL = os.environ.get("OPENAI_MODEL") or CONFIG.get("model", "local-model")

if OpenAI is not None:
    client = OpenAI(
        api_key=API_KEY,
        base_url=BASE_URL
    )
else:
    client = None

def call_llm(system: str, user: str, temperature: float = 0.1):
    """
    Calls the LLM API.
    """
    if client is None:
        print("[LLM ERROR] OpenAI client unavailable. Install the openai package or configure a local API endpoint.")
        return None

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=temperature,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"[LLM ERROR] Failed to call LLM: {e}")
        return None
