

class BaseBot:

    def _extract_cards(self, content):
        # No cards before the first [[
        split_on_open = content.split("[[")[1:] 
        # Only the cards within ]]
        split_on_close = [block.split("]]")[0] for block in split_on_open]
        return split_on_close
    