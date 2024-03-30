""" Card database
    Loads and manages card objects, based on local database
"""

from __future__ import annotations

import re
import os
import json
import logging

from typing import Dict, List

from os import path

from collections import namedtuple
from editdistance import eval

from dbobjs.card import Card

from constants import DATA_DIR, CARD_DIR, Platform

logger = logging.getLogger(__name__)

SimCard = namedtuple("SimilarCard", "card similarity")
CardResult = namedtuple("CardResult", "image text")


class CardDatabase:
    """Card database
    This object stores info about cards, including card objects and a list of card names
    It is used to retrieve cards from searches, primarily"""

    def __init__(self: CardDatabase) -> None:
        self._db_dir = os.path.join(DATA_DIR, CARD_DIR)
        if not os.path.isdir(DATA_DIR):
            os.mkdir(DATA_DIR)
            logger.info("No data dir; creating data dir")
        if not os.path.isdir(self._db_dir):
            os.mkdir(self._db_dir)
            logger.info("No card dir in data dir; creating data dir")
        self._cards: Dict[str, Card] = None
        self._card_list: List[str] = None
        self.parse_db()

    def clear_card_database(self: CardDatabase) -> None:
        """Deletes the entire card database; generally used during testing"""
        for f in os.listdir(self._db_dir):
            os.remove(os.path.join(self._db_dir, f))

    def parse_db(self: CardDatabase) -> None:
        """Parses all json files from the database into card objects
        and stores them in this object"""
        logger.info("Loading card database")
        cards = {}
        full_db = [
            json.load(open(path.join(self._db_dir, card)))
            for card in os.listdir(self._db_dir)
        ]
        for card_entry in full_db:
            card = Card(card_entry)
            # We don't want to load things like tokens and emblems
            if card.not_main_card:
                continue
            # We want to load the individual faces of a card, not the double-face-card object
            if card.faces or card.split_orientations:
                if card.faces:
                    faces = [Card(face) for face in card.faces]
                elif card.split_orientations:
                    faces = [
                        Card({**orientation, "image_uris": card.fullface_image})
                        for orientation in card.split_orientations
                    ]
                face_names = [face.name for face in faces]
                for ff, face in enumerate(faces):
                    face.other_faces = [
                        face_names[facenum]
                        for facenum, _ in enumerate(face_names)
                        if facenum != ff
                    ]
                    cards[self._simplify_name(face.name)] = face
            else:
                cards[self._simplify_name(card.name)] = card
        self._cards = cards
        self._card_list = sorted([name for name in self._cards.keys()])
        logger.info("Card database loaded")

    def get_card(self: CardDatabase, card_search: str, tgdc: Platform) -> CardResult:
        """Retrieves a single card by name, checking if its a sub-name and checkin for similar
        names if it is not found as a single card"""
        logger.info(f"Fetching card by query {card_search}")
        cardname = self._simplify_name(card_search)
        matched_card = None
        # People might search for the first part of a card name, such as searching "Ashaya" for
        # "Ashaya, Soul of the Wild"; this should catch that
        if cardname not in self._cards:
            matched_card = self._search_subname(cardname)
        if not matched_card:
            matched_card = self._search_similar(cardname)
        if not matched_card:
            matched_card = cardname
        logger.info(f"Retrieved card: {matched_card}")
        return self._retrieve(matched_card, tgdc)

    def _search_subname(self: CardDatabase, cardname: str) -> str:
        cnamelower = cardname.lower()
        for dbcard in self._card_list:
            if re.match(f"^{cnamelower}", dbcard.lower()):
                return dbcard.lower()
        return None

    def _search_similar(self: CardDatabase, tgtcard: str) -> str:
        most_similar = SimCard(None, float("inf"))
        for dbcard in self._card_list:
            similarity = eval(tgtcard, dbcard)
            if similarity < most_similar.similarity:
                most_similar = SimCard(dbcard, similarity)
        return most_similar.card

    def _retrieve(self: CardDatabase, cardname: str, tgdc: Platform) -> CardResult:
        card = self._cards[cardname]
        image = card.image_uri
        text = card.formatted_data(tgdc)
        return CardResult(image, text)

    def _simplify_name(self: CardDatabase, name: str) -> str:
        return re.sub(r"[\W\s]", "", re.sub(r" ", "_", name)).lower()
