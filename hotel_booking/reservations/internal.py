from __future__ import annotations

from datetime import date

from sqlalchemy import exists, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from .date_range import DateRange
from .domain import Guest, Reservation
from hotel_booking.rooms import Room


class InMemoryReservationStore:
    """In-memory store, intentionally mirroring the P03 example."""

    def __init__(self) -> None:
        self._rows: list[Reservation] = []

    def count(self) -> int:
        return len(self._rows)

    def has_overlap(self, room: Room, stay: DateRange) -> bool:
        return any(row.blocks(room, stay) for row in self._rows)

    def save(self, reservation: Reservation) -> None:
        self._rows.append(reservation)

    def find(self, reservation_id: str) -> Reservation | None:
        return next((row for row in self._rows if row.id == reservation_id), None)

    def count_confirmed(self, room: Room, stay: DateRange) -> int:
        return sum(1 for row in self._rows if row.blocks(room, stay))


class ReservationsTables(DeclarativeBase):
    """Tables owned by the Reservations module."""


class ReservationRow(ReservationsTables):
    """A reservation row in PostgreSQL."""

    __tablename__ = "reservations"

    id: Mapped[str] = mapped_column(primary_key=True)
    guest_name: Mapped[str]
    guest_email: Mapped[str]
    room: Mapped[str]
    check_in: Mapped[date]
    check_out: Mapped[date]
    status: Mapped[str]


class PostgresReservationStore:
    """PostgreSQL implementation of the reservation store."""

    def __init__(self, session: Session, rooms: list[Room]) -> None:
        self._session = session
        self._rooms = {room.number: room for room in rooms}
        self._loaded: list[tuple[ReservationRow, Reservation]] = []

    def count(self) -> int:
        return self._session.scalar(
            select(func.count()).select_from(ReservationRow)
        )

    def has_overlap(self, room: Room, stay: DateRange) -> bool:
        return bool(
            self._session.scalar(
                select(exists(self._confirmed(room, stay)))
            )
        )

    def save(self, reservation: Reservation) -> None:
        row = ReservationRow(
            id=reservation.id,
            guest_name=reservation.guest.name,
            guest_email=reservation.guest.email,
            room=reservation.room.number,
            check_in=reservation.stay.check_in,
            check_out=reservation.stay.check_out,
            status=reservation.status.value,
        )

        self._session.add(row)
        self._session.flush()

    def find(self, reservation_id: str) -> Reservation | None:
        row = self._session.get(ReservationRow, reservation_id)

        if row is None:
            return None

        reservation = Reservation(
            row.id,
            Guest(row.guest_name, row.guest_email),
            self._rooms[row.room],
            DateRange(row.check_in, row.check_out),
        )

        if row.status == "Cancelled":
            reservation.cancel()

        self._loaded.append((row, reservation))
        return reservation

    def count_confirmed(self, room: Room, stay: DateRange) -> int:
        return self._session.scalar(
            select(func.count()).select_from(
                self._confirmed(room, stay).subquery()
            )
        )

    def save_changes(self) -> None:
        """Persist status changes and commit."""

        for row, reservation in self._loaded:
            row.status = reservation.status.value

        self._session.commit()

    @staticmethod
    def _confirmed(room: Room, stay: DateRange):
        return select(ReservationRow.id).where(
            ReservationRow.room == room.number,
            ReservationRow.status == "Confirmed",
            ReservationRow.check_in < stay.check_out,
            stay.check_in < ReservationRow.check_out,
        )
