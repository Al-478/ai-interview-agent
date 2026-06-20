from openai import OpenAI
from app.core.config import config

_client = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=config.DEEPSEEK_API_KEY,
            base_url=config.DEEPSEEK_BASE_URL,
        )
    return _client


def chat(messages: list[dict], temperature: float = 0.7) -> str:
    """调用 LLM 对话，返回文本响应"""
    client = get_client()
    response = client.chat.completions.create(
        model=config.LLM_MODEL,
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message.content
