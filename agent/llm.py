import yaml
from pathlib import Path
from openai import OpenAI

CONFIG_PATH = Path(__file__).resolve().parents[1] / "config.yaml"

with open(CONFIG_PATH, "r") as f:
    CONFIG = yaml.safe_load(f)

# Initialize OpenAI client with local base URL
client = OpenAI(
    api_key=CONFIG.get("api_key", "sk-not-needed-for-local"),
    base_url=CONFIG.get("base_url", "http://localhost:1234/v1")
)

def call_llm(system: str, user: str, temperature: float = 0.1):
    """
    Calls the LLM API.
    """
    try:
        response = client.chat.completions.create(
            model=CONFIG.get("model", "local-model"),
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
