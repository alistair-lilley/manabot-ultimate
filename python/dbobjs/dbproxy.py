"""Database Proxy"""

from __future__ import annotations

import os
import re
import aiohttp
import aiofiles
import requests
import json
import logging

from typing import Dict

# from datetime import datetime

from constants import (
    DATA_DIR,
    CARD_DIR,
    RULES_FILE,
)

logger = logging.getLogger(__name__)

LAST_UPDATE_FILE = "updated.txt"


class DBProxy:
    """Database proxy: interface between bot and scryfall for loading card database
    also wotc for rules file but thats later"""

    def __init__(self: DBProxy, scryfall_url: str, rules_url: str) -> None:
        self._scryfall_db_url = scryfall_url
        self._rules_db_url = rules_url
        self._card_db_dir = os.path.join(DATA_DIR, CARD_DIR)
        self._rules_db_file = os.path.join(DATA_DIR, RULES_FILE)
        self._last_update_file = os.path.join(DATA_DIR, LAST_UPDATE_FILE)

    def clear_hash(self: DBProxy) -> None:
        with open(self._last_update_file, "w") as f:
            f.write("")

    async def _update_db(self: DBProxy) -> None:
        async with aiohttp.ClientSession() as session:
            await self._update_card_db(session)
            # await self._update_rules_db(session)

    async def _update_card_db(self: DBProxy, session: aiohttp.ClientSession) -> None:
        full_database_url = ""
        async with session.get(self._scryfall_db_url) as response:
            bulk_data = await response.json()
            data = bulk_data["data"]
            for item in data:
                if item["type"] == "oracle_cards":
                    full_database_url = item["download_uri"]
        async with session.get(full_database_url) as response:
            full_data = await response.json()
            await self._save_db(full_data)

    async def _save_db(self: DBProxy, database: Dict) -> None:
        logger.info("Savings all cards")
        count = len(database)
        for ii, card in enumerate(database):
            print(f"Saving card {ii+1} of {count}", end="\r")
            filename = self._simplify_name(card["name"]) + ".json"
            filepath = os.path.join(self._card_db_dir, filename)
            async with aiofiles.open(filepath, "w") as f:
                await f.write(json.dumps(card))
        logger.info("All cards saved to database")

    def _check_update(self: DBProxy) -> bool:
        if not os.path.exists(self._last_update_file):
            with open(self._last_update_file, "w") as f:
                f.write("")
        last_update = open(self._last_update_file).read()
        bulk_data = requests.get(self._scryfall_db_url).json()
        data = bulk_data["data"]
        newest_update = ""
        for item in data:
            if item["type"] == "oracle_cards":
                newest_update = item["updated_at"]
        return not (newest_update == last_update)

    def _write_updated(self: DBProxy) -> None:
        newest_update = ""
        data = requests.get(self._scryfall_db_url).json()["data"]
        for item in data:
            if item["type"] == "oracle_cards":
                newest_update = item["updated_at"]
        with open(self._last_update_file, "w") as f:
            f.write(newest_update)

    # async def _update_rules_db(self: DBProxy, session):
    #     rules_url = await self._find_rules_url(session)
    #     async with session.get(rules_url) as response:
    #         rules_text = await response.text()
    #         with open(self._rules_db_file, "w") as f:
    #             f.write(rules_text)

    # async def _find_rules_url(self: DBProxy, session):
    #     year, month, day = [
    #         int(piece) for piece in datetime.now().strftime("%Y %m %d").split()
    #     ]
    #     url_completed = self._complete_url(self._rules_db_url, year, month, day)
    #     # Basically we work backwards to find the latest update
    #     while True:
    #         rulestext = await (await session.get(url_completed)).text()
    #         if rulestext != "Not found\n":
    #             return url_completed
    #         year, month, day = self._decrement_date(year, month, day)
    #         url_completed = self._complete_url(self._rules_db_url, year, month, day)
    #         if (year, month, day) == (1993, 1, 1):
    #             raise ("Checked all dates, rules look up failed...")

    # def _complete_url(self: DBProxy, rules_url, year, month, day):
    #     subs = {"YR": year, "MO": month, "DAY": day}
    #     for sub in subs:
    #         rules_url = re.sub(f"%{sub}%", str(subs[sub]), rules_url)
    #     return rules_url

    # def _decrement_date(self: DBProxy, year, month, day):
    #     day -= 1
    #     if day == 0:
    #         day = 31
    #         month -= 1
    #     if month == 0:
    #         month = 12
    #         year -= 1
    #     return year, month, day

    def _simplify_name(self: DBProxy, name) -> str:
        return re.sub(r"[\W\s]", "", re.sub(r" ", "_", name)).lower()

    async def loop_check_updates(self: DBProxy) -> bool:
        logger.info("Starting check update loop")
        if self._check_update():
            logger.info("Updating")
            await self._update_db()
            self._write_updated()
            logger.info("Updating done")
            return True
        logger.info("Not updating")
        return False
