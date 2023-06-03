from constants import CardFields

class Card:

    def __init__(self, card_json_obj):
        self._json_obj = card_json_obj
        self._card_data = self._parse_json()
        self.image_uri = self._get_image_uri()

    def _parse_json(self):
        fields = {}
        for corefield in CardFields.COREFIELDS:
            if corefield in self._json_obj:
                fields[corefield] = self._json_obj[corefield]
        return fields
        
    def _get_image_uri(self):
        if CardFields.IMAGE_URIS in self._json_obj:
            return self._json_obj[CardFields.IMAGE_URIS][CardFields.LARGE]
        return "No URI found"

    def _format(self):
        out_lines = [f"{CardFields.PRETTYFIELDS[field]} "
                     f"{self._card_data[field]}" for field in self._card_data]
        out_text = '\n'.join(out_lines)
        return out_text

    @property
    def formatted_data(self):
        return self._format()
    
    @property
    def name(self):
        return self._card_data[CardFields.NAME]