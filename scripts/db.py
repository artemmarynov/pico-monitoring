import asyncpg
from common.settings import DatabaseSettings
from dotenv import load_dotenv


async def connect():
    load_dotenv()
    return await asyncpg.connect(**DatabaseSettings().connect_kwargs())
