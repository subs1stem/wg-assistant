from os import environ

from dotenv import load_dotenv

load_dotenv()


def get_bot_token() -> str:
    token = environ.get('TOKEN')
    if not token:
        raise RuntimeError('Missing required environment variable: TOKEN')
    return token


def get_bot_admins() -> list[int]:
    raw = environ.get('ADMIN_ID')
    if not raw:
        raise RuntimeError('Missing required environment variable: ADMIN_ID')
    try:
        return [int(x) for x in raw.split(',')]
    except ValueError:
        raise RuntimeError('ADMIN_ID must contain comma-separated integers')
