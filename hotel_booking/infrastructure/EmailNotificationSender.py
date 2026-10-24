from ..domain.reservation import Reservation


class EmailNotificationSender:
    """Simulates email delivery; no real messages are sent."""

    def __init__(self) -> None:
        self.sent = 0

    def send_confirmation(self, reservation: Reservation) -> None:
        self.sent += 1
