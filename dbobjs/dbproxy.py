import os
import re
import aiohttp
import aiofiles
import requests
import json

from datetime import datetime

from constants import (DATA_DIR, CARD_DIR, RULES_FILE, LAST_UPDATE_FILE,
                       JSON_EXT, DBProxyFields, CardFields)

class DBProxy:
    
    def __init__(self, scryfall_url, rules_url):
        self._scryfall_db_url = scryfall_url
        self._rules_db_url = rules_url
        self._card_db_dir = os.path.join(DATA_DIR, CARD_DIR)
        self._rules_db_file = os.path.join(DATA_DIR, RULES_FILE)
        self._last_update_file = os.path.join(DATA_DIR, LAST_UPDATE_FILE)

    def clear_hash(self):
        with open(self._last_update_file, 'w') as f:
            f.write("")
    
    async def _update_db(self):
        async with aiohttp.ClientSession() as session:
            await self._update_card_db(session)
            await self._update_rules_db(session)

    async def _update_card_db(self, session):
        full_database_url = ""
        async with session.get(self._scryfall_db_url) as response:
            bulk_data = await response.json()
            data = bulk_data[DBProxyFields.DATA]
            for item in data:
                if item[DBProxyFields.BULK_DATA_TYPE] == \
                    DBProxyFields.ORACLE_CARDS:
                    full_database_url = item[DBProxyFields.DOWNLOAD_URI]
        async with session.get(full_database_url) as response:
            full_data = await response.json()
            await self._save_db(full_data)

    async def _update_rules_db(self, session):
        rules_url = await self._find_rules_url(session)
        async with session.get(rules_url) as response:
            rules_text = await response.text()
            with open(self._rules_db_file, 'w') as f:
                f.write(rules_text)

    async def _save_db(self, database):
        count = len(database)
        print(f"Saving card 0 of {count}", end='\r')
        for ii, card in enumerate(database):
            print(f"Saving card {ii+1} of {count}", end='\r')
            filename = self._simplify_name(card[CardFields.NAME]) + JSON_EXT
            filepath = os.path.join(self._card_db_dir, filename)
            async with aiofiles.open(filepath, 'w') as f:
                await f.write(json.dumps(card))

    def _check_update(self):
        if not os.path.exists(self._last_update_file):
            with open(self._last_update_file, 'w') as f:
                f.write("")
        last_update = open(self._last_update_file).read()
        bulk_data = requests.get(self._scryfall_db_url).json()
        data = bulk_data[DBProxyFields.DATA]
        newest_update = ""
        for item in data:
            if item[DBProxyFields.BULK_DATA_TYPE] == DBProxyFields.ORACLE_CARDS:
                newest_update = item[DBProxyFields.LAST_UPDATE]
        return not (newest_update == last_update)
    
    def _write_updated(self):
        newest_update = ""
        data = requests.get(self._scryfall_db_url).json()[DBProxyFields.DATA]
        for item in data:
            if item[DBProxyFields.BULK_DATA_TYPE] == DBProxyFields.ORACLE_CARDS:
                newest_update = item[DBProxyFields.LAST_UPDATE]
        with open(self._last_update_file, 'w') as f:
            f.write(newest_update)

    async def _find_rules_url(self, session):
        year, month, day = [int(piece) for piece in 
                            datetime.now().strftime("%Y %m %d").split()]
        url_completed = self._complete_url(self._rules_db_url, year, month, day)
        # Basically we work backwards to find the latest update
        while True:
            rulestext = await (await session.get(url_completed)).text()
            if rulestext != "Not found\n":
                return url_completed
            year, month, day = self._decrement_date(year, month, day)
            url_completed = self._complete_url(self._rules_db_url, year, month,
                                                day)
            if (year, month, day) == (1993, 1, 1):
                raise("Checked all dates, rules look up failed...")


    def _complete_url(self, rules_url, year, month, day):
        subs = {'YR': year, 'MO': month, 'DAY': day}
        for sub in subs:
            rules_url = re.sub(f"%{sub}%", str(subs[sub]), rules_url)
        return rules_url
    
    
    def _decrement_date(self, year, month, day):
        day -= 1
        if day == 0:
            day = 31
            month -= 1
        if month == 0:
            month = 12
            year -= 1
        return year, month, day

    def _simplify_name(self, name):
        return re.sub(r'[\W\s]', '', re.sub(r' ', '_', name)).lower()

    async def loop_check_updates(self):
        if self._check_update():
            print("Updating")
            await self._update_db()
            self._write_updated()
            print("\n")
            print("Updating done")
            return True
        print("Not updating")
        return False