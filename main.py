import asyncio
import discord
import argparse
import logging

from dotenv import dotenv_values

from botobjs.dcinter import DCInterface
from botobjs.tginter import TGInterface
from dbobjs import Database, CardDatabase, DBProxy

from constants import BULK_DATA_URL, RULES_URL

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s::%(levelname)s::%(module)s.%(funcName)s::%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser()
parser.add_argument("--clear", action="store_true")

config = dotenv_values(".env")

DCTOKEN = config["DCTOKEN"]
TGTOKEN = config["TGTOKEN"]

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

if __name__ == "__main__":
    args = parser.parse_args()
    dbproxy = DBProxy(BULK_DATA_URL, RULES_URL)
    carddb = CardDatabase()
    database = Database(dbproxy, carddb)
    if args.clear:
        database.clear_data()
    dcbot = DCInterface(database, intents=intents)
    tgbot = TGInterface(TGTOKEN, database)
    loop = asyncio.new_event_loop()
    # loop.run_until_complete(tgbot.bot.skip_updates())
    loop.create_task(database.run_check_update())
    loop.create_task(tgbot.start_polling(tgbot.bot))
    loop.create_task(dcbot.start(DCTOKEN))
    loop.run_forever()
