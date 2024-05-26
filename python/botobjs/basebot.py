from __future__ import annotations

from typing import List, Tuple


class BaseBot:
    def _extract_cards(self: BaseBot, content: str) -> List[str]:
        # No cards before the first [[
        split_on_open = content.split("[[")[1:]
        # Only the cards within ]]
        split_on_close = [block.split("]]")[0] for block in split_on_open]
        return split_on_close

    def _extract_set_code(self: BaseBot, content: str) -> str:
        if content.count("#") != 1:
            return None
        return content.split("#")[1]
