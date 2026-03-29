from typing import Optional


class DefenceStock:
    def __init__(
        self,
        name: str,
        code: str,
        themes: list[str],
        id: Optional[int] = None,
    ):
        self.id = id
        self.name = name
        self.code = code
        self.themes = themes
