import os
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv

# 加载 .env 文件（向上查找直到找到）
_env_path = Path(__file__).resolve().parent.parent.parent / ".env"
if _env_path.exists():
    load_dotenv(_env_path)


@dataclass
class Config:
    """全局配置，从环境变量读取"""

    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "deepseek-chat")

    INTERVIEW_MAX_ROUNDS: int = int(os.getenv("INTERVIEW_MAX_ROUNDS", "5"))

    CORS_ORIGINS: list = None

    def __post_init__(self):
        if self.CORS_ORIGINS is None:
            origins = os.getenv("CORS_ORIGINS", "*")
            self.CORS_ORIGINS = origins.split(",") if origins != "*" else ["*"]


config = Config()
