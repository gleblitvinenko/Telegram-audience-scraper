import csv

from telethon.tl import types
from telethon.tl.types import User

from scrapers.scraper import Scraper


class ChannelScraper(Scraper):
    """Class for scraping users from a channel and dumping to CSV."""
    async def get_entity_data(self, entity_url: str) -> dict[str, str | int]:
        """
            Get entity data for the channel.

            Args:
                entity_url (str): The URL of the channel.

            Returns:
                dict: A dictionary containing channel title and channel ID.
        """
        channel_data = await self.client.get_entity(entity_url)
        return {"channel_title": channel_data.title, "channel_id": channel_data.id}

    async def get_users_from_entity(
        self, entity_url: str, number_of_users: int = 1000
    ) -> list[types.User]:
        """
            Get users from the channel.

            Args:
                entity_url (str): The URL of the channel.
                number_of_users (int): The number of users to retrieve (default is 1000).

            Returns:
                list[types.User]: A list of users from the channel.
        """
        channel_data = await self.client.get_entity(entity_url)
        channel_id = channel_data.id
        commentators = []
        counter = 0
        async for post in self.client.iter_messages(channel_id):
            async for message in self.client.iter_messages(
                channel_id, reply_to=post.id
            ):
                if counter == number_of_users:
                    return commentators
                if (
                    isinstance(message.__dict__.get("_sender"), User)
                    and message.__dict__.get("_sender") not in commentators
                ):
                    commentators.append((message.__dict__.get("_sender")))
                    counter += 1

    async def dump_users(self, entity_url, number_of_users: int) -> str:
        """
            Dump users to a CSV file.

            Args:
                entity_url (str): The URL of the channel.
                number_of_users (int): The number of users to dump.

            Returns:
                str: The file path of the dumped CSV file.
        """
        channel_title = (await self.get_entity_data(entity_url)).get("channel_title")
        channel_id = (await self.get_entity_data(entity_url)).get("channel_id")
        users = await self.get_users_from_entity(entity_url, number_of_users)

        with open(f"{channel_title}.csv", "w", encoding="UTF-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(self.CSV_ROW)
            for user in users:
                writer.writerow(
                    [
                        user.__dict__.get("username"),
                        user.__dict__.get("id"),
                        user.__dict__.get("access_hash"),
                        user.__dict__.get("first_name"),
                        user.__dict__.get("last_name"),
                        user.__dict__.get("phone"),
                        channel_title,
                        channel_id,
                    ]
                )

        return f"{channel_title}.csv"

    async def run(self, entity_url: str, number_of_users: int):
        """
            Run the scraping process.

            Args:
                entity_url (str): The URL of the channel.
                number_of_users (int): The number of users to scrape.

            Returns:
                str: The file path of the dumped CSV file.
        """
        async with self.client:
            file_path = await self.dump_users(entity_url, number_of_users)
            return file_path
