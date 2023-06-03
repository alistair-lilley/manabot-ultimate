import discord

from botobjs.basebot import BaseBot

class DCInterface(discord.Client, BaseBot):

    def __init__(self, database, intents=None):
        self._database = database
        super().__init__(intents=intents)

    async def on_message(self, message):
        if message.author == self.user:
            return
        
        elif message.content.startswith("!rule"):
            rule_query = message.content.split(' ', 1)[1:]
            rule = self._database.retrieve_rule(rule_query)
            await message.channel.send(rule)
        
        elif "[[" in message.content and "]]" in message.content:
            cardnames = self._extract_cards(message.content)
            cards = [self._database.retrieve_card(card) for card in cardnames]
            for card in cards:
                await message.channel.send(card.text)
                await message.channel.send(card.image)
                