# Card fields
class CardFields:
    NAME = "name"
    MANA_COST = "mana_cost"
    #COLOR_ID = "color_identity"
    #CMC = "cmc"
    TYPE = "type_line"
    #KEYWORDS = "keywords"
    POWER = "power"
    TOUGHNESS = "toughness"
    LOYALTY = "loyalty"
    TEXT = "oracle_text"
    IMAGE_URIS = "image_uris"
    LARGE = "large"
    #ALL_PARTS = "all_parts" # not sure how to implement this
    COREFIELDS = [
        NAME,
        MANA_COST,
        TYPE,
        POWER,
        TOUGHNESS,
        LOYALTY,
        TEXT,
    ]
    PRETTYFIELDS = {
        NAME: "Name:",
        MANA_COST: "Cost:",
        TYPE: "Type:",
        POWER: "Power:",
        TOUGHNESS: "Toughness:",
        LOYALTY: "Loyalty:",
        TEXT: "Text:",
    }

# Database download fields
class DBProxyFields:
    DATA = "data"
    BULK_DATA_TYPE = "type"
    ORACLE_CARDS = "oracle_cards"
    DOWNLOAD_URI = "download_uri"
    LAST_UPDATE = "updated_at"

# Paths and dirs
DATA_DIR = "data"
CARD_DIR = "cards"
JSON_EXT = ".json"
RULES_FILE = "rules.txt"
LAST_UPDATE_FILE = "updated.txt"

# Numeric values
INF = float('inf')
SECOND = 1
MINUTE = 60 * SECOND
HOUR = 60 * MINUTE
DAY = 24 * HOUR

# Urls
BULK_DATA_URL = "https://api.scryfall.com/bulk-data"
RULES_URL = "https://media.wizards.com/" \
                "%YR%/downloads/MagicCompRules%20%YR%%MO%%DAY%.txt"