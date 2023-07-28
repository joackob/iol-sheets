from enum import Enum


class Scope(Enum):
    def __str__(self) -> str:
        return self.value

    READONLY = "https://www.googleapis.com/auth/spreadsheets.readonly"
    WRITEABLE = "https://www.googleapis.com/auth/spreadsheets"
