import asyncio
import os

import aiofiles
from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BufferedInputFile
from dotenv import load_dotenv

import text_templates as tt
from database_manager import DBManager
from keyboards import languages_keyboard, menu_keyboard
from scrapers.channels_scraper import ChannelScraper
from scrapers.groups_scraper import GroupScraper

load_dotenv()

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher(bot=bot, storage=MemoryStorage())
router = Router()

db_manager = DBManager()


class States(StatesGroup):
    main_menu = State()
    choosing_language = State()
    input_group_url = State()
    input_channel_url = State()
    input_group_users_number = State()
    input_channel_users_number = State()


# --------------- ⬇️ START ⬇️ ---------------


@router.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    telegram_id = message.from_user.id
    if not db_manager.is_user_exists(telegram_id=telegram_id):
        db_manager.create_user(telegram_id=telegram_id)

    language = db_manager.get_user_language(telegram_id=telegram_id)

    await state.update_data(language=language)

    await message.answer(
        text=f"{tt.start_message.get(language)}",
        reply_markup=menu_keyboard(language),
    )


# --------------- ⬇️ SCRAPE GROUPS ⬇️ ---------------


@router.message(F.text == tt.scrape_chat.get("ru"))
@router.message(F.text == tt.scrape_chat.get("ua"))
async def scrape_group(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    language = state_data["language"]
    await message.answer(text=tt.input_group_link.get(language))
    await state.set_state(States.input_group_url)


@router.message(F.text, States.input_group_url)
async def input_group_url(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    language = state_data["language"]
    await state.update_data(url=message.text)
    await message.answer(text=tt.input_number_of_users.get(language))
    await state.set_state(States.input_group_users_number)


@router.message(F.text, States.input_group_users_number)
async def input_group_users_number(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    language, url, number_of_users = (
        state_data["language"],
        state_data.get("url"),
        message.text,
    )
    try:
        number_of_users = int(number_of_users)
    except ValueError:
        await message.answer(tt.number_of_users_error.get(language))
    await state.set_state(States.main_menu)
    await message.answer(text=tt.scrapping_starts.get(language))
    await send_scraped_group_file(
        message=message, group_url=url, number_of_users=number_of_users, state=state
    )


async def send_scraped_group_file(
    message: types.Message,
    group_url: str,
    state: FSMContext,
    number_of_users: int = None,
) -> None:
    state_data = await state.get_data()
    language = state_data["language"]
    try:
        scraper = GroupScraper()
        file_path = await scraper.run(group_url, number_of_users)
        url, number_of_users = (
            state_data.get("url"),
            message.text,
        )
        try:
            number_of_users = int(number_of_users)
        except ValueError:
            pass
        group_title = file_path.split(".")[0]
        db_manager.add_new_scrape_request(
            telegram_id=message.from_user.id,
            entity_type="group",
            entity_title=group_title,
            entity_link=url,
            number_of_users=number_of_users,
        )

        async with aiofiles.open(file_path, "rb") as file:
            await message.answer_document(
                BufferedInputFile(await file.read(), filename=file_path),
                caption=tt.scrapping_done_successfully.get(language),
            )
        try:
            os.remove(file_path)
            print(f"File {file_path} successfully deleted.")
        except OSError as e:
            print(f"Error: {e.filename} - {e.strerror}")
    except Exception:
        await message.answer(text=tt.parsing_error.get(language))


# --------------- ⬇️ SCRAPE CHANNELS ⬇️ ---------------


@router.message(F.text == tt.scrape_channel.get("ru"))
@router.message(F.text == tt.scrape_channel.get("ru"))
async def scrape_channel(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    language = state_data.get("language")
    await message.answer(text=tt.input_channel_link.get(language))
    await state.set_state(States.input_channel_url)


@router.message(F.text, States.input_channel_url)
async def input_group_url(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    language = state_data["language"]
    await state.update_data(url=message.text)
    await message.answer(text=tt.input_number_of_users.get(language))
    await state.set_state(States.input_channel_users_number)


@router.message(F.text, States.input_channel_users_number)
async def input_group_users_number(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    language, url, number_of_users = (
        state_data["language"],
        state_data.get("url"),
        message.text,
    )
    try:
        number_of_users = int(number_of_users)
    except ValueError:
        await message.answer(tt.number_of_users_error.get(language))
    await state.set_state(States.main_menu)
    await message.answer(text=tt.scrapping_starts.get(language))
    await send_scraped_channel_file(
        message=message, channel_url=url, number_of_users=number_of_users, state=state
    )


async def send_scraped_channel_file(
    message: types.Message,
    channel_url: str,
    state: FSMContext,
    number_of_users: int = None,
) -> None:
    state_data = await state.get_data()
    language = state_data["language"]
    try:
        scraper = ChannelScraper()
        file_path = await scraper.run(
            entity_url=channel_url, number_of_users=number_of_users
        )
        url, number_of_users = (
            state_data.get("url"),
            message.text,
        )
        try:
            number_of_users = int(number_of_users)
        except ValueError:
            pass
        channel_title = file_path.split(".")[0]
        db_manager.add_new_scrape_request(
            telegram_id=message.from_user.id,
            entity_type="channel",
            entity_title=channel_title,
            entity_link=url,
            number_of_users=number_of_users,
        )

        async with aiofiles.open(file_path, "rb") as file:
            await message.answer_document(
                BufferedInputFile(await file.read(), filename=file_path),
                caption=tt.scrapping_done_successfully.get(language),
            )
        try:
            os.remove(file_path)
            print(f"File {file_path} successfully deleted.")
        except OSError as e:
            print(f"Error: {e.filename} - {e.strerror}")
    except Exception:
        await message.answer(text=tt.parsing_error.get(language))


# --------------- ⬇️ CHOOSING LANGUAGE ⬇️ ---------------


@router.message(F.text == tt.language.get("ru"))
@router.message(F.text == tt.language.get("ua"))
async def show_language(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    language = state_data["language"]
    await message.answer(
        text=tt.select_action_placeholder.get(language),
        reply_markup=languages_keyboard(language),
    )

    await state.set_state(States.choosing_language)


@router.message(F.text == tt.ru_lang.get("ru"), States.choosing_language)
@router.message(F.text == tt.ru_lang.get("ua"), States.choosing_language)
async def choose_language(message: types.Message, state: FSMContext):
    await state.clear()
    telegram_id = message.from_user.id
    db_manager.change_language(telegram_id=telegram_id, language="ru")
    await state.update_data(language="ru")
    await message.answer(
        text=f"{tt.language_selected.get('ru')}",
        reply_markup=menu_keyboard("ru"),
    )
    await state.set_state(States.main_menu)


@router.message(F.text == tt.ua_lang.get("ru"), States.choosing_language)
@router.message(F.text == tt.ua_lang.get("ua"), States.choosing_language)
async def choose_language(message: types.Message, state: FSMContext):
    await state.clear()
    telegram_id = message.from_user.id
    db_manager.change_language(telegram_id=telegram_id, language="ua")
    await state.update_data(language="ua")
    await message.answer(
        text=f"{tt.language_selected.get('ua')}",
        reply_markup=menu_keyboard("ua"),
    )
    await state.set_state(States.main_menu)


async def main():
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
