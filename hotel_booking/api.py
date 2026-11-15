"""The HTTP API: requests become BookingService calls and HTTP responses."""
from __future__ import annotations

import re
import threading
from contextlib import AbstractContextManager
from datetime import date
from pathlib import Path
from typing import Any, Callable

from fastapi import Body, FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response

from hotel_booking.reservations import BookingResult, BookingService, DateRange, Guest, Reservation, IReservationStore
from hotel_booking.rooms import Room
from hotel_booking.api_cache import AvailabilityCache

UnitOfWork = Callable[[], AbstractContextManager[BookingService]]
FIELDS = ("guestName", "guestEmail", "room", "checkIn", "checkOut")
BODY_DETAIL = "The body must be JSON with guestName, guestEmail, room, checkIn and checkOut."
DATE_DETAIL = "checkIn and checkOut must be dates such as 2026-11-12."



class Stats:
    """Thread-safe counters for GET /stats."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._counts = {
            "searches": 0,
            "databaseQueries": 0,
            "cacheHits": 0,
            "cacheMisses": 0,
        }

    def add(self, name: str) -> None:
        with self._lock:
            self._counts[name] += 1

    def as_dict(self) -> dict[str, int]:
        with self._lock:
            return dict(self._counts)


class CountingReservationStore:
    """Delegates to a store and counts database operations."""

    def __init__(self, store: IReservationStore, stats: Stats) -> None:
        self._store = store
        self._stats = stats

    def count(self) -> int:
        self._stats.add("databaseQueries")
        return self._store.count()

    def has_overlap(self, room: Room, stay: DateRange) -> bool:
        self._stats.add("databaseQueries")
        return self._store.has_overlap(room, stay)

    def save(self, reservation: Reservation) -> None:
        self._stats.add("databaseQueries")
        self._store.save(reservation)

    def find(self, reservation_id: str) -> Reservation | None:
        self._stats.add("databaseQueries")
        return self._store.find(reservation_id)

    def count_confirmed(self, room: Room, stay: DateRange) -> int:
        self._stats.add("databaseQueries")
        return self._store.count_confirmed(room, stay)


def problem(status: int, title: str, detail: str) -> JSONResponse:
    return JSONResponse(
        {"title": title, "status": status, "detail": detail},
        status_code=status,
        media_type="application/problem+json",
    )


def parse_date(text: Any) -> date | None:
    if not isinstance(text, str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", text):
        return None
    try:
        return date.fromisoformat(text)
    except ValueError:
        return None


def to_http(result: BookingResult) -> JSONResponse:
    if result.outcome == "Accepted":
        return JSONResponse(
            {
                "id": result.reservation_id,
                "status": "Confirmed",
                "notificationFailed": result.notification_failed,
            },
            status_code=201,
        )
    if result.outcome == "Unavailable":
        return problem(409, "Unavailable", "The room is booked for at least one night of this stay.")
    return problem(400, "InvalidDates", "checkOut must be after checkIn.")


def create_app(rooms: list[Room], unit_of_work: UnitOfWork, stats: Stats, cache: AvailabilityCache) -> FastAPI:
    app = FastAPI(openapi_url=None, docs_url=None, redoc_url=None)

    @app.exception_handler(RequestValidationError)
    def not_json(request, error) -> JSONResponse:
        return problem(400, "InvalidRequest", BODY_DETAIL)

    @app.get("/openapi.yaml")
    def contract() -> Response:
        path = Path(__file__).resolve().parent.parent / "docs" / "openapi.yaml"
        return Response(path.read_text(encoding="utf-8"), media_type="application/yaml")

    @app.get("/stats")
    def read_stats() -> JSONResponse:
        return JSONResponse(stats.as_dict())

    @app.get("/rooms/availability")
    def find_free_rooms(checkIn: str = "", checkOut: str = "", limit: str = "20", after: str = "") -> JSONResponse:
        check_in, check_out = parse_date(checkIn), parse_date(checkOut)
        if check_in is None or check_out is None:
            return problem(400, "InvalidDates", DATE_DETAIL)
        stay = DateRange(check_in, check_out)
        if not stay.is_valid():
            return problem(400, "InvalidDates", "checkOut must be after checkIn.")
        if not re.fullmatch(r"[0-9]{1,3}", limit) or not 1 <= int(limit) <= 100:
            return problem(400, "InvalidRequest", "limit must be a whole number from 1 to 100.")

        stats.add("searches")

        # Redis first; PostgreSQL only on a cache miss.
        key = cache.key(checkIn, checkOut)
        cached = cache.get(key)

        if cached is not None:
            stats.add("cacheHits")
            numbers = cached.split(",")
            free = [room for room in rooms if room.number in numbers]
        else:
            stats.add("cacheMisses")
            with unit_of_work() as service:
                free = service.find_free_rooms(stay)

            cache.set(key, ",".join(sorted(room.number for room in free)))
        rest = sorted((room for room in free if room.number > after), key=lambda room: room.number)
        page = rest[:int(limit)]
        return JSONResponse({
            "checkIn": checkIn,
            "checkOut": checkOut,
            "rooms": [{"number": room.number, "type": room.type} for room in page],
            "next": page[-1].number if len(rest) > len(page) else None,
        })

    @app.post("/reservations")
    def reserve(body: Any = Body(None)) -> JSONResponse:
        if not isinstance(body, dict) or not all(isinstance(body.get(field), str) and body[field] for field in FIELDS):
            return problem(400, "InvalidRequest", BODY_DETAIL)
        check_in, check_out = parse_date(body["checkIn"]), parse_date(body["checkOut"])
        if check_in is None or check_out is None:
            return problem(400, "InvalidDates", DATE_DETAIL)
        room = next((room for room in rooms if room.number == body["room"]), None)
        if room is None:
            return problem(400, "UnknownRoom", f"There is no room {body['room']}.")

        with unit_of_work() as service:
            result = service.reserve(Guest(body["guestName"], body["guestEmail"]), room, DateRange(check_in, check_out))
        return to_http(result)

    @app.delete("/reservations/{reservation_id}")
    def cancel(reservation_id: str) -> Response:
        with unit_of_work() as service:
            cancelled = service.cancel(reservation_id)
        if not cancelled:
            return problem(404, "NotFound", f"There is no confirmed reservation {reservation_id}.")
        return Response(status_code=204)

    return app
