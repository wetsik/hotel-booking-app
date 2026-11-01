from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Confirmation:
    reservation_id: str
    guest_email: str
    room_number: str


class INotificationSender(Protocol):
    def send_confirmation(self, confirmation: Confirmation) -> None:
        ...


__all__ = ["Confirmation", "INotificationSender"]