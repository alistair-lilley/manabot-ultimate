from aiogram import Bot, Dispatcher, types
from aiogram.utils import markdown

from botobjs.basebot import BaseBot

class TGInterface(Dispatcher, BaseBot):

    def __init__(self, token, database):
        self._bot = Bot(token)
        super().__init__(self._bot)
        self._database = database
        self.register_message_handler(self.on_message)

    async def on_message(self, message: types.Message):

        if "[[" in message.text and "]]" in message.text:
            cardnames = self._extract_cards(message.text)
            cards = [self._database.retrieve_card(card) for card in cardnames]
            for card in cards:
                await message.answer(card.image)
                await message.answer(card.text)

        elif message.text.startswith("!rule"):
            rule_query = message.text.split(' ', 1)[1:][0]
            rule = self._database.retrieve_rule(rule_query)
            await message.answer(rule)