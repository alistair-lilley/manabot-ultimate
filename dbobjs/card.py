import re

from constants import CardFields
from constants import TELEGRAM_MSG, MKDN_CHARS

class Card:

    def __init__(self, card_json_obj):
        self._json_obj = card_json_obj
        self._multi_faced = False
        self._other_faces = None
        self._card_data = self._parse_json()
        self.image_uri = self._get_image_uri()

    def _parse_json(self):
        fields = {}
        if CardFields.CARD_FACES in self._json_obj:
            fields[CardFields.FACES] = self._json_obj[CardFields.CARD_FACES]
            self._multi_faced = True
        else:
            for corefield in CardFields.COREFIELDS:
                if corefield in self._json_obj:
                    fields[corefield] = self._json_obj[corefield]
        return fields
        
    def _get_image_uri(self):
        if self._multi_faced:
            return "Multi faced"
        if CardFields.IMAGE_URIS in self._json_obj:
            return self._json_obj[CardFields.IMAGE_URIS][CardFields.LARGE]
        return "No URI found"

    def _format(self, tgdc):
        prettyfields = CardFields.PRETTYFIELDS
        bolding = '*' if tgdc == TELEGRAM_MSG else '**'
        for field in prettyfields:
            prettyfields[field] = f'{bolding}{prettyfields[field]}{bolding}'
        out_lines = [f"{prettyfields[field]} "
                     f"{self._card_data[field]}" for field in self._card_data]
        out_text = self._fix_formatting('\n'.join(out_lines)) \
            if tgdc == TELEGRAM_MSG else '\n'.join(out_lines)
        return out_text
    
    def _is_art_set(self):
        return len(self._json_obj[CardFields.SET]) == 4 \
            and self._json_obj[CardFields.SET].startswith('a')

    def formatted_data(self, tgdc):
        return self._format(tgdc)
    
    def _fix_formatting(self, text):
        for char in MKDN_CHARS:
            text = re.sub(re.escape(char), "\\" + re.escape(char), text)
        return text
    
    @property
    def name(self):
        return self._card_data[CardFields.NAME]
    
    @property
    def is_multi_faced(self):
        return self._multi_faced
    
    @property
    def faces(self):
        return self._card_data[CardFields.FACES]
    
    @property
    def other_faces(self):
        print(self._card_data[CardFields.OTHER_FACES])
        return ', '.join(self._card_data[CardFields.OTHER_FACES])
    
    @other_faces.setter
    def other_faces(self, names):
        self._card_data[CardFields.OTHER_FACES] = ', '.join(names)

    @property
    def is_art_set(self):
        return self._is_art_set()