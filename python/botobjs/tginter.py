"""Telegram interface"""

from __future__ import annotations

import logging

from typing import List

import hashlib

from aiogram import Bot, Dispatcher, types
from aiogram.utils import markdown

from dbobjs import CardResult, Database

from constants import Platform

from botobjs.basebot import BaseBot

logger = logging.getLogger(__name__)


class TGInterface(Dispatcher, BaseBot):
    def __init__(self, token: str, database: Database):
        super().__init__()
        self.bot = Bot(token)
        self._database = database
        self.message.register(self.on_message)
        self.inline_query.register(self.on_inline)

    async def on_message(self, message: types.Message):
        logger.info(f"Got in chat request on telegram: {message.text}")
        if "[[" in message.text and "]]" in message.text:
            cardnames = self._extract_cards(message.text)
            cards: List[CardResult] = [
                cardobj
                for card in cardnames
                for cardobj in self._database.retrieve_card(card, Platform.TELEGRAM)
            ]
            for card in cards:
                logger.info(f"{card}")
            for card in cards:
                await message.answer_photo(
                    photo=card.image, caption=card.text, parse_mode="MarkdownV2"
                )

        # elif message.text.startswith("!rule"):
        #     rule_query = message.text.split(" ", 1)[1:][0]
        #     rule = self._database.retrieve_rule(rule_query)
        #     await message.answer(rule)

    async def on_inline(self, inline_query: types.InlineQuery):
        logger.info(f"Got inline request on telegram: {inline_query.query}")
        card = inline_query.query
        full_card: CardResult = self._database.retrieve_card(card, Platform.TELEGRAM)
        name = full_card.text.split("\n")[0]
        result_id: str = hashlib.md5(card.encode()).hexdigest()
        image_item = types.InlineQueryResultPhoto(
            id=result_id,
            title=name,
            photo_url=full_card.image,
            thumbnail_url=full_card.thumbnail,
            caption=full_card.text,
            parse_mode="MarkdownV2",
        )
        await self.bot.answer_inline_query(
            inline_query.id, results=[image_item], cache_time=1
        )
