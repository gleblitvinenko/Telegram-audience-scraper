# Telegram audience scraper

## How to run:

* `git clone https://github.com/gleblitvinenko/Telegram-audience-scraper.git`

* `cd telegram-audience-scraper`

* `pip install requirements.txt`

* `python -m venv venv`

* `venv/Scripts/activate`

* Go to the website `https://my.telegram.org/apps` and register app to get App `api_id` and `api_hash`

* Go to the `https://t.me/BotFather` and register new bot and get bot token to access the HTTP API.

* Then enter in .env file `API_ID` `API_HASH` `BOT_TOKEN` `DB_NAME`

* Then run `main.py` and input in console necessary data.

## Note:

#### Many groups and channels have protection for such scraping. 
