from typing import Protocol

from hotel_booking.rooms import Room
from .date_range import DateRange
from .domain import Reservation


class IReservationStore(Protocol):
    def count(self) -> int: ...

    def has_overlap(self, room: Room, stay: DateRange) -> bool: ...

    def save(self, reservation: Reservation) -> None: ...

    def find(self, reservation_id: str) -> Reservation | None: ...

    def count_confirmed(self, room: Room, stay: DateRange) -> int: ...