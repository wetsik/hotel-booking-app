from ..domain.reservation import Reservation


class SmsNotificationSender:
    def __init__(self) -> None:
        self.sent = 0

    def send_confirmation(self, reservation: Reservation) -> None:
        self.sent += 1