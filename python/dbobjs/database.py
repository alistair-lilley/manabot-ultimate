"""Database object"""

from __future__ import annotations

import asyncio
import logging

from dbobjs import DBProxy, CardDatabase
from constants import Platform

from typing import List, TYPE_CHECKING

# from dbobjs.rulesdb import Rules

from constants import DAY

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from carddb import CardResult

MAXATTEMPT = 3

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

    def retrieve_card(self: Database, cardname: str, tgdc: Platform) -> List[CardResult]:
        """Retrieves a single card"""
        return self._carddb.get_card(cardname, tgdc)

    # def retrieve_rule(self, rulename) -> str:
    #     return self._rulesdb.retrieve_rule(rulename)

    async def run_check_update(self: Database) -> None:
        """Loops and checks for updates every day"""
        attempt = 0
        while True:
            try:
                updated = await self._dbproxy.loop_check_updates()
            except:
                attempt += 1
                logger.critical(f"Updating failed. Attempts: {attempt}/{MAXATTEMPT}") 
                if attempt == MAXATTEMPT:
                    logger.critical("Updating failed. Shutting down container.")
                    import sys
                    sys.exit()  
            if updated:
                self._carddb.parse_db()
                # self._rulesdb.make_rules_tree()
            await asyncio.sleep(DAY)
