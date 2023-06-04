import hashlib

from aiogram import Bot, Dispatcher, types

from botobjs.basebot import BaseBot

class TGInterface(Dispatcher, BaseBot):

    def __init__(self, token, database):
        self._bot = Bot(token)
        super().__init__(self._bot)
        self._database = database
        self.register_message_handler(self.on_message)
        self.register_inline_handler(self.on_inline)

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
    
    async def on_inline(self, inline_query: types.InlineQuery):
        card = inline_query.query
        full_card = self._database.retrieve_card(card)
        image = types.InputTextMessageContent(full_card.image)
        text = types.InputTextMessageContent(full_card.text)
        result_id: str = hashlib.md5(card.encode()).hexdigest()
        image_item = types.InlineQueryResultArticle(
            id=result_id,
            title=f"Image link",
            input_message_content=image
        )
        text_item = types.InlineQueryResultArticle(
            id=result_id+"1",
            title=f"Card text",
            input_message_content=text
        )
        await self._bot.answer_inline_query(inline_query.id,
                                             results=[image_item, text_item],
                                               cache_time=1)