from dataclasses import dataclass


@dataclass(frozen=True)
class BookingResult:
    outcome: str
    reservation_id: str | None = None
    notification_failed: bool = False

    def __str__(self) -> str:
        if self.reservation_id is None:
            return self.outcome
        return f"{self.outcome} {self.reservation_id}"
