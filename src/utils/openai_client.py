from openai import AsyncOpenAI
from core.config import config as cfg

client = AsyncOpenAI(api_key=cfg.openai.api_key)
