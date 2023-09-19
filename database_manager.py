import os
import sqlite3

from dotenv import load_dotenv


class DBManager:
    def __init__(self):
        load_dotenv()
        self.database_path = os.getenv("DB_NAME")
        self.connection = sqlite3.connect(self.database_path)
        self.cursor = self.connection.cursor()

        self.cursor.execute(
            """
                CREATE TABLE IF NOT EXISTS "users" (
                    "id" INTEGER PRIMARY KEY,
                    "telegram_id" INTEGER NOT NULL UNIQUE,
                    "language" VARCHAR
                )
            """
        )

        self.cursor.execute(
            """
                CREATE TABLE IF NOT EXISTS "channels links" (
                    "id" INTEGER PRIMARY KEY,
                    "user_id" INTEGER,
                    "link" VARCHAR,
                    "title" VARCHAR,
                    "number of users" INTEGER,
                    FOREIGN KEY ("user_id") REFERENCES "users"("id")
                )
            """
        )

        self.cursor.execute(
            """
                CREATE TABLE IF NOT EXISTS "groups links" (
                    "id" INTEGER PRIMARY KEY,
                    "user_id" INTEGER,
                    "link" VARCHAR,
                    "title" VARCHAR,
                    "number of users" INTEGER,
                    FOREIGN KEY ("user_id") REFERENCES "users"("id")
                )
            """
        )

        self.connection.commit()

    def is_user_exists(self, telegram_id: int) -> bool:
        result = self.cursor.execute(
            """
            SELECT telegram_id
            FROM users
            WHERE telegram_id = ?
            """,
            (telegram_id,),
        ).fetchone()
        return result is not None

    def create_user(self, telegram_id: int) -> None:
        self.cursor.execute(
            """
            INSERT INTO users
            (telegram_id, language) VALUES (?, ?)
            """,
            (telegram_id, "ru"),
        )
        self.connection.commit()

    def change_language(self, telegram_id: int, language: str) -> None:
        self.cursor.execute(
            """
            UPDATE users
            SET language = ?
            WHERE telegram_id = ?
            """,
            (language, telegram_id),
        )
        self.connection.commit()

    def get_user_language(self, telegram_id: int) -> str:
        language = self.cursor.execute(
            """
            SELECT language
            FROM users
            WHERE telegram_id = ?
            """,
            (telegram_id,),
        ).fetchone()

        return language[0]

    def get_user_pk_by_telegram_id(self, telegram_id: int) -> int:
        user_pk = self.cursor.execute(
            """
            SELECT id
            FROM "users"
            WHERE telegram_id = ?
            """,
            (telegram_id,),
        ).fetchone()

        return user_pk[0]

    def add_new_scrape_request(
        self,
        telegram_id: int,
        entity_type: str,
        entity_link: str,
        entity_title: str,
        number_of_users: int,
    ) -> None:
        user_pk = self.get_user_pk_by_telegram_id(telegram_id=telegram_id)

        table_name = "channels links" if entity_type == "channel" else "groups links"

        self.cursor.execute(
            f"""
            INSERT INTO "{table_name}"
            (user_id, link, title, "number of users") VALUES (?, ?, ?, ?)
            """,
            (user_pk, entity_link, entity_title, number_of_users),
        )
        self.connection.commit()
