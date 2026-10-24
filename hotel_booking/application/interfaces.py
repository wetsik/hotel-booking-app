
from typing import Protocol

from hotel_booking.domain.date_range import DateRange
from hotel_booking.domain.room import Room
from hotel_booking.domain.reservation import Reservation


class IReservationStore(Protocol):
    def count(self) -> int: ...

    def has_overlap(self, room: Room, stay: DateRange) -> bool: ...

    def save(self, reservation: Reservation) -> None: ...

    def find(self, reservation_id: str) -> Reservation | None: ...

    def count_confirmed(self, room: Room, stay: DateRange) -> int: ...


class INotificationSender(Protocol):
    def send_confirmation(self, reservation: Reservation) -> None: ...
