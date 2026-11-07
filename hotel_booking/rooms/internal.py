
# hotel_booking/rooms/internal.py
from __future__ import annotations

from sqlalchemy import Engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from hotel_booking.rooms.catalog import Room


class InMemoryRoomCatalog:
    """Keeps rooms in memory."""

    def __init__(self, rooms: list[Room]) -> None:
        self._rooms = list(rooms)

    def all(self) -> list[Room]:
        return list(self._rooms)


class RoomsTables(DeclarativeBase):
    """Tables owned by the Rooms module."""


class RoomRow(RoomsTables):
    """The rooms table defined in db/init.sql."""

    __tablename__ = "rooms"

    number: Mapped[str] = mapped_column(primary_key=True)
    type: Mapped[str]


class PostgresRoomCatalog:
    """Reads rooms from PostgreSQL."""

    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def all(self) -> list[Room]:
        with Session(self._engine) as session:
            return [
                Room(row.number, row.type)
                for row in session.scalars(select(RoomRow))
            ]
