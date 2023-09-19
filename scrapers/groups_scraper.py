import asyncio
import csv

from telethon.tl import types

from scrapers.scraper import Scraper


class GroupScraper(Scraper):
    async def get_entity_data(self, entity_url: str) -> dict[str, str | int]:
        group_data = await self.client.get_entity(entity_url)
        return {"group_title": group_data.title, "group_id": group_data.id}

    async def get_users_from_entity(
        self, entity_url: str, number_of_users: int
    ) -> list[types.User]:
        group_data = await self.client.get_entity(entity_url)
        users = await self.client.get_participants(group_data)
        try:
            return users[:number_of_users]
        except Exception:
            return users

    async def dump_users(self, entity_url: str, number_of_users: int) -> str:
        group_title = (await self.get_entity_data(entity_url)).get("group_title")
        group_id = (await self.get_entity_data(entity_url)).get("group_id")
        users = await self.get_users_from_entity(entity_url, number_of_users)

        with open(f"{group_title}.csv", "w", encoding="UTF-8", newline="") as file:
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
                        group_title,
                        group_id,
                    ]
                )

        return f"{group_title}.csv"

    async def run(self, entity_url: str, number_of_users: int) -> str:
        async with self.client:
            file_path = await self.dump_users(entity_url, number_of_users)
            return file_path

