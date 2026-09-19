"""
LLM Client — OpenRouter (Gemini 2.5 Flash)
API key comes ONLY from st.secrets["OPENROUTER_API_KEY"].
In Streamlit Cloud: Settings → Secrets → paste:
    OPENROUTER_API_KEY = "sk-or-xxxxxxxxxxxx"
"""
import streamlit as st
from openai import OpenAI

OPENROUTER_BASE = "https://openrouter.ai/api/v1"
MODEL           = "google/gemini-2.5-flash"


def get_client() -> OpenAI:
    api_key = st.secrets["OPENROUTER_API_KEY"]
    return OpenAI(
        base_url=OPENROUTER_BASE,
        api_key=api_key,
        default_headers={
            "HTTP-Referer": "https://lexaguard.ai",
            "X-Title": "LexaGuard AI",
        },
    )


def chat(client: OpenAI, messages: list[dict],
         temperature: float = 0.2, max_tokens: int = 4096) -> str:
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content.strip()
