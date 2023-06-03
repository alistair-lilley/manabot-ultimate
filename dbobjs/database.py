import asyncio

from dbobjs.dbproxy import DBProxy
from dbobjs.rulesdb import Rules
from dbobjs.carddb import CardDatabase

from constants import DAY

class Database:

    def __init__(self, scryfall_url, rules_url):
        self._dbproxy = DBProxy(scryfall_url, rules_url)
        self._rulesdb = Rules()
        self._carddb = CardDatabase()

    def clear_data(self):
        self._dbproxy.clear_hash()
        self._rulesdb.clear_rules()
        self._carddb.clear_cards()
    
    def retrieve_card(self, cardname):
        return self._carddb.get_card(cardname)
    
    def retrieve_rule(self, rulename):
        return self._rulesdb.retrieve_rule(rulename)
    
    async def run_check_update(self):
        while True:
            updated = await self._dbproxy.loop_check_updates()
            if updated:
                self._carddb.parse_db()
                self._rulesdb.make_rules_tree()
            await asyncio.sleep(DAY)