""" Card """

from __future__ import annotations

import logging

from typing import Dict, List, Any

import re

from constants import Platform

logger = logging.getLogger(__name__)

ARTSETCODELENGTH = 4

PRETTYFIELDS = {
    "name": "Name:",
    "mana_cost": "Cost:",
    "type_line": "Type:",
    "power": "Power:",
    "toughness": "Toughness:",
    "loyalty": "Loyalty:",
    "oracle_text": "Text:",
    "other_faces": "Other Faces:",
}

# These layouts aren't actually main cards, so we don't load them
IGNORELAYOUT = [
    "art_series",
    "emblem",
    "planar",
    "token",
    "double_faced_token",
    "vanguard",
    "scheme",
    "reversible_card",
]

DOUBLEFACE = [
    "transform",
    "modal_dfc",
]

SPLIT = [
    "adventure",
    "split",
    "flip",
]

REQUIRED = [
    "name",
    "mana_cost",
    "type_line",
    "oracle_text",
    "power",
    "toughness",
    "loyalty",
]

MKDN_CHARS = "_~`>#+-=|.![](){}*"


class Card:
    def __init__(self: Card, card_json_obj: Dict) -> None:
        self._json_obj = card_json_obj
        self._other_faces = None
        self._split_orientations = None
        self._fullface_image = None
        self.not_main_card = False
        self._bolding = {
            Platform.TELEGRAM: "*",
            Platform.DISCORD: "**",
        }
        self._card_data = self.parse_json()

    def parse_json(self: Card) -> Dict[str, Any]:
        fields = None
        # The cards with the "Card" type for their card type and dont have card faces
        # aren't real cards and we wanna ignore them too
        if self._json_obj["object"] == "card_face":
            fields = {}
        elif (
            self._json_obj["layout"] in IGNORELAYOUT
            or self._json_obj["type_line"] == "Card"
        ):
            self.not_main_card = True
        elif self._json_obj["layout"] in DOUBLEFACE:
            self._other_faces = self._json_obj["card_faces"]
        elif self._json_obj["layout"] in SPLIT:
            self._split_orientations = self._json_obj["card_faces"]
            self._fullface_image = self._json_obj["image_uris"]
        else:
            fields = {}
        if any([self._other_faces, self._split_orientations, self.not_main_card]):
            pass
        else:
            for corefield in REQUIRED:
                if corefield in self._json_obj:
                    fields[corefield] = self._json_obj[corefield]
        return fields

    def get_image_uri(self: Card, thumbnail: bool = False) -> str:
        try:
            assert self._other_faces == None
        except RuntimeError as e:
            err = (
                "Card requested is a multiface card and should not be accessed. "
                "If this happened, something got FUCKED up."
            )
            logger.critical(err)
            raise e(err)
        if "image_uris" in self._json_obj:
            if thumbnail:
                return self._json_obj["image_uris"]["small"]
            return self._json_obj["image_uris"]["large"]
        return "No URI found"

    def formatted_data(self: Card, tgdc: Platform) -> str:
        bold = self._bolding[tgdc]
        fields_pretty = PRETTYFIELDS.copy()
        for field in fields_pretty:
            fields_pretty[field] = f"{bold}{fields_pretty[field]}{bold}"
        data_fields = [
            (fieldkey, self._escape_non_mkdn(field)) if tgdc == Platform.TELEGRAM else field
            for fieldkey, field in self._card_data.items()
        ]
        out_lines = [f"{fields_pretty[fieldkey]} {field}" for fieldkey, field in data_fields]
        out_text = "\n".join(out_lines)
        return out_text

    def _escape_non_mkdn(self: Card, text: str) -> str:
        for char in MKDN_CHARS:
            text = re.sub(re.escape(char), "\\" + re.escape(char), text)
        return text

    @property
    def name(self: Card) -> str:
        return self._card_data["name"]

    @property
    def faces(self: Card) -> List[str]:
        return self._other_faces

    @property
    def split_orientations(self: Card) -> List[str]:
        return self._split_orientations

    @property
    def fullface_image(self: Card) -> Dict[str, List[str]]:
        return self._fullface_image

    @property
    def image_uri(self: Card) -> str:
        return self.get_image_uri()

    @property
    def thumbnail_uri(self: Card) -> str:
        return self.get_image_uri(thumbnail=True)

    @property
    def other_faces(self: Card) -> str:
        return ", ".join(self._card_data["other_faces"])

    @other_faces.setter
    def other_faces(self: Card, names: List[str]) -> None:
        self._card_data["other_faces"] = names
