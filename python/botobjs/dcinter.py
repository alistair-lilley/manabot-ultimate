"""Discord interface"""

from __future__ import annotations

import discord

from typing import List

from dbobjs import CardResult, Database

from constants import Platform

from botobjs.basebot import BaseBot


class DCInterface(discord.Client, BaseBot):
    def __init__(self, database: Database, intents=None):
        self._database = database
        super().__init__(intents=intents)

    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return

        # elif message.content.startswith("!rule"):
        #     rule_query = message.content.split(" ", 1)[1:]
        #     rule = self._database.retrieve_rule(rule_query)
        #     await message.channel.send(rule)

        elif "[[" in message.content and "]]" in message.content:
            cardnames = self._extract_cards(message.content)
            cards: List[CardResult] = [
                cardobj
                for card in cardnames
                for cardobj in self._database.retrieve_card(card, Platform.DISCORD)
            ]
            for card in cards:
                await message.channel.send(f"{card.image}\n{card.text}")
