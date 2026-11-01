from dataclasses import dataclass


@dataclass(frozen=True)
class Room:
    number: str
    type: str
