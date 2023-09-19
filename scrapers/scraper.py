import os
from abc import ABC, abstractmethod

from dotenv import load_dotenv
from telethon import TelegramClient


class Scraper(ABC):
    """Abstract base class for scrapers."""
    def __init__(self) -> None:
        """
            Initialize the scraper.

            This constructor initializes common properties and sets up the Telegram client.

        """
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
        """
            Get entity data from the provided URL.

            Args:
                entity_url (str): The URL of the entity.

            Returns:
                dict: A dictionary containing entity data.
        """
        pass

    @abstractmethod
    async def get_users_from_entity(self, entity_url: str, number_of_users: int):
        """
            Get users from the provided entity URL.

            Args:
                entity_url (str): The URL of the entity.
                number_of_users (int): The number of users to retrieve.

            Returns:
                list: A list of users.
        """
        pass

    @abstractmethod
    async def dump_users(self, entity_url: str, number_of_users: int):
        """
            Dump users to a storage.

            Args:
                entity_url (str): The URL of the entity.
                number_of_users (int): The number of users to dump.

            Returns:
                str: The file path or storage identifier.
        """
        pass

    @abstractmethod
    async def run(self, entity_url: str, number_of_users: int):
        """
            Run the scraper.

            Args:
                entity_url (str): The URL of the entity.
                number_of_users (int): The number of users to scrape.

            Returns:
                str: The file path or storage identifier.
        """
        pass
