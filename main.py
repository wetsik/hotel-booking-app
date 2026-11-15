
# main.py
"""Composition Root for the Hotel Booking application."""

import sys
from contextlib import contextmanager

import uvicorn
from redis import Redis

from hotel_booking.api import create_app, Stats, CountingReservationStore
from hotel_booking.api_cache import AvailabilityCache, RedisKeyValueStore
from hotel_booking.rooms import Room
from hotel_booking.reservations import BookingService
from hotel_booking.reservations.internal import InMemoryReservationStore
from hotel_booking.notifications.internal import EmailNotificationSender
from hotel_booking.payments.internal import SimulatedPaymentProcessor

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from hotel_booking.rooms.internal import PostgresRoomCatalog
from hotel_booking.reservations.internal import PostgresReservationStore


def create_application(slow_step_seconds: float = 0):
    rooms = [
        Room("R7", "Standard"),
        Room("R8", "Deluxe"),
    ]

    store = InMemoryReservationStore()
    notifications = EmailNotificationSender()
    payments = SimulatedPaymentProcessor()

    booking_service = BookingService(
        rooms=rooms,
        store=store,
        email=notifications,
        slow_step_seconds=slow_step_seconds,
    )

    return booking_service, store, notifications, payments



def run_api() -> None:
    db_port = os.getenv("HOTEL_DB_PORT", "5432")

    engine = create_engine(
        f"postgresql+psycopg://hotel:hotel@localhost:{db_port}/hotel"
    )

    rooms = PostgresRoomCatalog(engine).all()
    notifications = EmailNotificationSender()
    stats = Stats()

    redis = Redis(
        host="localhost",
        port=int(os.getenv("HOTEL_REDIS_PORT", "6379")),
        decode_responses=True,
    )
    redis.ping()
    cache = AvailabilityCache(RedisKeyValueStore(redis))

    @contextmanager
    def unit_of_work():
        with Session(engine) as session:
            store = PostgresReservationStore(session, rooms)

            yield BookingService(
                rooms,
                CountingReservationStore(store, stats),
                notifications,
            )

            store.save_changes()

    uvicorn.run(
        create_app(rooms, unit_of_work, stats, cache),
        host="localhost",
        port=5080,
    )




def main() -> None:
    if len(sys.argv) == 1:
        run_api()

    elif sys.argv[1] == "--demo":
        from hotel_booking.demo import run_demo
        run_demo()

    elif sys.argv[1] == "--race":
        from hotel_booking.demo import run_race
        run_race()

    else:
        raise SystemExit(
            f"Unknown argument: {sys.argv[1]}"
        )


if __name__ == "__main__":
    main()
