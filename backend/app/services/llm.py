from openai import OpenAI
from app.core.config import config


def get_client(api_key: str = None) -> OpenAI:
    """获取 LLM 客户端，api_key 为空时从环境变量读取"""
    key = api_key or config.DEEPSEEK_API_KEY
    if not key:
        raise RuntimeError("DeepSeek API Key 未设置，请在侧边栏输入或设置环境变量 DEEPSEEK_API_KEY")
    return OpenAI(
        api_key=key,
        base_url=config.DEEPSEEK_BASE_URL,
    )


def chat(messages: list[dict], temperature: float = 0.7, api_key: str = None) -> str:
    """调用 LLM 对话，返回文本响应"""
    client = get_client(api_key)
    response = client.chat.completions.create(
        model=config.LLM_MODEL,
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message.content
