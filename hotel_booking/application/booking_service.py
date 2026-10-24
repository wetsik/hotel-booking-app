import time

from ..domain.date_range import DateRange
from ..domain.guest import Guest
from ..domain.reservation import Reservation
from ..domain.room import Room
from .interfaces import IReservationStore, INotificationSender
from .booking_result import BookingResult


class BookingService:
    def __init__(
        self,
        rooms: list[Room],
        store: IReservationStore,
        email: INotificationSender,
        slow_step_seconds: float = 0,
    ) -> None:
        self.rooms = rooms
        self.store = store
        self.email = email
        self.slow_step_seconds = slow_step_seconds

    def find_free_rooms(self, stay: DateRange) -> list[Room]:
        return [room for room in self.rooms if not self.store.has_overlap(room, stay)]

    def reserve(self, guest: Guest, room: Room, stay: DateRange) -> BookingResult:
        if not stay.is_valid():
            return BookingResult("InvalidDates")
        if self.store.has_overlap(room, stay):
            return BookingResult("Unavailable")

        time.sleep(self.slow_step_seconds)

        reservation = Reservation(f"R{101 + self.store.count()}", guest, room, stay)
        self.store.save(reservation)
        self.email.send_confirmation(reservation)
        return BookingResult("Accepted", reservation.id)

    def cancel(self, reservation_id: str) -> bool:
        reservation = self.store.find(reservation_id)
        return reservation is not None and reservation.cancel()
