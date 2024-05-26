"""Database object"""

from __future__ import annotations

import asyncio

from dbobjs import DBProxy, CardDatabase, Card
from constants import Platform

# from dbobjs.rulesdb import Rules

from constants import DAY


class Database:
    """Database object"""

    def __init__(
        self: Database, dbproxy: DBProxy, carddb: CardDatabase
    ) -> None:  # , rulesdb):
        self._dbproxy = dbproxy
        self._carddb = carddb
        # self._rulesdb = Rules()

    def clear_data(self: Database) -> None:
        """Clears all data in the database, used on startup sometimes"""
        self._dbproxy.clear_hash()
        self._carddb.clear_card_database()
        # self._rulesdb.clear_rules()

    def retrieve_card(self: Database, cardname: str, tgdc: Platform) -> Card:
        """Retrieves a single card"""
        return self._carddb.get_card(cardname, tgdc)

    # def retrieve_rule(self, rulename) -> str:
    #     return self._rulesdb.retrieve_rule(rulename)

    async def run_check_update(self: Database) -> None:
        """Loops and checks for updates every day"""
        while True:
            updated = await self._dbproxy.loop_check_updates()
            if updated:
                self._carddb.parse_db()
                # self._rulesdb.make_rules_tree()
            await asyncio.sleep(DAY)
