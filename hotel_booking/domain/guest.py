from dataclasses import dataclass


@dataclass(frozen=True)
class Guest:
    name: str
    email: str
