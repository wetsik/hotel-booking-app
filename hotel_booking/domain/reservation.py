from enum import Enum

from .date_range import DateRange
from .guest import Guest
from .room import Room


class ReservationStatus(Enum):
    CONFIRMED = "Confirmed"
    CANCELLED = "Cancelled"


class Reservation:
    def __init__(self, reservation_id: str, guest: Guest, room: Room, stay: DateRange) -> None:
        self.id = reservation_id
        self.guest = guest
        self.room = room
        self.stay = stay
        self.status = ReservationStatus.CONFIRMED

    def blocks(self, room: Room, stay: DateRange) -> bool:
        return (
            self.status == ReservationStatus.CONFIRMED
            and self.room == room
            and self.stay.overlaps(stay)
        )

    def cancel(self) -> bool:
        if self.status == ReservationStatus.CANCELLED:
            return False
        self.status = ReservationStatus.CANCELLED
        return True
