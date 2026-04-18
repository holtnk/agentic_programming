from pathlib import Path
import yaml
import time
from openai import OpenAI


# -----------------------------
# Load config safely
# -----------------------------
CONFIG_PATH = Path(__file__).resolve().parents[1] / "config.yaml"

with open(CONFIG_PATH, "r") as f:
    CONFIG = yaml.safe_load(f)


client = OpenAI(
    base_url=CONFIG["base_url"],
    api_key=CONFIG.get("api_key", "lm-studio")
)


# -----------------------------
# Core LLM call with retries
# -----------------------------
def call_llm(system, user, temperature=0.2, max_retries=2):
    last_error = None

    for attempt in range(max_retries + 1):
        try:
            resp = client.chat.completions.create(
                model=CONFIG["model"],
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user}
                ],
                temperature=temperature,
                timeout=CONFIG.get("timeout", 60)
            )

            # Validate response
            if not resp or not resp.choices:
                raise ValueError("Empty response from model")

            content = resp.choices[0].message.content

            if content is None or not isinstance(content, str):
                raise ValueError("Invalid model output")

            return content.strip()

        except Exception as e:
            last_error = e
            print(f"[LLM ERROR] attempt {attempt+1}/{max_retries+1}: {e}")

            # Backoff before retry
            time.sleep(1.5 * (attempt + 1))

    # Final failure fallback
    raise RuntimeError(f"LLM call failed after retries: {last_error}")