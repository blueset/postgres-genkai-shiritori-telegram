import os
from dotenv import load_dotenv


def fetch_env_var(key: str, optional: bool = False) -> str:
    val = os.getenv(key)
    if val is None and not optional:
        raise Exception(f"{key} is not set.")
    return val


load_dotenv()

TELEGRAM_BOT_TOKEN = fetch_env_var("TELEGRAM_BOT_TOKEN")
DATABASE_NAME = fetch_env_var("DATABASE_NAME")
DATABASE_USER = fetch_env_var("DATABASE_USER")
DATABASE_PASSWORD = fetch_env_var("DATABASE_PASSWORD")
DATABASE_HOST = fetch_env_var("DATABASE_HOST")
DATABASE_PORT = int(fetch_env_var("DATABASE_PORT"))

WEBHOOK_URL = fetch_env_var("WEBHOOK_URL", optional=True)
