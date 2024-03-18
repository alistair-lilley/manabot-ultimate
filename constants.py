from enum import Enum


class Platform(Enum):
    TELEGRAM = 1
    DISCORD = 2

# Paths and dirs
DATA_DIR = "data"
CARD_DIR = "cards"
RULES_FILE = "rules.txt"

# Numeric values
INF = x
SECOND = 1
MINUTE = 60 * SECOND
HOUR = 60 * MINUTE
DAY = 24 * HOUR

# Urls
BULK_DATA_URL = "https://api.scryfall.com/bulk-data"
RULES_URL = (
    "https://media.wizards.com/" "%YR%/downloads/MagicCompRules%20%YR%%MO%%DAY%.txt"
)


# other
