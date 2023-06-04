import re
import os
import json

from os import path

from collections import namedtuple
from editdistance import eval

from dbobjs.card import Card

from constants import DATA_DIR, CARD_DIR, INF

SimCard = namedtuple("SimilarCard", "card similarity")
CardResult = namedtuple("CardResult", "image text")

class CardDatabase:

    def __init__(self):
        self._db_dir = os.path.join(DATA_DIR, CARD_DIR)
        if not os.path.isdir(DATA_DIR):
            os.mkdir(DATA_DIR)
        if not os.path.isdir(self._db_dir):
            os.mkdir(self._db_dir)
        self._cards = None
        self._card_list = None
        self.parse_db()
    
    def clear_cards(self):
        for f in os.listdir(self._db_dir):
            os.remove(os.path.join(self._db_dir, f))

    def parse_db(self):
        print("loading card db")
        cards = {}
        full_db = [json.load(open(path.join(self._db_dir, card))) 
                   for card in os.listdir(self._db_dir)]
        for card_entry in full_db:
            card = Card(card_entry)
            cards[self._simplify_name(card.name)] = card
        self._cards = cards
        self._card_list = sorted([self._simplify_name(name)
                                  for name in self._cards.keys()])
        print("card db loaded")

    def get_card(self, card_search):
        cardname = self._simplify_name(card_search)
        if cardname not in self._cards:
            cardname = self._search_similar(cardname)
        return self._retrieve(cardname)

    def _search_similar(self, tgtcard):
        most_similar = SimCard(None, INF)
        for dbcard in self._card_list:
            similarity = eval(tgtcard, dbcard)
            if similarity < most_similar.similarity:
                most_similar = SimCard(dbcard, similarity)
        return most_similar.card

    def _retrieve(self, cardname):
        card = self._cards[cardname]
        image = card.image_uri
        text = card.formatted_data
        return CardResult(image, text)

    def _simplify_name(self, name):
        return re.sub(r'[\W\s]', '', re.sub(r' ', '_', name)).lower()