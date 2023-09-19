import os
from abc import ABC, abstractmethod

from dotenv import load_dotenv
from telethon import TelegramClient


class Scraper(ABC):
    def __init__(self) -> None:
        self.CSV_ROW = [
            "username",
            "user id",
            "access hash",
            "first name",
            "last name",
            "phone",
            "group name",
            "group id",
        ]
        load_dotenv()
        API_ID, API_HASH = int(os.getenv("API_ID")), os.getenv("API_HASH")
        self.client = TelegramClient("anon", API_ID, API_HASH)

    @abstractmethod
    async def get_entity_data(self, entity_url: str):
        pass

    @abstractmethod
    async def get_users_from_entity(self, entity_url: str, number_of_users: int):
        pass

    @abstractmethod
    async def dump_users(self, entity_url: str, number_of_users: int):
        pass

    @abstractmethod
    async def run(self, entity_url: str, number_of_users: int):
        pass
